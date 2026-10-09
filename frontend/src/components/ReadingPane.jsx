import { CircleCheck, Loader2, Radio, Workflow } from 'lucide-react';

export default function ReadingPane({ data, connected, isLoading, isChatOpen, onOpenChat }) {
  return (
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
          <div className={`hidden sm:flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border text-[10px] font-medium ${connected ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-300' : 'border-slate-700 bg-slate-900 text-slate-500'}`}>
            {connected ? <CircleCheck className="w-3.5 h-3.5" /> : <Radio className="w-3.5 h-3.5" />}
            <span>{isLoading ? 'Conectando' : connected ? 'Backend conectado' : 'Sin conexión'}</span>
          </div>
          {!isChatOpen && (
            <button
              type="button"
              onClick={onOpenChat}
              className="flex items-center gap-2 px-4 py-2 bg-amber-600 hover:bg-amber-500 text-white rounded-xl font-medium transition shadow-md shadow-amber-950/30 text-xs"
            >
              <span>Abrir Asistente IA</span>
            </button>
          )}
        </div>
      </header>

      <div className="max-w-4xl w-full mx-auto p-6 md:p-10 space-y-8">
        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-20 text-slate-500">
            <Loader2 className="w-8 h-8 animate-spin mb-3 text-amber-500" />
            <p className="text-sm">Cargando documentos históricos...</p>
          </div>
        ) : data.length === 0 ? (
          <p className="py-20 text-center text-sm text-slate-500">No se pudieron cargar los documentos históricos.</p>
        ) : (
          data.map((item, index) => (
            <section
              key={item.id || item.titulo || index}
              id={`section-${index}`}
              className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 md:p-8 shadow-xl scroll-mt-24"
            >
              <h2 className="text-xl md:text-2xl font-semibold text-amber-400 mb-4">{item.titulo || item.documento}</h2>
              <div className="text-slate-300 text-sm md:text-base leading-relaxed whitespace-pre-line space-y-4">
                {item.contenido || item.texto || JSON.stringify(item)}
              </div>
            </section>
          ))
        )}
      </div>
    </main>
  );
}