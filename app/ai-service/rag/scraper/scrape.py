"""Simple scraping scaffold for the RAG dataset.
- Respects robots.txt
- Uses rate limiting per domain
- Tries direct JSON/XHR endpoints first when possible
- Falls back to Playwright when content is JS-driven
- Saves raw_html + cleaned text + metadata JSON under data/web/ or data/json/
- Writes a data/scrape_index.csv summary

This script is a scaffold and won't run fully without installing dependencies (requests, playwright, beautifulsoup4)
"""
import os
import time
import csv
import json
import yaml
import hashlib
from urllib.parse import urlparse
import urllib.robotparser as robotparser
from collections import defaultdict
from datetime import datetime
from core.config import settings

# External libs - optional imports here to avoid hard dependency
try:
    import requests
except Exception:
    requests = None

try:
    from bs4 import BeautifulSoup
except Exception:
    BeautifulSoup = None

# Playwright is optional and only used when JS rendering required
try:
    from playwright.sync_api import sync_playwright
except Exception:
    sync_playwright = None


def _slugify(s: str) -> str:
    h = hashlib.sha1(s.encode('utf-8')).hexdigest()[:10]
    return ''.join(c if c.isalnum() else '_' for c in s)[:40] + '_' + h


def respect_robots(url: str) -> bool:
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    rp = robotparser.RobotFileParser()
    try:
        rp.set_url(robots_url)
        rp.read()
        return rp.can_fetch(settings.SCRAPER_USER_AGENT, url)
    except Exception:
        # If robot parsing fails, default to allowing (better to be permissive than block accidentally)
        return True


def save_scraped(url: str, raw_html: str, cleaned_text: str, meta: dict, dest_dir: str):
    os.makedirs(dest_dir, exist_ok=True)
    slug = _slugify(url)
    raw_path = os.path.join(dest_dir, f"{slug}.html")
    txt_path = os.path.join(dest_dir, f"{slug}.txt")
    meta_path = os.path.join(dest_dir, f"{slug}.json")

    with open(raw_path, 'w', encoding='utf-8') as fh:
        fh.write(raw_html)
    with open(txt_path, 'w', encoding='utf-8') as fh:
        fh.write(cleaned_text)
    with open(meta_path, 'w', encoding='utf-8') as fh:
        json.dump(meta, fh, ensure_ascii=False, indent=2)

    return raw_path, txt_path, meta_path


def extract_text_from_html(html: str) -> str:
    if BeautifulSoup is None:
        return ''
    soup = BeautifulSoup(html, 'html.parser')
    for tag in soup(['script', 'style', 'noscript']):
        tag.decompose()
    texts = []
    for el in soup.find_all(['h1','h2','h3','h4','p','li']):
        txt = el.get_text(separator=' ', strip=True)
        if txt:
            texts.append(txt)
    return '\n\n'.join(texts)


