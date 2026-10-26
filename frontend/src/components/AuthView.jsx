import React, { useState } from 'react';

const API_BASE = "http://localhost:8000";

export default function AuthView({ onAuthenticated }) {
  const [mode, setMode] = useState("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const submit = async (event) => {
    event.preventDefault();
    setError("");
    setSubmitting(true);

    try {
      if (mode === "register") {
        const registration = await fetch(`${API_BASE}/api/auth/register`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username, password }),
        });
        if (!registration.ok) {
          const body = await registration.json();
          throw new Error(body.detail || "Could not create account");
        }
      }

      const form = new URLSearchParams({ username, password });
      const response = await fetch(`${API_BASE}/api/auth/token`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: form,
      });
      const body = await response.json();
      if (!response.ok) {
        throw new Error(body.detail || "Sign in failed");
      }
      onAuthenticated(body.access_token);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center p-6">
      <form onSubmit={submit} className="w-full max-w-sm space-y-5 rounded-xl border border-slate-800 bg-slate-900 p-7 shadow-xl">
        <div>
          <p className="text-xs font-bold tracking-widest text-blue-400">APEXALPHA</p>
          <h1 className="mt-2 text-xl font-semibold">{mode === "login" ? "Sign in" : "Create your account"}</h1>
          <p className="mt-1 text-sm text-slate-400">Sign in to access your financial research.</p>
        </div>

        <label className="block space-y-1.5 text-sm text-slate-300">
          Username
          <input
            autoComplete="username"
            required
            minLength={3}
            maxLength={50}
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            className="w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 text-white outline-none focus:border-blue-500"
          />
        </label>

        <label className="block space-y-1.5 text-sm text-slate-300">
          Password
          <input
            type="password"
            autoComplete={mode === "login" ? "current-password" : "new-password"}
            required
            minLength={8}
            maxLength={72}
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            className="w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 text-white outline-none focus:border-blue-500"
          />
        </label>

        {error && <p role="alert" className="text-sm text-red-400">{error}</p>}

        <button
          type="submit"
          disabled={submitting}
          className="w-full rounded bg-blue-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-blue-500 disabled:opacity-50"
        >
          {submitting ? "Please wait..." : mode === "login" ? "Sign in" : "Create account"}
        </button>

        <p className="text-center text-sm text-slate-400">
          {mode === "login" ? "New here?" : "Already registered?"}{" "}
          <button
            type="button"
            onClick={() => {
              setMode(mode === "login" ? "register" : "login");
              setError("");
            }}
            className="text-blue-400 hover:text-blue-300"
          >
            {mode === "login" ? "Create an account" : "Sign in"}
          </button>
        </p>
      </form>
    </main>
  );
}
