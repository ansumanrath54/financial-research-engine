import React from 'react';

export default function RiskSection({ riskFactors }) {
  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-5">
      <h3 className="text-xs uppercase font-semibold text-slate-400 tracking-wider mb-3">
        Attributed SEC 10-K / 10-Q Disclosures
      </h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {riskFactors.map((rf, i) => (
          <div key={i} className="p-3.5 bg-slate-950/40 border border-slate-800/80 rounded">
            <div className="flex items-center justify-between mb-1.5">
              <span className="font-semibold text-xs text-blue-400">{rf.ticker} // {rf.risk_title}</span>
            </div>
            <p className="text-xs text-slate-300 mb-2 leading-relaxed">{rf.summary}</p>
            <span className="text-[10px] font-mono text-slate-500 block truncate">
              Source: {rf.citation}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}