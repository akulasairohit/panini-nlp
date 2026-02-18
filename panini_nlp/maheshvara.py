import math
from pathlib import Path

def is_prime(n):
    if n <= 1:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True

class MaheshvaraAnalyzer:
    def __init__(self, data_path="panini_nlp/data/Maheshvara_Sutras.txt"):
        self.data_path = Path(data_path)
        self.sutras = []
        if self.data_path.exists():
            self.load_sutras()
        else:
            # Fallback data if file missing
            self.sutras = [
                "अ इ उ ण्", "ऋ ऌ क्", "ए ओ ङ्", "ऐ औ च्", 
                "ह य व र ट्", "ल ण्", "ञ म ङ ण न म्", "झ भ ञ्", 
                "घ ढ ध ष्", "ज ब ग ड द श्", "ख फ छ ठ थ च ट त व्", 
                "क प य्", "श ष स र्", "ह ल्"
            ]

    def load_sutras(self):
        content = self.data_path.read_text(encoding="utf-8")
        # Parse lines like "१. अ इ उ ण् ।"
        for line in content.splitlines():
            line = line.strip()
            if not line: continue
            # Remove number "1. " and ending " ।"
            clean = line.split(".", 1)[-1].replace("।", "").strip()
            self.sutras.append(clean)

    def analyze(self):
        print(f"{'Sutra':<30} | {'Count':<5} | {'Type':<10}")
        print("-" * 50)
        
        primes = 0
        total = 0
        
        for s in self.sutras:
            # Phonemes are space separated. Last one is Anubandha (marker).
            # But in "a i u N", space separated "अ इ उ ण्"
            parts = s.split()
            # Count elements excluding the last one (halant marker)
            # Wait, paper says "a i u" = 3. 
            # "a i u N" has 4 parts. So count is len - 1.
            
            # Special handling if needed, but assuming space structure holds
            count = len(parts) - 1
            if count < 1: count = 0 # Safety
            
            p_status = "Prime" if is_prime(count) else "Non-Prime"
            if is_prime(count):
                primes += 1
            
            print(f"{s:<30} | {count:<5} | {p_status:<10}")
            total += 1
            
        print("-" * 50)
        percentage = (primes / total) * 100 if total > 0 else 0
        print(f"Total Sutras: {total}")
        print(f"Prime Counts: {primes}")
        print(f"Primal Density: {percentage:.1f}%")

if __name__ == "__main__":
    analyzer = MaheshvaraAnalyzer()
    analyzer.analyze()
