**WordPress sitemap downloader written in Python **is a solution for downloading and analyzing WordPress website sitemaps with specific filtering capabilities. Here's the main purpose:

The script is designed to selectively download WordPress sitemaps, particularly focusing on content-rich pages while ignoring auxiliary content. It's useful in several scenarios:

1. **Content Auditing**: Helps website owners or SEO specialists collect URLs of main content pages (posts, services, case studies) while filtering out less important URLs (attachments, tags, comments). This makes it easier to perform content audits or analysis.

2. **Site Migration**: When moving a WordPress site, this tool helps gather a comprehensive list of important URLs that need to be migrated or redirected, ensuring no critical content is lost in the process.

3. **SEO Analysis**: By downloading and parsing sitemaps of specific content types, it enables analysis of site structure, content organization, and URL patterns - all crucial for SEO optimization.

4. **Content Inventory**: Creates a filtered inventory of a WordPress site's content, focusing on meaningful pages rather than auxiliary content. This is particularly useful for large websites where manual URL collection would be impractical.

I'll start by analyzing the imports and then move to the main components of the code. Let's begin with the imports:


**Imports Analysis:**

The script uses several Python standard library and third-party imports:

`import os` - The operating system module provides a way to interact with the operating system, particularly for file and directory operations. In this script, it's primarily used for creating directories and handling file paths, which is essential for saving the downloaded sitemaps.

`import re` - The regular expressions module enables pattern matching and manipulation of strings. This script uses it in the `should_download_sitemap` function to filter sitemap URLs based on specific patterns, determining which sitemaps should be downloaded and which should be skipped.

`import time` - The time module provides various time-related functions. In this script, it's used specifically for the `time.sleep()` function to add delays between sitemap downloads, implementing a polite crawling behavior that prevents overwhelming the target server.

`import xml.etree.ElementTree as ET` - The XML ElementTree module provides a simple way to parse and create XML data. Since sitemaps are XML files, this module is crucial for parsing the sitemap index and individual sitemap files to extract URLs and other information.

