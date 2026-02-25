// Global Variables
let scrapedData = [];
let filteredData = [];
let currentFilter = { category: 'all', quality: 'all', search: '' };

// API Configuration
const API_BASE_URL = 'http://localhost:5000';

// Mock Data Templates
const mockDomains = ['example.com', 'demo-site.org', 'sample-blog.net', 'tech-news.io', 'web-dev.com'];
const mockTitles = [
    'Advanced Web Scraping Techniques',
    'Product Launch 2025',
    'Latest Technology News',
    'How to Build Modern Web Apps',
    'Best Practices for Data Collection',
    'Understanding Web APIs',
    'Machine Learning in 2025',
    'Cloud Computing Solutions',
    'Cybersecurity Best Practices',
    'Mobile App Development Guide'
];
const mockContentSnippets = [
    'Web scraping has evolved significantly over the years. Modern techniques involve sophisticated approaches to data extraction, including handling dynamic content, managing rate limits, and respecting robots.txt files.',
    'Our latest product features cutting-edge technology that revolutionizes the way businesses operate. With advanced analytics, real-time monitoring, and seamless integration capabilities.',
    'Breaking news in the tech industry today. Major companies announce new partnerships, innovative startups secure funding, and emerging technologies continue to reshape our digital landscape.',
    'Modern web applications require sophisticated approaches to architecture, state management, and user experience. Learn the best practices for building scalable and maintainable applications.',
    'Data collection is crucial for business intelligence. Implementing proper data pipelines, ensuring data quality, and maintaining compliance with privacy regulations are essential considerations.',
    'Application Programming Interfaces (APIs) are the backbone of modern web services. Understanding REST, GraphQL, and WebSocket protocols is essential for developers.',
    'Machine learning continues to advance rapidly. From natural language processing to computer vision, AI technologies are becoming more accessible and powerful.',
    'Cloud platforms offer scalable solutions for businesses of all sizes. Learn about different deployment strategies, cost optimization, and security best practices.',
    'Protecting digital assets is more important than ever. Implement strong authentication, encryption, and monitoring to safeguard your systems.',
    'Mobile development has matured with frameworks like React Native and Flutter. Create cross-platform applications with native performance.'
];
const contentCategories = ['Article', 'Product', 'Blog', 'News', 'Documentation', 'Landing Page', 'Forum'];
const qualityLevels = ['High', 'Medium', 'Low'];

// Initialize App
function startApp() {
    document.getElementById('welcome-screen').style.display = 'none';
    document.getElementById('main-app').style.display = 'block';
    showToast('Welcome to Advanced Web Scraper Pro!', 'info');
}

// Toggle Input Type
function toggleInputType(type) {
    const toggleBtns = document.querySelectorAll('.toggle-btn');
    toggleBtns.forEach(btn => btn.classList.remove('active'));
    document.querySelector(`[data-type="${type}"]`).classList.add('active');
    
    if (type === 'single') {
        document.getElementById('single-input').style.display = 'block';
        document.getElementById('bulk-input').style.display = 'none';
    } else {
        document.getElementById('single-input').style.display = 'none';
        document.getElementById('bulk-input').style.display = 'block';
    }
}

// Update Delay Slider Value
document.addEventListener('DOMContentLoaded', () => {
    const delaySlider = document.getElementById('delay-slider');
    if (delaySlider) {
        delaySlider.addEventListener('input', (e) => {
            document.getElementById('delay-value').textContent = e.target.value;
        });
    }
    
    // Setup get started button
    const getStartedBtn = document.querySelector('.get-started-btn');
    if (getStartedBtn) {
        getStartedBtn.addEventListener('click', startApp);
    }
});

