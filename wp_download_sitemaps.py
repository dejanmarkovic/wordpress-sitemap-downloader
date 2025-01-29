import os
import re
import time
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlparse

import requests


def get_headers():
    """
    Return headers that mimic a regular browser request
    """
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xml,application/xhtml+xml,text/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }


def make_request(url, timeout=30):
    """
    Make an HTTP request with proper headers and error handling
    """
    session = requests.Session()
    return session.get(url, headers=get_headers(), timeout=timeout, verify=True)


def should_download_sitemap(sitemap_url):
    """
    Determine if a sitemap should be downloaded based on its URL/content type.
    """
    url_lower = sitemap_url.lower()

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
    should_exclude = any(re.search(pattern, url_lower) for pattern in exclude_patterns)

    return should_include and not should_exclude


def download_sitemap(base_url, output_dir="sitemaps"):
    """
    Download filtered sitemap_index.xml and relevant child sitemaps from a WordPress site
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Try different possible sitemap URLs
    sitemap_variants = [
        "/sitemap_index.xml",
        "/wp-sitemap.xml",
        "/sitemap.xml",
        "/sitemap-index.xml",
    ]

    sitemap_found = False
    for sitemap_path in sitemap_variants:
        sitemap_index_url = urljoin(base_url, sitemap_path)
        try:
            print(f"Trying to download sitemap from: {sitemap_index_url}")
            response = make_request(sitemap_index_url)
            response.raise_for_status()
            sitemap_found = True
            break
        except requests.exceptions.RequestException as e:
            print(f"Couldn't access {sitemap_path}: {str(e)}")
            continue

    if not sitemap_found:
        print("Error: Could not find sitemap at any common locations")
        return

    try:
        # Save sitemap index
        index_path = os.path.join(output_dir, "sitemap_index.xml")
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(response.text)
        print(f"\nSuccessfully downloaded sitemap index to {index_path}")

        # Parse sitemap index
        try:
            root = ET.fromstring(response.content)
        except ET.ParseError:
            print(
                "Warning: XML parsing failed. The response might be HTML or invalid XML."
            )
            print("Response content preview:")
            print(response.text[:500])
            return

        # Find all sitemap URLs (handle both new and old WordPress sitemap formats)
        ns = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        sitemaps = root.findall(".//ns:loc", ns) or root.findall(".//loc")

        if not sitemaps:
            print(
                "No sitemaps found in the index. The site might be using a different format."
            )
            print("Raw content preview:")
            print(response.text[:500])
            return

        # Filter and download relevant sitemaps
        relevant_sitemaps = []
        skipped_sitemaps = []

        for sitemap in sitemaps:
            sitemap_url = sitemap.text
            if should_download_sitemap(sitemap_url):
                relevant_sitemaps.append(sitemap_url)
            else:
                skipped_sitemaps.append(os.path.basename(sitemap_url))

        print(f"\nFound {len(relevant_sitemaps)} relevant sitemaps to download")
        print(f"Skipping {len(skipped_sitemaps)} sitemaps")

        # Download each relevant sitemap
        for i, sitemap_url in enumerate(relevant_sitemaps, 1):
            filename = os.path.basename(sitemap_url)

            try:
                print(f"\nDownloading sitemap {i}/{len(relevant_sitemaps)}: {filename}")
                sitemap_response = make_request(sitemap_url)
                sitemap_response.raise_for_status()

                sitemap_path = os.path.join(output_dir, filename)
                with open(sitemap_path, "w", encoding="utf-8") as f:
                    f.write(sitemap_response.text)

                print(f"✓ Successfully downloaded: {filename}")
                time.sleep(1)  # Be nice to the server

            except requests.exceptions.RequestException as e:
                print(f"Error downloading {filename}: {e}")
                continue

        print("\nDownload Summary:")
        print(
            f"✓ Successfully downloaded {len(relevant_sitemaps)} sitemaps to {output_dir}/"
        )
        print("\nSkipped sitemaps:")
        for skipped in skipped_sitemaps:
            print(f"- {skipped}")

    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")


def analyze_sitemap_content(sitemap_path):
    """
    Analyze the content of a downloaded sitemap file
    """
    try:
        tree = ET.parse(sitemap_path)
        root = tree.getroot()

        ns = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        urls = root.findall(".//ns:loc", ns) or root.findall(".//loc")

        print(f"\nAnalyzing {os.path.basename(sitemap_path)}:")
        print(f"Found {len(urls)} URLs")

        if urls:
            print("\nSample URLs:")
            for url in urls[:3]:
                print(f"- {url.text}")

    except ET.ParseError as e:
        print(f"Error parsing sitemap {sitemap_path}: {e}")


if __name__ == "__main__":
    # Replace with your WordPress site URL
    wordpress_url = "https://hypestudio.org"  # Your site URL
    output_directory = "filtered_sitemaps"

    # Download filtered sitemaps
    download_sitemap(wordpress_url, output_directory)

    # Analyze downloaded sitemaps
    print("\nAnalyzing downloaded sitemaps...")
    if os.path.exists(output_directory):
        for filename in os.listdir(output_directory):
            if filename.endswith(".xml") and filename != "sitemap_index.xml":
                analyze_sitemap_content(os.path.join(output_directory, filename))
