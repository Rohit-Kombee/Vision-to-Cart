# Vision-to-Product URL (Hackathon Prototype)

This project is the working prototype for the **Vision-to-Cart / MCP Commerce Intelligence** idea.

Current approach:

1. User uploads a product image in a lightweight FastAPI UI.
2. AI extracts product attributes from the image (for example product type).
3. FastAPI calls Magrabi ecom endpoint: `/api/variant-match/`.
4. Ecom service returns a matching variant with URL from DB (`product_productvariant.url`).
5. Frontend prints: `This is the URL for your matching product: ...`

---

## Why this prototype exists

For hackathon speed, AI extraction is built as a **separate FastAPI app**.

Target production direction:

- Move this logic into a **new app/module inside `magrabi-ecom-services`**
- Keep matching and channel logic in Saleor backend
- On storefront side, use this result to trigger the required cart mutation flow

---

## Architecture

```text
[Image Upload UI]
      |
      v
[FastAPI Matcher]
  - AI attribute extraction
  - auth token handling
      |
      v
[magrabi-ecom-services]
  POST /api/variant-match/
  - match variant by attributes/channel
  - return DB variant URL + metadata
```

---

## Run locally

### 1) Start Magrabi ecom services

From `magrabi-ecom-services`:

```bash
docker compose -f docker-compose-dev.yml up -d
```

Ensure backend is reachable at `http://localhost:8000`.

### 2) Start this FastAPI app

```bash
cd product-image-matcher
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app:app --reload --port 5050
```

Open: `http://127.0.0.1:5050`

---

## Environment configuration (`.env`)

- `ECOM_ATTRIBUTE_MATCH_URL`  
  Example: `http://localhost:8000/api/variant-match/`

- Auth options (first available is used):
  - `ECOM_API_TOKEN`
  - `SALEOR_API_TOKEN`
  - `SALEOR_USER_EMAIL` + `SALEOR_USER_PASSWORD` (auto token generation using `tokenCreate`)

- `SALEOR_GRAPHQL_URL`  
  Used when generating token from user credentials.

- `SALEOR_CHANNEL_SLUG`  
  Example: `magrabi-sa-web`

- AI extraction:
  - `LOCAL_VISION_MODEL` (default: `openai/clip-vit-base-patch32`)
  - Optional fallback: `OPENAI_API_KEY` + `USE_OPENAI_VISION=true`

---

## Current status

- Attribute extraction is AI-driven.
- Variant URL is fetched from Magrabi DB-backed model (`ProductVariant.url`).
- Endpoint supports channel-aware matching and fallback matching strategy.

---

## Demo video

Add your video file and link it here.

Recommended:

1. Create folder: `docs/`
2. Put video file: `docs/demo.mp4`
3. Keep this section in README:

```md
## Demo video

[Watch demo video](docs/demo.mp4)
```

If you upload to Drive/YouTube, replace with public URL:

```md
## Demo video

[Watch demo video](https://your-video-link)
```

---

## Next step (post-hackathon)

Refactor this FastAPI prototype into a native app inside `magrabi-ecom-services` so the full flow (AI extraction -> variant match -> storefront/cart mutation) runs under one backend domain.
