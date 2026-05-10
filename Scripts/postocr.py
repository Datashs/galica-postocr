#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
===============================================================================
PIPELINE POST-OCR — postocr.py
===============================================================================

Description :
    Applique les 12 scripts de normalisation (02 à 14, sauf 10) en séquence
    sur un corpus texte brut issu de l'OCR Gallica.

    À la fin, produit :
      - mon_corpus_postocr.txt   : texte normalisé
      - mon_corpus_postocr.md    : rapport des modifications par script

Ordre des scripts :
    02  Apostrophes non standard   → U+0027
    03  Tirets typographiques      → tiret ASCII
    04  Caractères de contrôle     → suppression
    05  Espaces multiples/spéciaux → normalisation
    06  Ordinaux mal formés        → 1ere→1re, 2me→2e…
    07  Mois avec majuscule        → minuscule
    08  Abréviations sans point    → M.→M., Dr→Dr.…
    09  Ponctuation collée         → espaces :;!?
    11  Chiffres romains déformés  → Vil→VII, T. Il→T. II…
    12  Références bibliographiques → T.VI→T. VI, pp.N→pp. N…
    13  Guillemets droits parasites → In-8"→In-8°, "5→5…
    14  Ligatures manquantes        → oeuvre→œuvre, voeu→vœu…

    10  Virgules collées            → membres,les → membres, les

    Script 10 (points de suspension) : remplacé par 10_virgules.py
    L'ancien script 10 est exclu définitivement (tableaux/TDM).

    Scripts 15 (mots collés) et 16 (formes inconnues) 
    17 (traitement probabiliste des hapax) : cycles interactifs,
    à lancer manuellement après ce pipeline.

Dépendances :
    Les scripts doivent se trouver dans SCRIPTS_DIR (voir paramètre en tête).

Structure attendue :

    PostOCR/
        scripts/                  ← SCRIPTS_DIR, lancer depuis ici
            02apost.py … 16_inconnus.py
            postocr.py
            Lexiq/
                lefff_formes.txt
        corpus/
            raw/                  ← fichiers OCR Gallica bruts
                1877_jette.txt
            processed/            ← sorties de ce script
                1877_jette_postocr.txt
            rapports/             ← rapports .md produits par ce script
        modeles/                  ← modèles scripts 15 et 16

USAGE :
    python postocr.py mon_corpus.txt
    python postocr.py mon_corpus.txt --rapport            (rapport détaillé)
    python postocr.py mon_corpus.txt --max 30             (exemples par script)
    python postocr.py mon_corpus.txt -o mon_corpus_v2.txt (nom de sortie)

ARGUMENTS :
    CORPUS          Fichier texte à traiter (obligatoire)
    -o, --output    Fichier de sortie (défaut : CORPUS_postocr.txt)
    --rapport       Inclure les exemples de corrections dans le rapport
    --max N         Nombre max d'exemples par script dans le rapport (défaut 20)

FICHIERS PRODUITS :
    CORPUS_postocr.txt   Texte normalisé
    CORPUS_postocr.md    Rapport Markdown des modifications

ÉTAPES SUIVANTES (manuelles) :
    python 15_decoupage.py CORPUS_postocr.txt   # mots collés
    python 16_inconnus.py  CORPUS_postocr.txt   # formes inconnues

===============================================================================
"""

import re
import sys
import argparse
from pathlib import Path
from datetime import datetime


# =============================================================================
# PARAMÈTRES CONFIGURABLES
# =============================================================================

# Répertoire contenant les scripts 02apost.py … 14_ligatures.py
# Par défaut : même répertoire que ce fichier
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent

# Nombre maximum d'exemples de corrections affichés par script dans le rapport
MAX_EXEMPLES_DEFAUT = 20

# =============================================================================
# CHARGEMENT DES SCRIPTS
# =============================================================================

def charger_script(nom_fichier: str) -> dict:
    r"""Charge les fonctions d'un script sans exécuter son __main__."""
    chemin = SCRIPTS_DIR / nom_fichier
    if not chemin.exists():
        raise FileNotFoundError(f"Script introuvable : {chemin}")
    with open(chemin, encoding='utf-8') as f:
        src = f.read()
    ns = {}
    exec(src.split('def main')[0], ns)
    return ns


