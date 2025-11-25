// Site-specific types

export interface BuilderFormData {
  requirements: string;
  framework?: 'react' | 'vue' | 'nextjs' | 'html';
  designStyle?: 'modern' | 'minimal' | 'brutalist' | 'glassmorphism' | 'neomorphism' | 'gradient' | 'retro' | 'cyberpunk';
  features?: string[];
  colorScheme?: string;
}

export interface CodeUpdateRequest {
  site_id: string;
  html_code?: string;
  css_code?: string;
  js_code?: string;
  change_description?: string;
}

export interface CodeGenerateRequest {
  session_id: string;
  requirements: string;
  framework?: string;
  design_style?: string;
  features?: string[];
}
