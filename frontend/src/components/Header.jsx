import React, { useState } from 'react';
import { PanelLeft, Activity, UserRound, LogOut } from 'lucide-react';

export default function Header({
  onToggleSidebar,
  onOpenTrace,
  username,
  theme,
  onThemeChange,
  onLogout,
  estimatedCost,
}) {
  const [profileOpen, setProfileOpen] = useState(false);

  return (
    <header className="h-14 border-b border-slate-800 px-6 flex items-center justify-between bg-slate-900/30">
      <div className="flex items-center gap-3">
        <button 
          onClick={onToggleSidebar} 
          className="p-1.5 text-slate-400 hover:text-white rounded hover:bg-slate-800 transition"
        >
          <PanelLeft className="w-4 h-4" />
        </button>
        <h1 className="text-sm font-semibold tracking-tight text-white flex items-center gap-2">
          <span className="text-blue-500 font-bold">APEXALPHA</span> // Financial Engine
        </h1>
      </div>

      <div className="flex items-center gap-3">
        <button 
          onClick={onOpenTrace}
          className="flex items-center gap-2 text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-1.5 rounded border border-slate-700 transition"
        >
          <Activity className="w-3.5 h-3.5 text-blue-400" />
          <span>Inspect Agent Trace</span>
          {estimatedCost > 0 && (
            <span className="text-slate-500 font-mono text-[11px]">(${estimatedCost})</span>
          )}
        </button>
        <div className="relative">
          <button
            type="button"
            aria-label="Open profile menu"
            aria-expanded={profileOpen}
            onClick={() => setProfileOpen((open) => !open)}
            className="p-2 text-slate-300 hover:text-white rounded border border-slate-700 hover:bg-slate-800 transition"
          >
            <UserRound className="w-4 h-4" />
          </button>
          {profileOpen && (
            <div className="absolute right-0 top-full mt-2 min-w-56 rounded-lg border border-slate-700 bg-slate-900 p-2 shadow-xl z-50">
              <div className="px-3 py-2 text-sm text-slate-200 truncate" title={username}>
                {username}
              </div>
              <div className="my-1 border-t border-slate-800" />
              <label className="block px-3 py-2 text-xs text-slate-400">
                Theme
                <select
                  value={theme}
                  onChange={(event) => onThemeChange(event.target.value)}
                  className="mt-1.5 w-full rounded border border-slate-700 bg-slate-950 px-2.5 py-2 text-sm text-slate-200 outline-none focus:border-blue-500"
                >
                  <option value="classic">Classic</option>
                  <option value="light">Light</option>
                  <option value="dark">Dark</option>
                  <option value="system">System</option>
                </select>
              </label>
              <div className="my-1 border-t border-slate-800" />
              <button
                type="button"
                onClick={onLogout}
                className="w-full flex items-center gap-2 rounded px-3 py-2 text-left text-sm text-red-400 hover:bg-red-500/10 hover:text-red-300 transition"
              >
                <LogOut className="h-3.5 w-3.5" />
                <span>Log out</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}