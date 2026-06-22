# Can We still thinker with LLMs?

Explicit Computational Philology: An OCR Post-Correction Pipeline for
Historical French Corpora

**Philippe Rygiel**\
SEMIS Team, Inria\
ORCID: 0000-0002-5308-8961

*Working paper --- presented at the Time Machine General Assembly "on
AI" in June 2026*\
Pipeline available at: <https://github.com/Datashs/galica-postocr>\
Archived version: <https://doi.org/10.5281/zenodo.20112806>

This project is part of a broader programme of experimentation intended to support the writing of a forthcoming overview article for Le Mouvement Social, provisionally entitled “History through the Lens of Artificial Intelligence: What Large Language Models Do to Historical Practice.” Related outputs produced within the same research programme are also available on Zenodo: Philippe Rygiel, Navigating Academia (2026, DOI: 10.5281/zenodo.20783423) and Philippe Rygiel, Augmenting Historians (2026, DOI 10.5281/zenodo.20122308.). 


## Abstract

This article describes an OCR post-correction pipeline developed for
19th-century French historical corpora available on Gallica, the digital
library of the Bibliothèque nationale de France. The pipeline was
developed on *the Annuaire de l'Institut de droit international* (1877,
\~116,000 words) and applies seventeen scripts in sequence, covering
Unicode normalization, typographic standardization, semi-automatic
correction of merged words and unknown forms, and probabilistic
correction of hapaxes using the Damerau-Levenshtein distance. The
article advocates an approach we call *explicit computational
philology*: rather than delegating correction to opaque models,
including large language models, the pipeline explicitly calibrates
human supervision to the level of algorithmic uncertainty at each stage.
The article also examines the role of annotated source code as a form of
philological protocol. It traces the complete trajectory of the work,
including the failures---a local LLM voting set that revealed a design
flaw, and a benchmark that exposed the extent of performance variations
between models---because these failures are as methodologically
instructive as the final solution.

**Keywords:** OCR post-correction, digital humanities, computational
philology, historical corpora, Gallica, French, large language models,
reproducible research

## 1. Introduction

Large-scale digitization projects such as Gallica, the digital library
of the Bibliothèque nationale de France, have made vast quantities of
19th- and early 20th-century printed sources available to historians.
The plain-text OCR outputs they provide are often used as the basis for
computational analysis, but are rarely usable as-is. The per-character
error rates produced by standard OCR engines applied to 19th-century
typography in particular are high enough to degrade the performance of
downstream NLP tasks (Strien, Beelen 2020), due to the persistence, at
the corpus level, of systematic noise that is difficult to detect, and
justify the development of specific post-correction methods for
historical sources (Chiron et al. 2017).

The solutions already proposed for this problem fall into two broad
categories, neither of which is fully satisfactory for researchers
working on corpora intended for publication. Probabilistic and neural
correction methods, including recent approaches based on LLMs (Evershed
and Fitch 2014; Lyu et al. 2021), achieve high overall accuracy but tend
to operate as black boxes. The researcher cannot trace individual
corrections, verify their validity, or audit false positives in a corpus
that will be cited, transcribed, and examined by other researchers.
Furthermore, the effectiveness of LLMs for correcting large historical
corpora is highly dependent on linguistic context and the properties of
the material (Karneva, Ledins 2025). Rule-based standardization tools
offer greater transparency, but are generally designed for orthographic
variation across diachronic registers rather than for typographical and
encoding errors produced by modern OCR engines on 19th- and early
20th-century printed texts (Pettersson 2012; Piotrowski 2012).
Furthermore, they are linguistically agnostic, and thus blind to
typographical conventions specific to French.

