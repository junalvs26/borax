import React from 'react';
import { AppProvider, useApp } from './context/AppContext';
import { Sidebar } from './components/Sidebar';
import { ChatTab } from './components/tabs/ChatTab';
import { KnowledgeDrive } from './components/tabs/KnowledgeDrive';
import { IngestTab } from './components/tabs/IngestTab';
import { MediaTab } from './components/tabs/MediaTab';
import { DataTab } from './components/tabs/DataTab';
import { AgentSettingsTab } from './components/tabs/AgentSettingsTab';
import { ConfirmationModal } from './components/ConfirmationModal';

const MainContent: React.FC = () => {
  const { activeTab } = useApp();

  return (
    <main className="flex-1 flex flex-col h-screen overflow-hidden">
      {activeTab === 'chat' && <ChatTab />}
      {activeTab === 'drive' && <KnowledgeDrive />}
      {activeTab === 'ingest' && <IngestTab />}
      {activeTab === 'media' && <MediaTab />}
      {activeTab === 'data' && <DataTab />}
      {activeTab === 'agent' && <AgentSettingsTab />}
    </main>
  );
};

export function App() {
  return (
    <AppProvider>
      <div className="flex h-screen w-screen bg-slate-950 text-slate-100 font-sans overflow-hidden select-none">
        <Sidebar />
        <MainContent />
        <ConfirmationModal />
      </div>
    </AppProvider>
  );
}

export default App;
