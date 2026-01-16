#!/usr/bin/env python3
"""
Figma ↔ Localhost Sync Service
Syncs designs between Figma and localhost without needing a plugin
"""

import json
import requests
import time
from datetime import datetime
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FigmaLocalhostSync:
    def __init__(self, figma_file_url, localhost_api="http://localhost:8001"):
        """
        Initialize sync service
        
        Args:
            figma_file_url: Your Figma file URL
            localhost_api: Localhost API endpoint
        """
        self.figma_file_url = figma_file_url
        self.localhost_api = localhost_api
        self.sync_dir = Path("figma-sync-data")
        self.sync_dir.mkdir(exist_ok=True)
        self.sync_log = self.sync_dir / "sync.log"
        
        logger.info(f"Figma Sync Service initialized")
        logger.info(f"Figma File: {figma_file_url}")
        logger.info(f"Localhost API: {localhost_api}")

    def check_localhost_health(self):
        """Check if localhost API is running"""
        try:
            response = requests.get(f"{self.localhost_api}/api/health", timeout=5)
            if response.status_code == 200:
                logger.info("✓ Localhost API is healthy")
                return True
            else:
                logger.warning(f"✗ Localhost API returned {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            logger.error("✗ Cannot connect to localhost API")
            return False
        except Exception as e:
            logger.error(f"✗ Error checking localhost: {e}")
            return False

    def export_figma_metadata(self):
        """
        Export Figma file metadata to JSON
        (In production, this would use Figma API)
        """
        metadata = {
            "figma_url": self.figma_file_url,
            "timestamp": datetime.now().isoformat(),
            "sync_status": "ready",
            "pages": [],
            "components": [],
            "styles": []
        }
        
        metadata_file = self.sync_dir / "figma-metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"✓ Exported Figma metadata to {metadata_file}")
        return metadata

    def export_to_localhost(self, data):
        """Export design data to localhost"""
        try:
            response = requests.post(
                f"{self.localhost_api}/api/figma/export",
                json={
                    "source": "figma",
                    "timestamp": datetime.now().isoformat(),
                    "data": data
                },
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("✓ Successfully exported to localhost")
                return response.json()
            else:
                logger.warning(f"✗ Export failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"✗ Error exporting to localhost: {e}")
            return None

    def import_from_localhost(self):
        """Import design data from localhost"""
        try:
            response = requests.get(
                f"{self.localhost_api}/api/figma/import",
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("✓ Successfully imported from localhost")
                return response.json()
            else:
                logger.warning(f"✗ Import failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"✗ Error importing from localhost: {e}")
            return None

    def save_sync_config(self, config):
        """Save sync configuration"""
        try:
            response = requests.post(
                f"{self.localhost_api}/api/figma/sync-config",
                json={
                    "figma_url": self.figma_file_url,
                    "config": config,
                    "timestamp": datetime.now().isoformat()
                },
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("✓ Sync configuration saved")
                config_file = self.sync_dir / "sync-config.json"
                with open(config_file, 'w') as f:
                    json.dump(config, f, indent=2)
                return True
            else:
                logger.warning(f"✗ Config save failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"✗ Error saving config: {e}")
            return False

    def sync_cycle(self):
        """Run a complete sync cycle"""
        logger.info("=" * 60)
        logger.info("SYNC CYCLE STARTED")
        logger.info("=" * 60)
        
        # 1. Check health
        if not self.check_localhost_health():
            logger.error("Localhost is not available. Skipping sync.")
            return False
        
        # 2. Export Figma metadata
        metadata = self.export_figma_metadata()
        
        # 3. Export to localhost
        self.export_to_localhost(metadata)
        
        # 4. Import from localhost
        localhost_data = self.import_from_localhost()
        
        # 5. Save config
        config = {
            "auto_sync": True,
            "sync_interval": 30,
            "figma_file": self.figma_file_url,
            "last_sync": datetime.now().isoformat()
        }
        self.save_sync_config(config)
        
        logger.info("=" * 60)
        logger.info("SYNC CYCLE COMPLETED")
        logger.info("=" * 60)
        
        return True

    def watch_and_sync(self, interval=30):
        """Continuously watch and sync"""
        logger.info(f"Starting watch mode (interval: {interval}s)")
        
        try:
            while True:
                self.sync_cycle()
                logger.info(f"Waiting {interval}s before next sync...")
                time.sleep(interval)
        except KeyboardInterrupt:
            logger.info("Watch mode stopped by user")

# Main execution
if __name__ == "__main__":
    import sys
    
    # Configuration
    FIGMA_FILE_URL = "https://www.figma.com/board/lL7IWBeiwobQsbQXNxpEnN/Shotlist"
    LOCALHOST_API = "http://localhost:8001"
    
    # Create sync service
    sync = FigmaLocalhostSync(FIGMA_FILE_URL, LOCALHOST_API)
    
    # Run single sync cycle
    if len(sys.argv) > 1 and sys.argv[1] == "watch":
        # Watch mode: continuous syncing
        sync.watch_and_sync(interval=30)
    else:
        # Single sync
        sync.sync_cycle()