This article describes a third approach, developed as part of the
preparation of a study on the Yearbooks of the Institute of
International Law and other serial legal and statistical sources, the
combined body of which can feed into an information system useful for a
history of migration and mobility regulations in Europe. The approach
could be described as **explicit computational philology**: an OCR
post-correction pipeline in which each transformation is documented, and
each rule is accompanied by a record of the cases it handles and those
it deliberately does not handle. The level of human supervision is
explicitly calibrated to the level of algorithmic uncertainty involved
in each correction scheme.

The pipeline was not designed from the outset. It is the unexpected
byproduct of a series of failures that led to a change in tools and
perspective. The article first discusses this trajectory, because the
failures are methodologically instructive. It then describes the
architecture of the pipeline and revisits the role of annotated source
code as a form of philological protocol. This is a deliberate way of
making computational decisions accountable to the same requirements of
explicitness and justifiability as editorial decisions in historical
research.

Because code implements procedures connected to theories, it always
encodes an epistemology. Implementation choices reflect theories of the
material, theories of error, and theories of what counts as acceptable
evidence. Bowker and Star (1999) have shown, in a different context,
that classification systems encode values and theories of the world that
become all the more effective the more they go unnoticed. The pipeline
described here takes the opposite approach: making explicit what is
ordinarily latent, documenting what is ordinarily left unsaid, so that
the epistemology encoded in the code is legible, in the literal sense,
and remains open to challenge by the researcher using it, the peers
evaluating the resulting corpus, and the students, who are also invited
to read the code as one would read a critical apparatus.

Beyond the technical solution lies a broader question, one more specific
to our context. Can the researcher still practice, amidst LLMs, what
Fickers and van der Heijden (2020) call *"thinkering"*---the playful yet
critical experimentation with digital tools, a distant and digital echo
of bricolage---or has the age of engineers definitively arrived
(Lévi-Strauss 1962), turning the social scientist into a user of
generic, opaque, and disciplinarily indifferent solutions? Rather than
arbitrating between the lessons of this optimistic tradition and the
bleak prospects outlined by Jacques Ellul (Ellul 1954), this text---and
perhaps even more so the actual text that is the code of the constructed
pipeline---shows that today, in the context of historical work, this
commitment remains both possible and useful.

## 2. The Material and Its Constraints

The immediate context of this work is a research program devoted to the
regulation of mobility and migration in nineteenth-century Europe
(Rygiel 2021). Several serial sources available on Gallica are
invaluable in this regard: the *Annales des congrès internationaux de
statistique* (1853--1876), for their discussions on the definition and
measurement of demographic phenomena and the nomenclatures adopted, *the
Annuaire de l'Institut de droit international*, published beginning in
1877, for the Institute's deliberations on issues of international law,
particularly the legal status of foreigners and regulations governing
human mobility. Both sources have been digitized and are available in
plain text OCR format on Gallica but are not directly usable for
computational analysis.

Nineteenth-century statistical and legal publications are complex
typographical objects. They combine continuous prose, tables of varying
formats, hierarchical lists, marginal notes, and column headers
abbreviated according to conventions unrelated to those of contemporary
printed texts. OCR engines trained primarily on modern typography are
ill-equipped to handle these materials with precision, despite
significant progress.

Standard OCR applied to digitized images from these sources produces
results riddled with errors, the extent of which depends, among other
factors, on image quality and the date of digitization. Character
substitutions can be systematic: *l* and *t* are frequently confused in
certain fonts, and accented characters are altered according to
characteristic patterns. The OCR output also introduces structural
noise: merged tokens (*ledroit* for *le droit*), extraneous spaces
within words ( ), malformed ordinal numbers, and inconsistent
apostrophes and hyphens. In the corpus of *the Annuaire de l'Institut de
droit international* (approximately 116,000 words) on which this
pipeline was developed, these errors number in the thousands
(approximately 5,000).

It is possible to use *eScriptorium* or *Transkribus,* which have become
de facto standards for OCR/HTR processing of historical corpora.
However, their use entails either significant financial costs or access
to computing infrastructure and technical expertise. Above all, to
achieve truly effective post-correction, a considerable investment in
supervision and validation time is required.

