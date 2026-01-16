/**
 * Figma Plugin UI Logic
 * Handles user interactions and communication with backend
 */

interface PluginMessage {
  type: 'export-to-localhost' | 'import-from-localhost' | 'save-config' | 'notify';
  payload?: any;
}

// Tab switching
document.querySelectorAll('.tab-button').forEach(button => {
  button.addEventListener('click', () => {
    const tabName = button.getAttribute('data-tab');

    // Update button states
    document.querySelectorAll('.tab-button').forEach(b => b.classList.remove('active'));
    button.classList.add('active');

    // Update content visibility
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    document.getElementById(`${tabName}-tab`)?.classList.add('active');
  });
});

// Export button
document.getElementById('exportButton')?.addEventListener('click', () => {
  const targetFile = (document.getElementById('targetFile') as HTMLInputElement).value;
  const targetCss = (document.getElementById('targetCss') as HTMLInputElement).value;
  const overwrite = (document.getElementById('overwriteExport') as HTMLInputElement).checked;

  if (!targetFile.trim()) {
    showMessage('export-message', 'Please enter a target file name', 'error');
    return;
  }

  const payload = { targetFile, targetCss, overwrite };
  parent.postMessage({ pluginMessage: { type: 'export-to-localhost', payload } }, '*');

  updateStatus('export-status', 'Exporting... please wait');
});

// Import button
document.getElementById('importButton')?.addEventListener('click', () => {
  const importPage = (document.getElementById('importPage') as HTMLSelectElement).value;
  const localhostUrl = (document.getElementById('localhostUrl') as HTMLInputElement).value;

  if (!localhostUrl.trim()) {
    showMessage('import-message', 'Please enter a localhost URL', 'error');
    return;
  }

  const payload = { page: importPage, localhostUrl };
  parent.postMessage({ pluginMessage: { type: 'import-from-localhost', payload } }, '*');

  updateStatus('import-status', 'Importing... please wait');
});

// Settings button
document.getElementById('saveSettingsButton')?.addEventListener('click', () => {
  const settings = {
    localhostUrl: (document.getElementById('settingsUrl') as HTMLInputElement).value,
    apiUrl: (document.getElementById('settingsUrl') as HTMLInputElement).value,
    autoSync: (document.getElementById('autoSync') as HTMLInputElement).checked,
    watchMode: (document.getElementById('watchMode') as HTMLInputElement).checked,
    syncColors: (document.getElementById('syncColors') as HTMLInputElement).checked,
    syncTypography: (document.getElementById('syncTypography') as HTMLInputElement).checked,
  };

  parent.postMessage({ pluginMessage: { type: 'save-config', payload: settings } }, '*');

  showMessage('settings-message', 'Settings saved successfully', 'success');
});

/**
 * Show message in UI
 */
function showMessage(elementId: string, message: string, type: 'error' | 'success' | 'info'): void {
  const element = document.getElementById(elementId) as HTMLElement;
  if (element) {
    element.textContent = message;
    element.className = `message ${type}`;
    element.style.display = 'block';

    if (type === 'success' || type === 'info') {
      setTimeout(() => {
        element.style.display = 'none';
      }, 3000);
    }
  }
}

/**
 * Update status message
 */
function updateStatus(elementId: string, message: string): void {
  const element = document.getElementById(elementId) as HTMLElement;
  if (element) {
    element.textContent = message;
  }
}

/**
 * Handle messages from plugin backend
 */
window.onmessage = async (event: MessageEvent<any>) => {
  const pluginMessage = event.data.pluginMessage;

  if (pluginMessage && pluginMessage.type === 'notify') {
    const { tab, message, type } = pluginMessage.payload;
    showMessage(`${tab}-message`, message, type);
    updateStatus(`${tab}-status`, '');
  }
};

// Initialize - load saved settings
window.addEventListener('load', () => {
  // Request current config from plugin
  parent.postMessage({ pluginMessage: { type: 'get-config' } }, '*');
});