# =============================================================================
# COMPARAISON DE TEXTES
# =============================================================================

def trouver_differences(avant: str, apres: str, max_exemples: int = 20) -> tuple:
    r"""
    Compare deux textes token par token.
    Retourne (n_modifs, exemples) où exemples est une liste de
    (token_avant, token_apres, contexte, ligne).

    Utilise zip sur les tokens (séquences non-espace) — rapide et suffisant
    pour les scripts 02-14 qui ne créent pas de nouveaux tokens.
    Note : le comptage est approximatif pour les scripts 09 et 12 qui
    insèrent des espaces (effet de décalage dans le zip).
    """
    tokens_avant = list(re.finditer(r'\S+', avant))
    tokens_apres  = re.findall(r'\S+', apres)

    n_modifs  = 0
    exemples  = []

    for m_av, tb in zip(tokens_avant, tokens_apres):
        ta = m_av.group()
        if ta != tb:
            n_modifs += 1
            if len(exemples) < max_exemples:
                pos   = m_av.start()
                ligne = avant[:pos].count('\n') + 1
                ctx   = avant[max(0, pos - 25):pos + 25].replace('\n', '↵')
                exemples.append((ta, tb, ctx, ligne))

    n_modifs += abs(len(tokens_avant) - len(tokens_apres))
    return n_modifs, exemples


# =============================================================================
# PIPELINE
# =============================================================================

def construire_pipeline(ns: dict) -> list:
    r"""
    Retourne la liste ordonnée des étapes du pipeline.
    Chaque étape est (label, fonction_apply).
    La fonction_apply prend un texte et retourne (texte_corrigé, ...) ou texte.
    """

    def appliquer_09(texte):
        r1, _ = ns['09']['corriger_ponctuation'](texte)
        r2, _ = ns['09']['supprimer_espace_avant_virgule'](r1)
        r3, _ = ns['09']['corriger_point_colle'](r2)
        return r3

    return [
        ('02 Apostrophes',    lambda t: ns['02']['normalize_apostrophes'](t)),
        ('03 Tirets',         lambda t: ns['03']['normalize_tirets'](t)),
        ('04 Contrôle',       lambda t: ns['04']['clean_text'](t)),
        ('05 Espaces',        lambda t: ns['05']['normalize_all'](t)),
        ('06 Ordinaux',       lambda t: ns['06']['normalize_ordinaux'](t)),
        ('07 Mois',           lambda t: ns['07']['normalize_months'](t)),
        ('08 Abréviations',   lambda t: ns['08']['normalize_abbreviations'](t)),
        ('09 Ponctuation',    appliquer_09),
        ('11 Romains',        lambda t: ns['11']['corriger_romains'](t)),
        ('12 Refs biblio',    lambda t: ns['12']['normaliser_refs'](t)),
        ('13 Guillemets',     lambda t: ns['13']['corriger_guillemets'](t)),
        ('14 Ligatures',      lambda t: ns['14']['corriger_ligatures'](t)),
    ]


def appliquer_etape(label: str, texte: str, fn, max_exemples: int) -> tuple:
    r"""
    Applique une étape du pipeline et retourne
    (texte_après, n_modifs, exemples, erreur).
    En cas d'erreur, retourne le texte inchangé avec l'erreur documentée.
    """
    try:
        result = fn(texte)
        texte_apres = result[0] if isinstance(result, tuple) else result
    except Exception as e:
        return texte, 0, [], str(e)

    n_modifs, exemples = trouver_differences(texte, texte_apres, max_exemples)
    return texte_apres, n_modifs, exemples, None


# =============================================================================
# RAPPORT MARKDOWN
# =============================================================================

