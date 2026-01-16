/**
 * Code → Figma Import Logic
 * Converts HTML/CSS to Figma nodes
 */

import { DesignTokens } from './types';

/**
 * Parse HTML string and extract structure
 */
export function parseHtmlStructure(html: string): any[] {
  const elements: any[] = [];
  const regex = /<(\w+)[^>]*class="([^"]*)"[^>]*>([^<]*)<\/\1>/g;
  let match;

  while ((match = regex.exec(html)) !== null) {
    const [, tag, className, content] = match;
    elements.push({
      tag,
      className,
      content,
      id: `element-${elements.length}`,
    });
  }

  return elements;
}

/**
 * Parse CSS and extract styles
 */
export function parseCssStyles(css: string): Record<string, any> {
  const styles: Record<string, any> = {};
  const classRegex = /\.([a-z0-9-]+)\s*\{([^}]+)\}/gi;
  let match;

  while ((match = classRegex.exec(css)) !== null) {
    const [, className, declarations] = match;
    const style: any = {};

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

/**
 * Convert CSS color to Figma RGB
 */
export function cssColorToFigma(colorStr: string): { r: number; g: number; b: number } {
  // Handle rgb/rgba
  const rgbMatch = colorStr.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
  if (rgbMatch) {
    return {
      r: parseInt(rgbMatch[1]) / 255,
      g: parseInt(rgbMatch[2]) / 255,
      b: parseInt(rgbMatch[3]) / 255,
    };
  }

  // Handle hex
  const hexMatch = colorStr.match(/#([0-9a-f]{6})/i);
  if (hexMatch) {
    const hex = hexMatch[1];
    return {
      r: parseInt(hex.substr(0, 2), 16) / 255,
      g: parseInt(hex.substr(2, 2), 16) / 255,
      b: parseInt(hex.substr(4, 2), 16) / 255,
    };
  }

  // Default to black
  return { r: 0, g: 0, b: 0 };
}

/**
 * Apply CSS styles to Figma node
 */
export function applyStylesToNode(node: any, styles: Record<string, string>): void {
  // Apply fill color
  if (styles['background-color']) {
    const color = cssColorToFigma(styles['background-color']);
    node.fills = [
      {
        type: 'SOLID',
        color: color,
        opacity: 1,
      },
    ];
  }

  // Apply stroke
  if (styles['border']) {
    const borderMatch = styles['border'].match(/(\d+)px\s+solid\s+(.+)/);
    if (borderMatch) {
      const [, weight, color] = borderMatch;
      node.strokes = [
        {
          type: 'SOLID',
          color: cssColorToFigma(color),
          strokeWeight: parseInt(weight),
        },
      ];
    }
  }

  // Apply border radius
  if (styles['border-radius']) {
    const radius = parseInt(styles['border-radius']);
    if (!isNaN(radius)) {
      node.cornerRadius = radius;
    }
  }

  // Apply dimensions
  if (styles['width']) {
    node.resize(parseInt(styles['width']), node.height);
  }
  if (styles['height']) {
    node.resize(node.width, parseInt(styles['height']));
  }

  // Apply position
  if (styles['left']) {
    node.x = parseInt(styles['left']);
  }
  if (styles['top']) {
    node.y = parseInt(styles['top']);
  }

  // Apply typography
  if (styles['font-size']) {
    node.fontSize = parseInt(styles['font-size']);
  }
  if (styles['font-weight']) {
    node.fontWeight = parseInt(styles['font-weight']);
  }
  if (styles['color']) {
    node.fills = [
      {
        type: 'SOLID',
        color: cssColorToFigma(styles['color']),
      },
    ];
  }
}

/**
 * Create Figma nodes from HTML/CSS data
 */
export async function createFigmaNodesFromCode(
  html: string,
  css: string,
  designTokens: DesignTokens
): Promise<any[]> {
  const createdNodes: any[] = [];

  try {
    // Parse HTML and CSS
    const elements = parseHtmlStructure(html);
    const styles = parseCssStyles(css);

    // Create frame for layout
    const mainFrame = figma.createFrame();
    mainFrame.name = 'Imported from Localhost';
    mainFrame.resize(1440, 1024);
    mainFrame.fills = [{ type: 'SOLID', color: { r: 1, g: 1, b: 1 } }];

    // Create nodes for each element
    for (const element of elements) {
      const elementStyles = styles[element.className] || {};

      if (element.tag === 'div') {
        const frame = figma.createFrame();
        frame.name = element.className || 'Container';
        frame.x = parseInt(elementStyles['left'] || '0');
        frame.y = parseInt(elementStyles['top'] || '0');
        frame.resize(
          parseInt(elementStyles['width'] || '100'),
          parseInt(elementStyles['height'] || '50')
        );

        applyStylesToNode(frame, elementStyles);
        mainFrame.appendChild(frame);
        createdNodes.push(frame);
      } else if (element.tag === 'p' || element.tag === 'span') {
        const text = figma.createText();
        text.name = element.className || 'Text';
        text.characters = element.content || 'Text content';
        text.x = parseInt(elementStyles['left'] || '0');
        text.y = parseInt(elementStyles['top'] || '0');

        // Load font before setting text properties
        await figma.loadFontAsync({ family: 'Inter', style: 'Regular' });

        if (elementStyles['font-size']) {
          text.fontSize = parseInt(elementStyles['font-size']);
        }
        if (elementStyles['font-weight']) {
          text.fontWeight = parseInt(elementStyles['font-weight']);
        }

        applyStylesToNode(text, elementStyles);
        mainFrame.appendChild(text);
        createdNodes.push(text);
      } else if (element.tag === 'h1' || element.tag === 'h2' || element.tag === 'h3') {
        const text = figma.createText();
        text.name = `Heading (${element.tag})`;
        text.characters = element.content || element.tag;
        text.x = parseInt(elementStyles['left'] || '0');
        text.y = parseInt(elementStyles['top'] || '0');

        await figma.loadFontAsync({ family: 'Inter', style: 'Bold' });

        text.fontSize = parseInt(elementStyles['font-size'] || '24');
        text.fontWeight = 700;

        applyStylesToNode(text, elementStyles);
        mainFrame.appendChild(text);
        createdNodes.push(text);
      }
    }

    // Add frame to page and select it
    figma.currentPage.appendChild(mainFrame);
    figma.currentPage.selection = [mainFrame];
    figma.viewport.scrollAndZoomIntoView([mainFrame]);

    return createdNodes;
  } catch (error) {
    console.error('Error creating Figma nodes:', error);
    return [];
  }
}
