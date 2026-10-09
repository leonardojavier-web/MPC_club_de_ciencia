import { useEffect, useRef, useState } from 'react';
import ChatPanel from './components/ChatPanel';
import HistorySidebar from './components/HistorySidebar';
import ReadingPane from './components/ReadingPane';
import { useChat } from './hooks/useChat';
import { useChatPanelWidth } from './hooks/useChatPanelWidth';
import { useFoundationData } from './hooks/useFoundationData';

function App() {
  const { data, connected, isLoading: isLoadingData } = useFoundationData();
  const { messages, input, setInput, isLoading, thinkingMessage, sendMessage } = useChat();
  const { chatWidth, isResizing, startResize, resizeBy } = useChatPanelWidth();
  const [isSidebarOpen, setIsSidebarOpen] = useState(() => window.innerWidth >= 1024);
  const [isChatOpen, setIsChatOpen] = useState(() => window.innerWidth >= 768);
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, thinkingMessage]);

  const scrollToSection = (id) => {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="flex h-screen bg-slate-950 text-slate-100 font-sans overflow-hidden">
      <HistorySidebar
        data={data}
        isOpen={isSidebarOpen}
        onToggle={() => setIsSidebarOpen((open) => !open)}
        onNavigate={scrollToSection}
      />
      <ReadingPane
        data={data}
        connected={connected}
        isLoading={isLoadingData}
        isChatOpen={isChatOpen}
        onOpenChat={() => setIsChatOpen(true)}
      />
      {isChatOpen && (
        <>
          <button
            type="button"
            className="fixed inset-0 z-20 bg-slate-950/60 lg:hidden"
            onClick={() => setIsChatOpen(false)}
            aria-label="Cerrar panel de chat"
          />
          <ChatPanel
            messages={messages}
            input={input}
            setInput={setInput}
            isLoading={isLoading}
            thinkingMessage={thinkingMessage}
            onSend={sendMessage}
            onClose={() => setIsChatOpen(false)}
            chatWidth={chatWidth}
            isResizing={isResizing}
            onResizeStart={startResize}
            onResizeBy={resizeBy}
            chatEndRef={chatEndRef}
          />
        </>
      )}
    </div>
  );
}

export default App;