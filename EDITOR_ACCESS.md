# How to Access the Editor

## Quick Start

The editor is a **separate service** that runs alongside the documentation site. Here's how to access it:

### Step 1: Start the Editor Service

```bash
cd editor-service
./start.sh
```

This will start:
- Backend API on port 8001
- Frontend UI on port 8080

### Step 2: Open the Editor

Open your browser and go to:
```
http://localhost:8080
```

### Step 3: Use the Editor

- **Create New Pages**: Click the "+ New Document" button
- **Edit Existing Pages**: Click any document in the sidebar
- **Save Changes**: Click "Save" button (automatically commits to Git)
- **Preview**: Click "Preview" tab to see rendered markdown

## Running Both Services

You can run both the documentation site AND the editor at the same time:

**Terminal 1 - Documentation Site:**
```bash
source venv/bin/activate
mkdocs serve
```
→ http://127.0.0.1:8000 (View docs)

**Terminal 2 - Editor:**
```bash
cd editor-service
./start.sh
```
→ http://localhost:8080 (Edit docs)

## Troubleshooting

### Editor Not Loading?

1. Make sure the backend is running (check port 8001)
2. Check browser console for errors
3. Verify CORS settings if accessing from different domain

### Can't See Create/Edit Options?

The editor is a **separate web application**. You need to:
1. Start the editor service (see above)
2. Open http://localhost:8080 (not the MkDocs site)
3. The editor UI will have create/edit buttons

### Navigation Issues?

- All pages should now appear in the left navigation
- If a page doesn't appear, check `mkdocs.yml` navigation structure
- Rebuild the site: `mkdocs build`

---

**Note**: The MkDocs site (port 8000) is for **viewing** documentation. The Editor (port 8080) is for **creating/editing** documentation.