// Start Scraping - UPDATED FOR REAL BACKEND
async function startScraping() {
    const singleUrl = document.getElementById('url-input').value.trim();
    const bulkUrls = document.getElementById('bulk-url-input').value.trim();
    const activeInput = document.querySelector('.toggle-btn.active').dataset.type;
    
    let urls = [];
    if (activeInput === 'single') {
        if (!singleUrl) {
            showToast('Please enter a URL', 'error');
            return;
        }
        if (!isValidUrl(singleUrl)) {
            showToast('Please enter a valid URL', 'error');
            return;
        }
        urls = [singleUrl];
    } else {
        if (!bulkUrls) {
            showToast('Please enter at least one URL', 'error');
            return;
        }
        urls = bulkUrls.split('\n').filter(url => url.trim()).map(url => url.trim());
        const invalidUrls = urls.filter(url => !isValidUrl(url));
        if (invalidUrls.length > 0) {
            showToast(`Invalid URLs found: ${invalidUrls[0]}`, 'error');
            return;
        }
    }
    
    // Get configuration
    const config = getScrapingConfig();
    
    // Show loading state
    const btn = document.getElementById('start-scraping-btn');
    const btnText = document.getElementById('btn-text');
    const btnLoader = document.getElementById('btn-loader');
    btnText.style.display = 'none';
    btnLoader.style.display = 'block';
    btn.disabled = true;
    
    showToast(`Starting to scrape ${urls.length} URL(s)...`, 'info');
    
    // Scrape URLs using real backend
    try {
        if (urls.length === 1) {
            // Single URL scraping
            await performRealScraping(urls[0], config);
        } else {
            // Bulk URL scraping
            await performBulkScraping(urls, config);
        }
        
        // Show results
        displayResults();
        showToast(`Successfully scraped ${urls.length} URL(s)!`, 'success');
    } catch (error) {
        showToast(`Scraping failed: ${error.message}`, 'error');
        console.error('Scraping error:', error);
    } finally {
        // Reset button
        btnText.style.display = 'block';
        btnLoader.style.display = 'none';
        btn.disabled = false;
    }
}

// Validate URL
function isValidUrl(string) {
    try {
        new URL(string);
        return true;
    } catch (_) {
        return false;
    }
}

// Get Scraping Configuration
function getScrapingConfig() {
    const config = {
        depth: parseInt(document.getElementById('depth-select').value),
        userAgent: document.getElementById('user-agent-select').value,
        requestDelay: parseFloat(document.getElementById('delay-slider').value),
        extractTypes: []
    };
    
    document.querySelectorAll('.checkbox-label input[type="checkbox"]:checked').forEach(checkbox => {
        config.extractTypes.push(checkbox.dataset.type);
    });
    
    return config;
}

// Perform Real Scraping (Single URL) - NEW FUNCTION
async function performRealScraping(url, config) {
    try {
        // Prepare options for backend
        const options = {
            useSelenium: false, // Set to true for JavaScript-heavy sites
            extractText: config.extractTypes.includes('text'),
            extractImages: config.extractTypes.includes('images'),
            extractLinks: config.extractTypes.includes('links'),
            extractMetadata: config.extractTypes.includes('metadata'),
            extractHeadings: config.extractTypes.includes('headings'),
            extractTables: config.extractTypes.includes('tables'),
            extractForms: config.extractTypes.includes('forms')
        };
        
        // Call backend API
        const response = await fetch(`${API_BASE_URL}/api/scrape`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                url: url,
                options: options
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Scraping failed');
        }
        
        const result = await response.json();
        
        if (result.success) {
            // Map backend response to frontend format
            const mappedData = mapBackendDataToFrontend(result.data);
            scrapedData.push(mappedData);
        } else {
            throw new Error(result.error || 'Unknown error');
        }
        
    } catch (error) {
        console.error('Error scraping URL:', url, error);
        
        // Add error entry to results
        scrapedData.push({
            id: Date.now() + Math.random(),
            url: url,
            title: 'Error - Could not scrape',
            content: `Failed to scrape this URL: ${error.message}`,
            images: [],
            links: [],
            metadata: {
                description: 'Error occurred during scraping',
                keywords: [],
                headings: { h1: [], h2: [], h3: [] }
            },
            category: {
                contentType: 'Error',
                dataType: [],
                qualityScore: 'Low'
            },
            timestamp: new Date().toISOString(),
            domain: new URL(url).hostname,
            stats: {
                wordCount: 0,
                imageCount: 0,
                linkCount: 0
            }
        });
        
        throw error;
    }
}

