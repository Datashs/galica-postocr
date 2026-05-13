---
title: 'A Post-OCR Normalisation Pipeline for Historical French Corpora from Gallica'
tags:
  - Python
  - digital humanities
  - OCR post-correction
  - historical corpora
  - computational philology
  - French
authors:
  - name: Philippe Rygiel
    orcid: 0000-0002-5308-8961
    affiliation: 1
affiliations:
  - name: Équipe SEMIS, Inria
    index: 1
date: 10 May 2026
bibliography: paper.bib
---

# Summary

Plain-text OCR outputs from Gallica, the digital library of the Bibliothèque nationale de France (BnF), are widely used in historical research but often require substantial cleaning before they can be used for computational analysis. This pipeline provides a modular, fully auditable post-OCR normalisation workflow for 19th-century French historical corpora. It was developed on the *Annuaire de l'Institut de droit international* (1877, ~116,000 words) and is designed to be adapted to similar corpora. The repository includes documentation, example corpora, and reproducible command-line workflows.

The pipeline applies seventeen scripts in sequence, covering Unicode normalisation, typographic standardisation (apostrophes, dashes, ordinals, ligatures, punctuation spacing), semi-automatic correction of merged words and unknown forms, and probabilistic hapax correction using Damerau-Levenshtein distance. Each script is independently executable, produces a Markdown correction report, and documents its own false-positive rate. Human validation is built into scripts 15 and 16 as a deliberate design feature rather than a workaround.

# Statement of Need

Historical OCR errors in large corpora are numerous, systematic, and largely predictable. On a 116,000-word corpus, the pipeline applied here made approximately 5,000 targeted corrections. Leaving such errors uncorrected degrades the performance of downstream NLP tasks [@Chiron2017] and affects corpus-scale analysis in ways that are difficult to detect after the fact.

Existing approaches to post-OCR correction fall into three broad categories. Probabilistic and neural methods [@Evershed2014; @Lyu2021] as well as LLM-based approaches [@Levchenko2025] achieve high overall accuracy but operate as black boxes: the researcher cannot trace individual corrections, verify their validity, or audit false positives on a research corpus. Rule-based methods [@Pettersson2012; @Piotrowski2012] offer transparency but are designed for spelling normalisation across diachronic variation rather than for the typographic and encoding errors produced by modern OCR engines on 19th-century printed texts; moreover, existing tools are either language-agnostic — and therefore miss French-specific typographic conventions — or lack the explicit documentation of decisions and their rationale that philological work on research corpora requires. Corpus-based statistical approaches [@Reynaert2008] reduce OCR-induced variation through lexical distance matching but operate non-interactively, without exposing individual correction decisions to the researcher. This pipeline addresses a different need — not maximising correction throughput, but maintaining full philological control over every transformation applied to a corpus intended for publication. Existing OCR post-correction tools rarely expose false-positive accounting and human supervision regimes at the script level.

This pipeline takes a different approach, which might be termed **explicit computational philology**: every rule is documented in the source code with the cases it handles, the cases it does not, and the reasons why rules initially considered were ultimately excluded. The pipeline also deliberately refrains from delegating correction to a large language model: a convincing result is not a controlled result, and on a corpus intended for publication, what cannot be explained cannot be justified.

The software targets historians and digital humanities researchers working with Gallica plain-text OCR, particularly those processing serial corpora across multiple volumes where cumulative correction models (scripts 15–16) reduce redundant validation work. It is also designed as a teaching resource: doctoral students in history can read the scripts not only to run them, but to understand the epistemological choices behind each decision.

# Pipeline Architecture

The pipeline consists of four correction regimes of increasing uncertainty:

**Deterministic corrections (scripts 02–14)** handle errors with no known false positives on the development corpus: non-standard apostrophes, typographic dashes, control characters, space normalisation, malformed ordinals, month capitalisation, common abbreviations, punctuation spacing, run-together commas (filtered via the Lefff morphological lexicon [@Sagot2010]), garbled Roman numerals, bibliographic reference formatting, spurious quotation marks, and missing ligatures.

**Semi-automatic validation with learning (scripts 15–16)** addresses merged tokens (`ledroit` → `le droit`) and repeated unknown forms likely to be systematic OCR errors (`congrés` → `congrès`). Both scripts export TSV files for human review and persist validated decisions in JSON models that carry over across sessions and corpus volumes.

**Probabilistic correction (script 17)** applies Damerau-Levenshtein distance to hapaxes absent from the Lefff, distinguishing distance-1 corrections (applied automatically with ex-post audit) from distance-2 corrections (submitted to a global researcher decision after inspection of a representative sample).

This explicit formalisation of supervision regimes — deterministic, human-validated, probabilistic — reflects the view that different levels of algorithmic uncertainty warrant different levels of human oversight, and that this distinction should be made transparent rather than collapsed into a single automated step.

# Acknowledgements

The Lefff morphological lexicon [@Sagot2010] is central to scripts 10, 15, 16, and 17. The development corpus is drawn from Gallica (BnF), public domain.

# References
