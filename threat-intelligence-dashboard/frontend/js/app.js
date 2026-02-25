// Configuration
const API_BASE_URL = 'http://localhost:5000/api';

// State management
const appState = {
    scanHistory: [],
    apiKeys: {
        virustotal: '',
        abuseipdb: '',
        alienvault: ''
    },
    stats: {
        totalScans: 0,
        threatsDetected: 0,
        cleanResults: 0
    }
};

// DOM Elements
const sidebar = document.getElementById('sidebar');
const mainContent = document.getElementById('mainContent');
const menuToggle = document.getElementById('menuToggle');
const navLinks = document.querySelectorAll('.nav-link');
const pageTitle = document.getElementById('pageTitle');
const scanForm = document.getElementById('scanForm');
const scanBtn = document.getElementById('scanBtn');
const scanningIndicator = document.getElementById('scanningIndicator');
const targetInput = document.getElementById('targetInput');
const lookupType = document.getElementById('lookupType');
const errorMessage = document.getElementById('errorMessage');

// Views
const views = {
    dashboard: document.getElementById('dashboardView'),
    scan: document.getElementById('scanResultsView'),
    feeds: document.getElementById('feedsView'),
    history: document.getElementById('historyView'),
    reports: document.getElementById('reportsView'),
    settings: document.getElementById('settingsView')
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
    loadSettings();
    loadHistory();
    updateStats();
});

// Menu Toggle
menuToggle.addEventListener('click', () => {
    sidebar.classList.toggle('collapsed');
    sidebar.classList.toggle('active');
    mainContent.classList.toggle('expanded');
});

// Navigation
navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        const viewName = link.dataset.view;
        switchView(viewName);
    });
});

function switchView(viewName) {
    // Update active state
    navLinks.forEach(l => l.classList.remove('active'));
    document.querySelector(`[data-view="${viewName}"]`).classList.add('active');
    
    // Hide all views
    Object.values(views).forEach(view => view.style.display = 'none');
    
    // Show selected view
    if (views[viewName]) {
        views[viewName].style.display = 'block';
    }
    
    // Update page title
    const titles = {
        dashboard: 'Threat Intelligence Dashboard',
        scan: 'Scan Results',
        feeds: 'Live Threat Feeds',
        history: 'Scan History',
        reports: 'Reports',
        settings: 'Settings'
    };
    pageTitle.textContent = titles[viewName] || 'Dashboard';
}

// Scan Form Handler
scanForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const target = targetInput.value.trim();
    const type = lookupType.value;
    
    if (!target) {
        showError('Please enter a target to scan');
        return;
    }
    
    // Validate input
    if (!validateInput(target, type)) {
        showError('Invalid input format');
        return;
    }
    
    await performScan(target, type);
});

async function performScan(target, type) {
    try {
        // Show scanning state
        scanBtn.classList.add('scanning');
        scanBtn.disabled = true;
        scanningIndicator.classList.add('active');
        errorMessage.classList.remove('active');
        
        // Make API call
        const response = await fetch(`${API_BASE_URL}/scan`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                target: target,
                type: type,
                api_keys: appState.apiKeys
            })
        });
        
        if (!response.ok) {
            throw new Error('Scan failed');
        }
        
        const result = await response.json();
        
        // Display results
        displayScanResults(result, target, type);
        
        // Add to history
        addToHistory(target, type, result);
        
        // Update stats
        updateStats();
        
        // Switch to scan results view
        switchView('scan');
        
    } catch (error) {
        console.error('Scan error:', error);
        showError('Scan failed. Please check your API keys and try again.');
    } finally {
        // Hide scanning state
        scanBtn.classList.remove('scanning');
        scanBtn.disabled = false;
        scanningIndicator.classList.remove('active');
    }
}

