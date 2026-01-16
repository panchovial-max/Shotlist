/**
 * Figma Plugin Backend
 * Main plugin logic - runs in Figma context
 */

import { extractNodeData, generateDesignData } from './sync/figma-to-code';
import { parseHtmlStructure, createFigmaNodesFromCode } from './sync/code-to-figma';
import { PluginMessage, ExportPayload, ImportPayload, SyncConfig, DesignData } from './sync/types';

// Plugin configuration
let pluginConfig: SyncConfig = {
  localhostUrl: 'http://localhost:8000',
  apiUrl: 'http://localhost:8001',
  autoSync: false,
  watchMode: false,
  syncColors: true,
  syncTypography: true,
};

// Show plugin UI
// Use a simple approach: load UI without embedding HTML
figma.showUI('ui.html', { width: 360, height: 600 });

/**
 * Export Figma selection to localhost
 */
async function exportToLocalhost(payload: ExportPayload): Promise<void> {
  try {
    const selection = figma.currentPage.selection;

    if (selection.length === 0) {
      notifyUI('export', 'Please select at least one frame or component to export', 'error');
      return;
    }

    // Extract node data from selection
    const nodes = selection.map(node => extractNodeData(node as any));

    // Generate design data
    const designData = generateDesignData(nodes);

    // Send to localhost API
    const response = await fetch(`${pluginConfig.apiUrl}/api/figma/export`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        targetFile: payload.targetFile,
        targetCss: payload.targetCss,
        overwrite: payload.overwrite,
        designData: designData,
        timestamp: new Date().toISOString(),
      }),
    });

    const result = await response.json();

    if (result.success) {
      notifyUI(
        'export',
        `Successfully exported to ${payload.targetFile}`,
        'success'
      );
    } else {
      notifyUI('export', `Export failed: ${result.message}`, 'error');
    }
  } catch (error) {
    notifyUI('export', `Export error: ${(error as Error).message}`, 'error');
  }
}

/**
 * Import from localhost to Figma
 */
async function importFromLocalhost(payload: ImportPayload): Promise<void> {
  try {
    // Fetch HTML/CSS from localhost
    const response = await fetch(
      `${pluginConfig.apiUrl}/api/figma/import?page=${payload.page}`
    );

    if (!response.ok) {
      notifyUI('import', `Failed to fetch from localhost: ${response.statusText}`, 'error');
      return;
    }

    const data = await response.json();
    const { html, css, designTokens } = data;

    if (!html) {
      notifyUI('import', 'No HTML content to import', 'error');
      return;
    }

    // Create Figma nodes from HTML/CSS
    const createdNodes = await createFigmaNodesFromCode(html, css, designTokens);

    if (createdNodes.length > 0) {
      notifyUI(
        'import',
        `Successfully imported ${createdNodes.length} elements from ${payload.page}`,
        'success'
      );
    } else {
      notifyUI('import', 'Import completed but no elements were created', 'info');
    }
  } catch (error) {
    notifyUI('import', `Import error: ${(error as Error).message}`, 'error');
  }
}

/**
 * Save sync configuration
 */
async function saveConfig(config: SyncConfig): Promise<void> {
  try {
    // Update local config
    pluginConfig = { ...pluginConfig, ...config };

    // Send to localhost API
    await fetch(`${pluginConfig.apiUrl}/api/figma/sync-config`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        config: pluginConfig,
        timestamp: new Date().toISOString(),
      }),
    });

    notifyUI('settings', 'Configuration saved successfully', 'success');
  } catch (error) {
    notifyUI('settings', `Config save error: ${(error as Error).message}`, 'error');
  }
}

/**
 * Send notification to UI
 */
function notifyUI(
  tab: 'export' | 'import' | 'settings',
  message: string,
  type: 'error' | 'success' | 'info'
): void {
  figma.ui.postMessage({
    type: 'notify',
    payload: { tab, message, type },
  });
}

/**
 * Handle messages from UI
 */
figma.ui.onmessage = async (msg: PluginMessage) => {
  if (msg.type === 'export-to-localhost') {
    await exportToLocalhost(msg.payload);
  } else if (msg.type === 'import-from-localhost') {
    await importFromLocalhost(msg.payload);
  } else if (msg.type === 'save-config') {
    await saveConfig(msg.payload);
  } else if (msg.type === 'get-config') {
    // Send current config to UI
    figma.ui.postMessage({
      type: 'config',
      payload: pluginConfig,
    });
  } else if (msg.type === 'CLOSE') {
    figma.closePlugin();
  }
};

console.log('Figma Localhost Sync Plugin loaded');