`from urllib.parse import urljoin, urlparse` - These functions from the urllib.parse module handle URL manipulation. `urljoin` is used to combine base URLs with paths to create complete URLs, while `urlparse` (though imported, doesn't appear to be used in the current code) can break down URLs into their components.

`import requests` - This is a third-party HTTP library that simplifies making HTTP requests. The script uses it to download sitemap files from WordPress websites, handling various HTTP operations with features like sessions, headers, and timeout management.

Let me analyze the **main functions** step by step:

**1. get_headers() Function:**
```python
def get_headers():
    """Return headers that mimic a regular browser request"""
```
This function creates a dictionary of HTTP headers that mimics a legitimate web browser. It's crucial for making the script appear as a regular browser rather than a bot. The headers include a modern Chrome User-Agent, acceptable content types, language preferences, and connection settings. This helps prevent the script from being blocked by websites that might restrict automated access.

**2. make_request(url, timeout=30) Function:**
```python
def make_request(url, timeout=30):
    """Make an HTTP request with proper headers and error handling"""
```
This function creates a session object and makes HTTP GET requests with proper error handling. It uses the headers from `get_headers()` and implements a timeout mechanism. The session object helps maintain cookies and connection pooling across requests, which is more efficient than making individual requests. The verify=True parameter ensures SSL certificate verification for secure connections.

**3. should_download_sitemap(sitemap_url) Function:**
```python
def should_download_sitemap(sitemap_url):
    """Determine if a sitemap should be downloaded based on its URL/content type."""
```
This function implements the filtering logic for sitemaps using regular expressions. It contains two lists: `include_patterns` for sitemaps that should be downloaded (like posts, pages, services) and `exclude_patterns` for sitemaps that should be skipped (like attachments, tags, comments). The function returns True only if the URL matches an include pattern and doesn't match any exclude patterns, ensuring only relevant sitemaps are downloaded.

Let me continue with analyzing the remaining functions:

**4. download_sitemap(base_url, output_dir="sitemaps") Function:**
```python
def download_sitemap(base_url, output_dir="sitemaps"):
    """Download filtered sitemap_index.xml and relevant child sitemaps from a WordPress site"""
```
This is the main function that orchestrates the entire sitemap download process. It first creates the output directory if it doesn't exist. Then it tries multiple common sitemap URL patterns (like `/sitemap_index.xml`, `/wp-sitemap.xml`) to locate the main sitemap. Once found, it saves the index file and parses it to find child sitemaps. The function handles both old and new WordPress sitemap formats through XML namespace handling. It uses the `should_download_sitemap()` function to filter relevant sitemaps and downloads them with proper delay intervals to avoid server overload.

**5. analyze_sitemap_content(sitemap_path) Function:**
```python
def analyze_sitemap_content(sitemap_path):
    """Analyze the content of a downloaded sitemap file"""
```
This function performs analysis on individual downloaded sitemap files. It parses the XML content using ElementTree and extracts all URL locations using XML namespace-aware searching. It provides a summary of the sitemap content, including the total number of URLs found and displays sample URLs (first 3) for verification. The function includes error handling for XML parsing issues, which is important for identifying malformed or invalid sitemap files.

**6. Main Execution Block:**
```python
if __name__ == "__main__":
    wordpress_url = "https://hypestudio.org"
    output_directory = "filtered_sitemaps"
```
The script's entry point defines a default WordPress URL and output directory. It then calls the `download_sitemap()` function to initiate the download process and loops through the downloaded files to analyze each one using `analyze_sitemap_content()`. This structure allows the script to be both imported as a module and run directly as a standalone program.

Explaining the ```include_patterns and  exclude_patterns

include_patterns = [
        r"post-sitemap\.xml$",
        r"page-sitemap\.xml$",
        r"service-sitemap\.xml$",
        r"category-sitemap\.xml$",
        r"archive-sitemap\.xml$",
        r"services-sitemap\.xml$",
        r"ai-automation-sitemap\.xml$",
        r"projects-sitemap\.xml$",
        r"solutions-sitemap\.xml$",
        r"case-studies-sitemap\.xml$",
    ]

    exclude_patterns = [
        r"attachment-sitemap\.xml$",
        r"author-sitemap\.xml$",
        r"tag-sitemap\.xml$",
        r"comment-sitemap\.xml$",
        r"media-sitemap\.xml$",
        r"image-sitemap\.xml$",
        r"video-sitemap\.xml$",
        r"product-tag-sitemap\.xml$",
    ]

    should_include = any(re.search(pattern, url_lower) for pattern in include_patterns)
    should_exclude = any(re.search(pattern, url_lower) for pattern in exclude_pattern ```
Let me explain these patterns and their purpose in detail:

**Include Patterns Purpose:**
These patterns define the types of WordPress sitemaps that the script SHOULD download. Each pattern targets specific content types:
- `post-sitemap.xml`: Contains URLs of all blog posts
- `page-sitemap.xml`: Contains URLs of all static pages
- `service-sitemap.xml` and `services-sitemap.xml`: Contains URLs of service-related pages
- `category-sitemap.xml`: Contains URLs of category archive pages
- `archive-sitemap.xml`: Contains URLs of date-based archives
- `ai-automation-sitemap.xml`: Contains URLs specific to AI/automation content
- `projects-sitemap.xml`: Contains URLs of project pages
- `solutions-sitemap.xml`: Contains URLs of solution pages
- `case-studies-sitemap.xml`: Contains URLs of case studies

**Exclude Patterns Purpose:**
These patterns define the types of WordPress sitemaps that the script should SKIP. Each pattern filters out auxiliary content:
- `attachment-sitemap.xml`: Skips URLs of uploaded media attachments
- `author-sitemap.xml`: Skips URLs of author archive pages
- `tag-sitemap.xml`: Skips URLs of tag archive pages
- `comment-sitemap.xml`: Skips URLs related to comments
- `media-sitemap.xml`, `image-sitemap.xml`, `video-sitemap.xml`: Skips URLs of media files
- `product-tag-sitemap.xml`: Skips URLs of product tag pages (WooCommerce related)

The `.xml$` at the end of each pattern ensures an exact match at the end of the URL, and the `\` before the period escapes the special character. This filtering system allows the script to focus on downloading content-rich pages while avoiding auxiliary content that might not be necessary for the site's main content structure.


Github repository is located here: https://github.com/dejanmarkovic/wordpress-sitemap-downloader/