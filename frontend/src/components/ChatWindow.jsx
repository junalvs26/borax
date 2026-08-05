import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Database, Sparkles, StopCircle, RefreshCw } from 'lucide-react';

export default function ChatWindow({ selectedModel }) {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Olá! Sou sua IA totalmente local. O motor de tradução e RAG LanceDB está ativo.'
    }
  ]);
  const [input, setInput] = useState('');
  const [useRag, setUseRag] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isGenerating]);

  const handleSend = async (e) => {
    if (e) e.preventDefault();
    if (!input.trim() || isGenerating) return;

    if (!selectedModel) {
      alert('Por favor, selecione um modelo do Ollama no topo.');
      return;
    }

    const userQuery = input.trim();
    const userMessage = { role: 'user', content: userQuery };
    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    setInput('');
    setIsGenerating(true);

    const assistantMessage = { role: 'assistant', content: '' };
    setMessages((prev) => [...prev, assistantMessage]);

    try {
      const response = await fetch('http://localhost:8000/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: userQuery,
          model: selectedModel,
          use_rag: useRag,
          messages: updatedMessages.slice(-6)
        }),
      });

      if (!response.ok) {
        throw new Error(`Erro na requisição: ${response.statusText}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        setMessages((prev) => {
          const next = [...prev];
          const lastIdx = next.length - 1;
          if (next[lastIdx] && next[lastIdx].role === 'assistant') {
            next[lastIdx] = {
              ...next[lastIdx],
              content: next[lastIdx].content + chunk,
            };
          }
          return next;
        });
      }
    } catch (err) {
      setMessages((prev) => {
        const next = [...prev];
        const lastIdx = next.length - 1;
        if (next[lastIdx] && next[lastIdx].role === 'assistant') {
          next[lastIdx] = {
            ...next[lastIdx],
            content: `[Erro na resposta local: ${err.message}]`,
          };
        }
        return next;
      });
    } finally {
      setIsGenerating(false);
    }
  };

  const handleClearHistory = () => {
    setMessages([
      {
        role: 'assistant',
        content: 'Histórico de conversa reiniciado.'
      }
    ]);
  };

  return (
    <div className="flex flex-col h-full glass-panel overflow-hidden border-0 rounded-none md:rounded-xl">
      {/* Subheader Toolbar */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-white/10 bg-slate-900/50">
        <div className="flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-indigo-400" />
          <span className="text-xs font-semibold text-gray-200 uppercase tracking-wider">
            Consultar Base RAG Local
          </span>
        </div>

        <div className="flex items-center gap-4">
          <label className="flex items-center gap-2 cursor-pointer select-none text-xs font-medium text-gray-300">
            <input
              type="checkbox"
              checked={useRag}
              onChange={(e) => setUseRag(e.target.checked)}
              className="rounded accent-indigo-500 w-3.5 h-3.5"
            />
            <Database className="w-3.5 h-3.5 text-cyan-400" />
            <span>RAG Ativo (LanceDB)</span>
          </label>

          <button
            onClick={handleClearHistory}
            className="text-xs text-gray-400 hover:text-gray-200 flex items-center gap-1 transition-colors"
            title="Limpar Histórico"
          >
            <RefreshCw className="w-3 h-3" />
            Limpar
          </button>
        </div>
      </div>

      {/* Messages list */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex gap-3 max-w-3xl ${
              msg.role === 'user' ? 'ml-auto flex-row-reverse' : ''
            }`}
          >
            <div
              className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${
                msg.role === 'user'
                  ? 'bg-indigo-600 text-white'
                  : 'bg-slate-800 text-cyan-400 border border-slate-700'
              }`}
            >
              {msg.role === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
            </div>

            <div
              className={`p-3.5 rounded-2xl text-sm leading-relaxed ${
                msg.role === 'user'
                  ? 'bg-indigo-600/90 text-white rounded-tr-none'
                  : 'bg-slate-900/80 border border-white/10 text-gray-200 rounded-tl-none font-sans'
              }`}
            >
              {msg.content ? (
                <div className="whitespace-pre-wrap">{msg.content}</div>
              ) : (
                <div className="flex items-center gap-1.5 text-gray-400 animate-pulse text-xs">
                  <span>Buscando no LanceDB & gerando resposta...</span>
                </div>
              )}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input box */}
      <form onSubmit={handleSend} className="p-4 border-t border-white/10 bg-slate-900/40 flex gap-2">
        <input
          type="text"
          placeholder={selectedModel ? `Pergunte algo para ${selectedModel}...` : 'Selecione um modelo local...'}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={isGenerating || !selectedModel}
          className="input-dark flex-1 text-sm py-2.5 px-4"
        />
        <button
          type="submit"
          disabled={isGenerating || !input.trim() || !selectedModel}
          className="btn-primary px-5 py-2.5 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isGenerating ? (
            <StopCircle className="w-4 h-4 animate-spin text-white" />
          ) : (
            <Send className="w-4 h-4" />
          )}
        </button>
      </form>
    </div>
  );
}
