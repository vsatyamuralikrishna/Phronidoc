# Phronidoc

**Transforming team chaos into structural clarity.**

Phronidoc is an open-source knowledge architecture platform built for high-velocity teams who value documentation as a product.

## Overview

Phronidoc provides a comprehensive documentation platform with:

- 📚 **MkDocs-based documentation site** - Beautiful, searchable documentation
- ✏️ **Web-based editor** - Create and edit documentation directly in the browser
- 🔄 **Git integration** - Automatic commits and pushes on every change
- 📝 **Template library** - Pre-built templates for common documentation needs
- 👥 **Team-focused structure** - Organized by Engineering, Marketing, and Sales

## Quick Start

### View Documentation

```bash
# Activate virtual environment
source venv/bin/activate

# Start MkDocs server
mkdocs serve
```

Open: **http://127.0.0.1:8000**

### Use the Editor

```bash
cd editor-service
./start.sh
```

Open: **http://localhost:8080**

See [RUN.md](./RUN.md) for detailed instructions.

## Project Structure

```
.
├── docs/                    # Documentation source files
│   ├── engineering/        # Engineering documentation
│   ├── marketing/          # Marketing documentation
│   ├── sales/              # Sales documentation
│   └── templates/          # Documentation templates
├── editor-service/         # Web-based editor
│   ├── backend/           # FastAPI backend
│   └── frontend/          # Web UI
├── mkdocs.yml             # MkDocs configuration
└── requirements.txt       # Python dependencies
```

## Features

### Documentation Site
- Material theme with custom styling
- Search functionality
- Responsive design
- Template library for consistent documentation

### Editor Service
- Create new documentation pages
- Edit existing markdown files
- Live preview
- Automatic Git commits and pushes
- Search and filter documents

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)
- Git (for version control)

### Setup

1. **Clone the repository:**
   ```bash
   git clone git@github.com-personal:vsatyamuralikrishna/Phronidoc.git
   cd Phronidoc
   ```

2. **Install MkDocs dependencies:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Install Editor dependencies:**
   ```bash
   cd editor-service/backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## Usage

### Running the Documentation Site

```bash
source venv/bin/activate
mkdocs serve
```

The site will be available at `http://127.0.0.1:8000` and automatically reload when you make changes.

### Running the Editor

```bash
cd editor-service
./start.sh
```

Or manually:
```bash
# Terminal 1 - Backend
cd editor-service/backend
source venv/bin/activate
python main.py

# Terminal 2 - Frontend
cd editor-service/frontend
python3 -m http.server 8080
```

### Building Static Site

```bash
mkdocs build
```

This creates a `site/` directory with static HTML files ready for deployment.

## Git Integration

The editor automatically commits and pushes changes. See [editor-service/GIT_SETUP.md](./editor-service/GIT_SETUP.md) for setup instructions.

## Documentation

- [RUN.md](./RUN.md) - How to run the services
- [EDITOR_ACCESS.md](./EDITOR_ACCESS.md) - Editor usage guide
- [STATUS.md](./STATUS.md) - System status check
- [editor-service/README.md](./editor-service/README.md) - Editor service documentation

## Contributing

1. Create or edit documentation using the web editor
2. Changes are automatically committed to Git
3. Push to your branch and create a pull request

## License

Open-source - See LICENSE file for details.

## Support

For issues or questions:
- Open an issue on GitHub
- Check the documentation in `docs/`
- Review [editor-service/README.md](./editor-service/README.md) for editor-specific help

---

**Phronidoc** - Transforming team chaos into structural clarity.
