# LearningPad Documentation

## Running Locally

This is the LearningPad documentation site built with MkDocs. To run it locally:

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

   Or if you prefer using a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

### Running the Development Server

2. Start the MkDocs development server:
   ```bash
   mkdocs serve
   ```

3. Open your browser and navigate to:
   ```
   http://127.0.0.1:8000
   ```

The site will automatically reload when you make changes to the documentation files.

### Building the Site

To build a static version of the site:

```bash
mkdocs build
```

This will create a `site/` directory with the static HTML files.

### Other Useful Commands

- `mkdocs serve --dev-addr=0.0.0.0:8000` - Serve on all network interfaces
- `mkdocs build --clean` - Clean the site directory before building
- `mkdocs gh-deploy` - Deploy to GitHub Pages (if configured)
