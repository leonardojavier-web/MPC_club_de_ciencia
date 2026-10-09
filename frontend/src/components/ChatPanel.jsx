import { GripVertical, Loader2, Send, Sparkles, X } from 'lucide-react';

export default function ChatPanel({
  messages,
  input,
  setInput,
  isLoading,
  thinkingMessage,
  onSend,
  onClose,
  chatWidth,
  isResizing,
  onResizeStart,
  onResizeBy,
  chatEndRef,
}) {
  return (
    <aside
      className="fixed inset-y-0 right-0 z-30 flex w-[min(380px,calc(100vw-4rem))] flex-col bg-slate-900 border-l border-slate-800 shadow-2xl lg:relative lg:inset-auto lg:shrink-0"
      style={{ width: `min(${chatWidth}px, calc(100vw - 4rem))` }}
    >
      <button
        type="button"
        onPointerDown={onResizeStart}
        onKeyDown={(event) => {
          if (event.key === 'ArrowLeft') {
            event.preventDefault();
            onResizeBy(16);
          } else if (event.key === 'ArrowRight') {
            event.preventDefault();
            onResizeBy(-16);
          }
        }}
        className={`absolute left-0 top-0 bottom-0 z-40 flex w-3 -translate-x-1/2 cursor-col-resize items-center justify-center text-slate-600 transition hover:text-amber-400 ${isResizing ? 'text-amber-400' : ''}`}
        title="Arrastra para cambiar el ancho del chat"
        aria-label="Cambiar el ancho del chat"
        aria-orientation="vertical"
        aria-valuemin={300}
        aria-valuemax={560}
        aria-valuenow={Math.round(chatWidth)}
        role="separator"
        tabIndex={0}
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
          type="button"
          onClick={onClose}
          className="p-1.5 hover:bg-slate-800 rounded-lg text-slate-400 hover:text-white transition"
          title="Cerrar chat"
          aria-label="Cerrar chat"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      <div className="flex-1 p-4 md:p-5 overflow-y-auto space-y-4 bg-slate-900/70">
        {messages.map((message, index) => (
          <div key={`${message.role}-${index}`} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[90%] p-3.5 rounded-2xl text-xs md:text-sm leading-relaxed shadow-sm ${message.role === 'user' ? 'bg-amber-600 text-white rounded-br-none' : 'bg-slate-800 text-slate-200 rounded-bl-none border border-slate-700/60'}`}>
              {message.content}
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
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                onSend();
              }
            }}
            placeholder="Pregunta sobre la historia..."
            className="flex-1 bg-transparent border-none text-slate-200 text-xs md:text-sm focus:outline-none px-2"
          />
          <button
            type="button"
            onClick={onSend}
            disabled={isLoading || !input.trim()}
            title="Enviar mensaje"
            aria-label="Enviar mensaje"
            className="p-2 bg-amber-600 hover:bg-amber-500 disabled:opacity-50 text-white rounded-lg transition shrink-0"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>
  );
}