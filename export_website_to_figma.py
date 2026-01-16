#!/usr/bin/env python3
"""
Export Full Website to Figma
Imports all pages of the website into Figma using the Figma plugin API
"""

import requests
import json
import time
from pathlib import Path

# Configuration
LOCALHOST_API = "http://localhost:8001"
FIGMA_PLUGIN_API = "http://localhost:8000"  # If running Figma plugin server

# All pages to import
PAGES = [
    {'name': 'index', 'file': 'index.html', 'title': 'Homepage - PVB Estudio'},
    {'name': 'dashboard', 'file': 'dashboard.html', 'title': 'Dashboard'},
    {'name': 'settings', 'file': 'settings.html', 'title': 'Settings'},
    {'name': 'login', 'file': 'login.html', 'title': 'Login'}
]

def check_api_health():
    """Check if localhost API is running"""
    try:
        response = requests.get(f"{LOCALHOST_API}/api/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_page_data(page_name):
    """Get HTML/CSS data for a page"""
    try:
        response = requests.get(
            f"{LOCALHOST_API}/api/figma/import?page={page_name}",
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        else:
            print(f"✗ Failed to get {page_name}: {response.status_code}")
            return None
    except Exception as e:
        print(f"✗ Error getting {page_name}: {e}")
        return None

def create_figma_import_script():
    """Create a script that can be run in Figma to import all pages"""
    
    script_content = """
// Figma Plugin Script - Import Full Website
// Run this in Figma Plugin Console or as a plugin command

const pages = [
    'index',
    'dashboard', 
    'settings',
    'login'
];

async function importAllPages() {
    const localhostApi = 'http://localhost:8001';
    const createdFrames = [];
    
    for (const page of pages) {
        try {
            console.log(`Importing ${page}...`);
            
            // Fetch page data
            const response = await fetch(`${localhostApi}/api/figma/import?page=${page}`);
            const data = await response.json();
            
            if (data.html && data.css) {
                // Create frame for this page
                const frame = figma.createFrame();
                frame.name = `${page.charAt(0).toUpperCase() + page.slice(1)} Page`;
                frame.resize(1440, 2000); // Standard desktop size
                
                // Import HTML/CSS (this would use your existing import function)
                // For now, we'll create a placeholder
                const text = figma.createText();
                await figma.loadFontAsync({ family: "Inter", style: "Regular" });
                text.characters = `${page} - Imported from localhost`;
                text.x = 20;
                text.y = 20;
                frame.appendChild(text);
                
                createdFrames.push(frame);
                console.log(`✓ Imported ${page}`);
            }
        } catch (error) {
            console.error(`✗ Error importing ${page}:`, error);
        }
    }
    
    // Arrange frames horizontally
    let xOffset = 0;
    for (const frame of createdFrames) {
        frame.x = xOffset;
        frame.y = 0;
        xOffset += frame.width + 100; // 100px spacing
    }
    
    console.log(`✓ Imported ${createdFrames.length} pages`);
    return createdFrames;
}

// Run import
importAllPages();
"""
    
    script_path = Path("figma-import-all-pages.js")
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    print(f"✓ Created Figma import script: {script_path}")
    return script_path

def create_website_structure_json():
    """Create a JSON structure representing the full website"""
    
    website_structure = {
        "website": "PVB Estudio Creativo",
        "pages": [],
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    print("📦 Gathering website data...")
    
    for page in PAGES:
        print(f"  → Fetching {page['name']}...")
        data = get_page_data(page['name'])
        
        if data:
            website_structure["pages"].append({
                "name": page['name'],
                "title": page['title'],
                "file": page['file'],
                "html_length": len(data.get('html', '')),
                "css_length": len(data.get('css', '')),
                "has_design_tokens": bool(data.get('designTokens')),
                "sections": extract_sections(data.get('html', ''))
            })
            print(f"    ✓ {page['name']} loaded")
        else:
            print(f"    ✗ {page['name']} failed")
    
    # Save structure
    structure_path = Path("figma-sync-data/website-structure.json")
    structure_path.parent.mkdir(exist_ok=True)
    
    with open(structure_path, 'w') as f:
        json.dump(website_structure, f, indent=2)
    
    print(f"\n✓ Website structure saved to: {structure_path}")
    return structure_path

def extract_sections(html):
    """Extract main sections from HTML"""
    sections = []
    
    # Simple section extraction (look for section tags and main IDs)
    import re
    
    # Find section tags
    section_pattern = r'<section[^>]*(?:id|class)="([^"]+)"'
    sections_found = re.findall(section_pattern, html)
    
    # Find main divs with IDs
    div_pattern = r'<div[^>]*id="([^"]+)"'
    divs_found = re.findall(div_pattern, html)
    
    sections = list(set(sections_found + divs_found))
    
    return sections[:10]  # Return first 10 sections

def print_import_instructions():
    """Print instructions for importing to Figma"""
    
    instructions = """
╔══════════════════════════════════════════════════════════════╗
║  📱 HOW TO VIEW FULL WEBSITE IN FIGMA                        ║
╚══════════════════════════════════════════════════════════════╝

METHOD 1: Using Figma Plugin (Recommended)
───────────────────────────────────────────

1. Make sure API server is running:
   python3 api_server.py

2. Open Figma Desktop App

3. Open your Figma file:
   https://www.figma.com/board/lL7IWBeiwobQsbQXNxpEnN/Shotlist

4. Load the Localhost Sync plugin:
   - Plugins → Development → Import plugin from manifest
   - Navigate to: figma-localhost-sync/manifest.json

5. Import each page:
   - Open plugin: Plugins → Localhost Sync
   - Go to Import tab
   - Import each page one by one:
     • Select "index" → Click "Import from Localhost"
     • Select "dashboard" → Click "Import from Localhost"
     • Select "settings" → Click "Import from Localhost"
     • Select "login" → Click "Import from Localhost"

6. Arrange pages in Figma:
   - Each import creates a new frame
   - Arrange frames side by side or in a grid
   - You'll see the full website structure!


METHOD 2: Using API Directly
─────────────────────────────

You can also use the API endpoints directly:

1. Get homepage:
   curl http://localhost:8001/api/figma/import?page=index

2. Get dashboard:
   curl http://localhost:8001/api/figma/import?page=dashboard

3. Get all pages:
   curl http://localhost:8001/api/figma/import-all


METHOD 3: View Website Structure
─────────────────────────────────

Check the website structure file:
  cat figma-sync-data/website-structure.json

This shows all pages and their sections.


╔══════════════════════════════════════════════════════════════╗
║  💡 TIP: Create a "Website Overview" page in Figma         ║
║                                                              ║
║  Import all pages, then create a master frame showing:       ║
║  • Homepage (index)                                         ║
║  • Dashboard                                                ║
║  • Settings                                                 ║
║  • Login                                                    ║
║                                                              ║
║  This gives you a complete visual of your website!          ║
╚══════════════════════════════════════════════════════════════╝
"""
    
    print(instructions)

def main():
    """Main execution"""
    print("=" * 60)
    print("🌐 EXPORT FULL WEBSITE TO FIGMA")
    print("=" * 60)
    print()
    
    # Check API health
    print("1. Checking API server...")
    if not check_api_health():
        print("✗ API server is not running!")
        print("  Please start it with: python3 api_server.py")
        return
    print("✓ API server is running")
    print()
    
    # Create website structure
    print("2. Creating website structure...")
    create_website_structure_json()
    print()
    
    # Create import script
    print("3. Creating Figma import script...")
    create_figma_import_script()
    print()
    
    # Print instructions
    print_import_instructions()
    
    print("\n" + "=" * 60)
    print("✅ READY TO IMPORT TO FIGMA!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Open Figma Desktop App")
    print("2. Load the Localhost Sync plugin")
    print("3. Import each page using the plugin")
    print("4. Arrange all pages to see the full website!")

if __name__ == "__main__":
    main()

