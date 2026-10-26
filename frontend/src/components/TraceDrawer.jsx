import React from 'react';
import { Terminal, X } from 'lucide-react';

export default function TraceDrawer({ isOpen, onClose, telemetry, logs }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-y-0 right-0 w-96 bg-slate-900 border-l border-slate-800 shadow-2xl flex flex-col z-50">
      <div className="p-4 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Terminal className="w-4 h-4 text-blue-400" />
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-200">Execution Telemetry</span>
        </div>
        <button onClick={onClose} className="text-slate-400 hover:text-white">
          <X className="w-4 h-4" />
        </button>
      </div>

      <div className="p-4 border-b border-slate-800 bg-slate-950/50 grid grid-cols-2 gap-2 text-xs font-mono">
        <div>
          <span className="text-slate-500 block text-[10px]">TOTAL TOKENS</span>
          <span className="text-white font-semibold">
            {((telemetry?.input_tokens || 0) + (telemetry?.output_tokens || 0)).toLocaleString()}
          </span>
        </div>
        <div>
          <span className="text-slate-500 block text-[10px]">ESTIMATED COST</span>
          <span className="text-emerald-400 font-semibold">
            ${telemetry?.estimated_cost_usd || 0}
          </span>
        </div>
      </div>

      <div className="flex-1 p-4 overflow-y-auto font-mono text-[11px] space-y-1.5 text-slate-400">
        {logs.length === 0 ? (
          <span className="text-slate-600">Waiting for graph trigger...</span>
        ) : (
          logs.map((log, i) => (
            <div key={i} className="leading-snug">
              <span className="text-blue-400">{log}</span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}