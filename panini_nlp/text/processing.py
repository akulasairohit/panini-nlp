"""
Text Processing Module (Varna-Vibhasha).

Decomposes Devanagari text into atomic Phonemes for the Sandhi Engine.
"""

from typing import List
from ..sounds import SYMBOL_MAP, MATRA_MAP, VIRAMA, A, Phoneme

def decompose(text: str) -> List[Phoneme]:
    """
    Decompose Devanagari text into atomic Phonemes.
    
    Handles:
    - Implicit 'a' after consonants
    - Matras (vowel signs) -> Full Vowels
    - Virama (halant) -> Suppresses 'a'
    - Anusvara/Visarga
    
    Args:
        text (str): Devanagari input string (e.g. "देवालय")
        
    Returns:
        List[Phoneme]: Stream of atomic sounds (e.g. [D, E, V, A, ...])
    """
    phonemes: List[Phoneme] = []
    i = 0
    n = len(text)
    
    while i < n:
        char = text[i]
        
        # 1. Is it a known symbol?
        if char not in SYMBOL_MAP:
             # Skip unknown chars (whitespaces, punctuation)
             # Future: Add Punctuation/Space as Tokens
             i += 1
             continue
             
        p = SYMBOL_MAP[char]
        
        # 2. Vowel (Swara)
        if p.is_vowel:
            phonemes.append(p)
            i += 1
            continue
            
        # 3. Consonant (Vyanjana) - excluding special modifiers
        if not p.is_vowel and p != VIRAMA:
            # Emit the consonant
            phonemes.append(p)
            
            # Look ahead for modifier
            if i + 1 < n:
                next_char = text[i+1]
                
                # Case A: Matra (Vowel Sign)
                if next_char in MATRA_MAP:
                    phonemes.append(MATRA_MAP[next_char])
                    i += 2
                    continue
                
                # Case B: Virama (Halant)
                elif next_char == VIRAMA.symbol:
                    # Do NOT emit 'a'. Consonant is bare.
                    i += 2
                    continue
            
            # Case C: No modifier -> Implicit 'a'
            # (Unless it's Anusvara/Visarga which follow vowels/consonants? 
            # Actually Anusvara follows vowel. 
            # If we have 'Kam', it is K + A + M_dot.
            # So if next is Anusvara, we still need the 'a' on the 'K'.)
            
            phonemes.append(A)
            i += 1
            continue
            
        # 4. Modifiers (should have been handled by lookahead, but if standalone...)
        # e.g. Anusvara or Visarga at start? Unlikely.
        # But Visarga usually follows a Vowel.
        # If we encounter them here, just append.
        phonemes.append(p)
        i += 1
        
    return phonemes

def recompose(phonemes: List[Phoneme]) -> str:
    """
    Recompose Phonemes back into Devanagari text.
    (Simple version for v0.2)
    """
    res = []
    for idx, p in enumerate(phonemes):
        # 1. Vowel
        if p.is_vowel:
            # Check previous
            if idx > 0 and not phonemes[idx-1].is_vowel and phonemes[idx-1] != VIRAMA:
                 # If previous was a consonant that didn't get a virama, 
                 # it means we are the vowel for it.
                 # Check if we are 'A' (implicit)
                 if p == A:
                     continue # Don't write anything
                 elif p.as_matra:
                     res.append(p.as_matra)
                 else:
                     res.append(p.symbol) # Fallback (should be matra)
            else:
                 # Independent vowel (start of word or after another vowel)
                 res.append(p.symbol)
        
        # 2. Consonant
        else:
            res.append(p.symbol)
            # If next is NOT a vowel and NOT a modifier, we might need a Virama?
            # Actually, standard logic: always write consonant.
            # If next is NOT a vowel, we assume implicit 'a' in script 
            # UNLESS we explicitly write Virama.
            # Wait, my logic is reverse.
            # In list: [K, T] -> K has no vowel. So we MUST write [K, Virama, T].
            
            if not p.is_vowel and p.symbol not in {"्", "ं", "ः"}:
                # Check next
                has_vowel_next = False
                if idx + 1 < len(phonemes):
                    if phonemes[idx+1].is_vowel:
                        has_vowel_next = True
                
                if not has_vowel_next:
                    # Consonant with no vowel following -> Needs Virama
                    res.append(VIRAMA.symbol)
                    
    return "".join(res)
