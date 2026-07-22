# MotoMod AI — REST API Reference Documentation

This document describes the structure, authentication headers, error messages, and endpoint payload schemas for the MotoMod AI Backend API.

---

## 1. Global Specifications

### Base URL
- Local Dev: `http://localhost:8000/api/v1`
- Production: `https://api.motomod.ai/api/v1`

### Authentication Headers
Authenticate API requests using standard JWT Access Tokens in the `Authorization` header:

```http
Authorization: Bearer <your_jwt_access_token>
```

### Generic Error Payload Envelope
```json
{
  "detail": "Detailed message explaining the validation error or resource mismatch."
}
```

---

## 2. Authentication API (`/auth`)

### 2.1 User Account Registration
- **Method & Path**: `POST /auth/register`
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "username": "rider_john",
    "password": "SecurePassword123!",
    "confirm_password": "SecurePassword123!",
    "full_name": "John Doe"
  }
  ```
- **Response (201 Created)**:
  ```json
  {
    "id": "c3e98031-4171-46df-9d33-bc4b9f2c8d23",
    "email": "user@example.com",
    "username": "rider_john",
    "full_name": "John Doe",
    "avatar_url": null,
    "bio": null,
    "city": null,
    "country": "India",
    "role": "user",
    "status": "active",
    "is_email_verified": true,
    "theme_preference": "dark",
    "created_at": "2026-07-16T12:00:00Z"
  }
  ```

### 2.2 Account Login
- **Method & Path**: `POST /auth/login`
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "SecurePassword123!"
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "access_token": "ey...",
    "refresh_token": "ey...",
    "token_type": "bearer",
    "expires_in": 1800,
    "user": {
      "id": "c3e98031-4171-46df-9d33-bc4b9f2c8d23",
      "email": "user@example.com",
      "username": "rider_john",
      "full_name": "John Doe",
      "role": "user",
      "status": "active",
      "is_email_verified": true,
      "theme_preference": "dark",
      "created_at": "2026-07-16T12:00:00Z"
    }
  }
  ```

---

## 3. Motorcycle Catalog API (`/bikes`)

### 3.1 Fetch Brand Manufacturers
- **Method & Path**: `GET /bikes/brands`
- **Parameters**: `page` (int), `per_page` (int)
- **Response (200 OK)**:
  ```json
  {
    "items": [
      {
        "id": "a1c52d87-bc5b-43d9-9523-a1bf44a703a1",
        "name": "Royal Enfield",
        "slug": "royal-enfield",
        "country": "India",
        "founded_year": 1901,
        "logo_url": null,
        "is_active": true,
        "created_at": "2026-07-16T12:00:00Z"
      }
    ],
    "meta": {
      "total": 22,
      "page": 1,
      "per_page": 20,
      "total_pages": 2,
      "has_next": true,
      "has_prev": false
    }
  }
  ```

### 3.2 Fetch Variant Specifications
- **Method & Path**: `GET /bikes/variants/{variant_id}`
- **Response (200 OK)**:
  ```json
  {
    "id": "d8e390c5-55a2-4a11-b0de-7a3c75f0a0d4",
    "motorcycle_id": "f5e92c21-c4d3-4e12-b1ad-8fcf2c510a24",
    "variant_name": "Kamet White",
    "slug": "kamet-white",
    "year": 2024,
    "engine_cc": 452.0,
    "horsepower_bhp": 40.0,
    "torque_nm": 40.0,
    "mileage_kmpl": 30.0,
    "price_inr": 285000.0,
    "has_abs": true,
    "fuel_tank_liters": 17.0
  }
  ```

---

## 4. AI Performance Prediction API (`/predictions`)

### 4.1 Perform Performance Prediction
- **Method & Path**: `POST /predictions/performance`
- **Request Body**:
  ```json
  {
    "variant_id": "d8e390c5-55a2-4a11-b0de-7a3c75f0a0d4",
    "modification_ids": [
      "2a8e80d4-72df-4235-950c-e2cf44b6c310"
    ]
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "variant_id": "d8e390c5-55a2-4a11-b0de-7a3c75f0a0d4",
    "base_specs": {
      "horsepower_bhp": 40.0,
      "torque_nm": 40.0,
      "mileage_kmpl": 30.0,
      "top_speed_kmh": 140.0
    },
    "predicted_specs": {
      "horsepower_bhp": 41.8,
      "torque_nm": 41.2,
      "mileage_kmpl": 28.5,
      "top_speed_kmh": 143.12
    },
    "differences": {
      "horsepower_bhp": 1.8,
      "torque_nm": 1.2,
      "mileage_kmpl": -1.5,
      "top_speed_kmh": 3.12
    },
    "confidence_score": 0.89,
    "model_version": "1.0.0"
  }
  ```
