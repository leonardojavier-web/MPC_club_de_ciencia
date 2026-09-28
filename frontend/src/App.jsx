import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { History, ChevronLeft, ChevronRight, MessageSquare, Sparkles, X, Send, Loader2, CircleCheck, Radio, Workflow, GripVertical } from 'lucide-react';

const API_BASE = "http://127.0.0.1:8000/api";

function App() {
  const [connected, setConnected] = useState(false);
  const [messages, setMessages] = useState([
    { role: 'assistant', content: '¡Hola! Soy tu asistente historiador de Las Varillas. ¿En qué puedo ayudarte hoy?' }
  ]);
  const [input, setInput] = useState("");
  const [data, setData] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [thinkingMessage, setThinkingMessage] = useState("");
  const [servicesReady, setServicesReady] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isChatOpen, setIsChatOpen] = useState(true);
  const [chatWidth, setChatWidth] = useState(() => {
    const savedWidth = Number(localStorage.getItem('historia-chat-width'));
    return savedWidth >= 300 && savedWidth <= 560 ? savedWidth : 380;
  });
  const [isResizingChat, setIsResizingChat] = useState(false);

  const socketRef = useRef(null);
  const chatEndRef = useRef(null);
  const chatResizeRef = useRef(null);

  const fetchFundacion = async () => {
    try {
      const resp = await axios.get(`${API_BASE}/fundacion`);
      setData(resp.data.raw || (Array.isArray(resp.data) ? resp.data : []));
    } catch (e) {
      console.error("Error al obtener los datos de fundación", e);
    }
  };

  useEffect(() => {
    let reconnectTimer;

    const connectWebSocket = () => {
      const ws = new WebSocket("ws://127.0.0.1:8000/ws/chat");

      ws.onopen = () => setConnected(true);

      ws.onmessage = (event) => {
        try {
          const msgData = JSON.parse(event.data);
          if (msgData.type === "status") {
            setThinkingMessage(msgData.message);
          } else if (msgData.type === "ready") {
            setServicesReady(true);
            setThinkingMessage("");
          } else if (msgData.type === "response") {
            setMessages(prev => [...prev, { role: 'assistant', content: msgData.content }]);
            setIsLoading(false);
            setThinkingMessage("");
          } else if (msgData.type === "error") {
            setMessages(prev => [...prev, { role: 'assistant', content: `Error: ${msgData.message}` }]);
            setIsLoading(false);
            setThinkingMessage("");
          }
        } catch (err) {
          console.error("Error parseando mensaje WS:", err);
        }
      };

      ws.onclose = () => {
        setConnected(false);
        setServicesReady(false);
        reconnectTimer = setTimeout(connectWebSocket, 3000);
      };

      socketRef.current = ws;
    };

    fetchFundacion();
    connectWebSocket();
    return () => {
      clearTimeout(reconnectTimer);
      if (socketRef.current) socketRef.current.close();
    };
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, thinkingMessage]);

  useEffect(() => {
    localStorage.setItem('historia-chat-width', String(chatWidth));
  }, [chatWidth]);

  useEffect(() => {
    if (!isResizingChat) return undefined;

    const handlePointerMove = (event) => {
      const minimumWidth = 300;
      const maximumWidth = Math.min(560, window.innerWidth - 260);
      const nextWidth = Math.min(maximumWidth, Math.max(minimumWidth, window.innerWidth - event.clientX));
      setChatWidth(nextWidth);
    };
    const stopResizing = () => {
      setIsResizingChat(false);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    };

    window.addEventListener('pointermove', handlePointerMove);
    window.addEventListener('pointerup', stopResizing, { once: true });
    document.body.style.cursor = 'col-resize';
    document.body.style.userSelect = 'none';

    return () => {
      window.removeEventListener('pointermove', handlePointerMove);
      window.removeEventListener('pointerup', stopResizing);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    };
  }, [isResizingChat]);

  const startChatResize = (event) => {
    event.preventDefault();
    chatResizeRef.current = event.currentTarget;
    setIsResizingChat(true);
  };

  const scrollToSection = (id) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const sendMessage = () => {
    if (!input.trim() || isLoading) return;
    if (!socketRef.current || socketRef.current.readyState !== WebSocket.OPEN) {
      setMessages(prev => [...prev, { role: 'assistant', content: "El servidor de chat no está disponible. Reintentando conexión..." }]);
      return;
    }
    
    const userMsg = { role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setIsLoading(true);
    setThinkingMessage("Enviando mensaje...");
    
    socketRef.current.send(input);
    setInput("");
  };

  return (
    <div className="flex h-screen bg-slate-950 text-slate-100 font-sans overflow-hidden">

      {/* 1. ÍNDICE LATERAL (SIDEBAR) */}
      <aside
        className={`${
          isSidebarOpen ? 'w-64' : 'w-16'
        } transition-all duration-300 bg-slate-900 border-r border-slate-800 flex flex-col justify-between z-20 shrink-0`}
      >
        <div>
          <div className="flex items-center justify-between p-4 border-b border-slate-800">
            {isSidebarOpen && (
              <div className="flex items-center gap-2 font-bold text-amber-500 truncate">
                <History className="w-5 h-5 shrink-0" />
                <span className="truncate">Archivo Histórico</span>
              </div>
            )}
            <button
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="p-2 hover:bg-slate-800 rounded-xl text-slate-400 hover:text-white transition mx-auto"
            >
              {isSidebarOpen ? <ChevronLeft className="w-5 h-5" /> : <ChevronRight className="w-5 h-5" />}
            </button>
          </div>

          {isSidebarOpen && (
            <nav className="p-3 space-y-1.5 overflow-y-auto max-h-[calc(100vh-140px)]">
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 px-2">Secciones</p>
              {data.map((item, idx) => (
                <button
                  key={idx}
                  onClick={() => scrollToSection(`section-${idx}`)}
                  className="w-full text-left px-3 py-2 rounded-lg text-xs text-slate-300 hover:bg-slate-800 hover:text-amber-400 transition truncate"
                >
                  {item.titulo || `Sección ${idx + 1}`}
                </button>
              ))}
            </nav>
          )}
        </div>

        {isSidebarOpen && (
          <div className="p-3 border-t border-slate-800 text-[11px] text-slate-500 text-center">
            Las Varillas © {new Date().getFullYear()}
          </div>
        )}
      </aside>

      {/* 2. ÁREA DE LECTURA CENTRAL (AMPLIA Y CÓMODA) */}
      <main className="flex-1 flex flex-col overflow-y-auto relative bg-slate-950 min-w-0">
        <header className="sticky top-0 z-10 bg-slate-950/90 backdrop-blur-md border-b border-slate-800 px-6 py-4 flex justify-between items-center shadow-sm">
          <div className="min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <Workflow className="w-4 h-4 text-amber-400 shrink-0" />
              <span className="text-[10px] uppercase tracking-[0.18em] text-amber-400/80 font-semibold">Archivo vivo</span>
            </div>
            <h1 className="text-lg font-bold text-slate-100 truncate">Debate sobre la fundación de Las Varillas</h1>
            <p className="text-xs text-slate-400 truncate">Consulta documental coordinada por servicios MCP y Ollama</p>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <div className={`hidden sm:flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border text-[10px] font-medium ${connected && servicesReady ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-300' : 'border-slate-700 bg-slate-900 text-slate-500'}`}>
              {connected && servicesReady ? <CircleCheck className="w-3.5 h-3.5" /> : <Radio className="w-3.5 h-3.5" />}
              <span>{connected && servicesReady ? 'MCP + Ollama' : 'Conectando'}</span>
            </div>
            {!isChatOpen && (
              <button
                onClick={() => setIsChatOpen(true)}
                className="flex items-center gap-2 px-4 py-2 bg-amber-600 hover:bg-amber-500 text-white rounded-xl font-medium transition shadow-md shadow-amber-950/30 text-xs"
              >
                <MessageSquare className="w-4 h-4" />
                <span>Abrir Asistente IA</span>
              </button>
            )}
          </div>
        </header>

        <div className="max-w-4xl w-full mx-auto p-6 md:p-10 space-y-8">
          {data.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-20 text-slate-500">
              <Loader2 className="w-8 h-8 animate-spin mb-3 text-amber-500" />
              <p className="text-sm">Cargando documentos históricos...</p>
            </div>
          ) : (
            data.map((item, idx) => (
              <section
                key={idx}
                id={`section-${idx}`}
                className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 md:p-8 shadow-xl scroll-mt-24"
              >
                <h2 className="text-xl md:text-2xl font-semibold text-amber-400 mb-4">{item.titulo}</h2>
                <div className="text-slate-300 text-sm md:text-base leading-relaxed whitespace-pre-line space-y-4">
                  {item.contenido || item.texto || JSON.stringify(item)}
                </div>
              </section>
            ))
          )}
        </div>
      </main>

      {/* 3. PANEL DE CHAT LATERAL (DISEÑO FLUIDO) */}
      {isChatOpen && (
        <aside
          className="relative w-[min(380px,calc(100vw-4rem))] bg-slate-900 border-l border-slate-800 flex flex-col z-30 shadow-2xl shrink-0"
          style={{ width: `min(${chatWidth}px, calc(100vw - 4rem))` }}
        >
          <button
            type="button"
            onPointerDown={startChatResize}
            className={`absolute left-0 top-0 bottom-0 z-40 flex w-3 -translate-x-1/2 cursor-col-resize items-center justify-center text-slate-600 transition hover:text-amber-400 ${isResizingChat ? 'text-amber-400' : ''}`}
            title="Arrastra para cambiar el ancho del chat"
            aria-label="Cambiar el ancho del chat"
          >
            <span className="flex h-12 w-3 items-center justify-center rounded-full bg-slate-800/80 shadow-sm">
              <GripVertical className="h-4 w-4" />
            </span>
          </button>

          <div className="p-4 border-b border-slate-800 flex justify-between items-center bg-slate-900">
            <div className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-amber-400" />
              <div className="min-w-0">
                <h3 className="font-semibold text-slate-200 text-sm truncate">Asistente Varillas</h3>
                <p className="text-[10px] text-slate-500">{Math.round(chatWidth)} px de ancho</p>
              </div>
            </div>
            <button
              onClick={() => setIsChatOpen(false)}
              className="p-1.5 hover:bg-slate-800 rounded-lg text-slate-400 hover:text-white transition"
              title="Cerrar chat"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          <div className="flex-1 p-4 md:p-5 overflow-y-auto space-y-4 bg-slate-900/70">
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                    className={`max-w-[90%] p-3.5 rounded-2xl text-xs md:text-sm leading-relaxed shadow-sm ${
                    msg.role === 'user'
                      ? 'bg-amber-600 text-white rounded-br-none'
                      : 'bg-slate-800 text-slate-200 rounded-bl-none border border-slate-700/60'
                  }`}
                >
                  {msg.content}
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="flex items-center gap-3 text-xs text-amber-400 bg-slate-800/60 border border-amber-500/20 p-3 rounded-xl animate-pulse">
                <Loader2 className="w-4 h-4 animate-spin shrink-0" />
                <span>{thinkingMessage || 'Pensando...'}</span>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          <div className="p-4 border-t border-slate-800 bg-slate-900">
            <div className="flex items-center gap-2 bg-slate-950 border border-slate-800 rounded-xl p-2 focus-within:border-amber-500/50 transition">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                  }
                }}
                placeholder="Pregunta sobre la historia..."
                className="flex-1 bg-transparent border-none text-slate-200 text-xs md:text-sm focus:outline-none px-2"
              />
              <button
                onClick={sendMessage}
                disabled={isLoading || !input.trim()}
                className="p-2 bg-amber-600 hover:bg-amber-500 disabled:opacity-50 text-white rounded-lg transition shrink-0"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>
        </aside>
      )}

    </div>
  );
}

export default App;