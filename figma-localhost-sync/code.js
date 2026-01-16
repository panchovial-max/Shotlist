// sync/figma-to-code.ts
function extractNodeData(node) {
  const baseData = {
    id: node.id,
    name: node.name,
    type: node.type,
    x: node.x || 0,
    y: node.y || 0,
    width: node.width || 0,
    height: node.height || 0
  };
  if (node.fills && node.fills.length > 0) {
    baseData.fills = node.fills.map((fill) => ({
      type: fill.type,
      color: fill.color ? { r: fill.color.r, g: fill.color.g, b: fill.color.b, a: fill.color.a } : undefined,
      opacity: fill.opacity
    }));
  }
  if (node.strokes && node.strokes.length > 0) {
    baseData.strokes = node.strokes.map((stroke) => ({
      type: stroke.type,
      color: stroke.color ? { r: stroke.color.r, g: stroke.color.g, b: stroke.color.b } : undefined,
      weight: stroke.strokeWeight,
      opacity: stroke.opacity
    }));
  }
  if (node.cornerRadius)
    baseData.cornerRadius = node.cornerRadius;
  if (node.type === "TEXT") {
    baseData.text = node.characters;
    baseData.fontSize = node.fontSize;
    baseData.fontFamily = node.fontFamily;
    baseData.fontWeight = node.fontWeight;
  }
  if (node.layoutMode) {
    baseData.layoutMode = node.layoutMode;
    if (node.paddingTop !== undefined)
      baseData.paddingTop = node.paddingTop;
    if (node.paddingRight !== undefined)
      baseData.paddingRight = node.paddingRight;
    if (node.paddingBottom !== undefined)
      baseData.paddingBottom = node.paddingBottom;
    if (node.paddingLeft !== undefined)
      baseData.paddingLeft = node.paddingLeft;
    if (node.itemSpacing !== undefined)
      baseData.itemSpacing = node.itemSpacing;
  }
  return baseData;
}
function generateClassName(node) {
  return `figma-${node.id.replace(/[^a-z0-9-]/gi, "-").toLowerCase()}`.slice(0, 50);
}
function colorToCss(color) {
  const r = Math.round(color.r * 255);
  const g = Math.round(color.g * 255);
  const b = Math.round(color.b * 255);
  const a = color.a !== undefined ? color.a : 1;
  if (a < 1) {
    return `rgba(${r}, ${g}, ${b}, ${a})`;
  }
  return `rgb(${r}, ${g}, ${b})`;
}
function layoutToCss(node) {
  let css = "";
  if (node.layoutMode && node.layoutMode !== "NONE") {
    css += `display: flex;
`;
    if (node.layoutMode === "HORIZONTAL") {
      css += `flex-direction: row;
`;
    } else if (node.layoutMode === "VERTICAL") {
      css += `flex-direction: column;
`;
    }
    if (node.itemSpacing) {
      css += `gap: ${node.itemSpacing}px;
`;
    }
    if (node.paddingTop || node.paddingRight || node.paddingBottom || node.paddingLeft) {
      const pt = node.paddingTop || 0;
      const pr = node.paddingRight || 0;
      const pb = node.paddingBottom || 0;
      const pl = node.paddingLeft || 0;
      css += `padding: ${pt}px ${pr}px ${pb}px ${pl}px;
`;
    }
  }
  return css;
}
function generateHtml(nodes) {
  let html = "";
  for (const node of nodes) {
    const className = generateClassName(node);
    if (node.type === "FRAME" || node.type === "GROUP" || node.type === "COMPONENT") {
      html += `<div class="${className}">
`;
      if (node.name) {
        html += `  <!-- ${node.name} -->
`;
      }
      html += `</div>
`;
    } else if (node.type === "TEXT") {
      const tag = node.name?.startsWith("Heading") ? "h2" : "p";
      html += `<${tag} class="${className}">${node.text || node.name}</${tag}>
`;
    } else if (node.type === "RECTANGLE") {
      html += `<div class="${className}"></div>
`;
    }
  }
  return html;
}
function generateCss(nodes) {
  let css = "";
  for (const node of nodes) {
    const className = generateClassName(node);
    css += `.${className} {
`;
    if (node.width)
      css += `  width: ${node.width}px;
`;
    if (node.height)
      css += `  height: ${node.height}px;
`;
    css += `  left: ${node.x}px;
`;
    css += `  top: ${node.y}px;
`;
    css += `  position: absolute;
`;
    if (node.fills && node.fills[0]) {
      const fill = node.fills[0];
      if (fill.type === "SOLID" && fill.color) {
        css += `  background-color: ${colorToCss(fill.color)};
`;
      }
    }
    if (node.strokes && node.strokes[0]) {
      const stroke = node.strokes[0];
      if (stroke.type === "SOLID" && stroke.color) {
        css += `  border: ${stroke.weight || 1}px solid ${colorToCss(stroke.color)};
`;
      }
    }
    if (node.cornerRadius) {
      css += `  border-radius: ${node.cornerRadius}px;
`;
    }
    if (node.type === "TEXT") {
      if (node.fontSize)
        css += `  font-size: ${node.fontSize}px;
`;
      if (node.fontFamily)
        css += `  font-family: "${node.fontFamily}", sans-serif;
`;
      if (node.fontWeight)
        css += `  font-weight: ${node.fontWeight};
`;
      css += `  color: #000000;
`;
    }
    css += layoutToCss(node);
    css += `}

`;
  }
  return css;
}
function extractDesignTokens() {
  return {
    colors: {
      black: "#000000",
      white: "#FFFFFF",
      "gray-900": "#111827",
      "gray-800": "#1F2937",
      "gray-700": "#374151",
      "gray-600": "#4B5563",
      success: "#10B981",
      warning: "#F59E0B",
      error: "#EF4444",
      info: "#3B82F6",
      "light-gray": "#F3F4F6",
      border: "#E5E7EB"
    },
    typography: {
      display: { fontSize: 32, fontFamily: "Inter", fontWeight: 700, lineHeight: 1.2 },
      "heading-1": { fontSize: 24, fontFamily: "Inter", fontWeight: 600, lineHeight: 1.3 },
      "heading-2": { fontSize: 20, fontFamily: "Inter", fontWeight: 600, lineHeight: 1.3 },
      body: { fontSize: 14, fontFamily: "Inter", fontWeight: 400, lineHeight: 1.5 },
      small: { fontSize: 12, fontFamily: "Inter", fontWeight: 400, lineHeight: 1.4 }
    },
    spacing: {
      xs: 4,
      sm: 8,
      md: 12,
      lg: 16,
      xl: 24,
      "2xl": 32,
      "3xl": 48
    },
    borderRadius: {
      sm: 4,
      md: 8,
      lg: 12,
      xl: 16,
      full: 9999
    }
  };
}
function generateDesignData(nodes) {
  return {
    html: generateHtml(nodes),
    css: generateCss(nodes),
    nodes,
    designTokens: extractDesignTokens()
  };
}

