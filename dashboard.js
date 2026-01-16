// PVB Estudio Creativo Campaign Analytics Dashboard - JavaScript

const API_BASE = 'http://localhost:8001/api';

// Chart instances
let roiChart = null;
let revenueChart = null;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    console.log('🎨 PVB Estudio Creativo Campaign Analytics Dashboard');

    // Check authentication
    checkAuthentication();
});

// Check if user is authenticated
async function checkAuthentication() {
    const sessionId = localStorage.getItem('session_id');

    if (!sessionId) {
        window.location.href = 'login.html';
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/verify-session`, {
            headers: {
                'X-Session-ID': sessionId
            }
        });

        const data = await response.json();

        if (!data.valid) {
            localStorage.clear();
            window.location.href = 'login.html';
            return;
        }

        // User is authenticated, load user info
        await loadUserInfo();

        // Load initial data
        loadDashboardData();

        // Setup event listeners
        setupEventListeners();

        // Load campaigns for dropdown
        loadCampaignsList();

        // Initialize calendar
        if (window.calendarAPI) {
            window.calendarAPI.initialize();
        }

        // Initialize settings
        initializeSettings();

    } catch (error) {
        console.error('Authentication error:', error);
        alert('Error connecting to server. Please make sure the API server is running.');
    }
}

// Load user information
async function loadUserInfo() {
    const sessionId = localStorage.getItem('session_id');

    try {
        const response = await fetch(`${API_BASE}/user-info`, {
            headers: {
                'X-Session-ID': sessionId
            }
        });

        const data = await response.json();

        if (data.user) {
            // Update user greeting
            const greeting = document.getElementById('userGreeting');
            if (greeting) {
                greeting.textContent = `${data.user.full_name}'s Dashboard`;
            }
        }
    } catch (error) {
        console.error('Error loading user info:', error);
    }
}

// Setup event listeners
function setupEventListeners() {
    // Refresh button
    document.getElementById('refreshData').addEventListener('click', () => {
        console.log('Refreshing data...');
        loadDashboardData();
        if (window.calendarAPI) {
            window.calendarAPI.initialize();
        }
    });

    // Export button
    document.getElementById('exportData').addEventListener('click', exportData);

    // Settings button
    document.getElementById('settingsBtn').addEventListener('click', openSettings);

    // Logout button
    document.getElementById('logoutBtn').addEventListener('click', logout);

    // Filter changes
    document.getElementById('campaignSelect').addEventListener('change', loadDashboardData);
    document.getElementById('dateRange').addEventListener('change', loadDashboardData);
    document.getElementById('campaignType').addEventListener('change', loadCampaignsList);

    // Social Media Configuration button
    document.getElementById('socialMediaConfig').addEventListener('click', openSocialMediaConfig);
}

// Logout function
async function logout() {
    const sessionId = localStorage.getItem('session_id');

    try {
        await fetch(`${API_BASE}/logout`, {
            method: 'POST',
            headers: {
                'X-Session-ID': sessionId
            }
        });
    } catch (error) {
        console.error('Logout error:', error);
    }

    // Clear local storage
    localStorage.clear();

    // Redirect to login
    window.location.href = 'login.html';
}

// Get headers with session ID
function getHeaders() {
    return {
        'X-Session-ID': localStorage.getItem('session_id')
    };
}

// Show loading overlay
function showLoading() {
    document.getElementById('loadingOverlay').classList.add('active');
}

// Hide loading overlay
function hideLoading() {
    document.getElementById('loadingOverlay').classList.remove('active');
}

// Load all dashboard data
async function loadDashboardData() {
    showLoading();

    try {
        await Promise.all([
            loadKPIs(),
            loadROITrend(),
            loadRevenueCost(),
            loadSocialMedia(),
            loadSEOMetrics(),
            loadCampaignsTable()
        ]);

        console.log('✅ Dashboard data loaded');
    } catch (error) {
        console.error('❌ Error loading dashboard:', error);
        alert('Error loading dashboard data. Make sure the API server is running on port 8001.');
    } finally {
        hideLoading();
    }
}

