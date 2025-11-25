// Builder form types

export type Framework = 'react' | 'vue' | 'nextjs' | 'html';
export type DesignStyle = 'modern' | 'minimal' | 'corporate' | 'creative';
export type InputMode = 'text' | 'chat' | 'voice';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export interface FrameworkOption {
  id: Framework;
  name: string;
  description: string;
  icon: string;
}

export interface FeatureOption {
  id: string;
  name: string;
  description: string;
}
