"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { api } from "../lib/api";
import { t } from "../lib/i18n";

export default function Home() {
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

  if (!user) return <div className="min-h-screen flex items-center justify-center">{t(lang, "ui.loading")}</div>;

  const pillars = ["geist", "herz", "seele", "koerper", "aura"];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-50 p-6 md:p-10">
      <div className="max-w-5xl mx-auto">
        <header className="mb-12 text-center">
          <h1 className="text-5xl font-light text-slate-800 mb-3 tracking-wide">{t(lang, "appName")}</h1>
          <p className="text-lg text-slate-500 font-light">{t(lang, "ui.companionLine")}</p>
        </header>

        <div className="bg-white/80 backdrop-blur rounded-2xl shadow-sm border border-slate-200/50 p-8 md:p-10 mb-12">
          <h2 className="text-2xl font-light text-slate-700 mb-6 leading-relaxed">{t(lang, "welcome.title")}</h2>
          <div className="space-y-4 text-slate-600 leading-loose text-base">
            <p>{t(lang, "welcome.intro1")}</p>
            <p>{t(lang, "welcome.intro2")}</p>
            <p>{t(lang, "welcome.intro3")}</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          {pillars.map((p) => {
            const pillarConfig: Record<string, { icon: string; gradient: string; textColor: string; borderColor: string }> = {
              geist: { icon: '🧠', gradient: 'from-blue-50 to-indigo-100', textColor: 'text-blue-800', borderColor: 'border-blue-200/50' },
              herz: { icon: '❤️', gradient: 'from-rose-50 to-pink-100', textColor: 'text-rose-800', borderColor: 'border-rose-200/50' },
              seele: { icon: '✨', gradient: 'from-purple-50 to-violet-100', textColor: 'text-purple-800', borderColor: 'border-purple-200/50' },
              koerper: { icon: '💪', gradient: 'from-green-50 to-emerald-100', textColor: 'text-green-800', borderColor: 'border-green-200/50' },
              aura: { icon: '🌟', gradient: 'from-amber-50 to-yellow-100', textColor: 'text-amber-800', borderColor: 'border-amber-200/50' }
            };
            const config = pillarConfig[p] || pillarConfig['geist'];
            return (
              <div key={p} className={`bg-gradient-to-br ${config.gradient} rounded-2xl shadow-lg border ${config.borderColor} p-6 text-center hover:shadow-xl hover:scale-105 transition-all`}>
                <div className="text-4xl mb-3">{config.icon}</div>
                <h2 className={`text-xl font-medium ${config.textColor} mb-3`}>{t(lang, `pillars.${p}`)}</h2>
                <p className={`text-sm ${config.textColor} opacity-90 leading-relaxed`}>{t(lang, `pillarDescriptions.${p}`)}</p>
              </div>
            );
          })}
        </div>

        <div className="flex flex-col sm:flex-row gap-4 justify-center mb-8">
          <Link
            href="/journal"
            className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-10 py-4 rounded-full hover:from-blue-500 hover:to-indigo-500 active:scale-95 transition-all text-center font-light text-lg shadow-lg hover:shadow-xl flex items-center justify-center gap-3"
          >
            <span className="text-2xl">✍️</span>
            {t(lang, "writeEntry")}
          </Link>
          <Link
            href="/report"
            className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-10 py-4 rounded-full hover:from-purple-500 hover:to-pink-500 active:scale-95 transition-all text-center font-light text-lg shadow-lg hover:shadow-xl flex items-center justify-center gap-3"
          >
            <span className="text-2xl">📊</span>
            {t(lang, "report")}
          </Link>
        </div>

        <div className="text-center">
          <Link href="/settings" className="text-slate-500 hover:text-slate-700 transition-colors text-sm inline-flex items-center gap-2">
            <span>⚙️</span>
            {t(lang, "settings")}
          </Link>
        </div>
      </div>
    </div>
  );
}