// Load KPI metrics
async function loadKPIs() {
    const days = document.getElementById('dateRange').value;
    const campaignId = document.getElementById('campaignSelect').value;

    const response = await fetch(`${API_BASE}/kpis?days=${days}&campaign_id=${campaignId}`, {
        headers: getHeaders()
    });
    const data = await response.json();

    if (data.kpis) {
        // ROI
        document.getElementById('totalROI').textContent = `${data.kpis.roi.value}%`;
        document.getElementById('roiChange').textContent = `${data.kpis.roi.change >= 0 ? '+' : ''}${data.kpis.roi.change}%`;
        document.getElementById('roiChange').className = `kpi-change ${data.kpis.roi.change >= 0 ? 'positive' : 'negative'}`;

        // Revenue
        document.getElementById('totalRevenue').textContent = `$${formatNumber(data.kpis.revenue.value)}`;
        document.getElementById('revenueChange').textContent = `${data.kpis.revenue.change >= 0 ? '+' : ''}${data.kpis.revenue.change}%`;
        document.getElementById('revenueChange').className = `kpi-change ${data.kpis.revenue.change >= 0 ? 'positive' : 'negative'}`;

        // Conversions
        document.getElementById('totalConversions').textContent = formatNumber(data.kpis.conversions.value);
        document.getElementById('conversionsChange').textContent = `${data.kpis.conversions.change >= 0 ? '+' : ''}${data.kpis.conversions.change}%`;
        document.getElementById('conversionsChange').className = `kpi-change ${data.kpis.conversions.change >= 0 ? 'positive' : 'negative'}`;

        // ROAS
        document.getElementById('totalROAS').textContent = `${data.kpis.roas.value}x`;
        document.getElementById('roasChange').textContent = `${data.kpis.roas.change >= 0 ? '+' : ''}${data.kpis.roas.change}%`;
        document.getElementById('roasChange').className = `kpi-change ${data.kpis.roas.change >= 0 ? 'positive' : 'negative'}`;
    }
}

// Load ROI trend chart
async function loadROITrend() {
    const days = document.getElementById('dateRange').value;
    const campaignId = document.getElementById('campaignSelect').value;

    const response = await fetch(`${API_BASE}/roi-trend?days=${days}&campaign_id=${campaignId}`, {
        headers: getHeaders()
    });
    const data = await response.json();

    if (data.trend) {
        const ctx = document.getElementById('roiChart').getContext('2d');

        // Destroy existing chart
        if (roiChart) {
            roiChart.destroy();
        }

        // Create new chart
        roiChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.trend.labels,
                datasets: [{
                    label: 'ROI %',
                    data: data.trend.data,
                    borderColor: '#FF0000',
                    backgroundColor: 'rgba(255, 0, 0, 0.1)',
                    borderWidth: 3,
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                }
            }
        });
    }
}

// Load revenue vs cost chart
async function loadRevenueCost() {
    const days = document.getElementById('dateRange').value;
    const campaignId = document.getElementById('campaignSelect').value;

    const response = await fetch(`${API_BASE}/revenue-cost?days=${days}&campaign_id=${campaignId}`, {
        headers: getHeaders()
    });
    const result = await response.json();

    if (result.data) {
        const ctx = document.getElementById('revenueChart').getContext('2d');

        // Destroy existing chart
        if (revenueChart) {
            revenueChart.destroy();
        }

        // Create new chart
        revenueChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: result.data.labels,
                datasets: [
                    {
                        label: 'Revenue',
                        data: result.data.revenue,
                        backgroundColor: 'rgba(0, 255, 0, 0.6)',
                        borderColor: '#00FF00',
                        borderWidth: 2
                    },
                    {
                        label: 'Cost',
                        data: result.data.cost,
                        backgroundColor: 'rgba(255, 0, 0, 0.6)',
                        borderColor: '#FF0000',
                        borderWidth: 2
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '$' + value.toLocaleString();
                            }
                        }
                    }
                }
            }
        });
    }
}

