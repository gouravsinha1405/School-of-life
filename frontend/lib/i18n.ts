export const translations = {
  de: {
    appName: "Lebensschule",
    home: "Start",
    journal: "Tagebuch",
    report: "Mein aktueller Stand",
    settings: "Einstellungen",
    login: "Anmelden",
    register: "Registrieren",
    logout: "Abmelden",
    email: "E-Mail",
    password: "Passwort",
    language: "Sprache",
    writeEntry: "Tagebuch schreiben",
    mood: "Stimmung",
    energy: "Energie",
    save: "Speichern",
    cancel: "Abbrechen",
    delete: "Löschen",
    export: "Exportieren",
    deleteAccount: "Konto löschen",
    pillars: {
      geist: "Geist",
      herz: "Herz",
      seele: "Seele",
      koerper: "Körper",
      aura: "Aura",
    },
    pillarDescriptions: {
      geist: "Klarheit in deinen Gedanken",
      herz: "Verbindung zu deinen Gefühlen",
      seele: "Sinn und innere Wahrheit",
      koerper: "Energie und Vitalität",
      aura: "Deine innere Balance",
    },

    welcome: {
      title: "Willkommen in der Lebensschule — dein Start zu mehr Klarheit und Freiheit",
      intro1:
        "Schön, dass du hier bist. Die Lebensschule begleitet dich Schritt für Schritt zu mehr Klarheit, Energie und Freude.",
      intro2:
        "Wir beginnen mit einer sorgfältigen Betrachtung deiner aktuellen Situation im Bereich Geist — denn mentale Klarheit bildet die Grundlage für alle weiteren Schritte.",
      intro3: "Danach schauen wir systematisch auf Seele, Herz, Körper und Aura.",
    },

    intake: {
      heading: "Erster kurzer Check-in",
      hint:
        "Wenn du magst, beantworte ein paar Fragen. Du kannst auch einfach frei schreiben — beides ist okay.",
      day: "Wie sieht ein normaler Tag bei dir aus?",
      positive: "Was war in letzter Zeit positiv?",
      negative: "Was war belastend / negativ?",
      goals: "Ziele & Erwartungen (optional)",
      stress: "Stress (1–10)",
      highlight: "Ein Highlight",
      lowpoint: "Ein Tiefpunkt",
      freeText: "Freitext",
      freeTextPlaceholder: "Schreibe, was gerade da ist — in deinem Tempo…",
      saveAndOpen: "Speichern & Analyse ansehen",
    },

    ui: {
      entry: "Eintrag",
      back: "Zurück",
      reflection: "Spiegel",
      pillarScores: "Dimensionen",
      themes: "Themen",
      emotions: "Gefühle",
      recommendations: "Sanfte Impulse",
      daily: "Täglich",
      weekly: "Wöchentlich",
      rationale: "Kurz erklärt",
      loading: "Lädt…",
      companionLine: "Ein ruhiger Begleiter für deinen Alltag",
    },

    analysis: {
      generating: "Analyse wird erstellt…",
      pending: "Analyse ausstehend…",
      recompute: "Neu analysieren",
      recomputing: "Analyse wird neu erstellt…",
    },
  },
  en: {
    appName: "Lebensschule",
    home: "Home",
    journal: "Journal",
    report: "My Current State",
    settings: "Settings",
    login: "Login",
    register: "Register",
    logout: "Logout",
    email: "Email",
    password: "Password",
    language: "Language",
    writeEntry: "Write Entry",
    mood: "Mood",
    energy: "Energy",
    save: "Save",
    cancel: "Cancel",
    delete: "Delete",
    export: "Export",
    deleteAccount: "Delete Account",
    pillars: {
      geist: "Mind",
      herz: "Heart",
      seele: "Soul",
      koerper: "Body",
      aura: "Energy",
    },
    pillarDescriptions: {
      geist: "Clarity in your thoughts",
      herz: "Connection to your feelings",
      seele: "Meaning and inner truth",
      koerper: "Energy and vitality",
      aura: "Your inner balance",
    },

    welcome: {
      title: "Welcome to the School of Life — your start to more clarity and freedom",
      intro1: "We’re glad you’re here. Lebensschule guides you step by step toward greater clarity, energy, and joy.",
      intro2:
        "We begin with a careful look at your current state in the Mind dimension — because mental clarity forms the foundation for further change.",
      intro3: "After that, we work through Soul, Heart, Body, and Aura.",
    },

    intake: {
      heading: "Quick first check-in",
      hint: "If you like, answer a few questions. You can also just write freely — both are okay.",
      day: "What does a normal day look like for you?",
      positive: "What has been positive lately?",
      negative: "What has felt heavy / negative?",
      goals: "Goals & expectations (optional)",
      stress: "Stress (1–10)",
      highlight: "One highlight",
      lowpoint: "One low point",
      freeText: "Free text",
      freeTextPlaceholder: "Write what’s here right now — at your pace…",
      saveAndOpen: "Save & view analysis",
    },

    ui: {
      entry: "Entry",
      back: "Back",
      reflection: "Reflection",
      pillarScores: "Dimensions",
      themes: "Themes",
      emotions: "Emotions",
      recommendations: "Gentle suggestions",
      daily: "Daily",
      weekly: "Weekly",
      rationale: "In short",
      loading: "Loading…",
      companionLine: "A calm companion for your day",
    },

    analysis: {
      generating: "Generating analysis…",
      pending: "Analysis pending…",
      recompute: "Re-analyze",
      recomputing: "Re-generating analysis…",
    },
  },
};

export type Language = keyof typeof translations;

export function t(lang: Language, key: string): string {
  const keys = key.split(".");
  let val: any = translations[lang];
  for (const k of keys) {
    val = val?.[k];
  }
  return val || key;
}
