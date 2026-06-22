import requests
from dotenv import load_dotenv
import os
import base64
from PIL import Image
import io
load_dotenv()

backend_url = os.getenv("BACKEND_URL")

def generate_image(prompt: str):
    try:
        response = requests.post(
            f"{backend_url}/generate_image",
            headers={"ngrok-skip-browser-warning": "true"},
            json={"prompt": prompt},
            timeout=120,
        )

        # Surface HTTP errors (4xx / 5xx) before trying to parse JSON
        if not response.ok:
            print(f"Image backend error {response.status_code}: {response.text[:300]}")
            return None

        raw = response.text.strip()
        if not raw:
            print("Image backend returned an empty response.")
            return None

        data = response.json()

        if "image" not in data:
            print(f"Unexpected response shape: {data}")
            return None

        img_bytes = base64.b64decode(data["image"])
        image = Image.open(io.BytesIO(img_bytes))
        return image

    except requests.exceptions.Timeout:
        print("Image backend timed out.")
        return None
    except requests.exceptions.ConnectionError as e:
        print(f"Could not reach image backend: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None