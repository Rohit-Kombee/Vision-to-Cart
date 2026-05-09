"""Image -> Vision attributes -> Magrabi attribute API -> DB product URL."""

from __future__ import annotations

import base64
import json
import logging
import os
import re
from io import BytesIO
from pathlib import Path

import httpx
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
load_dotenv(BASE_DIR / ".env")

ECOM_ATTRIBUTE_MATCH_URL = os.getenv(
    "ECOM_ATTRIBUTE_MATCH_URL", "http://localhost:8000/api/variant-match/"
)
ECOM_API_TOKEN = os.getenv("ECOM_API_TOKEN", "")
ECOM_API_USERNAME = os.getenv("ECOM_API_USERNAME", "")
ECOM_API_PASSWORD = os.getenv("ECOM_API_PASSWORD", "")
SALEOR_GRAPHQL_URL = os.getenv("SALEOR_GRAPHQL_URL", "http://localhost:8000/graphql/")
SALEOR_API_TOKEN = os.getenv("SALEOR_API_TOKEN", "")
SALEOR_USER_EMAIL = os.getenv("SALEOR_USER_EMAIL", os.getenv("saleor_user_email", ""))
SALEOR_USER_PASSWORD = os.getenv(
    "SALEOR_USER_PASSWORD", os.getenv("saleor_user_password", "")
)
SALEOR_CHANNEL_SLUG = os.getenv("SALEOR_CHANNEL_SLUG", "default-channel")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
USE_OPENAI_VISION = os.getenv("USE_OPENAI_VISION", "false").lower() == "true"
LOCAL_VISION_MODEL = os.getenv("LOCAL_VISION_MODEL", "openai/clip-vit-base-patch32")

TOKEN_CREATE_MUTATION = """
mutation TokenCreate($email: String!, $password: String!) {
  tokenCreate(email: $email, password: $password) {
    token
    errors {
      message
      field
      code
    }
  }
}
"""

_runtime_saleor_token: str | None = None
_local_classifier = None


def _parse_json_from_model(text: str) -> dict:
    cleaned = re.sub(r"^```(?:json)?\s*", "", text.strip())
    cleaned = re.sub(r"\s*```$", "", cleaned)
    return json.loads(cleaned or "{}")


def _normalize_key(value: str) -> str:
    key = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return key


def _normalize_attr_map(raw: dict) -> dict:
    normalized = {}
    for key, val in raw.items():
        if val is None:
            continue
        out_key = _normalize_key(str(key))
        if not out_key:
            continue
        if isinstance(val, list):
            values = [str(v).strip().lower() for v in val if str(v).strip()]
            if values:
                normalized[out_key] = values
        else:
            value = str(val).strip().lower()
            if value:
                normalized[out_key] = value
    return normalized


def _get_local_classifier():
    global _local_classifier
    if _local_classifier is not None:
        return _local_classifier
    from transformers import pipeline

    _local_classifier = pipeline(
        "zero-shot-image-classification",
        model=LOCAL_VISION_MODEL,
    )
    return _local_classifier


def _infer_product_type_local(image_bytes: bytes) -> str:
    from PIL import Image

    labels = [
        "sunglasses",
        "eyeglasses",
        "reading glasses",
        "contact lenses",
        "glasses accessories",
    ]
    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    classifier = _get_local_classifier()
    result = classifier(image, candidate_labels=labels)
    if not result:
        return "sunglasses"
    # transformers returns list of dicts sorted by score desc
    top_label = str(result[0].get("label", "sunglasses")).lower().strip()
    if "contact" in top_label:
        return "contact_lenses_clear"
    if "eye" in top_label or "reading" in top_label:
        return "eyeglasses"
    if "accessor" in top_label:
        return "accessories_bycolor"
    return "sunglasses"


def _infer_color_local(image_bytes: bytes) -> str | None:
    from PIL import Image

    labels = [
        "black",
        "brown",
        "havana",
        "grey",
        "gold",
        "silver",
        "blue",
        "green",
        "transparent",
    ]
    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    classifier = _get_local_classifier()
    result = classifier(image, candidate_labels=labels)
    if not result:
        return None
    return str(result[0].get("label", "")).strip().lower() or None


def _analyze_with_openai(image_bytes: bytes, mime_type: str) -> tuple[dict, list[str]]:
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY not configured")

    client = OpenAI(api_key=OPENAI_API_KEY)
    image_b64 = base64.b64encode(image_bytes).decode("ascii")
    image_data_url = f"data:{mime_type};base64,{image_b64}"
    prompt = (
        "Analyze this eyewear product image for database attribute matching. "
        "Return JSON only with keys: attributes and keywords. "
        "attributes must be an object with attribute slugs and value slugs/text values. "
        "Prefer keys like: product_type, color, frame_shape, size, gender, brand. "
        "keywords should be a short array of useful fallback terms."
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe this item for product matching."},
                    {"type": "image_url", "image_url": {"url": image_data_url}},
                ],
            },
        ],
        max_tokens=260,
    )
    raw = (response.choices[0].message.content or "").strip()
    parsed = _parse_json_from_model(raw)
    attributes_raw = parsed.get("attributes") or {}
    keywords_raw = parsed.get("keywords") or []
    if isinstance(keywords_raw, str):
        keywords_raw = [keywords_raw]
    keywords = [str(x).strip() for x in keywords_raw if str(x).strip()]
    attributes = _normalize_attr_map(attributes_raw if isinstance(attributes_raw, dict) else {})
    return attributes, keywords


