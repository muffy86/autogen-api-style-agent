export interface WindowState {
  id: string;
  appId: string;
  title: string;
  x: number;
  y: number;
  width: number;
  height: number;
  minWidth: number;
  minHeight: number;
  isMinimized: boolean;
  isMaximized: boolean;
  isFocused: boolean;
  zIndex: number;
  preMaximizeBounds?: { x: number; y: number; width: number; height: number };
}

export interface AppDefinition {
  id: string;
  name: string;
  icon: string;
  description: string;
  defaultWidth: number;
  defaultHeight: number;
  minWidth: number;
  minHeight: number;
  singleton: boolean;
}

export interface FileAttachment {
  id: string;
  name: string;
  type: 'image' | 'document' | 'code' | 'other';
  mimeType: string;
  size: number;
  dataUrl?: string;
  file: File;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  model?: string;
  createdAt: Date;
  attachments?: MessageAttachment[];
  webSearchResults?: WebSearchResult[];
  toolCalls?: ToolCallResult[];
  artifacts?: MessageArtifact[];
}

export interface MessageAttachment {
  id: string;
  name: string;
  type: 'image' | 'document' | 'code' | 'other';
  url: string;
  mimeType: string;
}

export interface WebSearchResult {
  title: string;
  url: string;
  snippet: string;
  favicon?: string;
}

export interface ToolCallResult {
  id: string;
  name: string;
  status: 'running' | 'completed' | 'error';
  input?: Record<string, unknown>;
  output?: string;
  duration?: number;
}

export interface MessageArtifact {
  id: string;
  type: 'code' | 'html' | 'svg' | 'markdown' | 'mermaid';
  title: string;
  content: string;
  language?: string;
}

export interface Conversation {
  id: string;
  title: string;
  messages: ChatMessage[];
  model: string;
  systemPrompt: string;
  createdAt: Date;
  updatedAt: Date;
  pinned?: boolean;
}

export interface AIModel {
  id: string;
  name: string;
  provider: 'openai' | 'anthropic' | 'google' | 'xai' | 'groq';
  modelId: string;
  description: string;
  maxTokens: number;
  color: string;
}

export interface ContextMenuItem {
  id: string;
  label: string;
  icon?: any;
  shortcut?: string;
  separator?: boolean;
  disabled?: boolean;
  danger?: boolean;
  action: () => void;
}

export interface ContextMenuState {
  visible: boolean;
  x: number;
  y: number;
  items: ContextMenuItem[];
}

export interface PaletteCommand {
  id: string;
  title: string;
  description?: string;
  icon?: any;
  category: 'app' | 'action' | 'setting' | 'recent';
  shortcut?: string;
  action: () => void;
}

export interface Notification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message?: string;
  icon?: any;
  duration?: number;
  action?: { label: string; onClick: () => void };
  timerId?: ReturnType<typeof setTimeout>;
  createdAt: Date;
}

export interface SnapZone {
  region: 'left' | 'right' | 'top' | 'maximize';
  bounds: { x: number; y: number; width: number; height: number };
}