// Load social media metrics
async function loadSocialMedia() {
    const days = document.getElementById('dateRange').value;
    const campaignId = document.getElementById('campaignSelect').value;

    const response = await fetch(`${API_BASE}/social-media?days=${days}&campaign_id=${campaignId}`, {
        headers: getHeaders()
    });
    const data = await response.json();

    if (data.platforms) {
        // Instagram
        if (data.platforms.instagram) {
            document.getElementById('igImpressions').textContent = formatNumber(data.platforms.instagram.impressions);
            document.getElementById('igEngagement').textContent = formatNumber(data.platforms.instagram.engagement);
            document.getElementById('igFollowers').textContent = '+' + formatNumber(data.platforms.instagram.followers);
        }

        // Facebook
        if (data.platforms.facebook) {
            document.getElementById('fbImpressions').textContent = formatNumber(data.platforms.facebook.impressions);
            document.getElementById('fbEngagement').textContent = formatNumber(data.platforms.facebook.engagement);
            document.getElementById('fbReach').textContent = formatNumber(data.platforms.facebook.reach);
        }

        // LinkedIn
        if (data.platforms.linkedin) {
            document.getElementById('liImpressions').textContent = formatNumber(data.platforms.linkedin.impressions);
            document.getElementById('liEngagement').textContent = formatNumber(data.platforms.linkedin.engagement);
            document.getElementById('liClicks').textContent = formatNumber(data.platforms.linkedin.clicks);
        }

        // TikTok
        if (data.platforms.tiktok) {
            document.getElementById('ttViews').textContent = formatNumber(data.platforms.tiktok.impressions);
            document.getElementById('ttEngagement').textContent = formatNumber(data.platforms.tiktok.engagement);
            document.getElementById('ttShares').textContent = formatNumber(data.platforms.tiktok.followers);
        }
    }
}

// Load SEO metrics
async function loadSEOMetrics() {
    const days = document.getElementById('dateRange').value;

    const response = await fetch(`${API_BASE}/seo-metrics?days=${days}`, {
        headers: getHeaders()
    });
    const data = await response.json();

    if (data.metrics) {
        // Organic Traffic
        document.getElementById('organicTraffic').textContent = formatNumber(data.metrics.organic_traffic.value);
        document.getElementById('trafficChange').textContent = `${data.metrics.organic_traffic.change >= 0 ? '+' : ''}${data.metrics.organic_traffic.change}%`;
        document.getElementById('trafficChange').className = `metric-change ${data.metrics.organic_traffic.change >= 0 ? 'positive' : 'negative'}`;

        // Keyword Rankings
        document.getElementById('keywordRankings').textContent = formatNumber(data.metrics.keyword_rankings.value);
        document.getElementById('keywordsChange').textContent = `${data.metrics.keyword_rankings.change >= 0 ? '+' : ''}${data.metrics.keyword_rankings.change}`;
        document.getElementById('keywordsChange').className = `metric-change ${data.metrics.keyword_rankings.change >= 0 ? 'positive' : 'negative'}`;

        // Backlinks
        document.getElementById('backlinks').textContent = formatNumber(data.metrics.backlinks.value);
        document.getElementById('backlinksChange').textContent = `${data.metrics.backlinks.change >= 0 ? '+' : ''}${data.metrics.backlinks.change}`;
        document.getElementById('backlinksChange').className = `metric-change ${data.metrics.backlinks.change >= 0 ? 'positive' : 'negative'}`;

        // Domain Authority
        document.getElementById('domainAuthority').textContent = data.metrics.domain_authority.value;
        document.getElementById('daChange').textContent = `${data.metrics.domain_authority.change >= 0 ? '+' : ''}${data.metrics.domain_authority.change}`;
        document.getElementById('daChange').className = `metric-change ${data.metrics.domain_authority.change >= 0 ? 'positive' : 'negative'}`;
    }
}

