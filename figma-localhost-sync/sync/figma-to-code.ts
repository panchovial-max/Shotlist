/**
 * Figma → Code Export Logic
 * Converts Figma designs to HTML/CSS
 */

import { FigmaNodeData, DesignData, DesignTokens } from './types';

/**
 * Extract node data from Figma selection
 */
export function extractNodeData(node: any): FigmaNodeData {
  const baseData: FigmaNodeData = {
    id: node.id,
    name: node.name,
    type: node.type,
    x: node.x || 0,
    y: node.y || 0,
    width: node.width || 0,
    height: node.height || 0,
  };

  // Extract fills (colors)
  if (node.fills && node.fills.length > 0) {
    baseData.fills = node.fills.map((fill: any) => ({
      type: fill.type,
      color: fill.color ? { r: fill.color.r, g: fill.color.g, b: fill.color.b, a: fill.color.a } : undefined,
      opacity: fill.opacity,
    }));
  }

  // Extract strokes
  if (node.strokes && node.strokes.length > 0) {
    baseData.strokes = node.strokes.map((stroke: any) => ({
      type: stroke.type,
      color: stroke.color ? { r: stroke.color.r, g: stroke.color.g, b: stroke.color.b } : undefined,
      weight: stroke.strokeWeight,
      opacity: stroke.opacity,
    }));
  }

  // Extract styling
  if (node.cornerRadius) baseData.cornerRadius = node.cornerRadius;
  if (node.type === 'TEXT') {
    baseData.text = node.characters;
    baseData.fontSize = node.fontSize;
    baseData.fontFamily = node.fontFamily;
    baseData.fontWeight = node.fontWeight;
  }

  // Extract layout
  if (node.layoutMode) {
    baseData.layoutMode = node.layoutMode;
    if (node.paddingTop !== undefined) baseData.paddingTop = node.paddingTop;
    if (node.paddingRight !== undefined) baseData.paddingRight = node.paddingRight;
    if (node.paddingBottom !== undefined) baseData.paddingBottom = node.paddingBottom;
    if (node.paddingLeft !== undefined) baseData.paddingLeft = node.paddingLeft;
    if (node.itemSpacing !== undefined) baseData.itemSpacing = node.itemSpacing;
  }

  return baseData;
}

/**
 * Generate CSS class name from node
 */
function generateClassName(node: FigmaNodeData): string {
  return `figma-${node.id.replace(/[^a-z0-9-]/gi, '-').toLowerCase()}`.slice(0, 50);
}

/**
 * Convert Figma color to CSS RGB
 */
function colorToCss(color: { r: number; g: number; b: number; a?: number }): string {
  const r = Math.round(color.r * 255);
  const g = Math.round(color.g * 255);
  const b = Math.round(color.b * 255);
  const a = color.a !== undefined ? color.a : 1;

  if (a < 1) {
    return `rgba(${r}, ${g}, ${b}, ${a})`;
  }
  return `rgb(${r}, ${g}, ${b})`;
}

/**
 * Convert Figma layout to CSS flexbox
 */
function layoutToCss(node: FigmaNodeData): string {
  let css = '';

  if (node.layoutMode && node.layoutMode !== 'NONE') {
    css += `display: flex;\n`;

    if (node.layoutMode === 'HORIZONTAL') {
      css += `flex-direction: row;\n`;
    } else if (node.layoutMode === 'VERTICAL') {
      css += `flex-direction: column;\n`;
    }

    if (node.itemSpacing) {
      css += `gap: ${node.itemSpacing}px;\n`;
    }

    // Padding
    if (node.paddingTop || node.paddingRight || node.paddingBottom || node.paddingLeft) {
      const pt = node.paddingTop || 0;
      const pr = node.paddingRight || 0;
      const pb = node.paddingBottom || 0;
      const pl = node.paddingLeft || 0;
      css += `padding: ${pt}px ${pr}px ${pb}px ${pl}px;\n`;
    }
  }

  return css;
}

/**
 * Generate HTML from Figma nodes
 */
