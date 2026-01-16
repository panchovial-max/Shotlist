// This file holds the main code for plugins built with the Plugin API

// Show the plugin UI
figma.showUI(__html__, { 
  width: 320, 
  height: 480,
  title: "Localhost Sync"
});

// Handle different menu commands
if (figma.command === "settings") {
  figma.ui.postMessage({ type: 'show-settings' });
} else if (figma.command === "stop") {
  figma.ui.postMessage({ type: 'stop-sync' });
} else {
  figma.ui.postMessage({ type: 'start-sync' });
}

// Handle messages from the UI
figma.ui.onmessage = async msg => {
  if (msg.type === 'sync-selection') {
    const selection = figma.currentPage.selection;
    if (selection.length > 0) {
      // Get node data
      const nodeData = selection.map(node => ({
        id: node.id,
        name: node.name,
        type: node.type,
        x: node.x,
        y: node.y,
        width: node.width,
        height: node.height
      }));
      
      // Send back to UI for localhost sync
      figma.ui.postMessage({
        type: 'selection-data',
        data: nodeData
      });
    } else {
      figma.ui.postMessage({
        type: 'no-selection',
        message: 'Please select at least one layer to sync'
      });
    }
  }
  
  if (msg.type === 'get-document-info') {
    const documentInfo = {
      name: figma.root.name,
      pages: figma.root.children.map(page => ({
        id: page.id,
        name: page.name
      })),
      currentPage: {
        id: figma.currentPage.id,
        name: figma.currentPage.name
      }
    };
    
    figma.ui.postMessage({
      type: 'document-info',
      data: documentInfo
    });
  }
  
  if (msg.type === 'notify') {
    figma.notify(msg.message, {
      timeout: msg.timeout || 2000
    });
  }
  
  if (msg.type === 'close-plugin') {
    figma.closePlugin();
  }
};

// Listen for selection changes
figma.on("selectionchange", () => {
  figma.ui.postMessage({
    type: 'selection-changed',
    count: figma.currentPage.selection.length
  });
});