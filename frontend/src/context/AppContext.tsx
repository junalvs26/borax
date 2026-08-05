import React, { createContext, useContext, useState, useEffect } from 'react';
import { OllamaModel, ActiveTab, AgentExecuteResponse, MountedCartridge } from '../types';
import { getModels, checkBackendHealth, getCartridgeStatus } from '../services/api';

interface AppContextType {
  activeTab: ActiveTab;
  setActiveTab: (tab: ActiveTab) => void;
  models: OllamaModel[];
  selectedModel: string;
  setSelectedModel: (model: string) => void;
  activeTable: string;
  setActiveTable: (table: string) => void;
  executionMode: 'safe' | 'confirm' | 'unrestricted';
  setExecutionMode: (mode: 'safe' | 'confirm' | 'unrestricted') => void;
  allowedPaths: string[];
  setAllowedPaths: React.Dispatch<React.SetStateAction<string[]>>;
  pendingAgentPlan: AgentExecuteResponse | null;
  setPendingAgentPlan: (plan: AgentExecuteResponse | null) => void;
  backendOnline: boolean;
  refreshModels: () => Promise<void>;
  activeCartridge: MountedCartridge | null;
  setActiveCartridge: (cartridge: MountedCartridge | null) => void;
  refreshCartridge: () => Promise<void>;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [activeTab, setActiveTab] = useState<ActiveTab>('chat');
  const [models, setModels] = useState<OllamaModel[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>('qwen2.5-0.5b-instruct-q4_k_m.gguf');
  const [activeTable, setActiveTable] = useState<string>('knowledge_base');
  const [executionMode, setExecutionMode] = useState<'safe' | 'confirm' | 'unrestricted'>('safe');
  const [allowedPaths, setAllowedPaths] = useState<string[]>([]);
  const [pendingAgentPlan, setPendingAgentPlan] = useState<AgentExecuteResponse | null>(null);
  const [backendOnline, setBackendOnline] = useState<boolean>(false);
  const [activeCartridge, setActiveCartridge] = useState<MountedCartridge | null>(null);

  const fetchCartridge = async () => {
    const status = await getCartridgeStatus();
    setActiveCartridge(status);
    if (status && status.table_name) {
      setActiveTable(status.table_name);
    }
  };

  const fetchModels = async () => {
    const isOnline = await checkBackendHealth();
    setBackendOnline(isOnline);
    if (isOnline) {
      const fetched = await getModels();
      setModels(fetched);
      if (fetched.length > 0 && !fetched.some(m => m.name === selectedModel)) {
        setSelectedModel(fetched[0].name);
      }
      await fetchCartridge();
    }
  };

  useEffect(() => {
    fetchModels();
    const interval = setInterval(fetchModels, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <AppContext.Provider
      value={{
        activeTab,
        setActiveTab,
        models,
        selectedModel,
        setSelectedModel,
        activeTable,
        setActiveTable,
        executionMode,
        setExecutionMode,
        allowedPaths,
        setAllowedPaths,
        pendingAgentPlan,
        setPendingAgentPlan,
        backendOnline,
        refreshModels: fetchModels,
        activeCartridge,
        setActiveCartridge,
        refreshCartridge: fetchCartridge
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp deve ser usado dentro de um AppProvider');
  }
  return context;
};
