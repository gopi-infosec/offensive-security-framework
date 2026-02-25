// Configuration
const API_BASE_URL = 'http://localhost:8000';

// State
let currentScanId = null;
let scanResults = null;

// DOM Elements
const scanForm = document.getElementById('scanForm');
const domainInput = document.getElementById('domainInput');
const scanBtn = document.getElementById('scanBtn');
const progressContainer = document.getElementById('progressContainer');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const statusContainer = document.getElementById('statusContainer');
const statusMessage = document.getElementById('statusMessage');
const resultsSection = document.getElementById('resultsSection');
const analysisPanel = document.getElementById('analysisPanel');
const analyzeBtn = document.getElementById('analyzeBtn');
const downloadBtn = document.getElementById('downloadBtn');
const newScanBtn = document.getElementById('newScanBtn');

// Tab Elements
const tabButtons = document.querySelectorAll('.tab-btn');
const tabPanels = document.querySelectorAll('.tab-panel');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
});

// Setup Event Listeners
function setupEventListeners() {
    scanForm.addEventListener('submit', handleScan);
    analyzeBtn.addEventListener('click', handleAnalyze);
    downloadBtn.addEventListener('click', handleDownload);
    newScanBtn.addEventListener('click', handleNewScan);
    
    // Tab switching
    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => switchTab(btn.dataset.tab));
    });
}

// Handle Scan
async function handleScan(e) {
    e.preventDefault();
    
    const domain = domainInput.value.trim();
    
    if (!domain) {
        showStatus('Please enter a valid domain', 'error');
        return;
    }
    
    // Reset state
    resetUI();
    
    // Show progress
    showProgress('Initializing reconnaissance scan...', 10);
    disableButton(scanBtn, true);
    
    try {
        // Simulate progress updates
        const progressInterval = simulateProgress();
        
        // Make API call
        const response = await fetch(`${API_BASE_URL}/scan`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ domain })
        });
        
        clearInterval(progressInterval);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            currentScanId = data.scan_id;
            scanResults = data.data;
            
            showProgress('Scan completed successfully!', 100);
            showStatus('Reconnaissance scan completed!', 'success');
            
            setTimeout(() => {
                hideProgress();
                displayResults(scanResults);
            }, 1000);
        } else {
            throw new Error(data.message || 'Scan failed');
        }
        
    } catch (error) {
        console.error('Scan error:', error);
        showStatus(`Scan failed: ${error.message}`, 'error');
        hideProgress();
    } finally {
        disableButton(scanBtn, false);
    }
}

// Handle Analyze
async function handleAnalyze() {
    if (!currentScanId) {
        showStatus('No scan results to analyze', 'error');
        return;
    }
    
    disableButton(analyzeBtn, true);
    showStatus('Sending data to AI for analysis...', 'info');
    
    try {
        const response = await fetch(`${API_BASE_URL}/analyze/${currentScanId}`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            showStatus('AI analysis completed!', 'success');
            displayAnalysis(data.data);
            downloadBtn.classList.remove('hidden');
        } else {
            throw new Error(data.message || 'Analysis failed');
        }
        
    } catch (error) {
        console.error('Analysis error:', error);
        showStatus(`Analysis failed: ${error.message}`, 'error');
    } finally {
        disableButton(analyzeBtn, false);
    }
}

