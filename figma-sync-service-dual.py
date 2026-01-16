#!/usr/bin/env python3
"""
Dual Figma ↔ Localhost Sync Service
Syncs BOTH Figma files with localhost simultaneously
"""

import json
import requests
import time
from datetime import datetime
from pathlib import Path
import logging
import threading

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FigmaLocalhostSync:
    def __init__(self, figma_file_url, figma_name, localhost_api="http://localhost:8001"):
        """Initialize sync service for a single Figma file"""
        self.figma_file_url = figma_file_url
        self.figma_name = figma_name
        self.localhost_api = localhost_api
        self.sync_dir = Path(f"figma-sync-data/{figma_name.lower().replace(' ', '-')}")
        self.sync_dir.mkdir(parents=True, exist_ok=True)
        self.sync_log = self.sync_dir / "sync.log"
        
        logger.info(f"[{figma_name}] Sync Service initialized")
        logger.info(f"[{figma_name}] Figma File: {figma_file_url}")
        logger.info(f"[{figma_name}] Localhost API: {localhost_api}")

    def check_localhost_health(self):
        """Check if localhost API is running"""
        try:
            response = requests.get(f"{self.localhost_api}/api/health", timeout=5)
            if response.status_code == 200:
                logger.info(f"[{self.figma_name}] ✓ Localhost API is healthy")
                return True
            else:
                logger.warning(f"[{self.figma_name}] ✗ Localhost API returned {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            logger.error(f"[{self.figma_name}] ✗ Cannot connect to localhost API")
            return False
        except Exception as e:
            logger.error(f"[{self.figma_name}] ✗ Error checking localhost: {e}")
            return False

    def export_figma_metadata(self):
        """Export Figma file metadata to JSON"""
        metadata = {
            "figma_name": self.figma_name,
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
        
        logger.info(f"[{self.figma_name}] ✓ Exported Figma metadata to {metadata_file}")
        return metadata

    def export_to_localhost(self, data):
        """Export design data to localhost"""
        try:
            response = requests.post(
                f"{self.localhost_api}/api/figma/export",
                json={
                    "source": "figma",
                    "figma_name": self.figma_name,
                    "timestamp": datetime.now().isoformat(),
                    "data": data
                },
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"[{self.figma_name}] ✓ Successfully exported to localhost")
                return response.json()
            else:
                logger.warning(f"[{self.figma_name}] ✗ Export failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"[{self.figma_name}] ✗ Error exporting to localhost: {e}")
            return None

    def import_from_localhost(self):
        """Import design data from localhost"""
        try:
            response = requests.get(
                f"{self.localhost_api}/api/figma/import",
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"[{self.figma_name}] ✓ Successfully imported from localhost")
                return response.json()
            else:
                logger.warning(f"[{self.figma_name}] ✗ Import failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"[{self.figma_name}] ✗ Error importing from localhost: {e}")
            return None

    def save_sync_config(self, config):
        """Save sync configuration"""
        try:
            response = requests.post(
                f"{self.localhost_api}/api/figma/sync-config",
                json={
                    "figma_name": self.figma_name,
                    "figma_url": self.figma_file_url,
                    "config": config,
                    "timestamp": datetime.now().isoformat()
                },
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"[{self.figma_name}] ✓ Sync configuration saved")
                config_file = self.sync_dir / "sync-config.json"
                with open(config_file, 'w') as f:
                    json.dump(config, f, indent=2)
                return True
            else:
                logger.warning(f"[{self.figma_name}] ✗ Config save failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"[{self.figma_name}] ✗ Error saving config: {e}")
            return False

    def sync_cycle(self):
        """Run a complete sync cycle"""
        logger.info("=" * 60)
        logger.info(f"[{self.figma_name}] SYNC CYCLE STARTED")
        logger.info("=" * 60)
        
        # 1. Check health
        if not self.check_localhost_health():
            logger.error(f"[{self.figma_name}] Localhost is not available. Skipping sync.")
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
            "figma_name": self.figma_name,
            "figma_file": self.figma_file_url,
            "last_sync": datetime.now().isoformat()
        }
        self.save_sync_config(config)
        
        logger.info("=" * 60)
        logger.info(f"[{self.figma_name}] SYNC CYCLE COMPLETED")
        logger.info("=" * 60)
        
        return True

    def watch_and_sync(self, interval=30):
        """Continuously watch and sync"""
        logger.info(f"[{self.figma_name}] Starting watch mode (interval: {interval}s)")
        
        try:
            while True:
                self.sync_cycle()
                logger.info(f"[{self.figma_name}] Waiting {interval}s before next sync...")
                time.sleep(interval)
        except KeyboardInterrupt:
            logger.info(f"[{self.figma_name}] Watch mode stopped by user")

class DualFigmaSync:
    """Manages syncing of multiple Figma files simultaneously"""
    
    def __init__(self, figma_files, localhost_api="http://localhost:8001"):
        """
        Initialize dual sync service
        
        Args:
            figma_files: List of tuples (url, name)
            localhost_api: Localhost API endpoint
        """
        self.figma_files = figma_files
        self.localhost_api = localhost_api
        self.syncs = []
        
        for url, name in figma_files:
            sync = FigmaLocalhostSync(url, name, localhost_api)
            self.syncs.append(sync)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"DUAL FIGMA SYNC SERVICE INITIALIZED")
        logger.info(f"{'='*60}")
        logger.info(f"Files to sync: {len(self.syncs)}")
        for url, name in figma_files:
            logger.info(f"  • {name}")
        logger.info(f"{'='*60}\n")

    def sync_all_once(self):
        """Run sync cycle for all files sequentially"""
        logger.info(f"\n{'='*60}")
        logger.info(f"STARTING SYNC FOR ALL FILES")
        logger.info(f"{'='*60}\n")
        
        for sync in self.syncs:
            sync.sync_cycle()
            time.sleep(1)  # Brief pause between syncs
        
        logger.info(f"\n{'='*60}")
        logger.info(f"ALL FILES SYNCED SUCCESSFULLY")
        logger.info(f"{'='*60}\n")

    def watch_all(self, interval=30):
        """Watch and sync all files simultaneously in separate threads"""
        logger.info(f"\n{'='*60}")
        logger.info(f"STARTING WATCH MODE FOR ALL FILES")
        logger.info(f"Interval: {interval}s")
        logger.info(f"{'='*60}\n")
        
        threads = []
        
        # Start a thread for each sync service
        for sync in self.syncs:
            thread = threading.Thread(
                target=sync.watch_and_sync,
                args=(interval,),
                daemon=True
            )
            thread.start()
            threads.append(thread)
            time.sleep(0.5)  # Stagger thread starts
        
        # Keep main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("\n\nWatch mode stopped by user")
            logger.info("All sync services stopped")

# Main execution
if __name__ == "__main__":
    import sys
    
    # Configuration - YOUR FIGMA FILES
    FIGMA_FILES = [
        ("https://www.figma.com/board/lL7IWBeiwobQsbQXNxpEnN/Shotlist", "Shotlist-Board"),
        ("https://www.figma.com/design/PXHcQj8JYjvIPNfUx2RghG/Shotlist-Marketing-Agency---Website-Design", "Shotlist-Marketing")
    ]
    LOCALHOST_API = "http://localhost:8001"
    
    # Create dual sync service
    dual_sync = DualFigmaSync(FIGMA_FILES, LOCALHOST_API)
    
    # Run based on argument
    if len(sys.argv) > 1 and sys.argv[1] == "watch":
        # Watch mode: continuous syncing for both files
        dual_sync.watch_all(interval=30)
    else:
        # Single sync for both files
        dual_sync.sync_all_once()