While these tools certainly allow for the efficient delegation of a
large portion of the processing, they do not facilitate the
documentation of applied corrections on a decision-by-decision basis.
Yet in a multilingual corpus dense with abbreviations, legal terms, and
standardized statistical forms, OCR errors are concentrated precisely on
these elements of high analytical value: this is where an untraceable
correction is most likely to introduce silent biases. In this context,
it is not the overall accuracy score that matters, but philological
accountability.

Every transformation applied to the corpus must be documentable, every
decision must be justifiable, and the researcher must be able to explain
and defend each correction to the same standard that applies to any
other editorial decision regarding source editing.

## 3. A First Attempt: LLM Voting and What It Reveals

The initial approach to the problem was conceptually appealing. The idea
was simple: submit the noisy OCR output, segment by segment, to several
local LLMs and organize a vote. Each model proposed its own reading, and
the majority version was intended to be selected. If several independent
models converge on a reading, this convergence is a sign of reliability;
if they diverge, this divergence is a sign of documentable uncertainty.
The script is simple and runs smoothly; however, it takes twenty-four
hours to process seventy pages.

For a corpus of several hundred volumes, this can be considered a
concern. The experiment, however, reveals a more fundamental problem.
The request sent to the five models is structurally inconsistent. Since
the input file is highly noisy, the models do not segment the text in
the same way. The voting procedure assumes commensurable units across
models; the noisy input ensures that such commensurability does not
exist. The design flaw is evident.

The next step is to evaluate the comparative performance of five local
models on OCR correction tasks in order to determine a strategy. The
files generated by the LLMs are compared with a manually edited file
using three standard metrics: CER (*Character Error Rate*), WER ( ), and
the Levenshtein distance. The results across sixty-two segments are
unambiguous.

  ----------------------------------------------------
  Rank   Model          CER     WER      Levenshtein
  ------ -------------- ------- -------- -------------
  1      llama          0.161   0.873    79.5

  2      phi3           0.200   1.130    98.8

  3      mistral_nemo   0.210   1.161    103.6

  4      deepseek       3,929   25,179   1,937.4

  5      qwen3          6,915   44,577   3,415.6
  ----------------------------------------------------

*Table 1. OCR Benchmark --- Comparative performance of local LLM models
(CER and WER: lower values = better performance).*

The gap between the top three models and the bottom two spans two orders
of magnitude on CER and a factor of forty on Levenshtein distance. These
tools behave fundamentally differently in this context. The lesson is
clear: LLM performance varies considerably depending on the model, the
task, and the characteristics of the processed material. "Using an LLM"
is not a decision; it is the start of a complex testing process.

The best-performing model, llama, achieves a CER of 0.161. One in six
characters is incorrect. This is insufficient for semantic search or
automated text analysis. Worse still, under the conditions of this
experiment, each model produces an output that is more degraded,
according to these metrics, than the raw OCR output. Sending noisy OCR
to a local LLM, without prior training, does not improve the text: it
produces a different kind of degradation, one that is harder to
characterize and correct than the original degradation.

It is likely that 19th-century statistical and legal publications, with
their variable-format tables, their abbreviations that are not always
consistent, and their frequent font changes, are almost certainly
underrepresented in the training corpora of these models. The tool lacks
the contextual knowledge that would allow it to correct what it does not
recognize. Fluency and accuracy are not the same thing, and a model that
produces grammatically plausible French from degraded input does not
necessarily produce correct French, let alone an accurate edited text.

## 4. What the LLM can do: analyze errors rather than correct the text

The most useful result of this work emerged from a side experiment:
submitting a sample of the raw output from an OCR-extracted file to a
commercial LLM---not one from ---with the instruction not to correct the
text, but to identify common errors and analyze their structure.