// Load campaigns list for dropdown
async function loadCampaignsList() {
    const campaignType = document.getElementById('campaignType').value;

    const response = await fetch(`${API_BASE}/campaigns?type=${campaignType}`, {
        headers: getHeaders()
    });
    const data = await response.json();

    if (data.campaigns) {
        const select = document.getElementById('campaignSelect');
        const currentValue = select.value;

        // Clear existing options except "All Campaigns"
        select.innerHTML = '<option value="all">All Campaigns</option>';

        // Add campaign options
        data.campaigns.forEach(campaign => {
            const option = document.createElement('option');
            option.value = campaign.campaign_id;
            option.textContent = `${campaign.campaign_name} - ${campaign.client_name}`;
            select.appendChild(option);
        });

        // Restore previous selection if possible
        if (currentValue && select.querySelector(`option[value="${currentValue}"]`)) {
            select.value = currentValue;
        }
    }
}

// Load campaigns table
async function loadCampaignsTable() {
    const campaignType = document.getElementById('campaignType').value;

    const response = await fetch(`${API_BASE}/campaigns?type=${campaignType}`, {
        headers: getHeaders()
    });
    const data = await response.json();

    if (data.campaigns) {
        const tbody = document.getElementById('campaignsTableBody');
        tbody.innerHTML = '';

        data.campaigns.forEach(campaign => {
            const row = document.createElement('tr');

            row.innerHTML = `
                <td><strong>${campaign.campaign_name}</strong></td>
                <td>${campaign.client_name}</td>
                <td>${formatCampaignType(campaign.campaign_type)}</td>
                <td>$${formatNumber(campaign.budget)}</td>
                <td>$${formatNumber(campaign.spent)}</td>
                <td><strong>${campaign.roi.toFixed(2)}%</strong></td>
                <td><span class="status-badge ${campaign.status}">${campaign.status.toUpperCase()}</span></td>
                <td>
                    <button class="action-btn" onclick="viewCampaign(${campaign.campaign_id})">View</button>
                    <button class="action-btn" onclick="editCampaign(${campaign.campaign_id})">Edit</button>
                </td>
            `;

            tbody.appendChild(row);
        });
    }
}

// Export data
function exportData() {
    console.log('Exporting data...');
    window.open(`${API_BASE}/export`, '_blank');
}

// Open Settings Page
function openSettings() {
    console.log('Opening settings page...');
    window.location.href = 'settings.html';
}

