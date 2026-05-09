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

https://raw.githubusercontent.com/Rohit-Kombee/Vision-to-Cart/main/09.05.2026_14.33.09_REC.mp4

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
