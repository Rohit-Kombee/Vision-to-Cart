# Vision-to-Product URL Matching
### AI-Powered Commerce Intelligence Prototype

> ⚠️ Note: This repository does **not contain the complete codebase**.  
> A major part of the business logic, matching engine, and commerce functionality exists inside the `magrabi-ecom-services` backend.

An AI-powered prototype built for the **Vision-to-Cart / MCP Commerce Intelligence Challenge**.

This project demonstrates how a user-uploaded product image can be converted into a matching commerce product URL using AI attribute extraction and backend variant matching.

---

# How It Works

1. User uploads a product image.
2. AI extracts product attributes from the image.
3. FastAPI sends extracted attributes to:
   ```text
   POST /api/variant-match/
   ```
4. `magrabi-ecom-services` matches the closest product variant.
5. Backend returns:
   - Product URL
   - SKU
   - Variant metadata
6. Frontend displays the matching product URL.

---

# Architecture

```text
[Image Upload UI]
        │
        ▼
[FastAPI Matcher]
 - AI attribute extraction
 - Auth handling
        │
        ▼
[magrabi-ecom-services]
POST /api/variant-match/
 - Variant matching
 - Channel-aware filtering
 - DB-backed URL retrieval
```

---

# Core Idea

The returned product URL or SKU can later be used for:

- Add-to-cart mutations
- Storefront cart APIs
- Wishlist flows
- Personalized recommendations
- AI shopping assistants

Future flow:

```text
Image → AI Match → Variant URL/SKU → Cart Mutation
```

---

# Features

- AI-powered image attribute extraction
- FastAPI lightweight prototype UI
- Backend variant matching
- DB-backed product URL retrieval
- Channel-aware matching
- Flexible authentication handling

---

# Run Locally

## 1) Start Magrabi Ecom Services

```bash
docker compose -f docker-compose-dev.yml up -d
```

Backend should run on:

```text
http://localhost:8000
```

---

## 2) Start FastAPI App

```bash
cd product-image-matcher

python -m venv .venv

# Windows
.venv\Scripts\activate

pip install -r requirements.txt

copy .env.example .env

uvicorn app:app --reload --port 5050
```

Open:

```text
http://127.0.0.1:5050
```

---

# Environment Variables

```env
ECOM_ATTRIBUTE_MATCH_URL=http://localhost:8000/api/variant-match/

SALEOR_GRAPHQL_URL=http://localhost:8000/graphql/

SALEOR_CHANNEL_SLUG=magrabi-sa-web

LOCAL_VISION_MODEL=openai/clip-vit-base-patch32
```

Optional authentication:

```env
ECOM_API_TOKEN=your_token
```

or

```env
SALEOR_USER_EMAIL=user@example.com
SALEOR_USER_PASSWORD=your_password
```

---

# Current Status

Implemented:

- AI attribute extraction
- Variant matching API integration
- Product URL retrieval
- Lightweight FastAPI interface
- Channel-aware matching

Planned:

- Native integration into `magrabi-ecom-services`
- Direct cart/storefront mutation
- Better AI matching
- Production-grade optimization

---

# Demo Video

<video width="100%" controls>
  <source src="https://softwareitconsulting-my.sharepoint.com/:v:/g/personal/rohit_sahu_forchunex_com/IQA3do9CO48QTp3txh8KJcFLAUQSg8fcdr2wkqCqBfBRs9E?download=1" type="video/mp4">
</video>

If video preview is not supported:

[Watch Demo Video](https://softwareitconsulting-my.sharepoint.com/:v:/g/personal/rohit_sahu_forchunex_com/IQA3do9CO48QTp3txh8KJcFLAUQSg8fcdr2wkqCqBfBRs9E?nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJPbmVEcml2ZUZvckJ1c2luZXNzIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXciLCJyZWZlcnJhbFZpZXciOiJNeUZpbGVzTGlua0NvcHkifX0&e=OXdCUj)

---

# Future Direction

The long-term vision is a complete AI-powered commerce flow:

```text
Image Upload
      ↓
AI Attribute Extraction
      ↓
Variant Match
      ↓
Cart Mutation
      ↓
Checkout
```

This project is a prototype created to validate the concept and architecture of AI-assisted visual commerce.