// Perform Bulk Scraping - NEW FUNCTION
async function performBulkScraping(urls, config) {
    try {
        // Prepare options for backend
        const options = {
            useSelenium: false,
            extractText: config.extractTypes.includes('text'),
            extractImages: config.extractTypes.includes('images'),
            extractLinks: config.extractTypes.includes('links'),
            extractMetadata: config.extractTypes.includes('metadata'),
            extractHeadings: config.extractTypes.includes('headings'),
            extractTables: config.extractTypes.includes('tables'),
            extractForms: config.extractTypes.includes('forms')
        };
        
        // Call backend bulk API
        const response = await fetch(`${API_BASE_URL}/api/scrape-bulk`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                urls: urls,
                options: options
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Bulk scraping failed');
        }
        
        const result = await response.json();
        
        if (result.success) {
            // Map each result to frontend format
            result.results.forEach(item => {
                if (item.success) {
                    const mappedData = mapBackendDataToFrontend(item);
                    scrapedData.push(mappedData);
                } else {
                    // Add error entry
                    scrapedData.push({
                        id: Date.now() + Math.random(),
                        url: item.url,
                        title: 'Error - Could not scrape',
                        content: `Failed to scrape this URL: ${item.error}`,
                        images: [],
                        links: [],
                        metadata: {
                            description: 'Error occurred during scraping',
                            keywords: [],
                            headings: { h1: [], h2: [], h3: [] }
                        },
                        category: {
                            contentType: 'Error',
                            dataType: [],
                            qualityScore: 'Low'
                        },
                        timestamp: new Date().toISOString(),
                        domain: new URL(item.url).hostname,
                        stats: {
                            wordCount: 0,
                            imageCount: 0,
                            linkCount: 0
                        }
                    });
                }
            });
        } else {
            throw new Error(result.error || 'Unknown error');
        }
        
    } catch (error) {
        console.error('Error in bulk scraping:', error);
        throw error;
    }
}

// Map Backend Data to Frontend Format - NEW FUNCTION
function mapBackendDataToFrontend(backendData) {
    return {
        id: Date.now() + Math.random(),
        url: backendData.url,
        title: backendData.title || backendData.metadata?.title || 'Untitled',
        content: backendData.content || 'No content extracted',
        images: backendData.images || [],
        links: backendData.links || [],
        metadata: {
            description: backendData.metadata?.description || '',
            keywords: backendData.keywords || backendData.metadata?.keywords || [],
            headings: backendData.headings || { h1: [], h2: [], h3: [] }
        },
        category: {
            contentType: backendData.category?.contentType || 'Unknown',
            dataType: ['Text', 'Links', 'Images'],
            qualityScore: backendData.category?.qualityScore || 'Medium'
        },
        timestamp: new Date(backendData.timestamp * 1000).toISOString(),
        domain: backendData.domain,
        stats: {
            wordCount: backendData.wordCount || 0,
            imageCount: backendData.imageCount || 0,
            linkCount: backendData.linkCount || 0
        }
    };
}

// Generate Mock Images (KEPT FOR REFERENCE - NOT USED WITH REAL BACKEND)
function generateMockImages(url) {
    const count = Math.floor(Math.random() * 10) + 3;
    const images = [];
    for (let i = 0; i < count; i++) {
        images.push(`${url}/image${i + 1}.jpg`);
    }
    return images;
}

// Generate Mock Links (KEPT FOR REFERENCE - NOT USED WITH REAL BACKEND)
function generateMockLinks(url) {
    const count = Math.floor(Math.random() * 20) + 10;
    const links = [];
    for (let i = 0; i < count; i++) {
        links.push(`${url}/page${i + 1}`);
    }
    return links;
}

