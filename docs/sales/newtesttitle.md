# Phronidoc Documentation Editor Service

**Transforming team chaos into structural clarity.**

Phronidoc is an open-source knowledge architecture platform built for high-velocity teams who value documentation as a product.

A web-based editor for creating and editing documentation files.

## Features

- ✏️ **Edit existing documents** - Modify any markdown file in the docs directory
- ➕ **Create new documents** - Add new documentation pages
- 📁 **Section Management** - Create and manage sections and sub-sections dynamically
- 🔄 **Auto Navigation Updates** - Navigation in mkdocs.yml updates automatically
- 🗑️ **Delete documents** - Remove documentation files
- 👁️ **Live preview** - Preview markdown as you edit
- 🔍 **Search documents** - Quickly find files
- 📝 **Markdown editor** - Syntax highlighting and code completion
- 🔄 **Git integration** - Automatic commits and pushes

## Architecture

### Backend (FastAPI)
- RESTful API for document management
- File operations (CRUD)
- Security checks to prevent directory traversal
- Automatic Git commits and pushes
- Located in `backend/`

### Frontend (Vanilla JS)
- Modern web interface
- CodeMirror editor for markdown
- Marked.js for preview
- Located in `frontend/`

## Setup

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd editor-service/backend
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the server:
   ```bash
   python main.py
   ```

   Or using uvicorn directly:
   ```bash
   uvicorn main:app --reload --port 8001
   ```

The API will be available at `http://localhost:8001`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd editor-service/frontend
   ```

2. Serve the files using a simple HTTP server:

   **Python:**
   ```bash
   python3 -m http.server 8080
   ```

   **Node.js:**
   ```bash
   npx http-server -p 8080
   ```

   **Or use any web server** (nginx, Apache, etc.)

3. Open in browser:
   ```
   http://localhost:8080
   ```

## API Endpoints

### GET `/api/documents`
List all markdown documents

### GET `/api/documents/{path}`
Get a specific document by path

### POST `/api/documents`
Create a new document
```json
{
  "path": "engineering/new-page.md",
  "content": "# Title\n\nContent...",
  "title": "Optional Title"
}
```

### PUT `/api/documents/{path}`
Update an existing document
```json
{
  "content": "# Updated Title\n\nUpdated content...",
  "title": "Optional Title"
}
```

### DELETE `/api/documents/{path}`
Delete a document

### GET `/api/sections`
Get the complete section structure with sub-sections and documents

### POST `/api/sections`
Create a new top-level section
```json
{
  "name": "Product",
  "commit_message": "Optional custom commit message",
  "push": true
}
```

### POST `/api/sections/{section}/subsections`
Create a sub-section within a section
```json
{
  "name": "API",
  "commit_message": "Optional custom commit message",
  "push": true
}
```

### DELETE `/api/sections/{path}`
Delete a section or sub-section (e.g., `engineering` or `engineering/api`)

### GET `/api/navigation`
Get the current navigation structure from mkdocs.yml

### PUT `/api/navigation`
Manually update the navigation structure
```json
{
  "navigation": [...]
}
```

### GET `/api/navigation/validate`
Validate that all navigation entries point to existing files

### GET `/api/git/status`
Get git repository status

## Git Integration

The service automatically commits and pushes changes to Git. See [GIT_SETUP.md](./GIT_SETUP.md) for setup instructions.

**Features:**
- ✅ Automatic git commits on create/update/delete
- ✅ Automatic push to remote repository
- ✅ Custom commit messages support
- ✅ Git status endpoint

## Security Considerations

⚠️ **Important**: This is a development tool. For production use, you should:

1. **Add Authentication** - Implement user authentication
2. **Add Authorization** - Control who can edit what
3. **Restrict CORS** - Only allow your frontend domain
4. **Add Rate Limiting** - Prevent abuse
5. **Input Validation** - Validate all inputs
6. **Backup System** - Implement version control or backups

## Development

### Adding Authentication

You can add authentication to the FastAPI backend using:

```python
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

@app.get("/api/documents")
async def list_documents(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Verify token
    # ...
```

### Integrating with Git

You could add git integration to automatically commit changes:

```python
import subprocess

def git_commit(file_path, message):
    subprocess.run(['git', 'add', file_path])
    subprocess.run(['git', 'commit', '-m', message])
```

## Troubleshooting

### CORS Errors
If you see CORS errors, make sure the frontend URL is allowed in the backend CORS settings.

### File Not Found
Ensure the `docs` directory path is correct in `backend/main.py`

### Port Already in Use
Change the port in `main.py` or use a different port for uvicorn.

### Git Issues
See [GIT_SETUP.md](./GIT_SETUP.md) for git configuration help.

## About Phronidoc

Phronidoc is an open-source knowledge architecture platform built for high-velocity teams who value documentation as a product. It helps transform team chaos into structural clarity by providing powerful tools for creating, managing, and maintaining documentation.

## License

Open-source - See LICENSE file for details.
