/**
 * Shared type definitions for Figma ↔ Localhost sync
 */

export interface PluginMessage {
  type: 'export-to-localhost' | 'import-from-localhost' | 'save-config' | 'notify' | 'get-config';
  payload?: any;
}

export interface ExportPayload {
  targetFile: string;
  overwrite: boolean;
}

export interface ImportPayload {
  page: 'dashboard' | 'settings' | 'login' | 'index';
  localhostUrl: string;
}

export interface SyncConfig {
  localhostUrl: string;
  autoSync: boolean;
  watchMode: boolean;
  lastSync?: string;
}

export interface ApiResponse {
  success: boolean;
  message: string;
  data?: any;
  error?: string;
}

export interface DesignData {
  html: string;
  css: string;
  nodes: FigmaNodeData[];
  designTokens: DesignTokens;
}

export interface FigmaNodeData {
  id: string;
  name: string;
  type: string;
  x: number;
  y: number;
  width: number;
  height: number;
  fills?: FigmaFill[];
  strokes?: FigmaStroke[];
  cornerRadius?: number;
  text?: string;
  fontSize?: number;
  fontFamily?: string;
  fontWeight?: number;
  layoutMode?: 'HORIZONTAL' | 'VERTICAL' | 'NONE';
  paddingTop?: number;
  paddingRight?: number;
  paddingBottom?: number;
  paddingLeft?: number;
  itemSpacing?: number;
}

export interface FigmaFill {
  type: 'SOLID' | 'GRADIENT' | 'IMAGE';
  color?: FigmaColor;
  opacity?: number;
}

export interface FigmaStroke {
  type: 'SOLID';
  color?: FigmaColor;
  weight?: number;
  opacity?: number;
}

export interface FigmaColor {
  r: number;
  g: number;
  b: number;
  a?: number;
}

export interface DesignTokens {
  colors: Record<string, string>;
  typography: Record<string, TextStyle>;
  spacing: Record<string, number>;
  borderRadius: Record<string, number>;
}

export interface TextStyle {
  fontSize: number;
  fontFamily: string;
  fontWeight: number;
  lineHeight: number;
  letterSpacing?: number;
}