// sync/code-to-figma.ts
function parseHtmlStructure(html) {
  const elements = [];
  const regex = /<(\w+)[^>]*class="([^"]*)"[^>]*>([^<]*)<\/\1>/g;
  let match;
  while ((match = regex.exec(html)) !== null) {
    const [, tag, className, content] = match;
    elements.push({
      tag,
      className,
      content,
      id: `element-${elements.length}`
    });
  }
  return elements;
}
function parseCssStyles(css) {
  const styles = {};
  const classRegex = /\.([a-z0-9-]+)\s*\{([^}]+)\}/gi;
  let match;
  while ((match = classRegex.exec(css)) !== null) {
    const [, className, declarations] = match;
    const style = {};
    const declRegex = /([a-z-]+)\s*:\s*([^;]+);/gi;
    let declMatch;
    while ((declMatch = declRegex.exec(declarations)) !== null) {
      const [, prop, value] = declMatch;
      style[prop.trim()] = value.trim();
    }
    styles[className] = style;
  }
  return styles;
}
function cssColorToFigma(colorStr) {
  const rgbMatch = colorStr.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
  if (rgbMatch) {
    return {
      r: parseInt(rgbMatch[1]) / 255,
      g: parseInt(rgbMatch[2]) / 255,
      b: parseInt(rgbMatch[3]) / 255
    };
  }
  const hexMatch = colorStr.match(/#([0-9a-f]{6})/i);
  if (hexMatch) {
    const hex = hexMatch[1];
    return {
      r: parseInt(hex.substr(0, 2), 16) / 255,
      g: parseInt(hex.substr(2, 2), 16) / 255,
      b: parseInt(hex.substr(4, 2), 16) / 255
    };
  }
  return { r: 0, g: 0, b: 0 };
}
function applyStylesToNode(node, styles) {
  if (styles["background-color"]) {
    const color = cssColorToFigma(styles["background-color"]);
    node.fills = [
      {
        type: "SOLID",
        color,
        opacity: 1
      }
    ];
  }
  if (styles["border"]) {
    const borderMatch = styles["border"].match(/(\d+)px\s+solid\s+(.+)/);
    if (borderMatch) {
      const [, weight, color] = borderMatch;
      node.strokes = [
        {
          type: "SOLID",
          color: cssColorToFigma(color),
          strokeWeight: parseInt(weight)
        }
      ];
    }
  }
  if (styles["border-radius"]) {
    const radius = parseInt(styles["border-radius"]);
    if (!isNaN(radius)) {
      node.cornerRadius = radius;
    }
  }
  if (styles["width"]) {
    node.resize(parseInt(styles["width"]), node.height);
  }
  if (styles["height"]) {
    node.resize(node.width, parseInt(styles["height"]));
  }
  if (styles["left"]) {
    node.x = parseInt(styles["left"]);
  }
  if (styles["top"]) {
    node.y = parseInt(styles["top"]);
  }
  if (styles["font-size"]) {
    node.fontSize = parseInt(styles["font-size"]);
  }
  if (styles["font-weight"]) {
    node.fontWeight = parseInt(styles["font-weight"]);
  }
  if (styles["color"]) {
    node.fills = [
      {
        type: "SOLID",
        color: cssColorToFigma(styles["color"])
      }
    ];
  }
}
async function createFigmaNodesFromCode(html, css, designTokens) {
  const createdNodes = [];
  try {
    const elements = parseHtmlStructure(html);
    const styles = parseCssStyles(css);
    const mainFrame = figma.createFrame();
    mainFrame.name = "Imported from Localhost";
    mainFrame.resize(1440, 1024);
    mainFrame.fills = [{ type: "SOLID", color: { r: 1, g: 1, b: 1 } }];
    for (const element of elements) {
      const elementStyles = styles[element.className] || {};
      if (element.tag === "div") {
        const frame = figma.createFrame();
        frame.name = element.className || "Container";
        frame.x = parseInt(elementStyles["left"] || "0");
        frame.y = parseInt(elementStyles["top"] || "0");
        frame.resize(parseInt(elementStyles["width"] || "100"), parseInt(elementStyles["height"] || "50"));
        applyStylesToNode(frame, elementStyles);
        mainFrame.appendChild(frame);
        createdNodes.push(frame);
      } else if (element.tag === "p" || element.tag === "span") {
        const text = figma.createText();
        text.name = element.className || "Text";
        text.characters = element.content || "Text content";
        text.x = parseInt(elementStyles["left"] || "0");
        text.y = parseInt(elementStyles["top"] || "0");
        await figma.loadFontAsync({ family: "Inter", style: "Regular" });
        if (elementStyles["font-size"]) {
          text.fontSize = parseInt(elementStyles["font-size"]);
        }
        if (elementStyles["font-weight"]) {
          text.fontWeight = parseInt(elementStyles["font-weight"]);
        }
        applyStylesToNode(text, elementStyles);
        mainFrame.appendChild(text);
        createdNodes.push(text);
      } else if (element.tag === "h1" || element.tag === "h2" || element.tag === "h3") {
        const text = figma.createText();
        text.name = `Heading (${element.tag})`;
        text.characters = element.content || element.tag;
        text.x = parseInt(elementStyles["left"] || "0");
        text.y = parseInt(elementStyles["top"] || "0");
        await figma.loadFontAsync({ family: "Inter", style: "Bold" });
        text.fontSize = parseInt(elementStyles["font-size"] || "24");
        text.fontWeight = 700;
        applyStylesToNode(text, elementStyles);
        mainFrame.appendChild(text);
        createdNodes.push(text);
      }
    }
    figma.currentPage.appendChild(mainFrame);
    figma.currentPage.selection = [mainFrame];
    figma.viewport.scrollAndZoomIntoView([mainFrame]);
    return createdNodes;
  } catch (error) {
    console.error("Error creating Figma nodes:", error);
    return [];
  }
}

// code.ts
var pluginConfig = {
  localhostUrl: "http://localhost:8000",
  apiUrl: "http://localhost:8000",
  autoSync: false,
  watchMode: false,
  syncColors: true,
  syncTypography: true
};
figma.showUI("ui.html", { width: 360, height: 600 });
async function exportToLocalhost(payload) {
  try {
    const selection = figma.currentPage.selection;
    if (selection.length === 0) {
      notifyUI("export", "Please select at least one frame or component to export", "error");
      return;
    }
    const nodes = selection.map((node) => extractNodeData(node));
    const designData = generateDesignData(nodes);
    const url = new URL(`${pluginConfig.localhostUrl}/api/figma/export`);
    url.searchParams.append("file", payload.targetFile);
    url.searchParams.append("css", payload.targetCss);
    const response = await fetch(url.toString(), {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        targetFile: payload.targetFile,
        targetCss: payload.targetCss,
        overwrite: payload.overwrite,
        designData,
        timestamp: new Date().toISOString()
      })
    });
    if (!response.ok) {
      notifyUI("export", `Export failed: ${response.statusText}`, "error");
      return;
    }
    const contentType = response.headers.get("content-type");
    if (contentType && contentType.includes("application/json")) {
      const result = await response.json();
      if (result.success) {
        notifyUI("export", `Successfully exported to ${payload.targetFile}`, "success");
      } else {
        notifyUI("export", `Export failed: ${result.message || "Unknown error"}`, "error");
      }
    } else {
      notifyUI("export", "Export completed but response was not JSON", "info");
    }
  } catch (error) {
    notifyUI("export", `Export error: ${error.message || "Unknown error"}`, "error");
  }
}
async function importFromLocalhost(payload) {
  try {
    const url = new URL(`${pluginConfig.localhostUrl}/api/figma/import`);
    url.searchParams.append("page", payload.page);
    const response = await fetch(url.toString());
    if (!response.ok) {
      notifyUI("import", `Failed to fetch from localhost: ${response.statusText}`, "error");
      return;
    }
    const contentType = response.headers.get("content-type");
    if (!contentType || !contentType.includes("application/json")) {
      notifyUI("import", "Invalid response from server (not JSON)", "error");
      return;
    }
    const data = await response.json();
    const { html, css, designTokens } = data;
    if (!html) {
      notifyUI("import", "No HTML content to import", "error");
      return;
    }
    const createdNodes = await createFigmaNodesFromCode(html, css, designTokens);
    if (createdNodes.length > 0) {
      notifyUI("import", `Successfully imported ${createdNodes.length} elements from ${payload.page}`, "success");
    } else {
      notifyUI("import", "Import completed but no elements were created", "info");
    }
  } catch (error) {
    notifyUI("import", `Import error: ${error.message || "Unknown error"}`, "error");
  }
}
async function saveConfig(config) {
  try {
    pluginConfig = { ...pluginConfig, ...config };
    const url = `${pluginConfig.localhostUrl}/api/figma/sync-config`;
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        config: pluginConfig,
        timestamp: new Date().toISOString()
      })
    });
    if (!response.ok) {
      notifyUI("settings", `Config save failed: ${response.statusText}`, "error");
      return;
    }
    notifyUI("settings", "Configuration saved successfully", "success");
  } catch (error) {
    notifyUI("settings", `Config save error: ${error.message || "Unknown error"}`, "error");
  }
}
function notifyUI(tab, message, type) {
  if (!tab || !message || !type) {
    console.error("Invalid notifyUI call", { tab, message, type });
    return;
  }
  figma.ui.postMessage({
    type: "notify",
    payload: { tab, message, type }
  });
}
figma.ui.onmessage = async (msg) => {
  if (!msg || !msg.type) {
    console.error("Invalid message received", msg);
    return;
  }
  if (msg.type === "export-to-localhost") {
    await exportToLocalhost(msg.payload || {});
  } else if (msg.type === "import-from-localhost") {
    await importFromLocalhost(msg.payload || {});
  } else if (msg.type === "save-config") {
    await saveConfig(msg.payload || {});
  } else if (msg.type === "get-config") {
    figma.ui.postMessage({
      type: "config",
      payload: pluginConfig
    });
  } else if (msg.type === "CLOSE") {
    figma.closePlugin();
  }
};
console.log("Figma Localhost Sync Plugin loaded");
