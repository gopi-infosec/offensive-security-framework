from flask import Flask, request, jsonify
from flask_cors import CORS
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import re
import time
from urllib.parse import urlparse, urljoin
from collections import Counter
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Global dictionary to store active browser sessions
active_sessions = {}

def create_driver(headless=True):
    """Create a Selenium WebDriver instance"""
    chrome_options = Options()
    if headless:
        chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def extract_text_content(soup):
    """Extract meaningful text content from HTML"""
    # Remove script and style elements
    for script in soup(["script", "style", "meta", "link"]):
        script.decompose()
    
    text = soup.get_text(separator=' ', strip=True)
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_images(soup, base_url):
    """Extract all image URLs from the page"""
    images = []
    for img in soup.find_all('img'):
        src = img.get('src') or img.get('data-src')
        if src:
            # Convert relative URLs to absolute
            full_url = urljoin(base_url, src)
            images.append({
                'url': full_url,
                'alt': img.get('alt', '')
            })
    return images

def extract_links(soup, base_url):
    """Extract all links from the page"""
    links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        full_url = urljoin(base_url, href)
        links.append({
            'url': full_url,
            'text': a.get_text(strip=True)
        })
    return links

def extract_metadata(soup):
    """Extract metadata from HTML head"""
    metadata = {}
    
    # Title
    title_tag = soup.find('title')
    metadata['title'] = title_tag.string if title_tag else ''
    
    # Meta description
    desc_tag = soup.find('meta', attrs={'name': 'description'})
    metadata['description'] = desc_tag.get('content', '') if desc_tag else ''
    
    # Meta keywords
    keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
    metadata['keywords'] = keywords_tag.get('content', '').split(',') if keywords_tag else []
    
    # Open Graph tags
    og_title = soup.find('meta', property='og:title')
    metadata['og_title'] = og_title.get('content', '') if og_title else ''
    
    return metadata

def extract_headings(soup):
    """Extract all headings (H1-H6)"""
    headings = {
        'h1': [h.get_text(strip=True) for h in soup.find_all('h1')],
        'h2': [h.get_text(strip=True) for h in soup.find_all('h2')],
        'h3': [h.get_text(strip=True) for h in soup.find_all('h3')],
        'h4': [h.get_text(strip=True) for h in soup.find_all('h4')],
        'h5': [h.get_text(strip=True) for h in soup.find_all('h5')],
        'h6': [h.get_text(strip=True) for h in soup.find_all('h6')]
    }
    return headings

def extract_tables(soup):
    """Extract table data from the page"""
    tables = []
    for table in soup.find_all('table'):
        table_data = []
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all(['td', 'th'])
            row_data = [cell.get_text(strip=True) for cell in cells]
            table_data.append(row_data)
        if table_data:
            tables.append(table_data)
    return tables

def extract_forms(soup):
    """Extract form information"""
    forms = []
    for form in soup.find_all('form'):
        form_data = {
            'action': form.get('action', ''),
            'method': form.get('method', 'GET'),
            'inputs': []
        }
        for input_tag in form.find_all(['input', 'textarea', 'select']):
            form_data['inputs'].append({
                'name': input_tag.get('name', ''),
                'type': input_tag.get('type', 'text'),
                'id': input_tag.get('id', '')
            })
        forms.append(form_data)
    return forms

def extract_keywords(text, top_n=10):
    """Extract most common keywords from text"""
    # Remove common stop words
    stop_words = set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                      'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
                      'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                      'would', 'should', 'could', 'may', 'might', 'must', 'can', 'this',
                      'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'])
    
    # Tokenize and clean
    words = re.findall(r'\b[a-z]{3,}\b', text.lower())
    words = [w for w in words if w not in stop_words]
    
    # Count and return top keywords
    word_counts = Counter(words)
    return [word for word, count in word_counts.most_common(top_n)]

def categorize_content(url, soup, text):
    """Automatically categorize scraped content"""
    url_lower = url.lower()
    text_lower = text.lower()
    
    # Content type categorization based on URL patterns and keywords
    content_type = 'Unknown'
    
    if '/blog' in url_lower or 'blog' in text_lower[:500]:
        content_type = 'Blog'
    elif '/product' in url_lower or 'price' in text_lower[:500] or 'buy now' in text_lower[:500]:
        content_type = 'Product'
    elif '/news' in url_lower or '/article' in url_lower:
        content_type = 'News'
    elif '/doc' in url_lower or 'documentation' in text_lower[:500]:
        content_type = 'Documentation'
    elif '/forum' in url_lower or 'reply' in text_lower[:500]:
        content_type = 'Forum'
    elif 'about' in url_lower or 'contact' in url_lower or 'home' in url_lower:
        content_type = 'Landing Page'
    else:
        content_type = 'Article'
    
    # Quality score based on content richness
    word_count = len(text.split())
    image_count = len(soup.find_all('img'))
    link_count = len(soup.find_all('a'))
    
    if word_count > 1000 and image_count > 5:
        quality_score = 'High'
    elif word_count > 300:
        quality_score = 'Medium'
    else:
        quality_score = 'Low'
    
    return {
        'contentType': content_type,
        'qualityScore': quality_score
    }