It is not asked, therefore, to reconstruct a text it does not know, but
to describe patterns based on degraded data. The LLM, called upon as an
expert on the output rather than as a text corrector, produces an
analysis of recurring errors, which can be examined and validated---or
not---before writing deterministic post-correction scripts. These
implement explicit, testable, reproducible substitution rules that are
no longer probabilistic in nature.

The difference is significant. A correction generated by a language
model is a probabilistic output: it may be correct, it is generally
plausible, but it cannot be independently verified without a reference
text, and the reasoning behind it is not transparent. A substitution
rule derived from an analysis of error patterns can be read, tested,
challenged, and refined. It can be accompanied by documentation of the
cases it handles and those it does not. The false positive rate can be
measured.

The output is therefore not a text produced by a language model, but a
set of verifiable and documentable transformation rules that the model
helped formalize based on the observation of the material. Once the
rules are established, the correction process is independent of the
model that helped initiate it.

This distinction matters for a reason that goes beyond technical
reproducibility. In a corpus intended to feed an information system, or
for publication---which will be cited and used as evidence by other
researchers---a correction that cannot be explained cannot be justified.
The epistemological requirement for a research corpus is not fluidity
but traceability: the ability to reconstruct, for any given
transformation, the rule that produced it, the cases the rule was
intended to handle, and the cases it was meant to leave out.

This use of the LLM was not the intended outcome. It emerged from the
failure of the corrective approach. The lesson is not that LLMs are
useless for this work, but that their role is different from what was
initially imagined: they produce a signal, which still needs to be
interpreted and processed.

## 5. Pipeline Architecture: Supervision Calibrated for Uncertainty

The pipeline consists of seventeen scripts applied sequentially to the
OCR output in plain text. Its architecture reflects a deliberate stance
on the relationship between algorithmic uncertainty and human
supervision. The central principle is that different levels of
uncertainty warrant different levels of supervision, and that this
calibration must be made explicit rather than hidden in code.

The pipeline organizes its seventeen scripts into four correction
regimes of increasing uncertainty.

The first regime, covering scripts 02 through 14, handles
**deterministic corrections**. These are transformations with no known
false positives on the development corpus. This includes Unicode
normalization, non-standard apostrophes, typographic hyphens, control
characters, space normalization, malformed ordinals, capitalization of
months, common abbreviations, punctuation spacing, merged commas
filtered by the Lefff morphological lexicon (Sagot 2010), altered Roman
numerals, bibliographic reference formatting, stray quotation marks, and
missing ligatures. These scripts are applied automatically and without
supervision. The justification is not that no errors are possible, but
that the false positive rate on the development corpus is zero. This is
a local certainty, explicitly defined as such in the scripts'
documentation.

Script 11 provides an example of this logic. It corrects altered Roman
numerals and identifies 199 occurrences of "Il" in the corpus as
potentially erroneous readings of the Roman numeral II. But 196 of these
occurrences are the French subject pronoun. Correcting "Il" without
contextual constraints would produce 196 catastrophic false positives.
The script therefore applies the correction only in the three contexts
where the corpus guarantees that the reading is unambiguous: "T. Il"
(volume reference), "I. Il" (item reference), and "T. Vit" (where the
bibliographic context---volume number followed by a year---resolves the
ambiguity). Six corrections, zero false positives. The docstring states
this explicitly: *"the scripts in this pipeline always prioritize
precision over recall: it is better not to correct than to correct
incorrectly."*

The second approach (scripts 15 and 16) offers **semi-automatic
correction with cumulative learning**. Script 15 handles merged tokens
(*ledroit* → *le droit*); script 16 handles repeated unknown forms that
may represent systematic OCR errors (*congrés* → *congrès*). Both
scripts operate through a human validation cycle: candidate corrections
are exported to a TSV file, reviewed by the researcher in a spreadsheet,
and validated decisions are persisted in a JSON model that is carried
over from one session to another and from one volume to another within
the same serial corpus. The cumulative learning mechanism offers the
prospect that as the number of processed volumes increases, the number
of cases requiring validation will decrease: what has already been
decided is not resubmitted. Human supervision in this case is not a
workaround for an algorithmic weakness but a deliberate design feature
that reflects the irreducible ambiguity of certain correction decisions
and the necessity that these decisions be made by the researcher rather
than delegated to an algorithm.