def generer_rapport(corpus_path: Path, sortie_path: Path,
                    resultats: list, texte_original: str,
                    texte_final: str, avec_exemples: bool,
                    duree: float) -> str:
    r"""
    Génère un rapport Markdown des modifications appliquées.

    resultats : liste de (label, n_modifs, exemples, erreur, paras_ok)
    """
    n_paras_av = len([p for p in texte_original.split('\n\n') if p.strip()])
    n_paras_ap = len([p for p in texte_final.split('\n\n') if p.strip()])
    n_total    = sum(r[1] for r in resultats if r[3] is None)
    n_erreurs  = sum(1 for r in resultats if r[3] is not None)

    lignes = [
        f"# Rapport post-OCR — {corpus_path.name}",
        f"",
        f"Date : {datetime.now().strftime('%d/%m/%Y %H:%M')}  ",
        f"Durée : {duree:.1f}s  ",
        f"Scripts : {SCRIPTS_DIR.resolve()}  ",
        f"",
        f"## Corpus",
        f"",
        f"| | Avant | Après |",
        f"|---|---:|---:|",
        f"| Caractères | {len(texte_original):,} | {len(texte_final):,} |",
        f"| Paragraphes | {n_paras_av:,} | {n_paras_ap:,} |",
        f"",
        f"## Résultats par script",
        f"",
        f"| Script | Tokens modifiés | Paragraphes | Statut |",
        f"|---|---:|:---:|:---|",
    ]

    for label, n_modifs, exemples, erreur, paras_ok in resultats:
        if erreur:
            statut = f"❌ `{erreur[:60]}`"
            lignes.append(f"| {label} | — | — | {statut} |")
        else:
            paras_str = "✅" if paras_ok else "⚠️ §"
            lignes.append(
                f"| {label} | {n_modifs:,} | {paras_str} | |"
            )

    lignes += [
        f"",
        f"**Total : {n_total:,} tokens modifiés"
        + (f", {n_erreurs} erreur(s)**" if n_erreurs else "**"),
        f"",
    ]

    if avec_exemples:
        lignes += [
            f"## Exemples de corrections",
            f"",
        ]
        for label, n_modifs, exemples, erreur, paras_ok in resultats:
            if erreur or not exemples:
                continue
            lignes += [
                f"### {label}",
                f"",
                f"| Ligne | Avant | Après | Contexte |",
                f"|---:|---|---|---|",
            ]
            for ta, tb, ctx, ligne in exemples:
                ctx_esc = ctx.replace('|', '\\|')
                lignes.append(
                    f"| {ligne} | `{ta}` | `{tb}` | {ctx_esc} |"
                )
            lignes.append("")

    lignes += [
        f"## Étapes suivantes (manuelles)",
        f"",
        f"```bash",
        f"python 15_decoupage.py {sortie_path.name}   # mots collés",
        f"python 16_inconnus.py  {sortie_path.name}   # formes inconnues",
        f"```",
        f"",
        f"*Script 10 (virgules) : nécessite lefff_formes.txt dans le répertoire.*  ",
        f"*Script 14 (ligature æ) : désactivée — noms flamands.*  ",
    ]

    return '\n'.join(lignes)


