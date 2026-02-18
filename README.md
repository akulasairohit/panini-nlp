# Panini-NLP

**A Deterministic, Graph-based, Neuro-symbolic implementation of Pāṇini's Grammar.**

[![](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

`panini-nlp` is a Python library that decodes the **Aṣṭādhyāyī** not as a static text, but as a computable **Cyclic Directed Graph**. It provides the complete structural context of the grammar—every Sūtra and Dhātu—alongside deterministic engines for Sandhi, Prosody, and Phonetics.

---

## 🚀 Key Features

### 1. The Complete "Source Code"
Unlike other tools that implement only a few rules, `panini-nlp` contains the **Full Registry**:
- **3,996 Sūtras**: Every rule from the Aṣṭādhyāyī is present as a Python function stub in `panini_nlp/rules/`.
- **~2,000 Dhātus**: Every root from the Dhātupāṭha is registered in `panini_nlp/roots/`.
- **Maheshvara Sutras**: Implements the "Prime Number Architecture" (71.4% prime density) for phoneme compression.

### 2. Hybrid Neuro-Symbolic Architecture
- **Symbolic Core**: Deterministic engines for Sandhi (Euphonic Junction) and Chandas (Prosody).
- **Neural Guidance**: A Graph Neural Network (GNN) layer (`panini_nlp/gnn`) to resolve rule conflicts (Vipratisedha) by learning the graph topology.

### 3. "Seed Kernel" Efficiency
- The core logic fits in **< 50KB**.
- The entire structural knowledge base is generated from raw source texts.

---

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/meru-os/panini-nlp.git
cd panini-nlp

# Install mostly-pure Python core
pip install .

# Install with Neural Network support (PyTorch)
pip install .[gnn]
```

## 🛠️ Usage Examples

### 1. Deterministic Sandhi
Apply formal rules like *Akaḥ Savarṇe Dīrghaḥ* (6.1.101).

```python
from panini_nlp import SandhiEngine

sandhi = SandhiEngine()
result = sandhi.apply("dev", "alaya")
print(result) 
# Output: devālaya (Rule 6.1.101 applied)
```

### 2. Derivation Simulation (Prakriya)
Trace the path of a word through the grammar graph.

```python
# Run the included demo script
# python3 examples/derive_brahman.py

from panini_nlp.rules import registry as rule_registry

# Access Rule 1.1.1 (Growth Definitions)
rule = rule_registry.get("1.1.1")
print(f"{rule.id}: {rule.text}") 
# Output: 1.1.1: vṛddhir ādaic
```

### 3. Prosody Analysis (Chandas)
Analyze the binary rhythm of a verse (Laghu/Guru).

```python
from panini_nlp import ChandasAnalyzer

analyzer = ChandasAnalyzer()
meter = analyzer.analyze("dharmakṣetre kurukṣetre samavetā yuyutsavaḥ")
print(meter.pattern)
# Output: G L G G L G G G ... (Binary Stream)
```

---

## 📂 Project Structure

```text
panini-nlp/
├── panini_nlp/
│   ├── rules/          # 3996 Auto-generated Sutra stubs (Adhyaya 1-8)
│   ├── roots/          # ~2000 Auto-generated Root definitions (Gana 1-10)
│   ├── sandhi.py       # Deterministic Sandhi Engine
│   ├── chandas.py      # Pingala's Binary Prosody Algorithms
│   ├── maheshvara.py   # Prime Number Phonetic Analysis
│   ├── gnn/            # Graph Neural Network Models (PyTorch)
│   ├── data/           # Raw Source Texts (Ashtadhyayi.txt, Dhatupatha.txt)
│   └── validator.py    # Pipeline Orchestrator
├── examples/
│   ├── derive_brahman.py # Paper Example: Derivation of "Brahman"
│   └── derive_shuklam.py # Demo Example: "Shuklam Baradharam" analysis
├── requirements.txt
└── setup.py
```

## License

MIT License. Free for research and education.
