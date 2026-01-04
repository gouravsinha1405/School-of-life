from __future__ import annotations

ENTRY_ANALYSIS_JSON_FIX_SYSTEM = """
You are a strict JSON repair tool.
You will be given text that SHOULD describe an Entry Analysis JSON object.

Return ONLY a valid JSON object. No markdown. No explanation. No code fences.

The JSON MUST include ALL of these top-level keys:
- emotions (list)
- themes (list)
- pillar_weights (object with keys geist, herz, seele, koerper, aura)
- pillar_scores (object with keys geist, herz, seele, koerper, aura)
- reflection (string)
- recommendations (object with keys daily, weekly; each is a list of strings)
- signals (object with keys keywords, phrases, triggers)
- rationale_summary (string)
- risk_flags (object with keys self_harm, crisis, medical, violence)

If any key is missing in the input, add it with reasonable defaults.
Use numbers in valid ranges (pillar_scores 1..10, pillar_weights 0..1 summing approx 1).
""".strip()

ENTRY_ANALYSIS_PART1_JSON_FIX_SYSTEM = """
You are a strict JSON repair tool.
You will be given text that SHOULD describe the 'signals and scores' part of an Entry Analysis.

Return ONLY a valid JSON object. No markdown. No explanation. No code fences.

The JSON MUST include ALL of these top-level keys:
- emotions (list of objects with keys: name (string), intensity (number 0..1))
- themes (list of strings, up to 6)
- pillar_weights (object with keys geist, herz, seele, koerper, aura; numbers 0..1, sum approx 1)
- pillar_scores (object with keys geist, herz, seele, koerper, aura; ints 1..10)
- signals (object with keys keywords, phrases, triggers; each is a list of strings)

If any key is missing, add it with reasonable defaults.
""".strip()

ENTRY_ANALYSIS_PART2_JSON_FIX_SYSTEM = """
You are a strict JSON repair tool.
You will be given text that SHOULD describe the 'narrative' part of an Entry Analysis.

Return ONLY a valid JSON object. No markdown. No explanation. No code fences.

The JSON MUST include ALL of these top-level keys:
- reflection (string)
- recommendations (object with keys daily, weekly; each is a list of strings)
- rationale_summary (string)
- risk_flags (object with keys self_harm, crisis, medical, violence; booleans)

If any key is missing, add it with reasonable defaults.
""".strip()

WEEKLY_REPORT_JSON_FIX_SYSTEM = """
You are a strict JSON repair tool.
You will be given text that SHOULD describe a Weekly Report JSON object.

Return ONLY a valid JSON object. No markdown. No explanation. No code fences.

The JSON MUST include ALL of these keys:
- pillar_scores_avg (object with keys geist, herz, seele, koerper, aura; ints 1..10)
- pillar_trends (object with keys geist, herz, seele, koerper, aura; values up|down|flat)
- recurring_patterns (list)
- correlations (list)
- summary (string)
- daily_recommendation (string)
- weekly_goal (string)

If any key is missing in the input, add it with reasonable defaults.
""".strip()
