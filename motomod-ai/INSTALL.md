# MotoMod AI — Installation Guide

This document details the step-by-step setup procedure to deploy MotoMod AI locally for development and testing.

---

## Prerequisites
Before starting, ensure your host machine has the following tools installed:
1. **Python 3.11** or higher
2. **Flutter SDK 3.24.x** or higher (with Dart SDK 3.5.x)
3. **Docker Engine** (v27.x+) and **Docker Compose**
4. **PostgreSQL Client Utilities** (optional, for DB verification)

---

## Step 1: Environment Setup
Clone the codebase and copy the sample configuration template to the active environment file:

```bash
cd motomod-ai/backend
cp .env.example .env
```

Open `.env` and adjust the variables as required. (The defaults are optimized for Docker Compose integration).

---

## Step 2: Database and Services Launch
Spin up the backing service containers (PostgreSQL, Redis, MinIO) in the background:

```bash
docker-compose up -d db redis minio
```

Verify that all containers are healthy:
```bash
docker-compose ps
```

---

## Step 3: Backend API Setup (Python Environment)
If running the backend API outside of Docker for debugging:

1. Create a virtual environment:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the database migrations/seeding script:
   ```bash
   python app/core/seed.py
   ```

4. Start the FastAPI local server:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

---

## Step 4: Frontend App Setup (Flutter)
1. Navigate to the frontend directory:
   ```bash
   cd ../frontend
   ```

2. Download active dependencies:
   ```bash
   flutter pub get
   ```

3. Check device readiness:
   ```bash
   flutter devices
   ```

4. Run the application:
   ```bash
   flutter run
   ```
