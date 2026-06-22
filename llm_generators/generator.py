from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field, computed_field, create_model
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from llm_generators.prompts import (
    instagram_prompt,
    facebook_prompt,
    twitter_prompt,
    linkedin_prompt,
    blog_prompt,
)

# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

Platform = Literal["instagram", "facebook", "twitter", "linkedin", "blog post"]


class PlatformContent(BaseModel):
    """Generated content for a single platform."""

    platform: str = Field(..., description="Target platform name.")
    content: str = Field(..., description="Generated, platform-optimised text.")
    success: bool = Field(..., description="False if generation failed.")
    error: str | None = Field(
        default=None, description="Error message when success is False."
    )

    @computed_field  # type: ignore[misc]
    @property
    def word_count(self) -> int:
        """Approximate word count of the generated content."""
        return len(self.content.split())


class ContentGenerationResult(BaseModel):
    """Aggregated result returned by generate_response()."""

    results: dict[str, PlatformContent] = Field(
        default_factory=dict,
        description="Mapping of platform name → PlatformContent.",
    )

    @computed_field  # type: ignore[misc]
    @property
    def succeeded(self) -> list[str]:
        """Platforms that were generated successfully."""
        return [p for p, c in self.results.items() if c.success]

    @computed_field  # type: ignore[misc]
    @property
    def failed(self) -> list[str]:
        """Platforms where generation failed."""
        return [p for p, c in self.results.items() if not c.success]

    def get_content(self, platform: str) -> str | None:
        """Convenience helper — returns the raw text for *platform* or None."""
        entry = self.results.get(platform.lower().strip())
        return entry.content if entry and entry.success else None


# ---------------------------------------------------------------------------
# LLM setup — lazy factories (clients are created only when first used)
# ---------------------------------------------------------------------------

_gemini: ChatGoogleGenerativeAI | None = None
_ollama: ChatOllama | None = None


def get_gemini() -> ChatGoogleGenerativeAI:
    """Return a cached Gemini client, creating it on first call."""
    global _gemini
    if _gemini is None:
        _gemini = ChatGoogleGenerativeAI(model="gemini-2.0-flash-lite")
    return _gemini


def get_ollama(model: str = "gemma3:1b") -> ChatOllama:
    """Return a cached Ollama client, creating it on first call.

    The Ollama server is only contacted at this point, NOT at import time.
    """
    global _ollama
    if _ollama is None:
        _ollama = ChatOllama(model=model)
    return _ollama

# Map platform names → system-prompt factory functions
PLATFORM_PROMPTS: dict[str, object] = {
    "instagram": instagram_prompt,
    "facebook": facebook_prompt,
    "twitter": twitter_prompt,
    "linkedin": linkedin_prompt,
    "blog post": blog_prompt,
}


def _field_name(platform: str) -> str:
    """Convert platform name to a valid Pydantic field name (spaces → underscores)."""
    return platform.replace(" ", "_")


# ---------------------------------------------------------------------------
# Main function
# ---------------------------------------------------------------------------

def generate_response(
    article_content: str,
    platforms: list[str],
) -> ContentGenerationResult:
    """Generate platform-specific content for ALL platforms in a single LLM call.

    Args:
        article_content: The source article text to adapt.
        platforms: List of platform names.
                   Supported values: "instagram", "facebook", "twitter",
                   "linkedin", "blog post".

    Returns:
        A :class:`ContentGenerationResult` with a ``results`` dict keyed by
        platform name, plus computed ``succeeded`` / ``failed`` lists and
        per-entry ``word_count``.
    """
    keys = [p.lower().strip() for p in platforms]
    supported = [k for k in keys if k in PLATFORM_PROMPTS]
    unsupported = [k for k in keys if k not in PLATFORM_PROMPTS]

    results: dict[str, PlatformContent] = {}

    # Mark unsupported platforms immediately — no LLM call needed for these
    for key in unsupported:
        results[key] = PlatformContent(
            platform=key,
            content="",
            success=False,
            error=f"Unsupported platform: '{key}'",
        )

    if not supported:
        return ContentGenerationResult(results=results)

    # ------------------------------------------------------------------
    # 1. Build ONE combined system prompt from all requested platform prompts
    # ------------------------------------------------------------------
    sections: list[str] = []
    for key in supported:
        prompt_factory = PLATFORM_PROMPTS[key]  # type: ignore[operator]
        system_msg = prompt_factory()            # type: ignore[operator]
        sections.append(f"=== {key.upper()} ===\n{system_msg.content}")

    combined_system = (
        "You are a multi-platform content strategist.\n"
        "Generate content for ALL of the following platforms simultaneously "
        "from the article the user provides.\n"
        "Follow each platform's specific rules exactly as described below.\n\n"
        + "\n\n".join(sections)
    )

    # ------------------------------------------------------------------
    # 2. Dynamically build a Pydantic output schema — one field per platform
    # ------------------------------------------------------------------
    field_definitions = {
        _field_name(key): (
            str,
            Field(
                description=(
                    f"Generated content for {key}, "
                    f"following the {key.upper()} rules above."
                )
            ),
        )
        for key in supported
    }
    PlatformsOutput = create_model("PlatformsOutput", **field_definitions)

    # ------------------------------------------------------------------
    # 3. Single structured LLM call — LLM returns all platforms at once
    # ------------------------------------------------------------------
    try:
        # ↓ Toggle which LLM to use by commenting/uncommenting one line
        # llm = get_gemini()
        llm = get_ollama()   # uncomment for local Ollama (llama3.2)
        structured_llm = llm.with_structured_output(PlatformsOutput)
        output = structured_llm.invoke([
            SystemMessage(content=combined_system),
            HumanMessage(content=article_content),
        ])

        for key in supported:
            results[key] = PlatformContent(
                platform=key,
                content=getattr(output, _field_name(key), ""),
                success=True,
            )

    except Exception as exc:  # noqa: BLE001
        for key in supported:
            results[key] = PlatformContent(
                platform=key,
                content="",
                success=False,
                error=str(exc),
            )

    return ContentGenerationResult(results=results)