def _analyze_image(image_bytes: bytes, mime_type: str) -> tuple[dict, list[str]]:
    # Preferred path: local/open-source model, no paid API needed.
    try:
        product_type = _infer_product_type_local(image_bytes)
        color = _infer_color_local(image_bytes)
        attributes = {"product_type": product_type}
        if color:
            attributes["color"] = color
        keywords = [product_type] + ([color] if color else [])
        return attributes, keywords
    except Exception as exc:
        logger.warning("Local vision inference failed: %s", exc)

    # Optional fallback path if user enables OpenAI explicitly.
    if USE_OPENAI_VISION and OPENAI_API_KEY:
        try:
            return _analyze_with_openai(image_bytes, mime_type)
        except Exception as exc:
            logger.warning("OpenAI fallback inference failed: %s", exc)
    raise RuntimeError("AI attribute extraction failed. Configure local model or OpenAI fallback.")


async def _fetch_variant_from_ecom(attributes: dict) -> dict:
    headers = {"Content-Type": "application/json"}
    token = await _resolve_auth_token()
    if token:
        headers["Authorization"] = f"Bearer {token}"

    payload = {"attributes": attributes, "channel_slug": SALEOR_CHANNEL_SLUG}

    async with httpx.AsyncClient(timeout=30.0) as client:
        kwargs = {"json": payload, "headers": headers}
        if ECOM_API_USERNAME and ECOM_API_PASSWORD:
            kwargs["auth"] = (ECOM_API_USERNAME, ECOM_API_PASSWORD)
        response = await client.post(ECOM_ATTRIBUTE_MATCH_URL, **kwargs)
        if response.status_code >= 400:
            detail = response.text
            try:
                parsed = response.json()
                detail = parsed.get("error") or parsed.get("detail") or detail
            except Exception:
                pass
            raise RuntimeError(
                f"ecom endpoint returned {response.status_code}: {detail}"
            )
        return response.json()


async def _resolve_auth_token() -> str:
    """Resolve bearer token for ecom API in this order:
    1) ECOM_API_TOKEN
    2) SALEOR_API_TOKEN
    3) Runtime JWT generated from saleor_user_email/password
    """
    global _runtime_saleor_token

    if ECOM_API_TOKEN:
        return ECOM_API_TOKEN
    if SALEOR_API_TOKEN:
        return SALEOR_API_TOKEN
    if _runtime_saleor_token:
        return _runtime_saleor_token

    if not SALEOR_USER_EMAIL or not SALEOR_USER_PASSWORD:
        return ""

    payload = {
        "query": TOKEN_CREATE_MUTATION,
        "variables": {
            "email": SALEOR_USER_EMAIL,
            "password": SALEOR_USER_PASSWORD,
        },
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            SALEOR_GRAPHQL_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        body = response.json()

    if body.get("errors"):
        error = body["errors"][0].get("message", "Unknown GraphQL error")
        raise RuntimeError(f"Token generation failed: {error}")

    token_data = (body.get("data") or {}).get("tokenCreate") or {}
    errors = token_data.get("errors") or []
    if errors:
        raise RuntimeError(
            "Token generation failed: "
            + ", ".join((err.get("message") or err.get("code") or "error") for err in errors)
        )

    token = token_data.get("token") or ""
    if not token:
        raise RuntimeError("Token generation failed: empty token response.")

    _runtime_saleor_token = token
    return token


app = FastAPI(title="Vision to Product URL")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def index() -> FileResponse:
    index_file = STATIC_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="static/index.html not found")
    return FileResponse(index_file)


@app.post("/api/match")
async def match(image: UploadFile = File(...)) -> dict:
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Please upload a valid image.")

    image_bytes = await image.read()
    if len(image_bytes) > 12 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image exceeds 12 MB limit.")

    attributes, keywords = _analyze_image(image_bytes, image.content_type)
    if not attributes:
        raise HTTPException(status_code=400, detail="Could not extract usable attributes.")

    try:
        match = await _fetch_variant_from_ecom(attributes)
    except Exception as exc:
        logger.exception("Ecommerce attribute match failed")
        raise HTTPException(
            status_code=502,
            detail=(
                "Could not fetch match from ecommerce API. Verify ECOM_ATTRIBUTE_MATCH_URL, "
                "credentials, and SALEOR_CHANNEL_SLUG. Error: " + str(exc)
            ),
        ) from exc

    product_url = match.get("product_url")
    if not match.get("ok") or not product_url:
        return {
            "ok": False,
            "message": match.get("error") or "No matching product found in Magrabi catalog.",
            "product_url": None,
            "attributes": attributes,
            "keywords": keywords,
        }

    return {
        "ok": True,
        "message": f"This is the URL for your matching product: {product_url}",
        "product_url": product_url,
        "product_name": match.get("product_name"),
        "variant_id": match.get("variant_id"),
        "variant_sku": match.get("variant_sku"),
        "image_url": match.get("image_url"),
        "attributes": attributes,
        "keywords": keywords,
    }


if STATIC_DIR.exists():
    app.mount("/assets", StaticFiles(directory=STATIC_DIR), name="assets")