// Generate Keywords (KEPT FOR REFERENCE - NOT USED WITH REAL BACKEND)
function generateKeywords() {
    const keywords = ['web', 'scraping', 'data', 'extraction', 'automation', 'technology', 'development', 'api', 'content', 'analysis'];
    const count = Math.floor(Math.random() * 5) + 3;
    return keywords.sort(() => 0.5 - Math.random()).slice(0, count);
}

// Categorize Content (KEPT FOR REFERENCE - NOT USED WITH REAL BACKEND)
function categorizeContent(url, content) {
    let contentType = contentCategories[Math.floor(Math.random() * contentCategories.length)];
    
    // Simple URL-based categorization
    if (url.includes('blog')) contentType = 'Blog';
    else if (url.includes('news')) contentType = 'News';
    else if (url.includes('product')) contentType = 'Product';
    else if (url.includes('docs') || url.includes('documentation')) contentType = 'Documentation';
    
    const wordCount = content.split(' ').length;
    let qualityScore = 'Medium';
    if (wordCount > 200) qualityScore = 'High';
    else if (wordCount < 100) qualityScore = 'Low';
    
    return {
        contentType: contentType,
        dataType: ['Text', 'Links', 'Images'],
        qualityScore: qualityScore
    };
}

// Display Results
function displayResults() {
    filteredData = [...scrapedData];
    document.getElementById('results-section').style.display = 'block';
    
    // Update statistics
    updateStatistics();
    
    // Update category filters
    updateCategoryFilters();
    
    // Render results
    renderResults();
    
    // Scroll to results
    document.getElementById('results-section').scrollIntoView({ behavior: 'smooth' });
}

// Update Statistics
function updateStatistics() {
    const totalUrls = scrapedData.length;
    const totalWords = scrapedData.reduce((sum, item) => sum + item.stats.wordCount, 0);
    const totalImages = scrapedData.reduce((sum, item) => sum + item.stats.imageCount, 0);
    const totalLinks = scrapedData.reduce((sum, item) => sum + item.stats.linkCount, 0);
    
    document.getElementById('total-urls').textContent = totalUrls;
    document.getElementById('total-words').textContent = totalWords.toLocaleString();
    document.getElementById('total-images').textContent = totalImages.toLocaleString();
    document.getElementById('total-links').textContent = totalLinks.toLocaleString();
}

// Update Category Filters
function updateCategoryFilters() {
    const categories = {};
    scrapedData.forEach(item => {
        const cat = item.category.contentType;
        categories[cat] = (categories[cat] || 0) + 1;
    });
    
    const filterContainer = document.getElementById('category-filters');
    filterContainer.innerHTML = `
        <button class="category-btn active" data-category="all" onclick="filterByCategory('all')">
            <span>All Results</span>
            <span class="count" id="count-all">${scrapedData.length}</span>
        </button>
    `;
    
    Object.keys(categories).sort().forEach(cat => {
        filterContainer.innerHTML += `
            <button class="category-btn" data-category="${cat}" onclick="filterByCategory('${cat}')">
                <span>${cat}</span>
                <span class="count" id="count-${cat}">${categories[cat]}</span>
            </button>
        `;
    });
    
    // Update quality counts
    const qualityCounts = { High: 0, Medium: 0, Low: 0 };
    scrapedData.forEach(item => {
        qualityCounts[item.category.qualityScore]++;
    });
    document.getElementById('count-high').textContent = qualityCounts.High;
    document.getElementById('count-medium').textContent = qualityCounts.Medium;
    document.getElementById('count-low').textContent = qualityCounts.Low;
}

