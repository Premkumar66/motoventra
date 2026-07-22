# MotoMod AI 🏍️🤖
### AI-Powered Motorcycle Modification Recommendation & Performance Prediction Platform

---

## 🌟 Introduction
**MotoMod AI** is a production-ready, enterprise-grade platform that allows motorcycle enthusiasts to select any motorcycle variant, plan modifications visually via a 3D interface, and receive AI-driven forecasts on mileage, horsepower, torque, top speed, and resale value.

## 🏗️ System Architecture
MotoMod AI follows a clean, decoupled architecture:
- **Frontend**: Flutter Web & Mobile app using a feature-first BLoC state management design.
- **Backend API**: FastAPI (Python 3.11) with asynchronous PostgreSQL interactions and Redis-based sliding-window rate limiting.
- **ML Services**: Predictor ensemble combining XGBoost, LightGBM, and Random Forest models tracked using MLflow.
- **File Storage**: MinIO S3-compatible service hosting bike photos, custom assets, and dataset backups.

---

## 📂 Project Directory Structure
```
motomod-ai/
├── docs/                          # Architecture, SRS, database design, UML diagrams
├── backend/                       # FastAPI codebase
├── ml/                            # ML training & pipelines
├── frontend/                      # Flutter mobile + web codebase
├── etl/                           # Cleaners & pipelines
└── docker-compose.yml             # Single-command local environment launcher
```

---

## 🚀 Quick Start (Local Development)

### 1. Start Services using Docker Compose
```bash
docker-compose up --build
```
This boots the database, Redis instance, MinIO storage client, and the backend reload server.

### 2. Seed Initial brand/model catalog
```bash
# Enter backend container or activate virtualenv locally
pip install -r backend/requirements.txt
python backend/app/core/seed.py
```

### 3. Launch Flutter Application
```bash
cd frontend
flutter pub get
flutter run -d chrome  # or ios / android
```

---

## 📚 Technical Documentation
Detailed specifications are available in the [docs/](file:///c:/CCP%20PROJECT/Motoventra/motomod-ai/docs) directory:
- [Product Requirements Document (PRD)](file:///c:/CCP%20PROJECT/Motoventra/motomod-ai/docs/PRD.md)
- [Software Requirement Specification (SRS)](file:///c:/CCP%20PROJECT/Motoventra/motomod-ai/docs/SRS.md)
- [System Architecture Specification](file:///c:/CCP%20PROJECT/Motoventra/motomod-ai/docs/architecture.md)
- [Database Design & Schema](file:///c:/CCP%20PROJECT/Motoventra/motomod-ai/docs/database-design.md)
- [AI & ML Pipeline Details](file:///c:/CCP%20PROJECT/Motoventra/motomod-ai/docs/ml-pipeline.md)
- [REST API Reference](file:///c:/CCP%20PROJECT/Motoventra/motomod-ai/docs/api-documentation.md)
