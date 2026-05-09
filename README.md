# Vision-to-Product URL Matching  
### AI-Powered Commerce Intelligence Prototype

An AI-driven prototype built for the **Vision-to-Cart / MCP Commerce Intelligence Challenge**.

This project demonstrates how a user-uploaded product image can be transformed into a direct product match from the commerce database using AI-powered attribute extraction and backend variant matching.

The prototype combines:

- Image understanding
- AI-based attribute extraction
- Variant matching
- Commerce backend integration
- Direct product URL retrieval
- Future-ready cart integration flow

---

# Overview

The application allows a user to upload a product image through a lightweight FastAPI interface.

The system then:

1. Extracts visual product attributes using AI.
2. Sends extracted attributes to the commerce backend.
3. Matches the closest product variant from the database.
4. Returns the product URL stored in the backend (`product_productvariant.url`).
5. Displays the matched product URL to the user.

This prototype is designed as the first step toward a fully automated **Vision-to-Cart** commerce experience.

---

# Core Idea

The returned product URL (or SKU extracted from the matched variant) can be used to trigger downstream commerce actions such as:

- Add-to-cart mutations
- Storefront cart APIs
- Wishlist creation
- Personalized recommendations
- Smart shopping assistants

Future flow:

```text
Image → AI Attribute Extraction → Variant Match → SKU/URL → Cart Mutation
```

This creates a seamless AI-assisted shopping experience where users can visually search products and directly add them to their cart.

---

# Architecture

```text
                    ┌──────────────────────┐
                    │  Image Upload UI    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   FastAPI Matcher    │
                    │----------------------│
                    │ • AI attribute scan  │
                    │ • Auth token logic   │
                    │ • Request handling   │
                    └──────────┬──────────┘
                               │
                               ▼
               ┌────────────────────────────────┐
               │  magrabi-ecom-services         │
               │--------------------------------│
               │ POST /api/variant-match/       │
               │                                │
               │ • Variant attribute matching   │
               │ • Channel-aware filtering      │
               │ • DB-backed URL retrieval      │
               │ • Matching fallback strategy   │
               └────────────────────────────────┘
```

---

# Important Note About the Codebase

This repository contains the **FastAPI prototype layer** and lightweight integration logic only.

A significant portion of the business logic and commerce functionality exists inside the separate backend service:

- `magrabi-ecom-services`

That backend contains:

- Variant matching implementation
- Product models
- Channel-aware logic
- Commerce APIs
- Database-backed URL retrieval
- Internal matching strategies

Therefore, this repository should be considered a **working prototype/demo implementation** rather than the complete production-ready system.

---

# Features

- AI-powered product attribute extraction
- Lightweight FastAPI frontend
- Integration with Magrabi commerce backend
- Channel-aware variant matching
- Direct DB-backed product URL retrieval
- Flexible authentication support
- Fallback matching strategy
- Extensible architecture for cart/storefront integration

---

# Project Flow

```text
User uploads image
        │
        ▼
AI extracts product attributes
        │
        ▼
FastAPI sends attributes to:
POST /api/variant-match/
        │
        ▼
Commerce backend finds closest variant
        │
        ▼
Backend returns:
- Product URL
- SKU
- Variant metadata
        │
        ▼
Frontend displays matching product
```

---

# Current Prototype Status

Implemented:

- AI-driven attribute extraction
- Backend variant matching
- Database-backed product URL retrieval
- Channel-aware filtering
- Lightweight FastAPI UI
- Authentication handling
- Matching fallback strategy

Planned / Future Scope:

- Native integration inside `magrabi-ecom-services`
- Storefront cart mutation support
- SKU-based add-to-cart automation
- Personalized recommendation engine
- Improved AI visual matching
- Multi-image support
- Production-grade optimization

---

# Demo Video

Watch the prototype demo here:

[Demo Video](https://softwareitconsulting-my.sharepoint.com/:v:/g/personal/rohit_sahu_forchunex_com/IQA3do9CO48QTp3txh8KJcFLAUQSg8fcdr2wkqCqBfBRs9E?nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJPbmVEcml2ZUZvckJ1c2luZXNzIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXciLCJyZWZlcnJhbFZpZXciOiJNeUZpbGVzTGlua0NvcHkifX0&e=OXdCUj)

---

# Future Direction

The long-term goal is to move the entire flow into a unified commerce backend:

```text
AI Extraction
      ↓
Variant Matching
      ↓
Storefront Mutation
      ↓
Cart Creation
      ↓
Checkout Experience
```

This would allow users to discover and purchase products directly from images with minimal friction.

---

# Disclaimer

This project is a hackathon prototype created to demonstrate the concept and technical feasibility of AI-powered visual commerce matching.

The implementation is intentionally lightweight and focuses on validating the architecture and user flow rather than delivering a fully production-ready system.
