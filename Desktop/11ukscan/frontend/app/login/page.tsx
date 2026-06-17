"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

const STATIC_USERNAME = "akash123";
const STATIC_PASSWORD = "akash123";

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();

    if (username === STATIC_USERNAME && password === STATIC_PASSWORD) {
      document.cookie = "bankscan_auth=1; path=/; max-age=86400";
      router.push("/");
      return;
    }

    setError("Invalid username or password");
  }

  return (
    <main className="min-h-screen bg-[#0a0a14] flex items-center justify-center px-6">
      <div className="w-full max-w-sm rounded-2xl border border-white/10 bg-white/3 p-8">
        <div className="flex items-center gap-3 mb-8">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-violet-900/40">
            <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round"
                d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <div>
            <h1 className="text-base font-bold text-white tracking-tight">BankScan</h1>
            <p className="text-xs text-white/40 leading-none">Sign in</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-white/50 mb-1.5">Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-2.5 text-sm text-white placeholder-white/30 outline-none focus:border-violet-500/50"
              placeholder="Enter username"
              autoFocus
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-white/50 mb-1.5">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-2.5 text-sm text-white placeholder-white/30 outline-none focus:border-violet-500/50"
              placeholder="Enter password"
            />
          </div>

          {error && (
            <p className="text-xs text-red-400">{error}</p>
          )}

          <button
            type="submit"
            className="w-full rounded-xl bg-gradient-to-r from-violet-500 to-indigo-600 py-2.5 text-sm font-semibold text-white transition-all duration-200 hover:scale-[1.02]"
          >
            Sign in
          </button>
        </form>
      </div>
    </main>
  );
}
