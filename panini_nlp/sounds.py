"""
Sanskrit Phoneme Registry (Varnamala).

Defines atomic sounds and their properties for the Sandhi Engine.
"""

from dataclasses import dataclass
from typing import Dict, List, Set, Optional

@dataclass(frozen=True)
class Phoneme:
    symbol: str       # The atomic character (e.g., 'अ', 'क', '्')
    is_vowel: bool    # True if Swara (Ac)
    is_voiced: bool   # Ghosha
    place: str        # kantha, talu, murdha, danta, ostha, nasika
    as_matra: Optional[str] = None # The matra form if vowel (e.g., 'ा' for 'आ')

# ── Vowels (Swara / Ac) ──────────────────────────────────────────────────────
# Simple Vowels
A = Phoneme("अ", True, True, "kantha", "") 
AA = Phoneme("आ", True, True, "kantha", "ा")
I = Phoneme("इ", True, True, "talu", "ि")
II = Phoneme("ई", True, True, "talu", "ी")
U = Phoneme("उ", True, True, "ostha", "ु")
UU = Phoneme("ऊ", True, True, "ostha", "ू")
R = Phoneme("ऋ", True, True, "murdha", "ृ")
RR = Phoneme("ॠ", True, True, "murdha", "ॄ")
L = Phoneme("ऌ", True, True, "danta", "ॢ")

# Diphthongs
E = Phoneme("ए", True, True, "kantha-talu", "े")
AI = Phoneme("ऐ", True, True, "kantha-talu", "ै")
O = Phoneme("ओ", True, True, "kantha-ostha", "ो")
AU = Phoneme("औ", True, True, "kantha-ostha", "ौ")

# ── Consonants (Vyanjana / Hal) ──────────────────────────────────────────────
# Gutturals (Kavarga)
KA = Phoneme("क", False, False, "kantha")
KHA = Phoneme("ख", False, False, "kantha")
GA = Phoneme("ग", False, True, "kantha")
GHA = Phoneme("घ", False, True, "kantha")
NGA = Phoneme("ङ", False, True, "kantha")

# Palatals (Cavarga)
CA = Phoneme("च", False, False, "talu")
CHA = Phoneme("छ", False, False, "talu")
JA = Phoneme("ज", False, True, "talu")
JHA = Phoneme("झ", False, True, "talu")
NYA = Phoneme("ञ", False, True, "talu")

# Retroflex (Tavarga)
TA = Phoneme("ट", False, False, "murdha")
THA = Phoneme("ठ", False, False, "murdha")
DA = Phoneme("ड", False, True, "murdha")
DHA = Phoneme("ढ", False, True, "murdha")
NA = Phoneme("ण", False, True, "murdha")

# Dentals (Tavarga)
TA_D = Phoneme("त", False, False, "danta")
THA_D = Phoneme("थ", False, False, "danta")
DA_D = Phoneme("द", False, True, "danta")
DHA_D = Phoneme("ध", False, True, "danta")
NA_D = Phoneme("न", False, True, "danta")

# Labials (Pavarga)
PA = Phoneme("प", False, False, "ostha")
PHA = Phoneme("फ", False, False, "ostha")
BA = Phoneme("ब", False, True, "ostha")
BHA = Phoneme("भ", False, True, "ostha")
MA = Phoneme("म", False, True, "ostha")

# Semivowels (Antahstha)
YA = Phoneme("य", False, True, "talu")
RA = Phoneme("र", False, True, "murdha")
LA = Phoneme("ल", False, True, "danta")
VA = Phoneme("व", False, True, "danta-ostha")

# Sibilants (Usman)
SHA = Phoneme("श", False, False, "talu")
SSA = Phoneme("ष", False, False, "murdha")
SA = Phoneme("स", False, False, "danta")
HA = Phoneme("ह", False, True, "kantha")

# Modifiers
VIRAMA = Phoneme("्", False, False, "none")
ANUSVARA = Phoneme("ं", False, True, "nasika")
VISARGA = Phoneme("ः", False, False, "kantha")

# ── Registries ───────────────────────────────────────────────────────────────

# List of all phonemes
ALL_PHONEMES: List[Phoneme] = [
    A, AA, I, II, U, UU, R, RR, L, E, AI, O, AU,
    KA, KHA, GA, GHA, NGA,
    CA, CHA, JA, JHA, NYA,
    TA, THA, DA, DHA, NA,
    TA_D, THA_D, DA_D, DHA_D, NA_D,
    PA, PHA, BA, BHA, MA,
    YA, RA, LA, VA,
    SHA, SSA, SA, HA,
    VIRAMA, ANUSVARA, VISARGA
]

# Map: Symbol -> Phoneme
SYMBOL_MAP: Dict[str, Phoneme] = {p.symbol: p for p in ALL_PHONEMES}

# Map: Matra -> Independent Vowel (e.g., 'ा' -> 'आ')
MATRA_MAP: Dict[str, Phoneme] = {
    p.as_matra: p for p in ALL_PHONEMES 
    if p.is_vowel and p.as_matra
}

# Sets for quick lookup
AC = {p.symbol for p in ALL_PHONEMES if p.is_vowel}
HAL = {p.symbol for p in ALL_PHONEMES if not p.is_vowel and p != VIRAMA}
