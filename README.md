<<<<<<< HEAD
# motoventra
=======
# 🏍️ MotoMod AI & BikeVerse Dataset Collection Platform

[![GitHub Codespaces](https://img.shields.io/badge/GitHub-Codespaces-blue?logo=github)](https://github.com/Premkumar66/motoventra)
[![FastAPI](https://img.shields.io/badge/FastAPI-v0.115-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python)](https://www.python.org/)

An AI-powered motorcycle modification recommendation system and legal dataset collection pipeline covering **262+ motorcycle models** across **46 global manufacturers**.

---

## ⚡ Quick Start in GitHub Codespaces

1. Open repository [Premkumar66/motoventra](https://github.com/Premkumar66/motoventra) on GitHub.
2. Click **Code** ➔ **Codespaces** ➔ **Create codespace on main**.
3. Codespaces will automatically build the environment, install requirements, seed the catalog, and launch the web server on **Port 8000**.

---

## 🚀 Running Locally

```bash
cd motomod-ai/backend
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
python reset_db_seed.py
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your web browser.

---

## 🔐 Credentials
- **Admin**: `admin@motomod.ai` / `Admin@MotoMod2024!`
- **User**: `user@motomod.ai` / `User@MotoMod2024!`
>>>>>>> 7e4b816 (feat: MotoMod AI platform with BikeVerse Image Dataset Collection & Management System)