// Create Settings Modal
function createSettingsModal() {
    // Remove existing modal if it exists
    const existingModal = document.getElementById('settingsModal');
    if (existingModal) {
        existingModal.remove();
    }

    // Create modal
    const modal = document.createElement('div');
    modal.id = 'settingsModal';
    modal.className = 'settings-modal';
    modal.innerHTML = `
        <div class="settings-content">
            <div class="settings-header">
                <h2>⚙️ Settings & Preferences</h2>
                <button class="close-btn" onclick="closeSettingsModal()">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                        <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                </button>
            </div>
            
            <div class="settings-body">
                <!-- Appearance Settings -->
                <div class="settings-section">
                    <h3>🎨 Appearance</h3>
                    <div class="setting-item">
                        <label for="themeSelect">Theme</label>
                        <select id="themeSelect" class="setting-select">
                            <option value="light">Light</option>
                            <option value="dark">Dark</option>
                            <option value="auto">Auto (System)</option>
                        </select>
                    </div>
                    <div class="setting-item">
                        <label for="languageSelect">Language</label>
                        <select id="languageSelect" class="setting-select">
                            <option value="en">English</option>
                            <option value="es">Español</option>
                            <option value="fr">Français</option>
                        </select>
                    </div>
                </div>

                <!-- Dashboard Settings -->
                <div class="settings-section">
                    <h3>📊 Dashboard</h3>
                    <div class="setting-item">
                        <label for="refreshInterval">Auto-refresh Interval (seconds)</label>
                        <select id="refreshInterval" class="setting-select">
                            <option value="30">30 seconds</option>
                            <option value="60">1 minute</option>
                            <option value="300">5 minutes</option>
                            <option value="600">10 minutes</option>
                            <option value="0">Disabled</option>
                        </select>
                    </div>
                    <div class="setting-item">
                        <label class="checkbox-label">
                            <input type="checkbox" id="autoRefresh">
                            <span>Enable auto-refresh</span>
                        </label>
                    </div>
                    <div class="setting-item">
                        <label class="checkbox-label">
                            <input type="checkbox" id="showAdvanced">
                            <span>Show advanced metrics</span>
                        </label>
                    </div>
                </div>

                <!-- Notifications -->
                <div class="settings-section">
                    <h3>🔔 Notifications</h3>
                    <div class="setting-item">
                        <label class="checkbox-label">
                            <input type="checkbox" id="enableNotifications">
                            <span>Enable notifications</span>
                        </label>
                    </div>
                    <div class="setting-item">
                        <label class="checkbox-label">
                            <input type="checkbox" id="emailReports">
                            <span>Email daily reports</span>
                        </label>
                    </div>
                    <div class="setting-item">
                        <label class="checkbox-label">
                            <input type="checkbox" id="alertThresholds">
                            <span>Alert on performance thresholds</span>
                        </label>
                    </div>
                </div>

                <!-- Social Media Integration -->
                <div class="settings-section">
                    <h3>📱 Social Media Integration</h3>
                    <div class="setting-item">
                        <button class="btn-social-config" onclick="openSocialMediaConfig()">
                            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                                <path d="M8 1L10.5 5.5L15.5 6L11.75 9.5L12.5 14.5L8 12L3.5 14.5L4.25 9.5L0.5 6L5.5 5.5L8 1Z" stroke="currentColor" stroke-width="1.5" fill="currentColor"/>
                            </svg>
                            Configure Social Media Accounts
                        </button>
                    </div>
                </div>

                <!-- Data & Privacy -->
                <div class="settings-section">
                    <h3>🔒 Data & Privacy</h3>
                    <div class="setting-item">
                        <label class="checkbox-label">
                            <input type="checkbox" id="dataRetention">
                            <span>Enable data retention (keep data for 1 year)</span>
                        </label>
                    </div>
                    <div class="setting-item">
                        <label class="checkbox-label">
                            <input type="checkbox" id="analyticsTracking">
                            <span>Allow analytics tracking</span>
                        </label>
                    </div>
                </div>
            </div>
            
            <div class="settings-footer">
                <button class="btn-cancel" onclick="closeSettingsModal()">Cancel</button>
                <button class="btn-save" onclick="saveSettings()">Save Settings</button>
            </div>
        </div>
    `;

    // Add to body
    document.body.appendChild(modal);

    // Load current settings
    loadSettings();

    // Add click outside to close
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeSettingsModal();
        }
    });

    // Add escape key to close
    document.addEventListener('keydown', handleEscapeKey);
}

// Close Settings Modal
function closeSettingsModal() {
    const modal = document.getElementById('settingsModal');
    if (modal) {
        modal.remove();
        document.removeEventListener('keydown', handleEscapeKey);
    }
}

// Handle Escape Key
function handleEscapeKey(e) {
    if (e.key === 'Escape') {
        closeSettingsModal();
    }
}

// Load settings into the modal
function loadSettings() {
    // Get settings from localStorage with defaults
    const settings = {
        theme: localStorage.getItem('theme') || 'light',
        language: localStorage.getItem('language') || 'en',
        refreshInterval: localStorage.getItem('refreshInterval') || '60',
        autoRefresh: localStorage.getItem('autoRefresh') !== 'false',
        showAdvanced: localStorage.getItem('showAdvanced') !== 'false',
        enableNotifications: localStorage.getItem('enableNotifications') !== 'false',
        emailReports: localStorage.getItem('emailReports') !== 'false',
        alertThresholds: localStorage.getItem('alertThresholds') !== 'false',
        dataRetention: localStorage.getItem('dataRetention') !== 'false',
        analyticsTracking: localStorage.getItem('analyticsTracking') !== 'false'
    };
    
    // Apply settings to form elements
    const elements = {
        themeSelect: settings.theme,
        languageSelect: settings.language,
        refreshInterval: settings.refreshInterval,
        autoRefresh: settings.autoRefresh,
        showAdvanced: settings.showAdvanced,
        enableNotifications: settings.enableNotifications,
        emailReports: settings.emailReports,
        alertThresholds: settings.alertThresholds,
        dataRetention: settings.dataRetention,
        analyticsTracking: settings.analyticsTracking
    };
    
    // Set values
    Object.entries(elements).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) {
            if (element.type === 'checkbox') {
                element.checked = value;
            } else {
                element.value = value;
            }
        }
    });
}

