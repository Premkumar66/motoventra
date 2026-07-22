# MotoMod AI — Developer Guide

This guide details the conventions, coding styles, database patterns, and ML pipeline design to aid developers in contributing to MotoMod AI.

---

## 1. Code Style and Linters
To maintain codebase quality, we enforce standard formatting tools. Before committing code, please execute:

```bash
# Formats code imports and line wrapping
black backend/
isort backend/

# Checks for syntax and styling guidelines
flake8 backend/
```

---

## 2. Backend Clean Architecture Patterns
The FastAPI app implements the standard layered design structure:
- **Routes Layer (`app/api/v1/routes/`)**: Exposes endpoint signatures and controls HTTP status codes. No business processing happens here.
- **Service Layer (`app/services/`)**: The core domain executor. Handles calculations, transaction validations, and triggers background events.
- **Repository Layer (`app/repositories/`)**: Encapsulates DB persistence queries (SQLAlchemy). Solves ORM decoupling.
- **Models Layer (`app/models/`)**: Defines tables, constraints, and relational mappings.

---

## 3. Database Migration Guidelines
We use Alembic for version tracking:
1. When editing models under `app/models/`, compile a new database migration script:
   ```bash
   alembic revision --autogenerate -m "add_new_specification_field"
   ```
2. Review the generated version file in `backend/alembic/versions/`.
3. Apply migration to the active schema:
   ```bash
   alembic upgrade head
   ```

---

## 4. Machine Learning Module Guidelines
- **Weights storage**: Trained `.joblib` model binaries are serialized to `./ml/models/trained` and mirrored to the MinIO model bucket `motomod-ml-models`.
- **Adding new models**:
  1. Define model input/output schema in `backend/app/schemas/predictions.py`.
  2. Implement heuristic fallback inside `backend/app/api/v1/routes/predictions.py` to ensure endpoint resilience.
  3. Register training routines in `ml/pipelines/train.py`.