# =============================================================================
# POINT D'ENTRÉE
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Pipeline post-OCR — applique les scripts 02 à 14 (renumérotés),",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=r"""
Exemples :
  python postocr.py mon_corpus.txt
  python postocr.py mon_corpus.txt --rapport
  python postocr.py mon_corpus.txt --rapport --max 50
  python postocr.py mon_corpus.txt -o mon_corpus_v2.txt
        """
    )
    parser.add_argument('corpus', help="Fichier texte à traiter")
    parser.add_argument('-o', '--output', metavar='FICHIER',
                        help="Fichier de sortie (défaut : CORPUS_postocr.txt)")
    parser.add_argument('--rapport', action='store_true',
                        help="Inclure les exemples de corrections dans le rapport")
    parser.add_argument('--max', type=int, default=MAX_EXEMPLES_DEFAUT,
                        metavar='N',
                        help=f"Exemples max par script (défaut : {MAX_EXEMPLES_DEFAUT})")
    args = parser.parse_args()

    corpus_path = Path(args.corpus)
    if not corpus_path.exists():
        print(f"❌ Corpus introuvable : {corpus_path}")
        sys.exit(1)

    # Chemins de sortie
    if args.output:
        sortie_path = Path(args.output)
    else:
        # Sortie dans corpus/processed/ — créé automatiquement si absent
        sortie_path = Path('corpus/processed') / (corpus_path.stem + '_postocr.txt')
    rapport_dir = Path('corpus/rapports')
    rapport_dir.mkdir(parents=True, exist_ok=True)
    rapport_path = rapport_dir / (corpus_path.stem + '_postocr.md')

    # En-tête
    print("=" * 60)
    print("  PIPELINE POST-OCR")
    print("=" * 60)
    print(f"\n  Corpus  : {corpus_path.name}")
    print(f"  Sortie  : {sortie_path.name}")
    print(f"  Rapport : {rapport_path.name}")

    # Lecture
    with open(corpus_path, 'r', encoding='utf-8') as f:
        texte_original = f.read()

    n_paras = len([p for p in texte_original.split('\n\n') if p.strip()])
    print(f"\n  {len(texte_original):,} caractères — {n_paras} paragraphes")

    # Chargement des scripts
    print("\n  Chargement des scripts...", end=' ', flush=True)
    try:
        ns = {
            '02': charger_script('02apost.py'),
            '03': charger_script('03tirets.py'),
            '04': charger_script('04_controle.py'),
            '05': charger_script('05_espaces.py'),
            '06': charger_script('06_ordinaux.py'),
            '07': charger_script('07_mois.py'),
            '08': charger_script('08_abrev.py'),
            '09': charger_script('09_ponctuation.py'),
            '11': charger_script('11_romains.py'),
            '12': charger_script('12_refs.py'),
            '13': charger_script('13_guillemets.py'),
            '14': charger_script('14_ligatures.py'),
        }
        print("✅")
    except FileNotFoundError as e:
        print(f"\n❌ {e}")
        print("   Vérifier SCRIPTS_DIR en tête du script.")
        sys.exit(1)

    pipeline = construire_pipeline(ns)

    # Application des étapes
    print()
    print(f"  {'Script':<22} {'Tokens':>8}  Robustesse")
    print("  " + "─" * 50)

    t = texte_original
    resultats = []
    debut = datetime.now()

    for label, fn in pipeline:
        t_apres, n_modifs, exemples, erreur = appliquer_etape(
            label, t, fn, args.max
        )

        paras_av = len([p for p in t.split('\n\n') if p.strip()])
        paras_ap = len([p for p in t_apres.split('\n\n') if p.strip()])
        paras_ok = paras_av == paras_ap

        if erreur:
            print(f"  ❌ {label:<22}   ERREUR : {erreur[:40]}")
        elif n_modifs == 0:
            print(f"  ✅ {label:<22}   0 modification")
        else:
            para_note = '' if paras_ok else '  ⚠️  §'
            print(f"  ✅ {label:<22} {n_modifs:>6} token(s){para_note}")

        resultats.append((label, n_modifs, exemples, erreur, paras_ok))
        t = t_apres  # même en cas d'erreur on continue avec le texte inchangé

    duree = (datetime.now() - debut).total_seconds()

    # Résumé
    n_total   = sum(r[1] for r in resultats if r[3] is None)
    n_erreurs = sum(1 for r in resultats if r[3] is not None)
    n_paras_f = len([p for p in t.split('\n\n') if p.strip()])

    print()
    print("  " + "─" * 50)
    print(f"\n  Total corrections : {n_total:,} token(s)")
    print(f"  Paragraphes       : {n_paras} → {n_paras_f} "
          f"({'✅' if n_paras == n_paras_f else '⚠️ différence'})")
    if n_erreurs:
        print(f"  ⚠️  {n_erreurs} script(s) en erreur")
    print(f"  Durée             : {duree:.1f}s")

    # Écriture du corpus corrigé
    sortie_path.parent.mkdir(parents=True, exist_ok=True)
    with open(sortie_path, 'w', encoding='utf-8') as f:
        f.write(t)
    print(f"\n  ✅ Corpus corrigé  → {sortie_path}")

    # Écriture du rapport
    rapport = generer_rapport(
        corpus_path, sortie_path, resultats,
        texte_original, t, args.rapport, duree
    )
    with open(rapport_path, 'w', encoding='utf-8') as f:
        f.write(rapport)
    print(f"  ✅ Rapport         → {rapport_path}")

    # Rappel des étapes manuelles
    print()
    print("  Étapes suivantes (manuelles) :")
    print(f"    python 15_decoupage.py {sortie_path.name}")
    print(f"    python 16_inconnus.py  {sortie_path.name}")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
