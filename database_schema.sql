-- SHOTLIST Campaign Analytics Database Schema
-- Marketing Campaign Measurements & ROI Tracking

-- Campaigns Table
CREATE TABLE IF NOT EXISTS campaigns (
    campaign_id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_name TEXT NOT NULL,
    client_name TEXT NOT NULL,
    campaign_type TEXT NOT NULL, -- 'social_media', 'seo', 'email', 'paid_ads', 'content'
    start_date DATE NOT NULL,
    end_date DATE,
    budget DECIMAL(10, 2) NOT NULL,
    status TEXT DEFAULT 'active', -- 'active', 'paused', 'completed'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Social Media Metrics
CREATE TABLE IF NOT EXISTS social_media_metrics (
    metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER NOT NULL,
    platform TEXT NOT NULL, -- 'instagram', 'facebook', 'twitter', 'linkedin', 'tiktok'
    date DATE NOT NULL,
    impressions INTEGER DEFAULT 0,
    reach INTEGER DEFAULT 0,
    engagement INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    followers_gained INTEGER DEFAULT 0,
    spend DECIMAL(10, 2) DEFAULT 0,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id)
);

-- SEO Metrics
CREATE TABLE IF NOT EXISTS seo_metrics (
    metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER NOT NULL,
    date DATE NOT NULL,
    organic_traffic INTEGER DEFAULT 0,
    keyword_rankings INTEGER DEFAULT 0,
    backlinks INTEGER DEFAULT 0,
    domain_authority INTEGER DEFAULT 0,
    page_authority INTEGER DEFAULT 0,
    bounce_rate DECIMAL(5, 2) DEFAULT 0,
    avg_session_duration INTEGER DEFAULT 0, -- in seconds
    pages_per_session DECIMAL(5, 2) DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id)
);

-- ROI Metrics
CREATE TABLE IF NOT EXISTS roi_metrics (
    roi_id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER NOT NULL,
    date DATE NOT NULL,
    revenue DECIMAL(10, 2) DEFAULT 0,
    cost DECIMAL(10, 2) DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    leads INTEGER DEFAULT 0,
    roi_percentage DECIMAL(10, 2) DEFAULT 0,
    roas DECIMAL(10, 2) DEFAULT 0, -- Return on Ad Spend
    cpa DECIMAL(10, 2) DEFAULT 0, -- Cost Per Acquisition
    cpl DECIMAL(10, 2) DEFAULT 0, -- Cost Per Lead
    conversion_rate DECIMAL(5, 2) DEFAULT 0,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id)
);

-- Email Marketing Metrics
CREATE TABLE IF NOT EXISTS email_metrics (
    metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER NOT NULL,
    date DATE NOT NULL,
    emails_sent INTEGER DEFAULT 0,
    emails_delivered INTEGER DEFAULT 0,
    opens INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    unsubscribes INTEGER DEFAULT 0,
    bounces INTEGER DEFAULT 0,
    open_rate DECIMAL(5, 2) DEFAULT 0,
    click_rate DECIMAL(5, 2) DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id)
);

-- Paid Ads Metrics
CREATE TABLE IF NOT EXISTS paid_ads_metrics (
    metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER NOT NULL,
    platform TEXT NOT NULL, -- 'google_ads', 'facebook_ads', 'instagram_ads', 'linkedin_ads'
    date DATE NOT NULL,
    impressions INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    spend DECIMAL(10, 2) DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    ctr DECIMAL(5, 2) DEFAULT 0, -- Click Through Rate
    cpc DECIMAL(10, 2) DEFAULT 0, -- Cost Per Click
    cpm DECIMAL(10, 2) DEFAULT 0, -- Cost Per Mille (1000 impressions)
    quality_score DECIMAL(3, 1) DEFAULT 0,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id)
);

-- Create Indexes for Performance
CREATE INDEX IF NOT EXISTS idx_campaigns_status ON campaigns(status);
CREATE INDEX IF NOT EXISTS idx_campaigns_type ON campaigns(campaign_type);
CREATE INDEX IF NOT EXISTS idx_social_campaign ON social_media_metrics(campaign_id);
CREATE INDEX IF NOT EXISTS idx_social_date ON social_media_metrics(date);
CREATE INDEX IF NOT EXISTS idx_seo_campaign ON seo_metrics(campaign_id);
CREATE INDEX IF NOT EXISTS idx_seo_date ON seo_metrics(date);
CREATE INDEX IF NOT EXISTS idx_roi_campaign ON roi_metrics(campaign_id);
CREATE INDEX IF NOT EXISTS idx_roi_date ON roi_metrics(date);
