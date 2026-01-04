"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { api } from "../../lib/api";
import { t } from "../../lib/i18n";

export default function Journal() {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [lang, setLang] = useState<"de" | "en">("de");
  const [entries, setEntries] = useState<any[]>([]);
  const [day, setDay] = useState("");
  const [positive, setPositive] = useState("");
  const [negative, setNegative] = useState("");
  const [goals, setGoals] = useState("");
  const [stress, setStress] = useState(5);
  const [highlight, setHighlight] = useState("");
  const [lowpoint, setLowpoint] = useState("");
  const [text, setText] = useState("");
  const [mood, setMood] = useState(5);
  const [energy, setEnergy] = useState(5);
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api
      .getMe()
      .then((u) => {
        setUser(u);
        setLang(u.preferred_language || "de");
        return api.listEntries(20);
      })
      .then(setEntries)
      .catch(() => router.push("/login"));
  }, [router]);

  const handleSave = async () => {
    if (saving) return;
    setSaving(true);
    try {
      const parts: string[] = [];
      if (day.trim()) parts.push(`${t(lang, "intake.day")}: ${day.trim()}`);
      if (positive.trim()) parts.push(`${t(lang, "intake.positive")}: ${positive.trim()}`);
      if (negative.trim()) parts.push(`${t(lang, "intake.negative")}: ${negative.trim()}`);
      if (goals.trim()) parts.push(`${t(lang, "intake.goals")}: ${goals.trim()}`);
      parts.push(`${t(lang, "intake.stress")}: ${stress}`);
      if (highlight.trim()) parts.push(`${t(lang, "intake.highlight")}: ${highlight.trim()}`);
      if (lowpoint.trim()) parts.push(`${t(lang, "intake.lowpoint")}: ${lowpoint.trim()}`);
      if (text.trim()) parts.push(`${t(lang, "intake.freeText")}: ${text.trim()}`);

      const finalText = parts.join("\n");
      const created = await api.createEntry(finalText, mood, energy);

      setDay("");
      setPositive("");
      setNegative("");
      setGoals("");
      setStress(5);
      setHighlight("");
      setLowpoint("");
      setText("");
      setMood(5);
      setEnergy(5);
      setShowForm(false);

      // Navigate directly so the user immediately sees the (now synchronous) analysis.
      const entryId = created?.entry?.id;
      if (entryId) {
        router.push(`/journal/${entryId}`);
        return;
      }

      const updated = await api.listEntries(20);
      setEntries(updated);
    } catch (err) {
      alert("Failed to save entry");
    } finally {
      setSaving(false);
    }
  };

  if (!user) return <div className="min-h-screen flex items-center justify-center">{t(lang, "ui.loading")}</div>;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-50 p-6 md:p-10">
      <div className="max-w-4xl mx-auto">
        <header className="mb-10 flex justify-between items-center">
          <h1 className="text-4xl font-light text-slate-700">{t(lang, "journal")}</h1>
          <Link href="/" className="text-slate-500 hover:text-slate-700 transition-colors text-sm">
            {t(lang, "home")}
          </Link>
        </header>

        {!showForm && (
          <button
            onClick={() => setShowForm(true)}
            className="mb-8 bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-8 py-3 rounded-full hover:from-blue-500 hover:to-indigo-500 active:scale-95 transition-all font-light shadow-lg hover:shadow-xl flex items-center gap-2"
          >
            <span className="text-xl">✍️</span>
            {t(lang, "writeEntry")}
          </button>
        )}

        {showForm && (
          <div className="bg-white/90 backdrop-blur rounded-2xl shadow-sm border border-slate-200/50 p-8 mb-10">
            <div className="mb-6">
              <h2 className="text-2xl font-light text-slate-700 mb-2">{t(lang, "intake.heading")}</h2>
              <p className="text-sm text-slate-500 font-light">{t(lang, "intake.hint")}</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mb-5">
              <div>
                <label className="block text-sm font-light text-slate-600 mb-2">{t(lang, "intake.day")}</label>
                <textarea
                  value={day}
                  onChange={(e) => setDay(e.target.value)}
                  rows={3}
                  className="w-full border border-slate-200 rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-slate-300 focus:border-transparent transition-all"
                />
              </div>
              <div>
                <label className="block text-sm font-light text-slate-600 mb-2">{t(lang, "intake.positive")}</label>
                <textarea
                  value={positive}
                  onChange={(e) => setPositive(e.target.value)}
                  rows={3}
                  className="w-full border border-slate-200 rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-slate-300 focus:border-transparent transition-all"
                />
              </div>
              <div>
                <label className="block text-sm font-light text-slate-600 mb-2">{t(lang, "intake.negative")}</label>
                <textarea
                  value={negative}
                  onChange={(e) => setNegative(e.target.value)}
                  rows={3}
                  className="w-full border border-slate-200 rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-slate-300 focus:border-transparent transition-all"
                />
              </div>
              <div>
                <label className="block text-sm font-light text-slate-600 mb-2">{t(lang, "intake.goals")}</label>
                <textarea
                  value={goals}
                  onChange={(e) => setGoals(e.target.value)}
                  rows={3}
                  className="w-full border border-slate-200 rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-slate-300 focus:border-transparent transition-all"
                />
              </div>
            </div>

            <div className="mb-5">
              <label className="block text-sm font-light text-slate-600 mb-2">
                {t(lang, "intake.stress")}: {stress}
              </label>
              <input
                type="range"
                min="1"
                max="10"
                value={stress}
                onChange={(e) => setStress(Number(e.target.value))}
                className="w-full accent-slate-600"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mb-5">
              <div>
                <label className="block text-sm font-light text-slate-600 mb-2">{t(lang, "intake.highlight")}</label>
                <input
                  value={highlight}
                  onChange={(e) => setHighlight(e.target.value)}
                  className="w-full border border-slate-200 rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-slate-300 focus:border-transparent transition-all"
                />
              </div>
              <div>
                <label className="block text-sm font-light text-slate-600 mb-2">{t(lang, "intake.lowpoint")}</label>
                <input
                  value={lowpoint}
                  onChange={(e) => setLowpoint(e.target.value)}
                  className="w-full border border-slate-200 rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-slate-300 focus:border-transparent transition-all"
                />
              </div>
            </div>

            <label className="block text-sm font-light text-slate-600 mb-2">{t(lang, "intake.freeText")}</label>
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder={t(lang, "intake.freeTextPlaceholder")}
              rows={8}
              className="w-full border border-slate-200 rounded-xl p-3 mb-5 focus:outline-none focus:ring-2 focus:ring-slate-300 focus:border-transparent transition-all"
            />
            <div className="mb-5">
              <label className="block text-sm font-light text-slate-600 mb-2">
                {t(lang, "mood")}: {mood}
              </label>
              <input
                type="range"
                min="1"
                max="10"
                value={mood}
                onChange={(e) => setMood(Number(e.target.value))}
                className="w-full accent-slate-600"
              />
            </div>
            <div className="mb-6">
              <label className="block text-sm font-light text-slate-600 mb-2">
                {t(lang, "energy")}: {energy}
              </label>
              <input
                type="range"
                min="1"
                max="10"
                value={energy}
                onChange={(e) => setEnergy(Number(e.target.value))}
                className="w-full accent-slate-600"
              />
            </div>
            <div className="flex gap-4">
              <button 
                onClick={handleSave} 
                disabled={saving}
                className="bg-gradient-to-r from-green-600 to-emerald-600 text-white px-8 py-3 rounded-full hover:from-green-500 hover:to-emerald-500 active:scale-95 transition-all font-light shadow-lg hover:shadow-xl disabled:opacity-60 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {saving ? (
                  <>
                    <span className="animate-spin text-xl">🔄</span>
                    {lang === "de" ? "Speichern..." : "Saving..."}
                  </>
                ) : (
                  <>
                    <span className="text-xl">💾</span>
                    {t(lang, "intake.saveAndOpen")}
                  </>
                )}
              </button>
              <button
                onClick={() => setShowForm(false)}
                disabled={saving}
                className="bg-slate-100 text-slate-600 px-8 py-3 rounded-full hover:bg-slate-200 active:scale-95 transition-all font-light flex items-center gap-2 disabled:opacity-60 disabled:cursor-not-allowed"
              >
                <span className="text-xl">✕</span>
                {t(lang, "cancel")}
              </button>
            </div>
          </div>
        )}

        <div className="space-y-4">
          {entries.map((e) => (
            <Link
              key={e.id}
              href={`/journal/${e.id}`}
              className="block bg-white/80 backdrop-blur rounded-2xl border border-slate-200/50 p-6 hover:shadow-md transition-all"
            >
              <p className="text-sm text-slate-400 mb-3 font-light">{new Date(e.created_at).toLocaleString()}</p>
              <p className="text-slate-700 line-clamp-2 leading-relaxed">{e.text}</p>
              <div className="mt-3 text-xs text-slate-500 font-light">
                {t(lang, "mood")}: {e.mood_score} | {t(lang, "energy")}: {e.energy_score}
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
