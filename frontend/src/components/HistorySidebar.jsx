import { ChevronLeft, ChevronRight, History } from 'lucide-react';

export default function HistorySidebar({ data, isOpen, onToggle, onNavigate }) {
  return (
    <aside
      className={`${isOpen ? 'w-64' : 'w-16'} transition-all duration-300 bg-slate-900 border-r border-slate-800 flex flex-col justify-between z-20 shrink-0`}
    >
      <div>
        <div className="flex items-center justify-between p-4 border-b border-slate-800">
          {isOpen && (
            <div className="flex items-center gap-2 font-bold text-amber-500 truncate">
              <History className="w-5 h-5 shrink-0" />
              <span className="truncate">Archivo Histórico</span>
            </div>
          )}
          <button
            type="button"
            onClick={onToggle}
            title={isOpen ? 'Contraer índice' : 'Expandir índice'}
            aria-label={isOpen ? 'Contraer índice' : 'Expandir índice'}
            className="p-2 hover:bg-slate-800 rounded-xl text-slate-400 hover:text-white transition mx-auto"
          >
            {isOpen ? <ChevronLeft className="w-5 h-5" /> : <ChevronRight className="w-5 h-5" />}
          </button>
        </div>

        {isOpen && (
          <nav className="p-3 space-y-1.5 overflow-y-auto max-h-[calc(100vh-140px)]">
            <p className="text-xs font-semibold text-slate-500 uppercase mb-2 px-2">Secciones</p>
            {data.map((item, index) => (
              <button
                key={item.id || item.titulo || index}
                type="button"
                onClick={() => onNavigate(`section-${index}`)}
                className="w-full text-left px-3 py-2 rounded-lg text-xs text-slate-300 hover:bg-slate-800 hover:text-amber-400 transition truncate"
              >
                {item.titulo || `Sección ${index + 1}`}
              </button>
            ))}
          </nav>
        )}
      </div>

      {isOpen && (
        <div className="p-3 border-t border-slate-800 text-[11px] text-slate-500 text-center">
          Las Varillas © {new Date().getFullYear()}
        </div>
      )}
    </aside>
  );
}