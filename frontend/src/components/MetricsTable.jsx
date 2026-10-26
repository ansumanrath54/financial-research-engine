import React from 'react';

export default function MetricsTable({ tickers, metrics }) {
  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-lg overflow-hidden">
      <div className="px-5 py-3 border-b border-slate-800">
        <h3 className="text-xs uppercase font-semibold text-slate-400 tracking-wider">Deterministic Financial Metrics</h3>
      </div>
      <table className="w-full text-left text-xs">
        <thead className="bg-slate-950/50 text-slate-400 font-mono border-b border-slate-800">
          <tr>
            <th className="py-2.5 px-5">Financial Metric</th>
            <th className="py-2.5 px-5">{tickers[0] || "Ticker A"}</th>
            <th className="py-2.5 px-5">{tickers[1] || "Ticker B"}</th>
            <th className="py-2.5 px-5">Variance & Analysis</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800 font-mono">
          {metrics.map((row, i) => (
            <tr key={i} className="hover:bg-slate-800/30">
              <td className="py-3 px-5 text-slate-300 font-sans font-medium">{row.metric}</td>
              <td className="py-3 px-5 text-white font-semibold">{row.ticker_a_value}</td>
              <td className="py-3 px-5 text-white font-semibold">{row.ticker_b_value}</td>
              <td className="py-3 px-5 text-slate-400 font-sans">{row.delta_commentary}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}