# How to Run Phronidoc

## Option 1: View Documentation Only

To view the documentation site:

```bash
# Activate virtual environment (if not already active)
source venv/bin/activate

# Start MkDocs server
mkdocs serve
```

Then open: **http://127.0.0.1:8000**

---

## Option 2: Use the Editor (Create/Edit Docs)

To use the web-based editor for creating and editing documentation:

### Quick Start (Easiest)

```bash
cd editor-service
./start.sh
```

This starts both backend and frontend automatically.

### Manual Start

**Terminal 1 - Backend:**
```bash
cd editor-service/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd editor-service/frontend
python3 -m http.server 8080
```

Then open: **http://localhost:8080**

---

## Option 3: Run Both (View + Edit)

You can run both at the same time:

**Terminal 1 - Documentation Site:**
```bash
source venv/bin/activate
mkdocs serve
```
→ http://127.0.0.1:8000

**Terminal 2 - Editor Backend:**
```bash
cd editor-service/backend
source venv/bin/activate  # or create new venv
pip install -r requirements.txt
python main.py
```
→ http://localhost:8001 (API)

**Terminal 3 - Editor Frontend:**
```bash
cd editor-service/frontend
python3 -m http.server 8080
```
→ http://localhost:8080 (Editor UI)

---

## Quick Reference

| Service | Port | URL | Purpose |
|---------|------|-----|---------|
| MkDocs | 8000 | http://127.0.0.1:8000 | View documentation |
| Editor Backend | 8001 | http://localhost:8001 | API for editor |
| Editor Frontend | 8080 | http://localhost:8080 | Web editor UI |
| API Docs | 8001 | http://localhost:8001/docs | Swagger UI |

---

## First Time Setup

If you haven't set up yet:

```bash
# 1. Install MkDocs dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Install Editor dependencies
cd editor-service/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Git Integration

The editor automatically commits and pushes changes. Make sure:

1. Git is configured:
   ```bash
   git config user.name "Your Name"
   git config user.email "your.email@example.com"
   ```

2. Remote is set up:
   ```bash
   git remote add origin https://github.com/phronidoc/documentation.git
   ```

See `editor-service/GIT_SETUP.md` for detailed setup.
