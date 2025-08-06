## Bookmark Parser with Category Classification

This tool validates a list of URLs, fetches their content, and automatically classifies them into categories based on their domain, URL structure, and page content. The results are saved into an `output/` directory and can be viewed in an interactive HTML report.

### Features
- **Multiple Input Methods**: Provide links via a simple text file or directly import from a browser's `bookmarks.html` export file.
- **URL Validation**: Checks if URLs are reachable.
- **Metadata Extraction**: Extracts title and description from each page.
- **Content-based Categorization**: Classifies links using a configurable system of weighted keywords, URL patterns, and domain names.
- **Interactive Report**: Generates an `index.html` file to browse, filter, and search your categorized links.
- **Extensible Configuration**: Categories, keywords, and weights can be easily modified in the `categories.json` file.
- **Concurrent Processing**: Uses threading to process multiple URLs quickly, with a progress bar.

### Installation
1. Install Python dependencies:
   ```bash
   pip install requests beautifulsoup4 nltk tqdm
   ```
2. Download nltk data (only needs to be done once):
   ```python
   import nltk
   nltk.download('punkt')
   ```

### Usage

There are two ways to provide links:

**Option 1: Import from Browser Bookmarks (Recommended)**

1.  Export your bookmarks from your browser as an HTML file (e.g., `bookmarks.html`).
2.  Run the script with the `--bookmarks` flag:
    ```bash
    python main.py --bookmarks "C:\path\to\your\bookmarks.html"
    ```

**Option 2: Use a Text File**

1.  Add URLs to the `ссылки.txt` file (or any other text file), one URL per line.
2.  Run the script. If you use a file other than `ссылки.txt`, specify it with the `--input` flag.
    ```bash
    # Using the default ссылки.txt
    python main.py

    # Using a custom file
    python main.py --input my_links.txt
    ```

### Check Results

After the script runs, all output is placed in the `output/` directory:

-   **`output/index.html`**: The main interactive report. Open this file in your browser to see the results.
-   `output/categorized_links.json`: The raw data used by the HTML report.
-   `output/categorized_links.txt`: A simple text version of the categorized links.
-   `output/success.txt`: A list of all successfully processed URLs.
-   `output/failed.txt`: A list of URLs that failed, along with the error message.
-   `output/metadata_tokens.txt`: Detailed processing information for each link.

### Customization

You can customize the classification logic by editing `categories.json`:
-   `"categories"`: Add or modify keywords and their weights for content analysis.
-   `"domain_patterns"`: Assign a category to a specific website domain (e.g., `"github.com"`). This has a high priority.
-   `"url_patterns"`: Assign a category based on patterns in the URL path (e.g., `"/news/"`).