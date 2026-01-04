"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api } from "../../lib/api";
import { t } from "../../lib/i18n";

export default function Report() {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [lang, setLang] = useState<"de" | "en">("de");
  const [report, setReport] = useState<any>(null);

  useEffect(() => {
    api
      .getMe()
      .then((u) => {
        setUser(u);
        setLang(u.preferred_language || "de");
        return api.getCurrentReport();
      })
      .then(setReport)
      .catch(() => router.push("/login"));
  }, [router]);

  if (!user || !report) return <div className="min-h-screen flex items-center justify-center font-light text-slate-500">Loading...</div>;

  const pillars = ["geist", "herz", "seele", "koerper", "aura"];

  const chartData = report.series.map((s: any) => ({
    date: s.date,
    Geist: s.geist,
    Herz: s.herz,
    Seele: s.seele,
    Körper: s.koerper,
    Aura: s.aura,
  }));

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-50 p-6 md:p-10">
      <div className="max-w-6xl mx-auto">
        <header className="mb-10 flex justify-between items-center">
          <h1 className="text-4xl font-light text-slate-700">{t(lang, "report")}</h1>
          <Link href="/" className="text-slate-500 hover:text-slate-700 transition-colors text-sm">
            {t(lang, "home")}
          </Link>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-5 gap-5 mb-10">
          {pillars.map((p) => {
            const score = report.pillar_scores_avg[p] || 5;
            const trend = report.pillar_trends[p] || "flat";
            const arrow = trend === "up" ? "↑" : trend === "down" ? "↓" : "→";
            const pillarConfig: Record<string, { icon: string; gradient: string; textColor: string; borderColor: string }> = {
              geist: { icon: '🧠', gradient: 'from-blue-50 to-indigo-100', textColor: 'text-blue-700', borderColor: 'border-blue-200/50' },
              herz: { icon: '❤️', gradient: 'from-rose-50 to-pink-100', textColor: 'text-rose-700', borderColor: 'border-rose-200/50' },
              seele: { icon: '✨', gradient: 'from-purple-50 to-violet-100', textColor: 'text-purple-700', borderColor: 'border-purple-200/50' },
              koerper: { icon: '💪', gradient: 'from-green-50 to-emerald-100', textColor: 'text-green-700', borderColor: 'border-green-200/50' },
              aura: { icon: '🌟', gradient: 'from-amber-50 to-yellow-100', textColor: 'text-amber-700', borderColor: 'border-amber-200/50' }
            };
            const config = pillarConfig[p] || pillarConfig['geist'];
            return (
              <div key={p} className={`bg-gradient-to-br ${config.gradient} rounded-2xl shadow-lg border ${config.borderColor} p-6 text-center hover:shadow-xl transition-all`}>
                <div className="text-3xl mb-2">{config.icon}</div>
                <div className={`text-3xl font-light ${config.textColor} mb-2`}>
                  {score} <span className="text-xl">{arrow}</span>
                </div>
                <div className="text-sm text-slate-600 font-light">{t(lang, `pillars.${p}`)}</div>
              </div>
            );
          })}
        </div>

        {chartData.length > 0 && (
          <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-2xl shadow-lg border border-indigo-200/50 p-8 mb-6">
            <div className="flex items-center gap-3 mb-5">
              <span className="text-3xl">📈</span>
              <h2 className="text-2xl font-light text-indigo-900">Trends (Last 7 Days)</h2>
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="date" stroke="#94a3b8" style={{ fontSize: '12px', fontWeight: 300 }} />
                <YAxis domain={[1, 10]} stroke="#94a3b8" style={{ fontSize: '12px', fontWeight: 300 }} />
                <Tooltip contentStyle={{ borderRadius: '12px', border: '1px solid #e2e8f0', fontWeight: 300 }} />
                <Legend wrapperStyle={{ fontSize: '14px', fontWeight: 300 }} />
                <Line type="monotone" dataKey="Geist" stroke="#8884d8" strokeWidth={2} />
                <Line type="monotone" dataKey="Herz" stroke="#82ca9d" strokeWidth={2} />
                <Line type="monotone" dataKey="Seele" stroke="#ffc658" strokeWidth={2} />
                <Line type="monotone" dataKey="Körper" stroke="#ff7c7c" strokeWidth={2} />
                <Line type="monotone" dataKey="Aura" stroke="#a28bfe" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}

        {report.summary && (
          <div className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-2xl shadow-lg border border-blue-200/50 p-8 mb-6">
            <div className="flex items-center gap-3 mb-4">
              <span className="text-3xl">📝</span>
              <h2 className="text-2xl font-light text-blue-900">Summary</h2>
            </div>
            <p className="text-blue-800 whitespace-pre-wrap font-light leading-relaxed">{report.summary}</p>
          </div>
        )}

        {report.daily_recommendation && (
          <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-2xl shadow-lg border border-green-200/50 p-8 mb-6">
            <div className="flex items-center gap-3 mb-4">
              <span className="text-3xl">🎯</span>
              <h2 className="text-2xl font-light text-green-900">Daily Recommendation</h2>
            </div>
            <p className="text-green-800 font-light leading-relaxed">{report.daily_recommendation}</p>
          </div>
        )}

        {report.weekly_goal && (
          <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-2xl shadow-lg border border-purple-200/50 p-8">
            <div className="flex items-center gap-3 mb-4">
              <span className="text-3xl">🎪</span>
              <h2 className="text-2xl font-light text-purple-900">Weekly Goal</h2>
            </div>
            <p className="text-purple-800 font-light leading-relaxed">{report.weekly_goal}</p>
          </div>
        )}
      </div>
    </div>
  );
}