function displayScanResults(result, target, type) {
    const resultContainer = document.getElementById('resultContainer');
    const scanResults = document.getElementById('scanResults');
    
    // Update header
    document.getElementById('resultTarget').textContent = target;
    document.getElementById('resultType').textContent = type.toUpperCase();
    document.getElementById('resultTime').textContent = new Date().toLocaleString();
    
    // Build results HTML
    let resultsHTML = '';
    
    // VirusTotal
    if (result.virustotal) {
        const vt = result.virustotal;
        resultsHTML += `
            <div class="result-item ${vt.malicious > 0 ? 'danger' : ''}">
                <div>
                    <div class="result-label">VirusTotal Detection</div>
                    <div class="result-value">${vt.malicious}/${vt.total} engines</div>
                </div>
                <span class="card-badge ${vt.malicious > 0 ? 'danger' : ''}">${vt.malicious > 0 ? 'Malicious' : 'Clean'}</span>
            </div>
        `;
    }
    
    // AbuseIPDB
    if (result.abuseipdb) {
        const abuse = result.abuseipdb;
        const confidence = abuse.abuseConfidenceScore || 0;
        resultsHTML += `
            <div class="result-item ${confidence > 70 ? 'danger' : ''}">
                <div>
                    <div class="result-label">AbuseIPDB Confidence</div>
                    <div class="result-value">${confidence}%</div>
                </div>
                <span class="card-badge ${confidence > 70 ? 'danger' : confidence > 40 ? 'warning' : ''}">
                    ${confidence > 70 ? 'High Risk' : confidence > 40 ? 'Medium Risk' : 'Low Risk'}
                </span>
            </div>
        `;
    }
    
    // AlienVault OTX
    if (result.alienvault) {
        const otx = result.alienvault;
        const pulses = otx.pulse_count || 0;
        resultsHTML += `
            <div class="result-item ${pulses > 5 ? 'danger' : ''}">
                <div>
                    <div class="result-label">AlienVault OTX Pulses</div>
                    <div class="result-value">${pulses} pulses</div>
                </div>
                <span class="card-badge ${pulses > 5 ? 'warning' : ''}">${pulses > 5 ? 'Suspicious' : 'Normal'}</span>
            </div>
        `;
    }
    
    // Additional info
    if (result.metadata) {
        const meta = result.metadata;
        if (meta.country) {
            resultsHTML += `
                <div class="result-item">
                    <div>
                        <div class="result-label">Geolocation</div>
                        <div class="result-value">${meta.country}${meta.city ? ' (' + meta.city + ')' : ''}</div>
                    </div>
                    <span class="card-badge">🌍</span>
                </div>
            `;
        }
    }
    
    scanResults.innerHTML = resultsHTML;
    resultContainer.classList.add('active');
}

function addToHistory(target, type, result) {
    const historyItem = {
        target,
        type,
        result,
        timestamp: new Date().toISOString(),
        isMalicious: isThreatDetected(result)
    };
    
    appState.scanHistory.unshift(historyItem);
    
    // Update stats
    appState.stats.totalScans++;
    if (historyItem.isMalicious) {
        appState.stats.threatsDetected++;
    } else {
        appState.stats.cleanResults++;
    }
    
    saveHistory();
    renderHistory();
}

function isThreatDetected(result) {
    if (result.virustotal && result.virustotal.malicious > 0) return true;
    if (result.abuseipdb && result.abuseipdb.abuseConfidenceScore > 70) return true;
    if (result.alienvault && result.alienvault.pulse_count > 5) return true;
    return false;
}

function renderHistory() {
    const historyList = document.getElementById('historyList');
    
    if (appState.scanHistory.length === 0) {
        historyList.innerHTML = '<div class="empty-state"><div class="empty-state-icon">📜</div><div class="empty-state-text">No scan history yet</div></div>';
        return;
    }
    
    historyList.innerHTML = appState.scanHistory.map(item => `
        <div class="history-item">
            <div class="history-info">
                <div class="history-query">${item.target}</div>
                <div class="history-time">${item.type.toUpperCase()} • ${formatTimestamp(item.timestamp)}</div>
            </div>
            <div class="history-actions">
                <span class="card-badge ${item.isMalicious ? 'danger' : ''}">${item.isMalicious ? 'Malicious' : 'Clean'}</span>
                <button class="icon-btn" onclick="rescan('${item.target}', '${item.type}')">🔄</button>
            </div>
        </div>
    `).join('');
}

