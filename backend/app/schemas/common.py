from __future__ import annotations

from enum import Enum


class Language(str, Enum):
    de = "de"
    en = "en"


PILLARS = ("geist", "herz", "seele", "koerper", "aura")