// Render Results
function renderResults() {
    const grid = document.getElementById('results-grid');
    
    if (filteredData.length === 0) {
        grid.innerHTML = '<p style="color: #a0a0a0; text-align: center; grid-column: 1/-1;">No results found</p>';
        return;
    }
    
    grid.innerHTML = filteredData.map(item => `
        <div class="result-card" onclick="showDetail('${item.id}')">
            <div class="result-header">
                <a href="${item.url}" class="result-url" target="_blank" onclick="event.stopPropagation()">${item.url}</a>
                <h3 class="result-title">${item.title}</h3>
            </div>
            <p class="result-content">${item.content}</p>
            <div class="result-meta">
                <span class="meta-item">📝 ${item.stats.wordCount} words</span>
                <span class="meta-item">🖼️ ${item.stats.imageCount} images</span>
                <span class="meta-item">🔗 ${item.stats.linkCount} links</span>
            </div>
            <div class="result-tags">
                <span class="tag tag-category">${item.category.contentType}</span>
                <span class="tag tag-quality-${item.category.qualityScore.toLowerCase()}">${item.category.qualityScore} Quality</span>
            </div>
            <div class="result-timestamp">${formatTimestamp(item.timestamp)}</div>
        </div>
    `).join('');
}

// Format Timestamp
function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    const minutes = Math.floor(diff / 60000);
    
    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
    
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    
    return date.toLocaleDateString();
}

