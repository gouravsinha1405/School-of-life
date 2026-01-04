"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { api } from "../../lib/api";
import { t } from "../../lib/i18n";

export default function Settings() {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [lang, setLang] = useState<"de" | "en">("de");

  useEffect(() => {
    api
      .getMe()
      .then((u) => {
        setUser(u);
        setLang(u.preferred_language || "de");
      })
      .catch(() => router.push("/login"));
  }, [router]);

  const handleLanguageChange = async (nextLang: "de" | "en") => {
    try {
      const updated = await api.updateMe(nextLang);
      setUser(updated);
      setLang(updated.preferred_language || nextLang);
    } catch {
      alert("Language update failed");
    }
  };

  const handleExport = async () => {
    try {
      const data = await api.exportData();
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "lebensschule-export.json";
      a.click();
    } catch (err) {
      alert("Export failed");
    }
  };

  const handleDelete = async () => {
    if (!confirm("Are you sure you want to delete your account? This cannot be undone.")) return;
    try {
      await api.deleteAccount();
      router.push("/login");
    } catch (err) {
      alert("Delete failed");
    }
  };

  const handleLogout = async () => {
    try {
      await api.logout();
    } finally {
      router.push("/login");
      router.refresh();
    }
  };

  if (!user) return <div className="min-h-screen flex items-center justify-center font-light text-slate-500">Loading...</div>;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-50 p-6 md:p-10">
      <div className="max-w-2xl mx-auto">
        <header className="mb-10 flex justify-between items-center">
          <h1 className="text-4xl font-light text-slate-700">{t(lang, "settings")}</h1>
          <Link href="/" className="text-slate-500 hover:text-slate-700 transition-colors text-sm">
            {t(lang, "home")}
          </Link>
        </header>

        <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl shadow-lg border border-blue-200/50 p-8 mb-6">
          <div className="flex items-center gap-3 mb-5">
            <span className="text-3xl">👤</span>
            <h2 className="text-2xl font-light text-blue-900">Account</h2>
          </div>
          <p className="text-sm text-slate-600 mb-5 font-light">
            <strong className="font-medium">Email:</strong> {user.email}
          </p>
          <div className="mb-6">
            <label className="block text-sm font-light text-slate-600 mb-2">{t(lang, "language")}</label>
            <select
              value={lang}
              onChange={(e) => handleLanguageChange(e.target.value as "de" | "en")}
              className="w-full border border-slate-200 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-slate-300 focus:border-transparent transition-all font-light"
            >
              <option value="de">Deutsch</option>
              <option value="en">English</option>
            </select>
          </div>

          <div>
            <button
              onClick={handleLogout}
              className="bg-slate-700 text-white px-8 py-3 rounded-full hover:bg-slate-600 active:scale-95 transition-all font-light shadow-sm"
            >
              {t(lang, "logout")}
            </button>
          </div>
        </div>

        <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-2xl shadow-lg border border-green-200/50 p-8 mb-6">
          <div className="flex items-center gap-3 mb-5">
            <span className="text-3xl">💾</span>
            <h2 className="text-2xl font-light text-green-900">Data</h2>
          </div>
          <button onClick={handleExport} className="bg-gradient-to-r from-green-600 to-emerald-600 text-white px-8 py-3 rounded-full hover:from-green-500 hover:to-emerald-500 active:scale-95 transition-all font-light shadow-lg hover:shadow-xl flex items-center gap-2">
            <span className="text-xl">📥</span>
            {t(lang, "export")}
          </button>
        </div>

        <div className="bg-gradient-to-br from-red-50 to-rose-50 rounded-2xl shadow-lg border border-red-200/50 p-8">
          <div className="flex items-center gap-3 mb-5">
            <span className="text-3xl">⚠️</span>
            <h2 className="text-2xl font-light text-red-700">Danger Zone</h2>
          </div>
          <button onClick={handleDelete} className="bg-gradient-to-r from-red-600 to-rose-600 text-white px-8 py-3 rounded-full hover:from-red-500 hover:to-rose-500 active:scale-95 transition-all font-light shadow-lg hover:shadow-xl flex items-center gap-2">
            <span className="text-xl">🗑️</span>
            {t(lang, "deleteAccount")}
          </button>
        </div>
      </div>
    </div>
  );
}
