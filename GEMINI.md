## Project Overview

This project is a Python-based tool for parsing and categorizing a list of URLs. It can take a list of URLs from a text file or a browser's `bookmarks.html` file. It validates the URLs, extracts metadata (title and description), and then classifies them into predefined categories. The classification logic is configurable via an external `categories.json` file, which defines categories, weighted keywords, URL path patterns, and domain-specific patterns.

The results are saved in various text and JSON formats into an `output/` directory. The primary output is an interactive `index.html` report that allows for searching and filtering the categorized links.

**Main Technologies:**

*   Python
*   `requests` for fetching URLs
*   `BeautifulSoup4` for HTML parsing
*   `tqdm` for progress bars

**Architecture:**

The project consists of three main files:

*   `main.py`: The main entry point. It handles command-line arguments, reads URLs from either a text file or a bookmarks file, and uses a thread pool (`concurrent.futures`) to process URLs in parallel. It orchestrates the extraction and classification process and writes the output files.
*   `category_classifier.py`: This script contains the logic for classifying text and URLs. It loads its configuration from `categories.json` and scores links based on domain, URL path, and weighted keywords found in the page's metadata.
*   `categories.json`: A configuration file that defines the categories, keywords, weights, and patterns used for classification. This allows for easy customization without changing the Python code.

## Building and Running

**1. Install Dependencies:**

```bash
pip install requests beautifulsoup4 nltk tqdm
```

**2. Download NLTK data (one-time setup):**

```python
import nltk
nltk.download('punkt')
```

**3. Running the script:**

*   **From a bookmarks file:**
    ```bash
    python main.py --bookmarks /path/to/your/bookmarks.html
    ```
*   **From a text file (default `ссылки.txt`):**
    ```bash
    python main.py
    ```

All output files are saved to the `output/` directory.

## Development Conventions

*   **Configuration:** All classification logic (keywords, patterns, weights) is stored in `categories.json` to keep it separate from the application code.
*   **Concurrency:** The script uses a `ThreadPoolExecutor` to process multiple URLs in parallel, with a `tqdm` progress bar to show progress.
*   **Logging:** The script uses the `logging` module for output. It logs informational messages and errors.
*   **Output:** All generated files are placed in the `output/` directory to keep the root directory clean.
*   **Modularity:** The core classification logic is separated in `category_classifier.py`, while the main orchestration, file I/O, and web requests are in `main.py`.