def scrape_source(entry: dict, index_writer):
    url = entry.get('url')
    if not url:
        return
    if not respect_robots(url):
        # write a .blocked file to data indicating reason
        blocked_path = os.path.join(settings.DATA_DIR, f"{entry.get('id')}.blocked")
        with open(blocked_path, 'w', encoding='utf-8') as fh:
            fh.write(f"Blocked by robots.txt: {url}\n")
        index_writer.writerow([entry.get('id'), url, blocked_path, 'blocked', 'robots.txt'])
        return

    # Simple rate limiter placeholder: per-domain sleep map (use settings.rate limit)
    if not hasattr(scrape_source, '_last_called'):
        scrape_source._last_called = defaultdict(lambda: 0.0)
    parsed = urlparse(url)
    domain = parsed.netloc
    now = time.time()
    elapsed = now - scrape_source._last_called[domain]
    min_interval = 1.0 / max(0.0001, getattr(settings, 'SCRAPER_RATE_LIMIT', 1.0))
    if elapsed < min_interval:
        time.sleep(min_interval - elapsed)
    scrape_source._last_called[domain] = time.time()

    # Try simple GET
    if requests is None:
        index_writer.writerow([entry.get('id'), url, '', 'failed', 'requests_not_installed'])
        return

    try:
        r = requests.get(url, headers={'User-Agent': settings.SCRAPER_USER_AGENT}, timeout=10)
    except Exception as e:
        index_writer.writerow([entry.get('id'), url, '', 'failed', str(e)])
        return

    if r.status_code != 200:
        index_writer.writerow([entry.get('id'), url, '', 'failed', f'status_{r.status_code}'])
        return

    content_type = r.headers.get('Content-Type', '')
    raw = r.text

    # If JSON endpoint
    if 'application/json' in content_type or entry.get('type') == 'json':
        try:
            doc = r.json()
            # Save each top-level item as a JSON file when possible
            dest = os.path.join(settings.JSON_DIR, entry.get('id'))
            os.makedirs(dest, exist_ok=True)
            if isinstance(doc, list):
                for i, item in enumerate(doc):
                    path = os.path.join(dest, f"{entry.get('id')}_{i}.json")
                    with open(path, 'w', encoding='utf-8') as fh:
                        json.dump(item, fh, ensure_ascii=False)
                    index_writer.writerow([entry.get('id'), url, path, 'ok', 'json_item'])
            else:
                path = os.path.join(dest, f"{entry.get('id')}.json")
                with open(path, 'w', encoding='utf-8') as fh:
                    json.dump(doc, fh, ensure_ascii=False)
                index_writer.writerow([entry.get('id'), url, path, 'ok', 'json'])
            return
        except Exception as e:
            # fall back to HTML parsing
            pass

    # If HTML content
    cleaned = extract_text_from_html(raw)
    # If cleaned text is too short and Playwright is available, try rendering JS-driven content
    if (not cleaned or len(cleaned.split()) < 30) and sync_playwright is not None and getattr(settings, 'USE_PLAYWRIGHT_FALLBACK', True):
        try:
            rendered = _render_with_playwright(url, timeout=getattr(settings, 'PLAYWRIGHT_TIMEOUT_SECONDS', 20))
            if rendered:
                cleaned = extract_text_from_html(rendered)
                raw = rendered
        except Exception:
            pass
    dest_dir = os.path.join(settings.WEB_DIR)
    raw_path, txt_path, meta_path = save_scraped(url, raw, cleaned, {"source": url, "timestamp": datetime.utcnow().isoformat()}, dest_dir)
    index_writer.writerow([entry.get('id'), url, txt_path, 'ok', 'html'])


def main(config_path: str = None):
    cfg = {}
    if config_path is None:
        config_path = os.path.join(os.path.dirname(__file__), 'scrape_config.yaml')
    with open(config_path, 'r', encoding='utf-8') as fh:
        cfg = yaml.safe_load(fh)

    sources = cfg.get('sources', [])
    index_path = cfg.get('scrape_index') or settings.SCRAPE_INDEX
    os.makedirs(os.path.dirname(index_path), exist_ok=True)

    with open(index_path, 'w', encoding='utf-8', newline='') as csvfh:
        writer = csv.writer(csvfh)
        writer.writerow(['id', 'url', 'local_path', 'status', 'notes'])
        for src in sources:
            try:
                scrape_source(src, writer)
            except Exception as e:
                writer.writerow([src.get('id'), src.get('url'), '', 'failed', str(e)])


def _render_with_playwright(url: str, timeout: int = 20) -> str:
    """Render the page with Playwright and return the page HTML. Optional dependency."""
    if sync_playwright is None:
        raise RuntimeError('playwright not installed')
    html = ''
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.set_default_navigation_timeout(timeout * 1000)
            page.goto(url)
            # wait for network idle briefly
            page.wait_for_load_state('networkidle', timeout=timeout * 1000)
            html = page.content()
        finally:
            browser.close()
    return html


if __name__ == '__main__':
    main()