The third regime, script 17, applies a Damerau-Levenshtein
distance-based **probabilistic correction** to hapax forms absent from
the Lefff. This script distinguishes between two sub-regimes with
different supervision protocols. Corrections at distance 1---where a
single operation transforms the hapax into a known lexical form, and
where this form is unique at that distance---are applied automatically.
The first 100 such corrections are exported to an audit log for post-hoc
verification. Distance 2 corrections are handled differently: a sample
is exported for review by the researcher, who makes a decision---to
apply or not to apply---based on the estimated error rate in the sample.
The script calculates and displays Wilson confidence intervals to
support this decision and allow it to be documented.

This four-tiered structure encodes a theory of correction
responsibility. The more uncertain the correction, the more the
researcher must be involved in the decision. Deterministic rules require
no involvement beyond the initial validation of the rule. Semi-automatic
corrections require case-by-case validation, gradually replaced by
accumulated decisions. Probabilistic corrections require a statistical
judgment applied to the population as a whole. The researcher is never
absent from the process, but the nature of their involvement is
calibrated to the epistemic situation.

The pipeline is designed for serial corpora. The cumulative learning
models in scripts 15 and 16 are explicitly delimited by corpus type
rather than by individual document. A model built on one volume of *the
Annuaire de l'Institut de droit international* applies to the next, with
a marginal validation cost that decreases across the series. This is not
merely a practical convenience: it reflects a philological reality.
Errors in a serial corpus produced by the same printer, using the same
fonts, and digitized by the same equipment, are not independent, and the
Yearbook has had the same publisher since its inception. The pipeline's
learning architecture is calibrated to account for this reality.

We suggest here that the most powerful generic tool is not necessarily
the most appropriate tool for a specific corpus, a specific research
environment, specific material characteristics, and specific scholarly
requirements. A solution built around the properties of the material may
be more functional than a generic solution, not because it is
technically superior, but because it is epistemically better suited to
the task. This should not be understood as a condemnation of the use of
this or that tool, this or that device, but rather as a plea for patient
work on the texture of one's material, allowing for an understanding of
the structure of the errors that affect it, before building or adapting
software that explicitly encodes this understanding. The flip side of
the coin is undoubtedly that the pipeline described here is not portable
and generic in the sense that an LLM is. It is, at most, an example of a
possible and locally productive strategy. Its architecture, calibration
logic, and supervision schemes can be adapted to other historical serial
corpora.

## 6. Annotated Code as a Philological Protocol

Epistemological commitments determine the architecture of the pipeline
but are also encoded in its source code, particularly in the comments
that appear there . We offer here a reading of excerpts from the code of
four scripts to show how their annotations function as a form of
philological protocol. They constitute a record of the decisions made,
the alternatives considered and rejected, and the reasoning leading to
the decision.

This is not standard software documentation practice, but rather the
making visible of the encoded logics and choices. The reader,
particularly the student, can understand *why* a rule was designed as it
was and what epistemological status to assign to its outputs. The
docstring thus becomes not a comment but an explication of the text that
is the code.

### Script 17: Two Epistemic Regimes

Script 17 explicitly names the epistemological difference between the
two correction modes it proposes:

    — At d=1 (one operation): A hapax not found in the Lefff at a distance of 1 from a known word is, in the vast majority of cases, an isolated OCR error. The uniqueness filter further ensures that only one word from the Lefff is at this distance —
     There is no ambiguity regarding the correction to apply.
     We are in a state of OPERATIONAL CERTAINTY: we act automatically and document the action in a log for post-hoc audit.

    — At d=2 (two operations):
      The number of words in the Lefff at a distance of 2 from a given token is
      much higher. The search space expands
      . We are in a PROBABILISTIC DECISION-MAKING regime:
      we cannot certify that every correction is correct; we can
      only estimate that the majority are.

