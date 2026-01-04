"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { api } from "../../../lib/api";
import { t } from "../../../lib/i18n";

const stressReliefTips = {
  de: [
    "🌬️ Tiefes Atmen aktiviert Ihr parasympathisches Nervensystem und fördert Entspannung.",
    "🌿 Nur 5 Minuten in der Natur können Stress reduzieren und die Stimmung verbessern.",
    "💧 Ausreichend Wasser zu trinken hilft, Stress abzubauen und die kognitive Funktion zu verbessern.",
    "🎵 Musik zu hören kann den Cortisolspiegel senken und zur Entspannung beitragen.",
    "✍️ Tagebuch schreiben ist wissenschaftlich erwiesen, um Angst zu reduzieren und emotionale Klarheit zu fördern.",
    "🧘 Meditation für nur 10 Minuten täglich kann nachweislich Stress und Angst reduzieren.",
    "😊 Lächeln, auch erzwungen, kann Ihre Stimmung verbessern und Stress abbauen.",
    "🚶 Ein kurzer Spaziergang kann Endorphine freisetzen und Ihre Perspektive verändern.",
    "🤗 Soziale Verbindungen sind entscheidend für die psychische Gesundheit und den Stressabbau.",
    "🌙 Guter Schlaf ist grundlegend für emotionales Wohlbefinden und Stressbewältigung."
  ],
  en: [
    "🌬️ Deep breathing activates your parasympathetic nervous system, promoting relaxation.",
    "🌿 Just 5 minutes in nature can reduce stress and improve mood.",
    "💧 Staying hydrated helps reduce stress and improve cognitive function.",
    "🎵 Listening to music can lower cortisol levels and promote relaxation.",
    "✍️ Journaling is scientifically proven to reduce anxiety and promote emotional clarity.",
    "🧘 Meditating for just 10 minutes daily can measurably reduce stress and anxiety.",
    "😊 Smiling, even when forced, can improve your mood and reduce stress.",
    "🚶 A short walk can release endorphins and shift your perspective.",
    "🤗 Social connections are crucial for mental health and stress reduction.",
    "🌙 Quality sleep is fundamental for emotional well-being and stress management."
  ]
};