export function generateHtml(nodes: FigmaNodeData[]): string {
  let html = '';

  for (const node of nodes) {
    const className = generateClassName(node);

    if (node.type === 'FRAME' || node.type === 'GROUP' || node.type === 'COMPONENT') {
      html += `<div class="${className}">\n`;
      if (node.name) {
        html += `  <!-- ${node.name} -->\n`;
      }
      html += `</div>\n`;
    } else if (node.type === 'TEXT') {
      const tag = node.name?.startsWith('Heading') ? 'h2' : 'p';
      html += `<${tag} class="${className}">${node.text || node.name}</${tag}>\n`;
    } else if (node.type === 'RECTANGLE') {
      html += `<div class="${className}"></div>\n`;
    }
  }

  return html;
}

/**
 * Generate CSS from Figma nodes
 */
export function generateCss(nodes: FigmaNodeData[]): string {
  let css = '';

  for (const node of nodes) {
    const className = generateClassName(node);
    css += `.${className} {\n`;

    // Dimensions
    if (node.width) css += `  width: ${node.width}px;\n`;
    if (node.height) css += `  height: ${node.height}px;\n`;

    // Position
    css += `  left: ${node.x}px;\n`;
    css += `  top: ${node.y}px;\n`;
    css += `  position: absolute;\n`;

    // Colors
    if (node.fills && node.fills[0]) {
      const fill = node.fills[0];
      if (fill.type === 'SOLID' && fill.color) {
        css += `  background-color: ${colorToCss(fill.color)};\n`;
      }
    }

    // Strokes
    if (node.strokes && node.strokes[0]) {
      const stroke = node.strokes[0];
      if (stroke.type === 'SOLID' && stroke.color) {
        css += `  border: ${stroke.weight || 1}px solid ${colorToCss(stroke.color)};\n`;
      }
    }

    // Border radius
    if (node.cornerRadius) {
      css += `  border-radius: ${node.cornerRadius}px;\n`;
    }

    // Typography
    if (node.type === 'TEXT') {
      if (node.fontSize) css += `  font-size: ${node.fontSize}px;\n`;
      if (node.fontFamily) css += `  font-family: "${node.fontFamily}", sans-serif;\n`;
      if (node.fontWeight) css += `  font-weight: ${node.fontWeight};\n`;
      css += `  color: #000000;\n`;
    }

    // Layout
    css += layoutToCss(node);

    css += `}\n\n`;
  }

  return css;
}

/**
 * Build design tokens from Figma design
 */
export function extractDesignTokens(): DesignTokens {
  return {
    colors: {
      'black': '#000000',
      'white': '#FFFFFF',
      'gray-900': '#111827',
      'gray-800': '#1F2937',
      'gray-700': '#374151',
      'gray-600': '#4B5563',
      'success': '#10B981',
      'warning': '#F59E0B',
      'error': '#EF4444',
      'info': '#3B82F6',
      'light-gray': '#F3F4F6',
      'border': '#E5E7EB',
    },
    typography: {
      'display': { fontSize: 32, fontFamily: 'Inter', fontWeight: 700, lineHeight: 1.2 },
      'heading-1': { fontSize: 24, fontFamily: 'Inter', fontWeight: 600, lineHeight: 1.3 },
      'heading-2': { fontSize: 20, fontFamily: 'Inter', fontWeight: 600, lineHeight: 1.3 },
      'body': { fontSize: 14, fontFamily: 'Inter', fontWeight: 400, lineHeight: 1.5 },
      'small': { fontSize: 12, fontFamily: 'Inter', fontWeight: 400, lineHeight: 1.4 },
    },
    spacing: {
      'xs': 4,
      'sm': 8,
      'md': 12,
      'lg': 16,
      'xl': 24,
      '2xl': 32,
      '3xl': 48,
    },
    borderRadius: {
      'sm': 4,
      'md': 8,
      'lg': 12,
      'xl': 16,
      'full': 9999,
    },
  };
}

/**
 * Generate complete design data
 */
export function generateDesignData(nodes: FigmaNodeData[]): DesignData {
  return {
    html: generateHtml(nodes),
    css: generateCss(nodes),
    nodes: nodes,
    designTokens: extractDesignTokens(),
  };
}