// Filter by Category
function filterByCategory(category) {
    currentFilter.category = category;
    
    document.querySelectorAll('.category-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-category="${category}"]`).classList.add('active');
    
    applyFilters();
}

// Filter by Quality
function filterByQuality(quality) {
    currentFilter.quality = currentFilter.quality === quality ? 'all' : quality;
    
    document.querySelectorAll('.quality-filters .category-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    if (currentFilter.quality !== 'all') {
        document.querySelector(`[data-quality="${quality}"]`).classList.add('active');
    }
    
    applyFilters();
}

// Filter Results (Search)
function filterResults() {
    currentFilter.search = document.getElementById('search-input').value.toLowerCase();
    applyFilters();
}

// Apply All Filters
function applyFilters() {
    filteredData = scrapedData.filter(item => {
        // Category filter
        if (currentFilter.category !== 'all' && item.category.contentType !== currentFilter.category) {
            return false;
        }
        
        // Quality filter
        if (currentFilter.quality !== 'all' && item.category.qualityScore !== currentFilter.quality) {
            return false;
        }
        
        // Search filter
        if (currentFilter.search) {
            const searchText = `${item.title} ${item.content} ${item.url}`.toLowerCase();
            if (!searchText.includes(currentFilter.search)) {
                return false;
            }
        }
        
        return true;
    });
    
    renderResults();
}

// Sort Results
function sortResults() {
    const sortBy = document.getElementById('sort-select').value;
    
    switch (sortBy) {
        case 'date':
            filteredData.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
            break;
        case 'url':
            filteredData.sort((a, b) => a.url.localeCompare(b.url));
            break;
        case 'category':
            filteredData.sort((a, b) => a.category.contentType.localeCompare(b.category.contentType));
            break;
        case 'quality':
            const qualityOrder = { High: 1, Medium: 2, Low: 3 };
            filteredData.sort((a, b) => qualityOrder[a.category.qualityScore] - qualityOrder[b.category.qualityScore]);
            break;
    }
    
    renderResults();
}

// Show Detail Modal
function showDetail(id) {
    const item = scrapedData.find(item => item.id == id);
    if (!item) return;
    
    document.getElementById('detail-title').textContent = item.title;
    document.getElementById('detail-body').innerHTML = `
        <div style="margin-bottom: 20px;">
            <h3 style="color: #f5f5f5; margin-bottom: 10px;">URL</h3>
            <a href="${item.url}" target="_blank" style="color: #00d4ff; word-break: break-all;">${item.url}</a>
        </div>
        <div style="margin-bottom: 20px;">
            <h3 style="color: #f5f5f5; margin-bottom: 10px;">Content</h3>
            <p style="color: #a0a0a0; line-height: 1.8;">${item.content}</p>
        </div>
        <div style="margin-bottom: 20px;">
            <h3 style="color: #f5f5f5; margin-bottom: 10px;">Metadata</h3>
            <p style="color: #a0a0a0;"><strong>Description:</strong> ${item.metadata.description}</p>
            <p style="color: #a0a0a0;"><strong>Keywords:</strong> ${item.metadata.keywords.join(', ')}</p>
        </div>
        <div style="margin-bottom: 20px;">
            <h3 style="color: #f5f5f5; margin-bottom: 10px;">Headings</h3>
            <p style="color: #a0a0a0;"><strong>H1:</strong> ${item.metadata.headings.h1.join(', ')}</p>
            <p style="color: #a0a0a0;"><strong>H2:</strong> ${item.metadata.headings.h2.join(', ')}</p>
            <p style="color: #a0a0a0;"><strong>H3:</strong> ${item.metadata.headings.h3.join(', ')}</p>
        </div>
        <div style="margin-bottom: 20px;">
            <h3 style="color: #f5f5f5; margin-bottom: 10px;">Statistics</h3>
            <p style="color: #a0a0a0;"><strong>Word Count:</strong> ${item.stats.wordCount}</p>
            <p style="color: #a0a0a0;"><strong>Images:</strong> ${item.stats.imageCount}</p>
            <p style="color: #a0a0a0;"><strong>Links:</strong> ${item.stats.linkCount}</p>
        </div>
        <div>
            <h3 style="color: #f5f5f5; margin-bottom: 10px;">Category</h3>
            <p style="color: #a0a0a0;"><strong>Type:</strong> ${item.category.contentType}</p>
            <p style="color: #a0a0a0;"><strong>Quality:</strong> ${item.category.qualityScore}</p>
        </div>
    `;
    
    document.getElementById('detail-modal').style.display = 'flex';
}

// Close Detail Modal
function closeDetailModal() {
    document.getElementById('detail-modal').style.display = 'none';
}

// Show Export Modal
function showExportModal() {
    if (scrapedData.length === 0) {
        showToast('No data to export', 'error');
        return;
    }
    document.getElementById('export-modal').style.display = 'flex';
}

// Close Export Modal
function closeExportModal() {
    document.getElementById('export-modal').style.display = 'none';
    document.getElementById('export-progress').style.display = 'none';
    document.getElementById('progress-fill').style.width = '0%';
}

// Generate PDF
async function generatePDF() {
    const includeStats = document.getElementById('include-stats').checked;
    const includeImages = document.getElementById('include-images').checked;
    const twoColumns = document.getElementById('two-columns').checked;
    
    // Show progress
    document.getElementById('export-progress').style.display = 'block';
    
    // Simulate progress
    for (let i = 0; i <= 100; i += 10) {
        document.getElementById('progress-fill').style.width = i + '%';
        document.getElementById('progress-percent').textContent = i + '%';
        await delay(100);
    }
    
    try {
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF();
        
        let yPosition = 20;
        const pageHeight = doc.internal.pageSize.height;
        const margin = 20;
        const lineHeight = 7;
        
        // Title
        doc.setFontSize(20);
        doc.setFont(undefined, 'bold');
        doc.text('Advanced Web Scraper - Report', margin, yPosition);
        yPosition += 10;
        
        // Date
        doc.setFontSize(10);
        doc.setFont(undefined, 'normal');
        doc.text(`Generated on: ${new Date().toLocaleString()}`, margin, yPosition);
        yPosition += 15;
        
        // Statistics
        if (includeStats) {
            doc.setFontSize(14);
            doc.setFont(undefined, 'bold');
            doc.text('Summary Statistics', margin, yPosition);
            yPosition += 10;
            
            doc.setFontSize(10);
            doc.setFont(undefined, 'normal');
            doc.text(`Total URLs Scraped: ${scrapedData.length}`, margin, yPosition);
            yPosition += lineHeight;
            doc.text(`Total Words: ${scrapedData.reduce((sum, item) => sum + item.stats.wordCount, 0).toLocaleString()}`, margin, yPosition);
            yPosition += lineHeight;
            doc.text(`Total Images: ${scrapedData.reduce((sum, item) => sum + item.stats.imageCount, 0).toLocaleString()}`, margin, yPosition);
            yPosition += lineHeight;
            doc.text(`Total Links: ${scrapedData.reduce((sum, item) => sum + item.stats.linkCount, 0).toLocaleString()}`, margin, yPosition);
            yPosition += 15;
        }
        
        // Results
        doc.setFontSize(14);
        doc.setFont(undefined, 'bold');
        doc.text('Scraped Results', margin, yPosition);
        yPosition += 10;
        
        filteredData.forEach((item, index) => {
            // Check if new page needed
            if (yPosition > pageHeight - 60) {
                doc.addPage();
                yPosition = 20;
            }
            
            doc.setFontSize(12);
            doc.setFont(undefined, 'bold');
            doc.text(`${index + 1}. ${item.title}`, margin, yPosition);
            yPosition += lineHeight;
            
            doc.setFontSize(9);
            doc.setFont(undefined, 'normal');
            doc.setTextColor(0, 100, 200);
            doc.text(item.url, margin + 5, yPosition);
            yPosition += lineHeight;
            
            doc.setTextColor(0, 0, 0);
            const contentLines = doc.splitTextToSize(item.content, 170);
            doc.text(contentLines.slice(0, 3), margin + 5, yPosition);
            yPosition += lineHeight * Math.min(3, contentLines.length);
            
            doc.setFontSize(8);
            doc.text(`Category: ${item.category.contentType} | Quality: ${item.category.qualityScore} | Words: ${item.stats.wordCount}`, margin + 5, yPosition);
            yPosition += lineHeight + 5;
        });
        
        // Save PDF
        doc.save('web-scraper-report.pdf');
        
        showToast('PDF exported successfully!', 'success');
        closeExportModal();
    } catch (error) {
        console.error('PDF generation error:', error);
        showToast('Error generating PDF', 'error');
    }
}

// Export JSON
function exportJSON() {
    if (scrapedData.length === 0) {
        showToast('No data to export', 'error');
        return;
    }
    
    const dataStr = JSON.stringify(scrapedData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'scraped-data.json';
    link.click();
    URL.revokeObjectURL(url);
    
    showToast('JSON exported successfully!', 'success');
}

// Export CSV
function exportCSV() {
    if (scrapedData.length === 0) {
        showToast('No data to export', 'error');
        return;
    }
    
    const headers = ['URL', 'Title', 'Category', 'Quality', 'Word Count', 'Images', 'Links', 'Timestamp'];
    const rows = scrapedData.map(item => [
        item.url,
        item.title,
        item.category.contentType,
        item.category.qualityScore,
        item.stats.wordCount,
        item.stats.imageCount,
        item.stats.linkCount,
        new Date(item.timestamp).toLocaleString()
    ]);
    
    let csvContent = headers.join(',') + '\n';
    rows.forEach(row => {
        csvContent += row.map(cell => `"${cell}"`).join(',') + '\n';
    });
    
    const dataBlob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'scraped-data.csv';
    link.click();
    URL.revokeObjectURL(url);
    
    showToast('CSV exported successfully!', 'success');
}

// Clear Results
function clearResults() {
    if (scrapedData.length === 0) {
        showToast('No data to clear', 'error');
        return;
    }
    
    if (confirm('Are you sure you want to clear all scraped data?')) {
        scrapedData = [];
        filteredData = [];
        document.getElementById('results-section').style.display = 'none';
        document.getElementById('url-input').value = '';
        document.getElementById('bulk-url-input').value = '';
        showToast('All data cleared', 'info');
    }
}

// Toast Notification
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icons = {
        success: '✓',
        error: '✕',
        info: 'ℹ'
    };
    
    toast.innerHTML = `
        <span class="toast-icon">${icons[type]}</span>
        <span class="toast-message">${message}</span>
    `;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideInRight 0.3s ease reverse';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Utility: Delay function
function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Close modals on outside click
window.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) {
        closeExportModal();
        closeDetailModal();
    }
});