@app.route('/api/scrape', methods=['POST'])
def scrape():
    """Main scraping endpoint"""
    try:
        data = request.get_json()
        url = data.get('url')
        options = data.get('options', {})
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Parse options
        use_selenium = options.get('useSelenium', False)
        extract_text = options.get('extractText', True)
        extract_imgs = options.get('extractImages', True)
        extract_lnks = options.get('extractLinks', True)
        extract_meta = options.get('extractMetadata', True)
        extract_hdngs = options.get('extractHeadings', True)
        extract_tbls = options.get('extractTables', False)
        extract_frms = options.get('extractForms', False)
        
        # Get HTML content
        if use_selenium:
            driver = create_driver(headless=True)
            try:
                driver.get(url)
                # Wait for page to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                time.sleep(2)  # Additional wait for dynamic content
                html = driver.page_source
            finally:
                driver.quit()
        else:
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()
            html = response.text
        
        # Parse HTML
        soup = BeautifulSoup(html, 'lxml')
        
        # Extract data based on options
        result = {
            'url': url,
            'domain': urlparse(url).netloc,
            'timestamp': time.time()
        }
        
        text_content = extract_text_content(soup) if extract_text else ''
        result['content'] = text_content[:500]  # First 500 chars
        result['wordCount'] = len(text_content.split())
        
        if extract_imgs:
            result['images'] = extract_images(soup, url)
            result['imageCount'] = len(result['images'])
        
        if extract_lnks:
            result['links'] = extract_links(soup, url)
            result['linkCount'] = len(result['links'])
        
        if extract_meta:
            result['metadata'] = extract_metadata(soup)
            result['title'] = result['metadata'].get('title', '')
        
        if extract_hdngs:
            result['headings'] = extract_headings(soup)
        
        if extract_tbls:
            result['tables'] = extract_tables(soup)
        
        if extract_frms:
            result['forms'] = extract_forms(soup)
        
        # Auto-categorization
        category = categorize_content(url, soup, text_content)
        result['category'] = category
        
        # Extract keywords
        result['keywords'] = extract_keywords(text_content)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except requests.RequestException as e:
        return jsonify({'error': f'Request failed: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Scraping failed: {str(e)}'}), 500

@app.route('/api/scrape-bulk', methods=['POST'])
def scrape_bulk():
    """Scrape multiple URLs"""
    try:
        data = request.get_json()
        urls = data.get('urls', [])
        options = data.get('options', {})
        
        if not urls:
            return jsonify({'error': 'URLs array is required'}), 400
        
        results = []
        for url in urls:
            try:
                # Call single scrape function
                response = scrape_single_url(url, options)
                results.append(response)
            except Exception as e:
                results.append({
                    'url': url,
                    'error': str(e),
                    'success': False
                })
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        return jsonify({'error': f'Bulk scraping failed: {str(e)}'}), 500

def scrape_single_url(url, options):
    """Helper function to scrape a single URL"""
    use_selenium = options.get('useSelenium', False)
    
    if use_selenium:
        driver = create_driver(headless=True)
        try:
            driver.get(url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(2)
            html = driver.page_source
        finally:
            driver.quit()
    else:
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        html = response.text
    
    soup = BeautifulSoup(html, 'lxml')
    text_content = extract_text_content(soup)
    
    result = {
        'url': url,
        'domain': urlparse(url).netloc,
        'timestamp': time.time(),
        'content': text_content[:500],
        'wordCount': len(text_content.split()),
        'images': extract_images(soup, url),
        'links': extract_links(soup, url),
        'metadata': extract_metadata(soup),
        'headings': extract_headings(soup),
        'category': categorize_content(url, soup, text_content),
        'keywords': extract_keywords(text_content),
        'success': True
    }
    
    result['imageCount'] = len(result['images'])
    result['linkCount'] = len(result['links'])
    result['title'] = result['metadata'].get('title', '')
    
    return result

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Web Scraping API is running'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
