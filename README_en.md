# Post-OCR Pipeline for Historical Gallica Corpora

[DOI: 10.5281/zenodo.20112806](https://doi.org/10.5281/zenodo.20112806)


Post-OCR normalisation pipeline for 19th-century French historical corpora from Gallica.  
Developed on the *Annuaire de l'Institut de droit international* (1877), generalisable to any similar OCR corpus.  
Designed for reproducible processing of historical corpora, with explicit philological control and built-in human validation.

## Features

OCR normalisation ;  
auditable corrections ;  
tests ;  
human validation ;  
detailed reports.

## Why These Scripts

Texts retrieved from Gallica in plain-text format are often unusable directly for analysis. OCR produces systematic and predictable errors: non-standard apostrophes, varied typographic dashes, malformed ordinals, missing ligatures, merged punctuation, spurious quotation marks, garbled Roman numerals. On a corpus of 116,000 words, these errors amount to several thousand corrections to be made.

One could hand this cleaning task over to a large language model. We do not. Here is why.

**What an LLM does**: it produces a visually convincing result by making choices whose logic is opaque. You do not know exactly what it changed, why, or whether it introduced new errors while correcting others. On a corpus intended for research, this is unacceptable.

**What these scripts do**: each one does one precise, documented, verifiable thing. Every rule has been tested on the actual corpus. False positives have been counted and documented in the code. Rules that were too risky have been removed, with an explanation. The result is reproducible and auditable — every modification can be traced.

This is what might be called **explicit computational philology**: operations are visible, decisions are justified, limits are named.

This approach also has an explicit pedagogical dimension. These scripts are designed to be read as much as to be used. Every rule retained in the code is documented — with the cases it handles, the cases it does not handle, and the reasons why certain rules that were initially considered were abandoned. A student or doctoral researcher in history who opens `08_abrev.py` will find not only the code, but the explanation of why `par` → `par.` was removed (927 false positives, 0 true positives on the test corpus), why `cl` is not treated as an abbreviation (it is an OCR error for `et` in this corpus), and what this implies for decisions to be made on another corpus.

The point is not to learn Python. It is to learn to **work with one's material** — not to delegate technical choices to a tool whose decisions you do not understand, to document what you have done and why, to distinguish what you know from what you assume. These are the same requirements as source criticism, applied to digital tooling.

This approach is part of a broader reflection on what the training historians should look like in the age of large language models. The temptation is strong to hand over cleaning, extraction, and analysis to powerful and accessible tools — and the results are often visually convincing. But a convincing result is not a controlled result. On a corpus intended for research, the difference is essential: what you cannot explain, you cannot publish.

---

## What the Pipeline Does Not Claim to Do

- Correct all OCR errors — only those that are systematic and predictable
- Replace human proofreading
- Work without adjustment on any 19th-century corpus

Scripts 15 and 16 incorporate mandatory human validation at every cycle. This is not a design flaw — it is the moment when the historian's disciplinary judgement enters the loop, where no tool can replace it. Script 17 articulates two supervision modes (ex-post and ex-ante) depending on the Levenshtein distance value.

---

## Project Structure

```
PostOCR/
    scripts/                      ← normalisation scripts
        01Normalise.py
        02apost.py
        03tirets.py
        04_controle.py
        05_espaces.py
        06_ordinaux.py
        07_mois.py
        08_abrev.py
        09_ponctuation.py
        10_virgules.py
        11_romains.py
        12_refs.py
        13_guillemets.py
        14_ligatures.py
        15_decoupage.py
        16_inconnus.py
        17_levenshtein.py
        postocr.py                ← full pipeline (scripts 02–14)
      
        test_corpus.py            ← audit on a user corpus
        Lexiq/
            lefff_formes.txt      ← Lefff dictionary (to be downloaded separately)
    corpus/
        raw/                      ← raw Gallica OCR files
            mondoc.txt
        processed/                ← pipeline outputs
            
        rapports/                 ← modification reports (.md)
    modeles/                      ← learning models for scripts 15 and 16
        modele_decoupe.json
        modele_formes_inconnues.json
```

**Naming convention**: `YYYY_name.txt` for corpus files (e.g. `1877_jette.txt`).

---

## Dependencies

Python 3.8 or higher. No external libraries for scripts 02 to 14 — stdlib only.

Scripts 10, 15, and 16 require the **Lefff dictionary** (Lexique des Formes Fléchies du Français, approximately 110,000 entries). To be downloaded separately and placed in `scripts/Lexiq/lefff_formes.txt`.

Scripts 15 and 16 optionally accept **langid** for language detection on multilingual corpora.  
Script 17 requires **langid** to avoid a proliferation of false positives.

```bash
pip install langid
```

If langid is not installed, scripts 14, 15, and 16 fall back to heuristic-based alternatives.

---

## Usage

### Prerequisite — Validation and Audit on a User Corpus

The repository includes a `test_corpus.py` script for evaluating the behaviour of the pipeline on a user corpus. Defined from material with its own particular characteristics, it may be less useful in other contexts, or may require modifications.

#### Steps

```bash
python scripts/test_corpus.py corpus/raw/your_corpus.txt
```

For a detailed audit of the corrections applied:

```bash
python scripts/test_corpus.py corpus/raw/your_corpus.txt --audit
```

To limit the number of examples displayed:

```bash
python scripts/test_corpus.py corpus/raw/your_corpus.txt --audit --max 30
```

#### Functions

This script enables in particular:

- verification of the structural integrity of files;
- checking that paragraph breaks are preserved;
- inspection of corrections applied;
- identification of potentially problematic transformations;
- manual audit on a real corpus.

The goal is not to provide an exhaustive suite of unit tests, but a methodological evaluation tool adapted to the practices of digital humanities and the philological control of post-OCR corrections.

### Step 1 — 01Normalise.py — Unicode Normalisation

This script applies NFC Unicode normalisation to the entire corpus.

This step ensures consistent representation of accented characters, ligatures, and diacritics before post-OCR rules are applied.

It enables in particular:

- uniformisation of composite characters;
- stabilisation of regular expressions;
- consistency of lexical and statistical processing;
- reduction of ambiguities caused by OCR encoding.

This operation is a fundamental pre-processing step in the pipeline and must be run before all other scripts.

### Step 2 — Deterministic Corrections (Scripts 02–14)

### Orchestrator: `postocr.py`

Scripts can be run individually, or the orchestrator can be used instead.

It automatically applies the deterministic normalisation scripts (02 to 14, excluding the former script 10) to a plain-text corpus from Gallica or another historical OCR source.

The pipeline produces:

- a normalised text file;
- a Markdown report documenting the transformations applied;
- a summary of the number of corrections per step;
- contextualised examples of modifications.

Example:

```bash
python scripts/postocr.py corpus/raw/my_corpus.txt
```

With detailed report:

```bash
python scripts/postocr.py corpus/raw/my_corpus.txt --rapport
```

The pipeline applies the following steps in sequence:

| Step | Function |
|---|---|
| 01 | Unicode normalisation |
| 02–14 | Deterministic corrections |
| 15–16 | Semi-automatic manual validation |
| 17 | Probabilistic matching by lexical distance |

Scripts 15 and 16 are deliberately kept interactive in order to preserve philological control over ambiguous corrections.

### Step 3 — Interactive Validation (Scripts 15–16)

Script 15 detects words merged by OCR (`ledroit` → `le droit`) and proposes splits to validate.

```bash
python scripts/15_decoupage.py corpus/processed/1877_jette_postocr.txt
```

The script exports a TSV file to be validated in Numbers or Excel:
- `y` — correct split
- `n` — false positive, do not propose this word again
- `c` — incorrect split, enter the correct one in the `correction` column
- `?` — uncertain, will be proposed again in the next cycle

Press Enter once the file has been validated. Repeat until satisfied. The learning model is saved in `modeles/modele_decoupe.json` and persists between sessions.

Script 16 detects tokens absent from the Lefff that appear multiple times — likely systematic OCR errors (`congrés` → `congrès`).

```bash
python scripts/16_inconnus.py corpus/processed/1877_jette_postocr.txt
```

Same validation logic as script 15. For each form marked `y`, enter the correction in the `correction` column.

### Step 4 — Probabilistic Correction (Script 17)

Script 17 introduces a third correction regime based on Damerau-Levenshtein distance applied to hapaxes absent from the Lefff.

Unlike scripts 02–14 (deterministic rules) and scripts 15–16 (human validation case by case), this script distinguishes two levels of confidence:

- distance-1 corrections: applied automatically with ex-post audit;
- distance-2 corrections: submitted to a global decision by the researcher after inspection of a representative sample.

The script thus explicitly formalises different human supervision regimes according to the level of algorithmic uncertainty.

---

## Script Descriptions

| Script | Function | Corrections on jette (1877) | False positives |
|--------|----------|:---:|:---:|
| `test_corpus.py` | Corpus audit for pipeline testing | — | — |
| `postocr.py` | Pipeline orchestrator (scripts 02–14) | — | — |
| `01Normalise.py` | Unicode normalisation — **prerequisite for all processing** | — | — |
| `02apost.py` | Non-standard apostrophes → U+0027 | 0 | 0 |
| `03tirets.py` | Dashes U+2013/2014/2212 → ASCII dash | 2,841 | 0 |
| `04_controle.py` | Control characters, BOM | 1 | 0 |
| `05_espaces.py` | Multiple and special spaces | 0 | 0 |
| `06_ordinaux.py` | 1ere→1re, 2me→2e, 3me→3e… | 285 | 0 |
| `07_mois.py` | Month names with capital → lowercase | 107 | 0 |
| `08_abrev.py` | M→M., Dr→Dr., pp→pp., etc. | 113 | 0 |
| `09_ponctuation.py` | Spaces around :;!? | 1,217 | 0 |
| `10_virgules.py` | Run-together commas (Lefff filter) | ~45 | 0 |
| `11_romains.py` | Vil→VII, T. Il→T. II, T. Vit→T. VII | 12 | 0 |
| `12_refs.py` | T.VI→T. VI, pp.N→pp. N, et ss,→et ss. | 34 | 0 |
| `13_guillemets.py` | Spurious OCR straight quotation marks | 36 | 0 |
| `14_ligatures.py` | oeuvre→œuvre, voeu→vœu, coeur→cœur | 79 | 0 |
| `15_decoupage.py` | Merged words — interactive cycle | variable | ~25% |
| `16_inconnus.py` | Unknown forms — interactive cycle | variable | variable |
| `17_levenshtein.py` | Probabilistic hapax correction | variable | variable |

**Script 10**: requires the Lefff. Without the dictionary, returns the text unchanged with a warning.

**Scripts 15 and 16**: false positives are handled through human validation — the model learns not to propose them again.

---

## Technical Choices

### Why No General Rule for Commas (Script 09)

Script 09 handles double punctuation (`:;!?`), which follows uniform typographic rules in French. The comma was deliberately excluded: its exceptions are too numerous (decimal numbers, abbreviations, bibliographic lists). Script 10 handles the `word,word` case separately, using the Lefff as a safeguard.

### Why the Lefff Rather Than a Language Model

The Lefff is a reference lexicon: every entry has been verified. It does not make probabilistic generalisations. On a 19th-century corpus with foreign proper names (Rolin-Jaequemyns, Holtzendorff, Mancini), a language model would make assumptions that are difficult to control. The Lefff states exactly what it knows and nothing more.

### Why JSON Models Are Cumulative (Scripts 15 and 16)

Across forty similar volumes, OCR errors are often the same from one volume to the next. A cumulative model means that decisions made on the 1877 volume are applied automatically to subsequent ones — without revalidating what has already been processed.

### What Was Excluded and Why

- **Original script 10 (ellipsis points)**: permanently excluded — leader dots in tables and tables of contents would be destroyed.
- **æ ligature**: disabled — all instances of `ae` in the corpus are Flemish proper names (Jaequemyns ×40).
- **`par` → `par.`** as an abbreviation: 927 false positives on the test corpus, 0 true positives. Removed.
- **Correction of end-of-line word breaks**: requires human validation line by line — too heterogeneous to automate safely.

---

## Configurable Parameters

Each script exposes its adjustable parameters at the top of the file, before all other code. The main ones:

**`06_ordinaux.py`** — `roman=False` by default: Roman ordinals (XIXme) are not corrected without explicitly enabling this mode.

**`10_virgules.py`** — `MIN_LONGUEUR = 2`: minimum length of tokens processed. Additional rule: if both tokens are ≤ 2 characters simultaneously, the comma is not corrected (`de,la` remains unchanged).

**`15_decoupage.py`** — `SEUIL_MIN`, `LIMITE_EXPORT`, `NB_CYCLES_MAX`, `PREFIXE_SORTIE`.

**`16_inconnus.py`** — `SEUIL_MIN = 2`, `SEUIL_MAX = 10`: only forms appearing between 2 and 10 times are proposed. Below that: too much noise. Above: probably a domain-specific term.

---

## Development Corpus

*Annuaire de l'Institut de droit international*, first year, 1877.  
Source: Gallica BnF — plain-text OCR.  
763,276 characters, ~116,000 words, 4,920 paragraphs.

The Institut de droit international is a learned society founded in 1873, bringing together international jurists to codify international law. The Annuaire contains statutes, session proceedings, a chronological table of international events, treaty texts, and a bibliography. Its structure in five stable parts from one volume to the next makes the corpus particularly well-suited for generalisation across the forty volumes of the collection. For a study of the institution drawing on its annuals, see Rygiel, Philippe. *L'ordre des circulations? L'Institut de Droit international et la régulation des migrations (1870–1920)*. Éditions de la Sorbonne, 2021.

---

## Licence

Scripts: MIT.  
Gallica OCR corpus: public domain (documents prior to 1900).  
Lefff: LGPLLR licence — see the Lefff documentation.