// Save settings
function saveSettings() {
    // Get all settings from form elements
    const settings = {
        theme: document.getElementById('themeSelect')?.value || 'light',
        language: document.getElementById('languageSelect')?.value || 'en',
        refreshInterval: document.getElementById('refreshInterval')?.value || '60',
        autoRefresh: document.getElementById('autoRefresh')?.checked || false,
        showAdvanced: document.getElementById('showAdvanced')?.checked || false,
        enableNotifications: document.getElementById('enableNotifications')?.checked || false,
        emailReports: document.getElementById('emailReports')?.checked || false,
        alertThresholds: document.getElementById('alertThresholds')?.checked || false,
        dataRetention: document.getElementById('dataRetention')?.checked || false,
        analyticsTracking: document.getElementById('analyticsTracking')?.checked || false
    };
    
    // Save to localStorage
    Object.entries(settings).forEach(([key, value]) => {
        localStorage.setItem(key, value);
    });
    
    // Apply theme immediately
    applyTheme(settings.theme);
    
    // Apply auto-refresh settings
    if (settings.autoRefresh && settings.refreshInterval > 0) {
        startAutoRefresh(parseInt(settings.refreshInterval) * 1000);
    } else {
        stopAutoRefresh();
    }
    
    console.log('✅ Settings saved successfully:', settings);
    
    // Show success message
    showNotification('Settings saved successfully!', 'success');
    
    // Close modal
    closeSettingsModal();
}

// View campaign details
function viewCampaign(campaignId) {
    console.log('Viewing campaign:', campaignId);
    document.getElementById('campaignSelect').value = campaignId;
    loadDashboardData();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Edit campaign (placeholder)
function editCampaign(campaignId) {
    alert(`Edit campaign functionality coming soon! Campaign ID: ${campaignId}`);
}

// Utility: Format number with commas
function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    }
    if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toLocaleString();
}

// Utility: Format campaign type
function formatCampaignType(type) {
    const types = {
        'social_media': 'Social Media',
        'seo': 'SEO',
        'email': 'Email',
        'paid_ads': 'Paid Ads',
        'content': 'Content'
    };
    return types[type] || type;
}

// Open Social Media Configuration Modal
function openSocialMediaConfig() {
    // Create a modal for social media configuration
    const modal = document.createElement('div');
    modal.className = 'social-config-modal';
    modal.innerHTML = `
        <div class="social-config-content">
            <h2>Social Media Configuration</h2>
            <div class="config-section">
                <h3>Platform Credentials</h3>
                <div class="platform-config">
                    <label for="instagramToken">Instagram Access Token</label>
                    <input type="text" id="instagramToken" placeholder="Enter Instagram Token">
                </div>
                <div class="platform-config">
                    <label for="facebookToken">Facebook Access Token</label>
                    <input type="text" id="facebookToken" placeholder="Enter Facebook Token">
                </div>
                <div class="platform-config">
                    <label for="linkedinToken">LinkedIn Access Token</label>
                    <input type="text" id="linkedinToken" placeholder="Enter LinkedIn Token">
                </div>
                <div class="platform-config">
                    <label for="tiktokToken">TikTok Access Token</label>
                    <input type="text" id="tiktokToken" placeholder="Enter TikTok Token">
                </div>
            </div>
            <div class="config-section">
                <h3>Tracking Settings</h3>
                <div class="tracking-config">
                    <label>
                        <input type="checkbox" id="trackImpressions"> Track Impressions
                    </label>
                    <label>
                        <input type="checkbox" id="trackEngagement"> Track Engagement
                    </label>
                    <label>
                        <input type="checkbox" id="trackFollowers"> Track Followers
                    </label>
                </div>
            </div>
            <div class="modal-actions">
                <button id="saveSocialConfig">Save Configuration</button>
                <button id="cancelSocialConfig">Cancel</button>
            </div>
        </div>
    `;

    // Add to body
    document.body.appendChild(modal);

    // Add event listeners for save and cancel
    document.getElementById('saveSocialConfig').addEventListener('click', saveSocialMediaConfig);
    document.getElementById('cancelSocialConfig').addEventListener('click', () => {
        document.body.removeChild(modal);
    });
}