The labels---*operational certainty* and *probabilistic decision*---are
not technical terms. They are epistemological characterizations. They
indicate to the researcher what type of assertion the script makes and
what type of responsibility it assumes by accepting its outputs. The
script then operationalizes this distinction through a concrete
supervision protocol: automatic application with an audit log for d=1,
sample inspection and global decision for d=2. It calculates and
displays Wilson confidence intervals to aid decision-making and allow
the researcher to document the estimated false positive rate in their
research log.

The transposition operation, which extends the standard Levenshtein
distance to capture character inversions, is handled in the same way.
The docstring notes that the gain on this corpus is marginal (about two
cases out of two thousand) but that the operation is implemented for the
sake of completeness. Implementation choices are thus documented and
justified.

### Script 16: Error theory encoded in the parameters

Script 16 handles repeated unknown forms, i.e., tokens absent from Lefff
that appear between a minimum and maximum frequency threshold. The
threshold values are configurable parameters, but their docstring makes
clear that their settings are not without effect and cannot be chosen
arbitrarily:

    MIN_THRESHOLD: minimum number of occurrences to flag a form (default: 2)
                Hapaxes (1 occurrence) are ignored — too much noise.
                A random OCR error does not repeat;
                a systematic error does.
    THRESHOLD_MAX: maximum occurrences (default: 10)
                Beyond that, the form is likely a recurring proper noun
                or a technical term in the domain, not an OCR error.

The minimum threshold encodes a theory of OCR errors: random errors do
not recur, systematic errors do. The maximum threshold encodes a theory
of the corpus: high-frequency unknown forms in a specialized legal
corpus are more likely to correspond to domain-specific vocabulary or
proper nouns than to errors. These are statements about the processed
material and are formulated as such. A researcher adapting the pipeline
to a different corpus can adjust these parameters based on the
properties of their material.

We have also attempted to document aspects of the code that may appear
purely technical, when in fact they stem from choices dictated by the
nature of the material or the specific effects of the functions being
called. This is the case, for instance, with the use of `langid` in the
context of scripts that strive as much as possible to avoid relying on
external libraries---in order to make the pipeline more stable, more
auditable, and more sustainable. The docstring notes that this language
identification library, used to filter out non-French tokens, is
unreliable for tokens shorter than eight characters. Its use on isolated
tokens is explicitly characterized as a heuristic rather than a source
of certainty. Some foreign-language tokens will slip through the filter
and thus appear in the audit sample. This limitation is known,
documented, and managed through human oversight rather than by an
additional automatic filter, whose reliability in this case would be
questionable.

### Script 15: Cumulative Learning and Philological Work Time

Script 15, which handles merged tokens, introduces a dimension absent
from the other two: the accumulation of validated decisions from one
session to the next and from one corpus volume to the next. The learning
model persists in a JSON file that is explicitly delimited by corpus
type:

    IMPORTANT — one model per corpus type:
      OCR errors vary by source and time period. A
      of press articles from the 1950s will not have the same merged tokens as a
      19th-century legal corpus. Use separate model files
      for corpora of different types.

This practical guideline reflects a philological reality: the structure
of errors in a serial corpus is a property of its material conditions of
production and digitization, not a generic property of the OCR output.

The practical consequence is evident in the validation data. On the
first volume processed, script 15 generated 47 candidate corrections,
all of which were validated by the researcher in a single pass. A
representative sample is presented in Table 2.

  ----------------------------------------
  Merged token   Suggestion     Decision
  -------------- -------------- ----------
  have elapsed   have elapsed   o

  maybe          maybe          o

  Estates        Estates        o
  General        General        

  minutes        minutes        o

  damages        damages        o
  ----------------------------------------