// Handle Download
async function handleDownload() {
    if (!currentScanId) {
        showStatus('No report available', 'error');
        return;
    }
    
    try {
        showStatus('Generating PDF report...', 'info');
        
        const response = await fetch(`${API_BASE_URL}/report/${currentScanId}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `recon_report_${scanResults.domain}_${Date.now()}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        showStatus('Report downloaded successfully!', 'success');
        
    } catch (error) {
        console.error('Download error:', error);
        showStatus(`Download failed: ${error.message}`, 'error');
    }
}

// Handle New Scan
function handleNewScan() {
    resetUI();
    domainInput.value = '';
    domainInput.focus();
}

// Display Results
function displayResults(results) {
    // Show results section
    resultsSection.classList.remove('hidden');
    
    // Update stats
    document.getElementById('subdomainCount').textContent = results.subdomains.length;
    document.getElementById('liveHostCount').textContent = results.live_hosts.length;
    document.getElementById('openPortCount').textContent = Object.keys(results.open_ports).length;
    document.getElementById('endpointCount').textContent = results.endpoints.length;
    
    // Display subdomains
    const subdomainsOutput = document.getElementById('subdomainsOutput');
    subdomainsOutput.innerHTML = results.subdomains.length > 0
        ? results.subdomains.map(sd => `<div style="color: #10b981;">✓ ${sd}</div>`).join('')
        : '<div style="color: #f59e0b;">No subdomains found</div>';
    
    // Display live hosts
    const hostsOutput = document.getElementById('hostsOutput');
    hostsOutput.innerHTML = results.live_hosts.length > 0
        ? results.live_hosts.map(host => `<div style="color: #10b981;">✓ ${host}</div>`).join('')
        : '<div style="color: #f59e0b;">No live hosts found</div>';
    
    // Display ports
    const portsOutput = document.getElementById('portsOutput');
    if (Object.keys(results.open_ports).length > 0) {
        let portsHTML = '';
        for (const [host, ports] of Object.entries(results.open_ports)) {
            portsHTML += `<div style="color: #dc2626; margin-bottom: 10px;">
                <strong>${host}</strong><br>
                <span style="color: #10b981; margin-left: 20px;">Ports: ${ports.join(', ')}</span>
            </div>`;
        }
        portsOutput.innerHTML = portsHTML;
    } else {
        portsOutput.innerHTML = '<div style="color: #f59e0b;">No open ports detected</div>';
    }
    
    // Display technologies
    const techOutput = document.getElementById('techOutput');
    if (Object.keys(results.technologies).length > 0) {
        let techHTML = '';
        for (const [host, techs] of Object.entries(results.technologies)) {
            techHTML += `<div style="color: #dc2626; margin-bottom: 10px;">
                <strong>${host}</strong><br>
                <span style="color: #10b981; margin-left: 20px;">${techs.join(', ')}</span>
            </div>`;
        }
        techOutput.innerHTML = techHTML;
    } else {
        techOutput.innerHTML = '<div style="color: #f59e0b;">No technologies detected</div>';
    }
    
    // Display endpoints
    const endpointsOutput = document.getElementById('endpointsOutput');
    endpointsOutput.innerHTML = results.endpoints.length > 0
        ? results.endpoints.map(ep => `<div style="color: #10b981;">→ ${ep}</div>`).join('')
        : '<div style="color: #f59e0b;">No endpoints discovered</div>';
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Display Analysis
function displayAnalysis(analysis) {
    // Show analysis panel
    analysisPanel.classList.remove('hidden');
    
    // Set risk level
    const riskValue = document.getElementById('riskValue');
    riskValue.textContent = analysis.risk_level;
    riskValue.className = `risk-value ${analysis.risk_level}`;
    
    // Attack surface
    document.getElementById('attackSurface').textContent = analysis.attack_surface_summary;
    
    // Vulnerabilities
    const vulnList = document.getElementById('vulnerabilities');
    vulnList.innerHTML = analysis.possible_vulnerabilities
        .map(vuln => `<li>⚠️ ${vuln}</li>`)
        .join('');
    
    // Interesting endpoints
    const endpointsList = document.getElementById('interestingEndpoints');
    endpointsList.innerHTML = analysis.interesting_endpoints
        .map(ep => `<li>🎯 ${ep}</li>`)
        .join('');
    
    // Recommendations
    const recList = document.getElementById('recommendations');
    recList.innerHTML = analysis.security_recommendations
        .map(rec => `<li>🛡️ ${rec}</li>`)
        .join('');
    
    // Detailed analysis
    document.getElementById('detailedAnalysis').textContent = analysis.detailed_analysis;
    
    // Scroll to analysis
    analysisPanel.scrollIntoView({ behavior: 'smooth' });
}

// Switch Tab
function switchTab(tabName) {
    // Update buttons
    tabButtons.forEach(btn => {
        if (btn.dataset.tab === tabName) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
    
    // Update panels
    tabPanels.forEach(panel => {
        if (panel.id === `tab-${tabName}`) {
            panel.classList.add('active');
        } else {
            panel.classList.remove('active');
        }
    });
}

// Show Progress
function showProgress(text, percentage) {
    progressContainer.classList.remove('hidden');
    progressText.textContent = text;
    progressFill.style.width = `${percentage}%`;
}

// Hide Progress
function hideProgress() {
    progressContainer.classList.add('hidden');
}

// Simulate Progress
function simulateProgress() {
    let progress = 10;
    const messages = [
        'Enumerating subdomains...',
        'Detecting live hosts...',
        'Scanning ports...',
        'Detecting technologies...',
        'Discovering endpoints...',
        'Finalizing scan...'
    ];
    let messageIndex = 0;
    
    return setInterval(() => {
        progress += Math.random() * 15;
        if (progress > 95) progress = 95;
        
        if (progress > (messageIndex + 1) * 15) {
            messageIndex = Math.min(messageIndex + 1, messages.length - 1);
        }
        
        showProgress(messages[messageIndex], progress);
    }, 1500);
}

// Show Status
function showStatus(message, type = 'info') {
    statusContainer.classList.remove('hidden');
    statusMessage.textContent = message;
    statusMessage.className = `status-message ${type}`;
    
    // Auto-hide after 5 seconds for success messages
    if (type === 'success') {
        setTimeout(() => {
            statusContainer.classList.add('hidden');
        }, 5000);
    }
}

// Disable Button
function disableButton(button, disabled) {
    button.disabled = disabled;
    if (disabled) {
        button.style.opacity = '0.6';
        button.style.cursor = 'not-allowed';
    } else {
        button.style.opacity = '1';
        button.style.cursor = 'pointer';
    }
}

// Reset UI
function resetUI() {
    hideProgress();
    statusContainer.classList.add('hidden');
    resultsSection.classList.add('hidden');
    analysisPanel.classList.add('hidden');
    downloadBtn.classList.add('hidden');
    currentScanId = null;
    scanResults = null;
}