// Save Social Media Configuration
async function saveSocialMediaConfig() {
    const config = {
        instagram: document.getElementById('instagramToken').value,
        facebook: document.getElementById('facebookToken').value,
        linkedin: document.getElementById('linkedinToken').value,
        tiktok: document.getElementById('tiktokToken').value,
        tracking: {
            impressions: document.getElementById('trackImpressions').checked,
            engagement: document.getElementById('trackEngagement').checked,
            followers: document.getElementById('trackFollowers').checked
        }
    };

    try {
        const response = await fetch(`${API_BASE}/social-config`, {
            method: 'POST',
            headers: {
                ...getHeaders(),
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });

        const result = await response.json();

        if (result.success) {
            alert('Social Media Configuration Saved Successfully!');
            document.body.removeChild(document.querySelector('.social-config-modal'));
            loadDashboardData(); // Refresh data with new configuration
        } else {
            alert('Failed to save configuration: ' + result.message);
        }
    } catch (error) {
        console.error('Error saving social media configuration:', error);
        alert('Error saving configuration. Please try again.');
    }
}

// Auto-refresh functionality
let autoRefreshInterval = null;

function startAutoRefresh(intervalMs) {
    stopAutoRefresh(); // Clear existing interval
    autoRefreshInterval = setInterval(() => {
        console.log('🔄 Auto-refreshing dashboard data...');
        loadDashboardData();
    }, intervalMs);
    console.log(`✅ Auto-refresh started (${intervalMs/1000}s interval)`);
}

function stopAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
        console.log('⏹️ Auto-refresh stopped');
    }
}

// Theme application
function applyTheme(theme) {
    const body = document.body;
    
    // Remove existing theme classes
    body.classList.remove('theme-light', 'theme-dark');
    
    if (theme === 'dark') {
        body.classList.add('theme-dark');
    } else if (theme === 'auto') {
        // Use system preference
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            body.classList.add('theme-dark');
        } else {
            body.classList.add('theme-light');
        }
    } else {
        body.classList.add('theme-light');
    }
    
    console.log(`🎨 Theme applied: ${theme}`);
}

// Notification system
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(notification => notification.remove());
    
    // Create notification
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span class="notification-message">${message}</span>
            <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
        </div>
    `;
    
    // Add to body
    document.body.appendChild(notification);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 3000);
}

// Initialize settings on page load
function initializeSettings() {
    const theme = localStorage.getItem('theme') || 'light';
    const autoRefresh = localStorage.getItem('autoRefresh') !== 'false';
    const refreshInterval = parseInt(localStorage.getItem('refreshInterval')) || 60;
    
    // Apply theme
    applyTheme(theme);
    
    // Start auto-refresh if enabled
    if (autoRefresh && refreshInterval > 0) {
        startAutoRefresh(refreshInterval * 1000);
    }
}

// Console message
console.log(`
╔════════════════════════════════════════════════╗
║   🎨 PVB Estudio Creativo Campaign Analytics Dashboard    ║
║   Built with ❤️ by Claude Code                ║
╚════════════════════════════════════════════════╝
`);