*Table 2. Excerpt from the TSV for validation of script 15, cycle 1 (47
cases, 0 refusals).*

The second run produced no new cases: the model had converged in a
single pass. On a second volume of the same series, these 47 decisions
will be applied automatically without human intervention. In this sense,
the JSON model is a form of expert memory: a structured repository of
philological decisions that can be inspected, challenged, and
transferred.

### Script 14: Disciplinary Knowledge Encoded in the Code

A final example illustrates a different dimension of the same practice.
Script 14 restores the French ligature œ (*oeuvre* → *œuvre*, *voeu* →
*vœu*, etc.)---79 corrections in the development corpus, zero false
positives. But the script also contains a rule that is documented and
deliberately disabled:

    Why NOT “ae” → “æ” in this corpus:
      A comprehensive analysis of the corpus reveals that all words containing
      “ae” are proper nouns, often Flemish and Dutch:
          Jaequemyns (×40), Portugael (×11), Disraeli (×4), Zachariae (×3)...
      These names DO NOT use the æ ligature—this is the correct spelling
      of these surnames (Rolin-Jaequemyns is one of the founders of
      the Institute).
      The æ rule is therefore disabled for this corpus.
      It is documented below for adaptation to other corpora.

Knowing that Rolin-Jaequemyns is one of the founders of the Institute of
International Law, and that his name does not use a ligature, is a
historical fact that has nothing to do with computation. Its presence in
the source code, as justification for a disabled rule, is a concrete
example of disciplinary expertise shaping algorithmic behavior.

### The script annotated as a methodological document

These annotations are not intended for a developer who needs to
understand the implementation, but for a historian who needs to
understand the epistemological commitments embedded in the tool they are
using. They document not only what the code does but what it asserts,
and what the researcher must contribute that the code cannot provide.
This practice has a precedent in the tradition of critical editing,
where apparatus and commentary serve precisely this function and make
visible the decisions that produced the text and the alternatives that
were considered and rejected. The annotated pipeline script is, in this
sense, a form of editorial apparatus for computational philological
work.

## 7. Conclusion

This article describes a winding path. Local LLM votes revealed a design
flaw. A benchmark exposed the extent of performance variations between
models and the inadequacy of raw LLM correction for degraded historical
material. A side experiment with a commercial LLM produced an analysis
of the error structure that enabled the drafting of deterministic
correction rules. The pipeline that emerged from this process applies
these rules within an architecture that explicitly calibrates human
supervision to algorithmic uncertainty, and documents each decision in
source code designed to be read as a methodological record as much as a
technical document. This is because, in the context of the research
conducted, it was necessary to preserve the ability to reconstruct and
justify the transformations applied to the text.

This requirement is difficult to meet if one relies on a system that
functions as a black box. It is satisfied, at least in principle, by a
pipeline in which every rule is documented, every supervision regime
explicitly calibrated, and the researcher's role defined---in a manner
appropriate to the level of uncertainty---at every stage of the
correction process.

This is what we have called explicit computational philology, which also
serves an educational function in a teaching context. The term is not
intended to distinguish traditional scholarship from computational
scholarship but to highlight the fact that certain computational methods
sacrifice disciplinary standards for the sake of efficiency. The
pipeline described here is undoubtedly slower and less immediately
generalizable than correction via an LLM. It requires more investment
from the researcher, though not necessarily more time if one takes into
account the demands of fine-tuning. It also has the advantage of
producing a corpus whose quality can be characterized, whose corrections
can be traced, and whose error profile can be defined, thereby
attempting to meet the requirements of scholarly editing.

Two conclusions can be drawn from the experiment. Relying on the most
powerful and generic tool available is an understandable decision but
not always optimal when the material has very specific properties. The
most appropriate response may then be to understand the structure of the
problem in order to tailor an ad hoc processing method to it.