export default function EntryDetail() {
  const params = useParams();
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [lang, setLang] = useState<"de" | "en">("de");
  const [entry, setEntry] = useState<any>(null);
  const [analysis, setAnalysis] = useState<any>(null);
  const [analysisPending, setAnalysisPending] = useState(false);
  const [recomputing, setRecomputing] = useState(false);
  const [currentTipIndex, setCurrentTipIndex] = useState(0);

  useEffect(() => {
    let cancelled = false;
    let pollTimer: any = null;

    const run = async () => {
      try {
        const u = await api.getMe();
        if (cancelled) return;
        setUser(u);
        setLang(u.preferred_language || "de");

        const e = await api.getEntry(params.id as string);
        if (cancelled) return;
        setEntry(e);

        const first = await api.getEntryAnalysis(params.id as string);
        if (cancelled) return;
        setAnalysis(first);

        if (first) return;

        setAnalysisPending(true);

        let attempts = 0;
        pollTimer = setInterval(async () => {
          attempts += 1;
          try {
            const a = await api.getEntryAnalysis(params.id as string);
            if (cancelled) return;
            if (a) {
              setAnalysis(a);
              setAnalysisPending(false);
              clearInterval(pollTimer);
              pollTimer = null;
              return;
            }
          } catch {
            // keep polling a bit; transient backend errors shouldn't break UX
          }
          if (attempts >= 15) {
            setAnalysisPending(false);
            clearInterval(pollTimer);
            pollTimer = null;
          }
        }, 1000);
      } catch {
        router.push("/login");
      }
    };

    run();

    return () => {
      cancelled = true;
      if (pollTimer) clearInterval(pollTimer);
    };
  }, [params.id, router]);

  // Rotate tips while analysis is pending
  useEffect(() => {
    if (!analysisPending && !recomputing) return;
    
    const tipTimer = setInterval(() => {
      setCurrentTipIndex((prev) => (prev + 1) % stressReliefTips[lang].length);
    }, 4000);

    return () => clearInterval(tipTimer);
  }, [analysisPending, recomputing, lang]);

  if (!user || !entry) return <div className="min-h-screen flex items-center justify-center">{t(lang, "ui.loading")}</div>;

  const handleRecompute = async () => {
    try {
      setRecomputing(true);
      setAnalysisPending(true);
      const a = await api.recomputeEntryAnalysis(params.id as string);
      setAnalysis(a);
    } catch {
      // keep UX simple; existing analysis (even fallback) stays visible
      alert("Failed to recompute analysis");
    } finally {
      setRecomputing(false);
      setAnalysisPending(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-50 p-6 md:p-10">
      <div className="max-w-4xl mx-auto">
        <header className="mb-10 flex justify-between items-center">
          <h1 className="text-4xl font-light text-slate-700">{t(lang, "ui.entry")}</h1>
          <Link href="/journal" className="text-slate-500 hover:text-slate-700 transition-colors text-sm">
            {t(lang, "ui.back")}
          </Link>
        </header>

        <div className="bg-white/90 backdrop-blur rounded-2xl border border-slate-200/50 p-8 mb-6 shadow-sm">
          <p className="text-sm text-slate-400 mb-4 font-light">{new Date(entry.created_at).toLocaleString()}</p>
          <p className="text-slate-700 whitespace-pre-wrap mb-4 leading-relaxed">{entry.text}</p>
          <div className="flex gap-6 text-sm text-slate-500 font-light">
            <span>{t(lang, "mood")}: {entry.mood_score}</span>
            <span>{t(lang, "energy")}: {entry.energy_score}</span>
          </div>
        </div>

        <div className="mb-8">
          <button
            onClick={handleRecompute}
            disabled={recomputing || analysisPending}
            className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-8 py-3 rounded-full hover:from-purple-500 hover:to-pink-500 active:scale-95 transition-all font-light shadow-lg hover:shadow-xl disabled:opacity-60 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {recomputing ? (
              <>
                <span className="animate-spin">🔄</span>
                {t(lang, "analysis.recomputing")}
              </>
            ) : (
              <>
                <span>🔍</span>
                {t(lang, "analysis.recompute")}
              </>
            )}
          </button>
        </div>

        {(analysisPending || recomputing) && !analysis && (
          <div className="bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 rounded-3xl border border-purple-200/50 p-10 mb-6 shadow-lg">
            <div className="text-center mb-8">
              <div className="inline-block relative">
                <div className="w-20 h-20 border-4 border-purple-200 border-t-purple-600 rounded-full animate-spin"></div>
                <div className="absolute inset-0 flex items-center justify-center text-3xl">✨</div>
              </div>
              <h3 className="text-2xl font-light text-purple-900 mt-6 mb-2">
                {lang === "de" ? "Ihre Gedanken werden analysiert..." : "Analyzing your thoughts..."}
              </h3>
              <p className="text-sm text-purple-700 font-light">
                {lang === "de" ? "Bitte haben Sie einen Moment Geduld" : "Please wait a moment"}
              </p>
            </div>

            <div className="bg-white/60 backdrop-blur rounded-2xl p-6 border border-purple-200/30 min-h-[120px] flex items-center justify-center transition-all duration-500">
              <p className="text-center text-purple-800 text-lg font-light leading-relaxed animate-fade-in">
                {stressReliefTips[lang][currentTipIndex]}
              </p>
            </div>

            <div className="mt-6 flex justify-center gap-2">
              {stressReliefTips[lang].map((_, i) => (
                <div
                  key={i}
                  className={`h-2 rounded-full transition-all duration-300 ${
                    i === currentTipIndex ? "w-8 bg-purple-600" : "w-2 bg-purple-300"
                  }`}
                />
              ))}
            </div>
          </div>
        )}

        {!analysis && !analysisPending && !recomputing && (
          <div className="bg-gradient-to-br from-amber-50 to-orange-50 rounded-2xl border border-amber-200/50 p-8 shadow-sm">
            <div className="flex items-center gap-3 mb-3">
              <span className="text-3xl">⏳</span>
              <h3 className="text-xl font-light text-amber-900">{t(lang, "analysis.pending")}</h3>
            </div>
            <p className="text-amber-800 font-light">
              {lang === "de" 
                ? "Die Analyse wird gerade erstellt. Dies kann einige Momente dauern." 
                : "The analysis is being created. This may take a few moments."}
            </p>
          </div>
        )}

        {analysis && (
          <div className="space-y-5">
            <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl border border-blue-200/50 p-8 shadow-lg">
              <div className="flex items-center gap-3 mb-4">
                <span className="text-3xl">💭</span>
                <h2 className="text-2xl font-light text-blue-900">{t(lang, "ui.reflection")}</h2>
              </div>
              <p className="text-blue-800 whitespace-pre-wrap leading-relaxed">{analysis.reflection}</p>
            </div>

            <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-2xl border border-purple-200/50 p-8 shadow-lg">
              <div className="flex items-center gap-3 mb-5">
                <span className="text-3xl">📊</span>
                <h2 className="text-2xl font-light text-purple-900">{t(lang, "ui.pillarScores")}</h2>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-6">
                {Object.entries(analysis.pillar_scores).map(([k, v]: any) => {
                  const icons: Record<string, string> = { geist: '🧠', herz: '❤️', seele: '✨', koerper: '💪', aura: '🌟' };
                  const colors: Record<string, string> = { 
                    geist: 'text-blue-700', 
                    herz: 'text-rose-700', 
                    seele: 'text-purple-700', 
                    koerper: 'text-green-700', 
                    aura: 'text-amber-700' 
                  };
                  return (
                    <div key={k} className="text-center">
                      <div className="text-2xl mb-2">{icons[k]}</div>
                      <div className={`text-3xl font-light ${colors[k]} mb-1`}>{v}</div>
                      <div className="text-sm text-slate-600 font-light">{t(lang, `pillars.${k}`)}</div>
                    </div>
                  );
                })}
              </div>
            </div>

            {analysis.themes?.length > 0 && (
              <div className="bg-gradient-to-br from-teal-50 to-cyan-50 rounded-2xl border border-teal-200/50 p-8 shadow-lg">
                <div className="flex items-center gap-3 mb-4">
                  <span className="text-3xl">🏷️</span>
                  <h2 className="text-2xl font-light text-teal-900">{t(lang, "ui.themes")}</h2>
                </div>
                <div className="flex flex-wrap gap-2">
                  {analysis.themes.map((th: string, i: number) => (
                    <span key={i} className="bg-gradient-to-r from-teal-100 to-cyan-100 text-teal-700 px-4 py-2 rounded-full text-sm font-light border border-teal-200">
                      {th}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {analysis.emotions?.length > 0 && (
              <div className="bg-gradient-to-br from-rose-50 to-orange-50 rounded-2xl border border-rose-200/50 p-8 shadow-lg">
                <div className="flex items-center gap-3 mb-4">
                  <span className="text-3xl">😊</span>
                  <h2 className="text-2xl font-light text-rose-900">{t(lang, "ui.emotions")}</h2>
                </div>
                <div className="space-y-3">
                  {analysis.emotions.map((em: any, i: number) => (
                    <div key={i} className="flex items-center gap-4">
                      <span className="text-slate-600 font-light min-w-[120px]">{em.name}</span>
                      <div className="flex-1 bg-slate-100 rounded-full h-2">
                        <div
                          className="bg-slate-600 h-2 rounded-full transition-all"
                          style={{ width: `${em.intensity * 100}%` }}
                        />
                      </div>
                      <span className="text-xs text-slate-400 font-light min-w-[40px] text-right">{Math.round(em.intensity * 100)}%</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {(analysis.recommendations?.daily?.length > 0 || analysis.recommendations?.weekly?.length > 0) && (
              <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-2xl border border-green-200/50 p-8 shadow-lg">
                <div className="flex items-center gap-3 mb-4">
                  <span className="text-3xl">💡</span>
                  <h2 className="text-2xl font-light text-green-900">{t(lang, "ui.recommendations")}</h2>
                </div>
                {analysis.recommendations.daily?.length > 0 && (
                  <div className="mb-6">
                    <h3 className="font-light text-slate-600 mb-3 text-lg">{t(lang, "ui.daily")}</h3>
                    <ul className="space-y-2">
                      {analysis.recommendations.daily.map((r: string, i: number) => (
                        <li key={i} className="text-slate-600 font-light flex items-start gap-2">
                          <span className="text-slate-400 mt-1">•</span>
                          <span>{r}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                {analysis.recommendations.weekly?.length > 0 && (
                  <div>
                    <h3 className="font-light text-slate-600 mb-3 text-lg">{t(lang, "ui.weekly")}</h3>
                    <ul className="space-y-2">
                      {analysis.recommendations.weekly.map((r: string, i: number) => (
                        <li key={i} className="text-slate-600 font-light flex items-start gap-2">
                          <span className="text-slate-400 mt-1">•</span>
                          <span>{r}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-2xl border border-indigo-200/50 p-8 shadow-lg">
              <div className="flex items-center gap-3 mb-4">
                <span className="text-3xl">🔍</span>
                <h2 className="text-2xl font-light text-indigo-900">{t(lang, "ui.rationale")}</h2>
              </div>
              <p className="text-indigo-800 text-sm font-light leading-relaxed">{analysis.rationale_summary}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
