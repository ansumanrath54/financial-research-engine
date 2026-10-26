import React from 'react';

export default function Sidebar({ isOpen, sessions, onSelectSession, onNewSession }) {
  return (
    <aside className={`${isOpen ? 'w-64' : 'w-0'} transition-all duration-200 border-r border-slate-800 bg-slate-900/60 flex flex-col overflow-hidden`}>
      <div className="p-4 border-b border-slate-800 flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Past Analyses</span>
        <button 
          onClick={onNewSession} 
          className="text-xs bg-blue-600 hover:bg-blue-500 text-white px-2.5 py-1 rounded font-medium transition"
        >
          + New
        </button>
      </div>
      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        {sessions.length === 0 ? (
          <p className="text-xs text-slate-500 p-2">No past research sessions yet.</p>
        ) : (
          sessions.map(s => (
            <button 
              key={s.thread_id}
              onClick={() => onSelectSession(s.thread_id)}
              className="w-full text-left p-2.5 rounded text-xs hover:bg-slate-800/80 transition-colors truncate block"
            >
              <div className="font-medium text-slate-200 truncate">{s.title}</div>
              <div className="text-[11px] text-slate-500 truncate">{s.query}</div>
            </button>
          ))
        )}
      </div>
    </aside>
  );
}