This amounts to considering that digital tinkering (Rygiel 2017) or
*thinkering* (Fickers and van der Heijden 2020) can still have not only
meaning but practical utility and enable the construction of a tool that
encodes disciplinary knowledge, reflects on its own limitations, and
remains consistent with the epistemological requirements of the field.
At the very least, this remains conceivable and possible even in an
environment where increasingly powerful generic tools are emerging.

The pipeline is available as open-source software, along with complete
documentation and the development corpus, at
<https://github.com/Datashs/galica-postocr>. An archived version with a
persistent identifier is available on Zenodo at
<https://doi.org/10.5281/zenodo.20112806>. Researchers working on
similar corpora are invited to adapt the pipeline to their own data; a
dedicated script is available to evaluate its performance on the target
corpus.

## References



Bowker, Geoffrey C., and Susan Leigh Star. 1999. *Sorting Things Out: Classification and Its Consequences*. Cambridge, MA: MIT Press.

Chiron, Guillaume, Aurelie Levcopoulos, Bertrand Coüasnon, and Alexis Viard. 2017. "Tools for OCR Post-Correction." In *Proceedings of the 5th International Workshop on Historical Document Imaging and Processing*, 78–83.

Ellul, Jacques. 1954. *La Technique ou l'enjeu du siècle*. Paris: Armand Colin.

Evershed, Jonathan, and Kent Fitch. 2014. "Correcting OCR Errors in Historic Digitized Newspapers." In *Proceedings of the Australasian Language Technology Association Workshop*, 19–27.

Fickers, Andreas, and Tim van der Heijden. 2020. "Inside the Trading Zone: Thinkering in a Digital History Lab." *Digital Humanities Quarterly* 14 (3). <http://dhq.digitalhumanities.org/vol/14/3/000472/000472.html>

Kanerva, Jenna, Cassandra Ledins, Siiri Käpyaho, and Filip Ginter. 2025. "OCR Error Post-Correction with LLMs in Historical Documents: No Free Lunches." In *Proceedings of the Third Workshop on Resources and Representations for Under-Resourced Languages and Domains (RESOURCEFUL-2025)*, 38–47. Tallinn: University of Tartu Library. <https://aclanthology.org/2025.resourceful-1.8/>

Lévi-Strauss, Claude. 1962. *La Pensée sauvage*. Paris: Plon.

Lyu, Lijun, Maria Koutraki, Martin Krickl, and Besnik Fetahu. 2021. "Neural OCR Post-Hoc Correction of Historical Corpora." *Transactions of the Association for Computational Linguistics* 9: 479–493. <https://aclanthology.org/2021.tacl-1.29/>

Pettersson, Eva. 2012. "Spelling Normalization and Linguistic Analysis of Historical Text for Information Extraction." Ph.D. dissertation, Uppsala University.

Piotrowski, Michael. 2012. *Natural Language Processing for Historical Texts*. San Rafael: Morgan & Claypool.

Rygiel, Philippe. 2017. *Historien à l'âge numérique*. Villeurbanne: Presses de l'ENSSIB.

Rygiel, Philippe. 2021. *L'ordre des circulations ? L'Institut de droit international et la régulation des migrations (1870–1920)*. Paris: Éditions de la Sorbonne.

Sagot, Benoît. 2010. "The Lefff, a Freely Available and Large-Coverage Morphological and Syntactic Lexicon for French." In *Proceedings of the 7th International Conference on Language Resources and Evaluation*, 2744–2751.

van Strien, Daniel, Kaspar Beelen, Mariona Coll Ardanuy, Kasra Hosseini, Barbara McGillivray, and Giovanni Colavizza. 2020. "Assessing the Impact of OCR Quality on Downstream NLP Tasks." In *Proceedings of the 12th International Conference on Agents and Artificial Intelligence*, 484–496. <https://doi.org/10.17863/CAM.52068>

