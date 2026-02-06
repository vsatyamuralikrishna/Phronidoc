# Quick Start Guide

## Option 1: Using the Startup Script (Easiest)

```bash
cd editor-service
./start.sh
```

This will:
- Set up the backend virtual environment
- Install dependencies
- Start the backend API on port 8001
- Start the frontend on port 8080

Then open http://localhost:8080 in your browser.

## Option 2: Manual Setup

### Backend

```bash
cd editor-service/backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Backend runs on: http://localhost:8001

### Frontend

In a new terminal:

```bash
cd editor-service/frontend
python3 -m http.server 8080
```

Frontend runs on: http://localhost:8080

## Usage

1. Open http://localhost:8080 in your browser
2. Click "New Document" to create a new page
3. Select a document from the sidebar to edit
4. Use the editor to modify content
5. Click "Save" to save changes
6. Use "Preview" to see rendered markdown

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

## Troubleshooting

### Port Already in Use
Change the port in `backend/main.py` or use different ports for frontend.

### CORS Errors
Make sure the frontend URL matches the CORS settings in `backend/main.py`.

### File Not Found
Ensure the `docs` directory path is correct relative to the backend.
