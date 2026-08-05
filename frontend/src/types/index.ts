export interface OllamaModel {
  name: string;
  size?: number;
  digest?: string;
  modified_at?: string;
}

export interface ChatMessage {
  id?: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp?: string;
}

export interface MountedCartridge {
  id: string;
  mounted: boolean;
  name: string;
  type?: 'knpack' | 'document' | 'dataset' | 'default';
  table_name?: string;
  vectors_count?: number;
  size_bytes?: number;
  system_prompt?: string;
  files_list?: string[];
  mounted_at?: string;
  cover_color?: string;
}

export interface MultiCartridgeState {
  mounted: boolean;
  cartridges: MountedCartridge[];
  table_names: string[];
  table_name: string;
  system_prompt: string;
  total_vectors: number;
  name: string;
  type: string;
export interface DocumentWizardPreferences {
  theme: string;
  sections?: string;
  cartridge_id?: string;
  document_type: 'abnt' | 'technical' | 'proposal' | 'summary';
  tone: 'scientific' | 'direct' | 'didactic';
  structure?: string;
  export_format: 'docx' | 'pdf' | 'txt';
  filename?: string;
}

export interface WizardInitiateResponse {
  status: string;
  wizard_active: boolean;
  prompt_original: string;
  suggested_preferences: DocumentWizardPreferences;
  options: {
    document_types: Array<{ id: string; label: string; desc: string }>;
    tones: Array<{ id: string; label: string; desc: string }>;
    export_formats: Array<{ id: string; label: string }>;
  };
}

export interface ChatSession {
  id: string;
  title: string;
  messages: ChatMessage[];
  cartridges?: MountedCartridge[];
  message_count: number;
  created_at?: string;
  updated_at: string;
}

export interface PowerCommand {
  id: string;
  name: string;
  trigger: string;
  description: string;
  icon: string;
  action_type: 'tab' | 'action';
  target_tab?: ActiveTab;
}

export interface IngestResponse {
  status: string;
  filename: string;
  chunks_count: number;
  total_characters: number;
  table_name: string;
  message?: string;
}

export interface MediaTranscribeResponse {
  status: string;
  source: string;
  is_youtube: boolean;
  language: string;
  language_probability: number;
  duration: number;
  full_transcript: string;
  segments_count: number;
  segments: Array<{
    start: number;
    end: number;
    text: string;
  }>;
  rag_ingested: boolean;
  table_name: string;
}

export interface DataAnalyzeResponse {
  status: string;
  file_path?: string;
  user_query: string;
  sql_executed: string;
  total_rows: number;
  columns: string[];
  results: Array<Record<string, any>>;
  summary: string;
  error_details?: string;
}

export interface AgentAction {
  tool: string;
  args: Record<string, any>;
}

export interface AgentExecuteResponse {
  status: 'completed' | 'requires_confirmation' | 'error';
  execution_mode: 'safe' | 'confirm' | 'unrestricted';
  instruction: string;
  requires_confirmation?: boolean;
  plan_id?: string;
  pending_actions?: AgentAction[];
  actions_executed_count?: number;
  results?: Array<{
    tool: string;
    args: Record<string, any>;
    result?: any;
    error?: string;
  }>;
  message?: string;
}

export type ActiveTab = 'chat' | 'drive' | 'ingest' | 'media' | 'data' | 'agent';
