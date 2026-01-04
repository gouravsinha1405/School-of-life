"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { api } from "../../lib/api";

export default function Login() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      await api.login(email, password);
      router.push("/");
    } catch (err: any) {
      setError(err.message || "Login failed");
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-50 flex items-center justify-center p-4">
      <div className="bg-white/90 backdrop-blur rounded-3xl shadow-lg border border-slate-200/50 p-10 max-w-md w-full">
        <h1 className="text-3xl font-light text-slate-700 mb-8 text-center">Anmelden</h1>
        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-sm font-light text-slate-600 mb-2">E-Mail</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full border border-slate-200 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-slate-300 focus:border-transparent transition-all"
            />
          </div>
          <div>
            <label className="block text-sm font-light text-slate-600 mb-2">Passwort</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full border border-slate-200 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-slate-300 focus:border-transparent transition-all"
            />
          </div>
          {error && <p className="text-red-500 text-sm">{error}</p>}
          <button type="submit" className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-3 rounded-full hover:from-blue-500 hover:to-indigo-500 active:scale-95 transition-all font-light text-lg shadow-lg hover:shadow-xl flex items-center justify-center gap-2">
            <span className="text-xl">🔐</span>
            Anmelden
          </button>
        </form>
        <p className="mt-6 text-sm text-slate-500 text-center font-light">
          Noch kein Konto?{" "}
          <Link href="/register" className="text-slate-700 hover:text-slate-800 underline">
            Registrieren
          </Link>
        </p>
      </div>
    </div>
  );
}
