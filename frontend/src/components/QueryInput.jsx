import React from 'react';
import { Search } from 'lucide-react';

export default function QueryInput({ query, setQuery, onRun, loading }) {
  const suggestions = [
    "Compare NVDA vs MSFT: Q3 operating margin, AI CapEx, and export risks",
    "Compare AAPL vs GOOGL: Operating leverage and research expenditures",
    "Compare TSLA vs F: Free cash flow liquidity and regulatory factors"
  ];

  return (
    <div className="mb-6 space-y-2">
      <div className="flex gap-2">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
          <input 
            type="text" 
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && !loading && onRun()}
            placeholder="Ask any comparison (e.g. Compare NVDA vs MSFT operating margin and CapEx)..."
            className="w-full bg-slate-900 border border-slate-800 rounded-lg pl-10 pr-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500"
          />
        </div>
        <button 
          onClick={onRun}
          disabled={loading}
          className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white px-5 py-2.5 rounded-lg text-sm font-medium transition"
        >
          {loading ? "Analyzing..." : "Run Analysis"}
        </button>
      </div>

      <div className="flex flex-wrap gap-1.5 pt-1">
        {suggestions.map((s, idx) => (
          <button 
            key={idx}
            onClick={() => setQuery(s)}
            className="text-[11px] bg-slate-900/60 hover:bg-slate-800 text-slate-400 hover:text-slate-200 border border-slate-800 px-2 py-0.5 rounded transition"
          >
            {s.split(':')[0]}
          </button>
        ))}
      </div>
    </div>
  );
}