function updateStats() {
    document.getElementById('totalScans').textContent = appState.stats.totalScans;
    document.getElementById('threatsDetected').textContent = appState.stats.threatsDetected;
    document.getElementById('cleanResults').textContent = appState.stats.cleanResults;
}

function validateInput(value, type) {
    const patterns = {
        ip: /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/,
        domain: /^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$/,
        url: /^https?:\/\/.+/,
        hash: /^[a-fA-F0-9]{32,64}$/
    };
    
    return patterns[type] ? patterns[type].test(value) : true;
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.add('active');
    setTimeout(() => {
        errorMessage.classList.remove('active');
    }, 5000);
}

function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);
    
    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
    if (hours < 24) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    return `${days} day${days > 1 ? 's' : ''} ago`;
}

// Settings
const saveSettingsBtn = document.getElementById('saveSettingsBtn');
saveSettingsBtn.addEventListener('click', () => {
    appState.apiKeys.virustotal = document.getElementById('vtApiKey').value;
    appState.apiKeys.abuseipdb = document.getElementById('abuseApiKey').value;
    appState.apiKeys.alienvault = document.getElementById('otxApiKey').value;
    
    saveSettings();
    alert('Settings saved successfully!');
});

function saveSettings() {
    localStorage.setItem('tit_api_keys', JSON.stringify(appState.apiKeys));
}

function loadSettings() {
    const saved = localStorage.getItem('tit_api_keys');
    if (saved) {
        appState.apiKeys = JSON.parse(saved);
        document.getElementById('vtApiKey').value = appState.apiKeys.virustotal || '';
        document.getElementById('abuseApiKey').value = appState.apiKeys.abuseipdb || '';
        document.getElementById('otxApiKey').value = appState.apiKeys.alienvault || '';
    }
}

function saveHistory() {
    localStorage.setItem('tit_history', JSON.stringify(appState.scanHistory));
    localStorage.setItem('tit_stats', JSON.stringify(appState.stats));
}

function loadHistory() {
    const savedHistory = localStorage.getItem('tit_history');
    const savedStats = localStorage.getItem('tit_stats');
    
    if (savedHistory) {
        appState.scanHistory = JSON.parse(savedHistory);
        renderHistory();
    }
    
    if (savedStats) {
        appState.stats = JSON.parse(savedStats);
        updateStats();
    }
}

function rescan(target, type) {
    targetInput.value = target;
    lookupType.value = type;
    switchView('dashboard');
    setTimeout(() => {
        scanForm.dispatchEvent(new Event('submit'));
    }, 100);
}

function initializeApp() {
    console.log('🛡️ TIT - Threat Intelligence Toolkit initialized');
    console.log('📡 API Integration Instructions:');
    console.log('1. Get VirusTotal API key: https://www.virustotal.com/gui/my-apikey');
    console.log('2. Get AbuseIPDB API key: https://www.abuseipdb.com/account/api');
    console.log('3. Get AlienVault OTX API key: https://otx.alienvault.com/api');
    console.log('4. Enter keys in Settings tab');
}

// Update placeholder based on lookup type
lookupType.addEventListener('change', (e) => {
    const placeholders = {
        ip: '8.8.8.8, 192.168.1.1, etc.',
        domain: 'example.com, google.com, etc.',
        url: 'https://example.com/page',
        hash: 'SHA256 or MD5 hash'
    };
    targetInput.placeholder = `Enter ${placeholders[e.target.value]}`;
});
