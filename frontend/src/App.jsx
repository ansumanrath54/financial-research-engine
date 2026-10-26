import React, { useState, useEffect } from 'react';
import { ShieldCheck, FileText } from 'lucide-react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import QueryInput from './components/QueryInput';
import MetricsTable from './components/MetricsTable';
import RiskSection from './components/RiskSection';
import TraceDrawer from './components/TraceDrawer';
import AuthView from './components/AuthView';

const API_BASE = "http://localhost:8000";
const createThreadId = () => `thread-${crypto.randomUUID()}`;
const THEME_OPTIONS = ["classic", "light", "dark", "system"];

export default function App() {
  const [token, setToken] = useState(() => localStorage.getItem("access_token"));
  const [theme, setTheme] = useState(() => {
    const savedTheme = localStorage.getItem("app_theme");
    return THEME_OPTIONS.includes(savedTheme) ? savedTheme : "classic";
  });
  const [systemPrefersDark, setSystemPrefersDark] = useState(
    () => window.matchMedia("(prefers-color-scheme: dark)").matches
  );
  const [username, setUsername] = useState("");
  const [query, setQuery] = useState("Compare NVDA vs MSFT: Q3 operating margin, AI CapEx, and export risks");
  const [threadId, setThreadId] = useState(createThreadId);
  const [sessions, setSessions] = useState([]);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [traceDrawerOpen, setTraceDrawerOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  const [logs, setLogs] = useState([]);
  const [telemetry, setTelemetry] = useState({ input_tokens: 0, output_tokens: 0, estimated_cost_usd: 0, api_calls: 0 });
  const [report, setReport] = useState(null);
  const effectiveTheme = theme === "system"
    ? (systemPrefersDark ? "dark" : "light")
    : theme;

  useEffect(() => {
    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
    const updateSystemTheme = (event) => setSystemPrefersDark(event.matches);
    mediaQuery.addEventListener("change", updateSystemTheme);
    return () => mediaQuery.removeEventListener("change", updateSystemTheme);
  }, []);

  const changeTheme = (selectedTheme) => {
    if (!THEME_OPTIONS.includes(selectedTheme)) return;
    localStorage.setItem("app_theme", selectedTheme);
    setTheme(selectedTheme);
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    setToken(null);
    setThreadId(createThreadId());
    setSessions([]);
    setReport(null);
    setLogs([]);
    setUsername("");
  };

  const authenticate = (accessToken) => {
    localStorage.setItem("access_token", accessToken);
    setThreadId(createThreadId());
    setSessions([]);
    setReport(null);
    setLogs([]);
    setToken(accessToken);
  };

  const authenticatedFetch = async (url, options = {}) => {
    const headers = new Headers(options.headers || {});
    headers.set("Authorization", `Bearer ${token}`);
    const response = await fetch(url, { ...options, headers });
    if (response.status === 401) {
      logout();
    }
    return response;
  };

  useEffect(() => {
    if (!token) return;
    fetchProfile();
    fetchSessions();
  }, [token]);

  const fetchProfile = async () => {
    try {
      const response = await authenticatedFetch(`${API_BASE}/api/auth/me`);
      if (response.ok) {
        const profile = await response.json();
        setUsername(profile.username);
      }
    } catch (error) {
      console.warn("Could not load profile", error);
    }
  };

  const fetchSessions = async () => {
    try {
      const res = await authenticatedFetch(`${API_BASE}/api/sessions`);
      if (res.ok) {
        const data = await res.json();
        setSessions(data);
      }
    } catch (e) {
      console.warn("Could not load sessions", e);
    }
  };

  const loadPastSession = async (id) => {
    try {
      const res = await authenticatedFetch(`${API_BASE}/api/sessions/${id}`);
      if (res.ok) {
        const data = await res.json();
        setThreadId(data.thread_id);
        setQuery(data.query);
        setReport(data.report);
        setTelemetry(data.telemetry || { input_tokens: 0, output_tokens: 0, estimated_cost_usd: 0, api_calls: 0 });
      }
    } catch (e) {
      console.error(e);
    }
  };

  const startNewSession = () => {
    setThreadId(createThreadId());
    setQuery("");
    setReport(null);
    setLogs([]);
  };

  const runAnalysis = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setReport(null);
    setLogs([]);

    try {
      const response = await authenticatedFetch(`${API_BASE}/api/research/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ thread_id: threadId, query })
      });

      if (!response.ok) {
        let message = `Analysis request failed (${response.status})`;
        try {
          const body = await response.json();
          message = body.detail || message;
        } catch {
          // Keep the status-based message when the server response is not JSON.
        }
        throw new Error(message);
      }
      if (!response.body) {
        throw new Error("Analysis stream is unavailable");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) {
          buffer += decoder.decode();
        } else {
          buffer += decoder.decode(value, { stream: true });
        }

        const events = buffer.split(/\r?\n\r?\n/);
        buffer = done ? "" : events.pop() || "";

        for (const event of events) {
          const line = event.split(/\r?\n/).find((entry) => entry.startsWith('data: '));
          if (line) {
            const data = JSON.parse(line.slice(6));
            if (data.status === 'started') {
              setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] Analysis started; waiting for the first workflow step.`]);
            } else if (data.node) {
              setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] Node '${data.node}' completed.`]);
            }

            if (data.telemetry) setTelemetry(data.telemetry);
            if (data.errors?.length) {
              setLogs(prev => [...prev, ...data.errors.map((error) => `[ERROR] ${error}`)]);
            }
            if (data.final_report) {
              setReport(data.final_report);
              fetchSessions();
            }
          }
        }

        if (done) break;
      }
    } catch (err) {
      setLogs(prev => [...prev, `[ERROR] Connection failed: ${err.message}`]);
    } finally {
      setLoading(false);
    }
  };

  if (!token) {
    return <AuthView onAuthenticated={authenticate} />;
  }

  return (
    <div data-theme={effectiveTheme} className="app-shell flex h-screen w-screen overflow-hidden bg-slate-950 text-slate-100">
      <Sidebar 
        isOpen={sidebarOpen} 
        sessions={sessions} 
        onSelectSession={loadPastSession} 
        onNewSession={startNewSession} 
      />

      <main className="flex-1 flex flex-col overflow-hidden">
        <Header 
          onToggleSidebar={() => setSidebarOpen(!sidebarOpen)} 
          onOpenTrace={() => setTraceDrawerOpen(true)}
          username={username}
          theme={theme}
          onThemeChange={changeTheme}
          onLogout={logout}
          estimatedCost={telemetry.estimated_cost_usd}
        />

        <div className="p-6 max-w-5xl w-full mx-auto flex-1 overflow-y-auto">
          <QueryInput 
            query={query} 
            setQuery={setQuery} 
            onRun={runAnalysis} 
            loading={loading} 
          />

          {report ? (
            <div className="space-y-6">
              <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-5">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs uppercase font-semibold text-slate-400 tracking-wider">Executive Verdict</span>
                  <span className={`inline-flex items-center gap-1 text-[11px] font-mono px-2 py-0.5 rounded border ${
                    report.validation_status === 'VERIFIED'
                      ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                      : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                  }`}>
                    <ShieldCheck className="w-3 h-3" />
                    {report.validation_status === 'VERIFIED' ? 'Pydantic Verified' : 'Partial Data · Gemini unavailable'}
                  </span>
                </div>
                <p className="text-sm leading-relaxed text-slate-200">{report.executive_summary}</p>
              </div>

              <MetricsTable 
                tickers={report.tickers} 
                metrics={report.metrics_table} 
              />

              <RiskSection 
                riskFactors={report.risk_factors} 
              />
            </div>
          ) : (
            <div className="h-64 border border-dashed border-slate-800 rounded-lg flex flex-col items-center justify-center text-slate-500 text-xs">
              <FileText className="w-8 h-8 mb-2 text-slate-600" />
              <span>Enter a ticker research request above to run multi-agent analysis.</span>
            </div>
          )}
        </div>
      </main>

      <TraceDrawer 
        isOpen={traceDrawerOpen} 
        onClose={() => setTraceDrawerOpen(false)} 
        telemetry={telemetry} 
        logs={logs} 
      />
    </div>
  );
}