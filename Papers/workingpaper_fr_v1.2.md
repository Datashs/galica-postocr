# Peut on hacker au temps des LLMs?
Philologie computationnelle explicite : un pipeline de post-correction OCR pour les corpus historiques français

**Philippe Rygiel**  
Équipe SEMIS, Inria  
ORCID: 0000-0002-5308-8961

*Working paper — présenté assemblée génrale Time Machine "autour de l'IA" juin 2026*  
Pipeline disponible à : <https://github.com/Datashs/galica-postocr>  
Version archivée : <https://doi.org/10.5281/zenodo.20112806>

Ce projet s’inscrit dans une série d’expérimentations destinée à nourrir l’écriture d’un texte de synthèse à paraître pour le Mouvement Social (“L’histoire au révélateur de l’intelligence artificielle. Ce que les grands modèles de langue font aux pratiques historiennes”) à paraître. Les autres éléments développés à l’occasion de ce chantier sont également disponibles sur Github : Rygiel, Philippe. Navigating Academia. Zenodo, 2026. 10.5281/zenodo.20783423. et Rygiel, Philippe. 2026. Augmenting Historians, 10.5281/zenodo.20122308. 

---

## Résumé

Cet article décrit un pipeline de post-correction OCR développé pour les corpus historiques français du XIXe siècle disponibles sur Gallica, la bibliothèque numérique de la Bibliothèque nationale de France. Le pipeline a été développé sur l'*Annuaire de l'Institut de droit international* (1877, ~116 000 mots) et applique dix-sept scripts en séquence, couvrant la normalisation Unicode, la standardisation typographique, la correction semi-automatique des mots fusionnés et des formes inconnues, et la correction probabiliste des hapax par distance de Damerau-Levenshtein. L'article défend une approche que nous appelons *philologie computationnelle explicite* : plutôt que de déléguer la correction à des modèles opaques, y compris des grands modèles de langue, le pipeline calibre explicitement la supervision humaine au niveau d'incertitude algorithmique de chaque étape. L'article examine également le rôle du code source annoté comme forme de protocole philologique. Il suit la trajectoire complète du travail, y compris les échecs — un ensemble de vote de LLM locaux qui a révélé une erreur de conception, et un benchmark qui a exposé l'ampleur des variations de performance entre modèles — parce que ces échecs sont aussi instructifs sur le plan méthodologique que la solution finale.

**Mots-clés :** post-correction OCR, humanités numériques, philologie computationnelle, corpus historiques, Gallica, français, grands modèles de langue, recherche reproductible

---

## 1. Introduction

Les programmes de numérisation à grande échelle comme Gallica, la bibliothèque numérique de la Bibliothèque nationale de France, ont mis à la disposition des historiens de vastes quantités de sources imprimées du XIXe siècle et du début du XXe siècle. Les sorties OCR en texte brut qu'ils proposent sont souvent utilisées comme base d'analyse computationnelle, mais sont rarement utilisables telles quelles. Les taux d'erreur caractère produits par les moteurs OCR standard appliqués à la typographie du XIXe siècle en particulier sont suffisamment élevés pour dégrader les performances des tâches TAL en aval (Strien, Beelen 2020), du fait de la persistance, à l'échelle du corpus, de bruits systématiques difficiles à détecter, et justifient le dévelopement de méthodes spécifiques de post-correction pour les sources historiques (Chiron et al. 2017).

Les réponses déjà formulées à ce problème se répartissent en deux grandes catégories, aucune n'étant pleinement satisfaisante pour les chercheurs travaillant sur des corpus destinés à la publication. Les méthodes de correction probabilistes et neuronales, y compris les approches récentes fondées sur les LLM (Evershed et Fitch 2014 ; Lyu et al. 2021) atteignent une précision globale élevée, mais tendent à opérer comme des boîtes noires. Le chercheur ne peut pas tracer les corrections individuelles, vérifier leur validité, ni auditer les faux positifs sur un corpus qui sera cité, transcrit et examiné par d'autres chercheurs. De plus l'efficacité des LLms pour la correction de corpus historiques de grande taille est très fortement dépendante du contexte linguistique et des propriétés du matériaux (Karneva, Ledins 2025). Les outils de normalisation fondés sur des règles offrent plus de transparence, mais sont généralement conçus pour la variation orthographique à travers les registres diachroniques plutôt que pour les erreurs typographiques et d'encodage produites par les moteurs OCR modernes sur des textes imprimés du XIXe siècle et du début du XXe siècle (Pettersson 2012 ; Piotrowski 2012). Ils sont en outre soit agnostiques sur le plan linguistique, donc aveugles aux conventions typographiques propres au français.


Cet article décrit une troisième approche, développée dans le cadre de la préparation d'un travail autour des Annuaires de l'Institut de droit international, et d'autres sources juridiques et statistiques sérielles dont l'ensemble peut nourrir un système d'information utile à une histoire des régulations des migrations et de la mobilité en Europe. L'approche pourrait être qualifiée de **philologie computationnelle explicite** : un pipeline de post-correction OCR dans lequel chaque transformation est documentée, chaque règle est accompagnée d'un compte rendu des cas qu'elle traite et de ceux qu'elle ne traite délibérément pas. Le niveau de supervision humaine y est calibré explicitement au niveau d'incertitude algorithmique impliqué dans chaque régime de correction.

Le pipeline n'a pas été conçu d'emblée. Il est le sous-produit inattendu d'une série d'échecs qui ont conduit à changer d'outillage et de perspective. L'article évoque d'abord cette trajectoire, parce que les échecs sont méthodologiquement instructifs. Il décrit ensuite l'architecture du pipeline et revient sur le rôle du code source annoté comme forme de protocole philologique. C'est là une manière délibérée de rendre les décisions computationnelles comptables des mêmes exigences d'explicitation et de justifiabilité que les décisions éditoriales de la recherche historique.

Le code, parce qu'il met en œuvre des procédures connectées à des théories, encode toujours une épistémologie. Les choix d'implémentation reflètent des théories du matériau, des théories de l'erreur, des théories de ce qui compte comme preuve acceptable. Bowker et Star (1999) ont montré, dans un contexte différent, que les systèmes de classification encodent des valeurs et des théories du monde qui deviennent d'autant plus efficaces qu'elles se font oublier. Le pipeline décrit ici prend le parti inverse : rendre explicite ce qui est ordinairement latent, documenter ce qui est ordinairement tu, de façon que l'épistémologie encodée dans le code soit lisible, au sens propre, et reste contestable par le chercheur qui l'utilise, les pairs qui évaluent le corpus produit, et les étudiants aussi invités à lire le code comme on lit un apparat critique.

Au-delà de la solution technique se trouve une question plus large, plus propre à notre contexte. Le chercheur peut-il encore pratiquer au milieu des LLM ce que Fickers et van der Heijden (2020) appellent le *thinkering* — l'expérimentation ludique mais critique des outils numériques, écho lointain et numérique du bricolage — ou bien le temps des ingénieurs est-il définitivement advenu (Lévi-Strauss 1962), faisant du chercheur en sciences sociales l'utilisateur de solutions génériques, opaques et disciplinairement indifférentes ? Plutôt que d'arbitrer entre les enseignements de cette tradition optimiste et les sombres perspectives dessinées par Jacques Ellul (Ellul 1954), ce texte, et peut-être plus encore le texte véritable qu'est le code du pipeline construit, conduit à montrer qu'aujourd'hui, dans le contexte d'un travail historien, cet engagement reste à la fois possible et utile.

---

## 2. Le matériau et ses contraintes

Le contexte immédiat de ce travail est un programme de recherche consacré à la régulation des mobilités et des migrations dans l'Europe du XIXe siècle (Rygiel 2021). Plusieurs sources sérielles disponibles sur Gallica sont dans cette perspective précieuses : les *Annales des congrès internationaux de statistique* (1853–1876) par leurs débats sur la définition et la mesure des phénomènes démographiques et les nomenclatures adoptées, l'*Annuaire de l'Institut de droit international*, publié à partir de 1877, par les délibérations de l'Institut sur les questions de droit international, notamment le statut juridique des étrangers et les régulations des circulations humaines. Les deux sources sont numérisées et disponibles en OCR texte brut sur Gallica mais ne sont pas directement utilisables pour l'analyse computationnelle.

Les publications statistiques et juridiques du XIXe siècle sont des objets typographiques complexes. Elles combinent de la prose continue, des tableaux à géométrie variable, des listes hiérarchisées, des notes marginales et des en-têtes de colonnes abrégés selon des conventions sans rapport avec celles des textes imprimés contemporains. Les moteurs OCR entraînés principalement sur la typographie moderne sont mal équipés pour traiter finement ces matériaux, malgré d'importants progrès.

L'OCR standard appliquée aux images numérisées de ces sources produit des résultats parsemés d'erreurs en des proportions qui dépendent, entre autres critères, de la qualité des images et de la date de la numérisation. Les substitutions de caractères peuvent être systématiques : *l* et *t* sont fréquemment confondus dans certaines polices, les caractères accentués sont altérés selon des patterns caractéristiques. La sortie OCR introduit de plus un bruit structurel : tokens fusionnés (*ledroit* pour *le droit*), espaces parasites à l'intérieur des mots, ordinaux malformés, apostrophes et tirets incohérents. Sur le corpus de l'*Annuaire de l'Institut de droit international* (environ 116 000 mots) sur lequel ce pipeline a été développé, ces erreurs se comptent par milliers (environ 5 000).

Le recours à eScriptorium ou à Transkribus, devenus des standards de fait pour le traitement OCR/HTR des corpus historiques, est possible. Leur usage implique toutefois soit des coûts financiers importants, soit l'accès à une infrastructure de calcul et à des compétences techniques. Surtout, il faut, pour obtenir une post-correction réellement efficace, un investissement considérable en temps de supervision et de validation.

Ces outils permettent certes de déléguer efficacement une grande partie du traitement, mais ne facilitent pas la documentation décision par décision des corrections appliquées. Or dans un corpus multilingue dense en abréviations, en termes juridiques et en formes statistiques normalisées, les erreurs OCR se concentrent précisément sur ces éléments à haute valeur analytique : c'est là qu'une correction non traçable est le plus susceptible d'introduire des biais silencieux. En ce contexte, ce n'est pas le score global de précision qui importe, mais la responsabilité philologique.

Chaque transformation appliquée au corpus doit être documentable, chaque décision doit être justifiable, et le chercheur doit être en mesure d'expliquer et de défendre chaque correction selon le même standard que celui qui s'applique à toute autre décision éditoriale en matière d'édition de source.

---

## 3. Une première tentative : la votation de LLM et ce qu'elle révèle

La première approche du problème était conceptuellement séduisante. L'intuition était simple : soumettre la sortie OCR bruitée, segment par segment, à plusieurs LLM locaux et organiser une votation. Chaque modèle proposait sa lecture, la version majoritaire était destinée à être retenue. Si plusieurs modèles indépendants convergent sur une lecture, cette convergence est un signal de fiabilité ; s'ils divergent, cette divergence est un signal d'incertitude documentable. Le script est simple, s'exécute sans encombre ; par contre il faut vingt-quatre heures pour traiter soixante-dix pages.

Pour un corpus de plusieurs centaines de volumes ce peut être considéré comme un souci. L'expérience cependant révèle un problème plus fondamental. La demande adressée aux cinq modèles est structurellement incohérente. Le fichier entrant étant très bruité, les modèles ne segmentent pas le texte de la même façon. La procédure de vote suppose des unités commensurables entre modèles ; l'entrée bruitée garantit qu'une telle commensurabilité n'existe pas. L'erreur de conception est manifeste.

L'étape suivante consiste à évaluer les performances comparées de cinq modèles locaux sur des tâches de correction OCR afin de déterminer une stratégie. Les fichiers issus des LLM sont comparés avec un fichier édité manuellement, au moyen de trois métriques standard : le CER (*Character Error Rate*, taux d'erreur caractère par caractère), le WER (*Word Error Rate*, taux d'erreur par mots), et la distance de Levenshtein. Les résultats sur soixante-deux segments sont sans ambiguïté.

| Rang | Modèle | CER | WER | Levenshtein |
|------|--------|-----|-----|-------------|
| 1 | llama | 0,161 | 0,873 | 79,5 |
| 2 | phi3 | 0,200 | 1,130 | 98,8 |
| 3 | mistral_nemo | 0,210 | 1,161 | 103,6 |
| 4 | deepseek | 3,929 | 25,179 | 1937,4 |
| 5 | qwen3 | 6,915 | 44,577 | 3415,6 |

*Tableau 1. Benchmark OCR — performances comparées des modèles LLM locaux (CER et WER : valeurs basses = meilleures performances).*

L'écart entre les trois premiers modèles et les deux derniers couvre deux ordres de grandeur sur le CER et un facteur quarante sur la distance de Levenshtein. Ces outils agissent de manière fondamentalement différente dans ce contexte. La leçon est claire : les performances des LLM varient considérablement selon les modèles, les tâches, et les caractéristiques du matériau traité. « Utiliser un LLM » n'est pas une décision, c'est le début d'un complexe processus de tests.

Le modèle le plus performant, llama, obtient un CER de 0,161. Un caractère sur six erroné. C'est insuffisant pour une recherche sémantique ou une analyse textuelle automatisée. Pire encore, dans les conditions de cette expérimentation, chaque modèle produit une sortie plus dégradée, selon ces métriques, que la sortie OCR brute. Envoyer une OCR bruitée à un LLM local, sans apprentissage préalable, n'améliore pas le texte : cela produit une dégradation différente, plus difficile à caractériser et corriger que la dégradation d'origine.

Il est probable que les publications statistiques et juridiques du XIXe siècle, avec leurs tableaux à géométrie variable, leurs abréviations pas toujours stables et leurs changements fréquents de police, sont presque certainement sous-représentées dans les corpus d'entraînement de ces modèles. L'outil n'a pas les connaissances contextuelles qui lui permettraient de corriger ce qu'il ne reconnaît pas. Fluidité et exactitude ne sont pas la même chose, et un modèle qui produit du français grammaticalement plausible à partir d'une entrée dégradée ne produit pas pour autant du français correct, et moins encore un texte édité exact.

---

## 4. Ce que le LLM peut faire : analyser les erreurs plutôt que corriger le texte

Le résultat le plus utile de ce travail est sorti d'une expérimentation latérale : soumettre un échantillon de la sortie brute d'un fichier extrait d'une OCR à un LLM commercial non pas avec l'instruction de corriger le texte, mais de repérer les erreurs fréquentes et d'en analyser la structure.

Il ne lui est pas demandé donc de reconstruire un texte qu'il ne connaît pas, mais de décrire des régularités à partir d'un signal dégradé. Le LLM, sollicité comme expert de la sortie plutôt que comme correcteur du texte, produit une analyse des erreurs récurrentes, qu'il est possible d'examiner et de valider, ou non, avant de rédiger des scripts déterministes de post-correction. Ceux-ci implémentent des règles de substitution explicites, testables, reproductibles, qui n'ont plus rien de probabiliste.

La différence est de taille. Une correction produite par un modèle de langue est une sortie probabiliste : elle peut être juste, elle est généralement plausible, mais elle ne peut pas être vérifiée indépendamment sans texte de référence, et le raisonnement qui la sous-tend n'est pas accessible. Une règle de substitution dérivée d'une analyse des patterns d'erreurs peut être lue, testée, contestée et raffinée. Elle peut être accompagnée d'une documentation des cas traités et de ceux que l'on renonce à traiter ainsi. Le taux de faux positifs peut être mesuré.

La sortie n'est donc pas un texte produit par un modèle de langue, mais un ensemble de règles de transformation vérifiables et documentables que le modèle a aidé à formaliser depuis l'observation du matériau. Une fois les règles établies, le processus de correction est indépendant du modèle qui a contribué à l'initier.

Cette distinction importe pour une raison qui dépasse la reproductibilité technique. Sur un corpus destiné à nourrir un système d'information, ou à la publication, qui sera cité et utilisé comme preuve par d'autres chercheurs, une correction qui ne peut pas être expliquée ne peut pas être justifiée. L'exigence épistémologique pour un corpus de recherche n'est pas la fluidité mais la traçabilité : la capacité à reconstruire, pour toute transformation donnée, la règle qui l'a produite, les cas que la règle était destinée à traiter, et les cas qu'elle devait laisser de côté.

Cet usage du LLM n'était pas le résultat visé. Il a émergé de l'échec de l'approche corrective. La leçon n'est pas que les LLM sont inutiles pour ce travail, mais que leur rôle est différent de celui initialement imaginé : ils produisent un signal, qui demeure à interpréter et à traiter.

---

## 5. Architecture du pipeline : supervision calibrée sur l'incertitude

Le pipeline consiste en dix-sept scripts appliqués en séquence à la sortie OCR en texte brut. Son architecture reflète une prise de position délibérée sur la relation entre incertitude algorithmique et supervision humaine. Le principe central est que des niveaux d'incertitude différents justifient des niveaux de supervision différents, et que ce calibrage doit être rendu explicite plutôt que dissimulé dans un code.

Le pipeline organise ses dix-sept scripts en quatre régimes de correction d'incertitude croissante.

Le premier régime, couvrant les scripts 02 à 14, traite les **corrections déterministes**. Ce sont des transformations sans faux positif connu sur le corpus de développement. Cela inclut la normalisation Unicode, les apostrophes non standard, les tirets typographiques, les caractères de contrôle, la normalisation des espaces, les ordinaux malformés, la capitalisation des mois, les abréviations courantes, l'espacement de la ponctuation, les virgules fusionnées filtrées par le lexique morphologique Lefff (Sagot 2010), les chiffres romains altérés, le formatage des références bibliographiques, les guillemets parasites et les ligatures manquantes. Ces scripts sont appliqués automatiquement et sans supervision. La justification n'est pas qu'aucune erreur n'est possible, mais que le taux de faux positifs sur le corpus de développement est nul. C'est une certitude locale, explicitement définie comme telle dans la documentation des scripts.

Le script 11 fournit un exemple de cette logique. Il corrige les chiffres romains altérés et identifie 199 occurrences de « Il » dans le corpus comme lectures potentiellement erronées du chiffre romain II. Mais 196 de ces occurrences sont le pronom sujet français. Corriger « Il » sans contraintes contextuelles produirait 196 faux positifs catastrophiques. Le script n'applique donc la correction que dans les trois contextes où le corpus garantit que la lecture est non ambiguë : « T. Il » (référence de tome), « I. Il » (référence d'item), et « T. Vit » (où le contexte bibliographique — numéro de tome suivi d'une année — lève l'ambiguïté). Six corrections, zéro faux positif. Le docstring l'énonce explicitement : *« les scripts de ce pipeline privilégient toujours la précision sur le rappel : mieux vaut ne pas corriger que corriger à tort. »*

Le deuxième régime (scripts 15 et 16) propose une **correction semi-automatique avec apprentissage cumulatif**. Le script 15 gère les tokens fusionnés (*ledroit* → *le droit*) ; le script 16 gère les formes inconnues répétées susceptibles de représenter des erreurs OCR systématiques (*congrés* → *congrès*). Les deux scripts fonctionnent par un cycle de validation humaine : les corrections candidates sont exportées dans un fichier TSV, révisées par le chercheur dans un tableur, et les décisions validées sont persistées dans un modèle JSON qui est reporté d'une session à l'autre et d'un volume à l'autre d'un même corpus sériel. Le mécanisme d'apprentissage cumulatif permet d'espérer que lorsque le nombre de volumes traités s'élève, le nombre de cas requérant une validation diminue : ce qui a déjà été décidé n'est pas resoumis. La supervision humaine en ce cas n'est pas un palliatif à une faiblesse algorithmique mais une caractéristique de conception délibérée qui reflète l'ambiguïté irréductible de certaines décisions de correction et la nécessité que ces décisions soient assumées par le chercheur plutôt que déléguées à un algorithme.

Le troisième régime, script 17, applique une **correction probabiliste** par distance de Damerau-Levenshtein aux formes hapax absentes du Lefff. Ce script distingue deux sous-régimes avec des protocoles de supervision différents. Les corrections à distance 1 — où une seule opération transforme l'hapax en une forme lexicale connue, et où cette forme est unique à cette distance — sont appliquées automatiquement. Les cent premières corrections sont exportées dans un journal d'audit permettant une vérification post-hoc. Les corrections à distance 2 sont traitées différemment : un échantillon est exporté pour examen par le chercheur, qui prend une décision — appliquer ou ne pas appliquer — sur la base du taux d'erreur estimé dans l'échantillon. Le script calcule et affiche des intervalles de confiance de Wilson pour soutenir cette décision et permettre qu'elle soit documentée.

Cette structure à quatre régimes encode une théorie de la responsabilité de correction. Plus la correction est incertaine, plus le chercheur doit être présent dans la décision. Les règles déterministes ne requièrent aucune présence au-delà de la validation initiale de la règle. Les corrections semi-automatiques requièrent une validation cas par cas, progressivement remplacée par des décisions accumulées. Les corrections probabilistes requièrent un jugement statistique appliqué à la population dans son ensemble. Le chercheur n'est absent du processus à aucun moment, mais la forme de sa présence est calibrée à la situation épistémique.

Le pipeline est conçu pour les corpus sériels. Les modèles d'apprentissage cumulatif des scripts 15 et 16 sont explicitement délimités par type de corpus plutôt que par document individuel. Un modèle construit sur un volume de l'*Annuaire de l'Institut de droit international* s'applique au suivant, avec un coût marginal de validation décroissant à travers la série. Ce n'est pas seulement une commodité pratique : cela reflète une réalité philologique. Les erreurs d'un corpus sériel produit par le même imprimeur, avec les mêmes polices, numérisé par le même équipement, ne sont pas indépendantes, et l'Annuaire a le même éditeur depuis son origine. L'architecture d'apprentissage du pipeline est calibrée afin de tenir compte de cette réalité.

Nous suggérons ici que l'outil générique le plus puissant n'est pas nécessairement l'outil le plus approprié pour un corpus spécifique, un environnement de recherche spécifique, des caractéristiques matérielles spécifiques et des exigences savantes spécifiques. Une solution construite autour des propriétés du matériau peut être plus fonctionnelle qu'une solution générique, non parce qu'elle est techniquement supérieure, mais parce qu'elle est épistémiquement mieux ajustée à la tâche. Cela ne doit pas être compris comme la condamnation du recours à tel ou tel outil, tel ou tel dispositif, plutôt comme un plaidoyer pour un travail patient sur le grain de son matériau, permettant de comprendre la structure des erreurs qui l'affectent, avant de construire ou d'adapter un logiciel qui encode explicitement cette compréhension. Le revers de la médaille sans doute est que le pipeline décrit ici n'est pas portable et générique au sens où un LLM l'est. Il est, au plus, l'exemple d'une stratégie possible et localement productive. Son architecture, sa logique de calibrage et ses régimes de supervision peuvent être adaptés à d'autres corpus historiques sériels.

---

## 6. Le code annoté comme protocole philologique

Les engagements épistémologiques déterminent l'architecture du pipeline mais sont également encodés dans son code source, particulièrement dans les commentaires qui y figurent. Nous proposons ici une lecture d'extraits du code de quatre scripts afin de montrer comment leurs annotations fonctionnent comme une forme de protocole philologique. Elles constituent un registre des décisions prises, des alternatives envisagées et rejetées, et du raisonnement qui mène à la décision.

Ce n'est pas la pratique standard de documentation logicielle, mais la mise en visibilité des logiques et des choix encodés. Le lecteur, l'étudiant particulièrement, peut comprendre *pourquoi* une règle a été conçue comme elle l'a été et quel statut épistémologique assigner à ses sorties. Le docstring en devient non le commentaire mais l'explicitation du texte qu'est le code.

### Script 17 : deux régimes épistémiques

Le script 17 nomme explicitement la différence épistémologique des deux modes de correction qu'il propose :

```
— À d=1 (une opération) :
  Un hapax absent du Lefff à distance 1 d'un mot connu est dans
  la grande majorité des cas une erreur OCR isolée. Le filtre d'unicité
  garantit de surcroît qu'un seul mot du Lefff est à cette distance —
  il n'y a pas d'ambiguïté sur la correction à appliquer.
  On est dans un régime de CERTITUDE OPÉRATIONNELLE : on agit
  automatiquement, et on documente dans un journal pour audit post-hoc.

— À d=2 (deux opérations) :
  Le nombre de mots du Lefff à distance 2 d'un token donné est
  beaucoup plus élevé. L'espace de recherche s'étend de façon
  combinatoire. On est dans un régime de DÉCISION PROBABILISTE :
  on ne peut pas certifier que chaque correction est juste, on peut
  seulement estimer que la majorité le sont.
```

Les étiquettes — *certitude opérationnelle* et *décision probabiliste* — ne sont pas des termes techniques. Ce sont des caractérisations épistémologiques. Elles indiquent au chercheur quel type d'affirmation fait le script et quel type de responsabilité il assume en acceptant ses sorties. Le script opérationnalise ensuite cette distinction à travers un protocole de supervision concret : application automatique avec journal d'audit pour d=1, inspection d'échantillon et décision globale pour d=2. Il calcule et affiche des intervalles de confiance de Wilson aidant à la décision et permettant au chercheur de documenter le taux de faux positifs estimé dans son journal de recherche.

L'opération de transposition, qui étend la distance de Levenshtein standard pour capturer les inversions de caractères, est traitée de la même manière. Le docstring note que le gain sur ce corpus est marginal (environ deux cas sur deux mille) mais que l'opération est implémentée par souci d'exhaustivité. Les choix d'implémentation sont ainsi documentés et motivés.

### Script 16 : la théorie de l'erreur encodée dans les paramètres

Le script 16 traite les formes inconnues répétées, soit les tokens absents du Lefff qui apparaissent entre un seuil minimum et maximum de fréquence. Les valeurs de seuil sont des paramètres configurables, mais leur docstring manifeste que leur paramétrage n'est pas sans effet et ne peut être décidé arbitrairement :

```
SEUIL_MIN : occurrences minimales pour signaler une forme (défaut : 2)
            Les hapax (1 occurrence) sont ignorés — trop de bruit.
            Une erreur OCR aléatoire ne se répète pas ;
            une erreur systématique, si.
SEUIL_MAX : occurrences maximales (défaut : 10)
            Au-delà, la forme est probablement un nom propre récurrent
            ou un terme technique du domaine, pas une erreur OCR.
```

Le seuil minimum encode une théorie de l'erreur OCR : les erreurs aléatoires ne se répètent pas, les erreurs systématiques si. Le seuil maximum encode une théorie du corpus : les formes inconnues à haute fréquence dans un corpus juridique spécialisé sont plus susceptibles de correspondre à un vocabulaire spécifique au domaine ou à des noms propres qu'à des erreurs. Ce sont des affirmations relatives au matériau traité et elles sont formulées comme telles. Un chercheur adaptant le pipeline à un corpus différent peut ajuster ces paramètres en fonction des propriétés de son matériau.

Nous avons tenté également de documenter des particularités du code qui peuvent apparaître uniquement techniques, quand elles renvoient en fait à des choix déterminés par la nature du matériau ou les effets spécifiques des fonctions appelées. C'est le cas ainsi, dans le contexte de scripts tentant autant que possible d'éviter le recours à des librairies externes — afin de rendre le pipeline plus stable, plus auditable et plus pérenne — de l'usage de `langid`. Le docstring note que cette bibliothèque d'identification de langue, utilisée pour filtrer les tokens non français, est peu fiable sur les tokens de moins de huit caractères. Son utilisation sur des tokens isolés est explicitement caractérisée comme une heuristique plutôt que comme le vecteur de certitudes. Certains tokens en langue étrangère échapperont au filtre et apparaîtront donc dans l'échantillon d'audit. La limite est connue, documentée et gérée par la supervision humaine plutôt que par un filtre automatique supplémentaire dont la fiabilité propre serait en ce cas sujette à caution.

### Script 15 : apprentissage cumulatif et temps du travail philologique

Le script 15, qui gère les tokens fusionnés, introduit une dimension absente des deux autres : l'accumulation des décisions validées d'une session à l'autre et d'un volume à l'autre du corpus. Le modèle d'apprentissage persiste dans un fichier JSON qui est explicitement délimité par type de corpus :

```
IMPORTANT — un modèle par type de corpus :
  Les erreurs OCR varient selon les sources et les périodes. Un corpus
  de presse des années 1950 n'aura pas les mêmes tokens fusionnés qu'un
  corpus juridique du XIXe siècle. Utiliser des fichiers de modèle
  distincts pour des corpus de natures différentes.
```

L'instruction pratique correspond à une réalité philologique : la structure des erreurs d'un corpus sériel est une propriété de ses conditions matérielles de production et de numérisation, pas une propriété générique de la sortie OCR.

La conséquence pratique est visible dans les données de validation. Sur le premier volume traité, le script 15 a généré 47 corrections candidates, toutes validées par le chercheur en un seul passage. Un échantillon représentatif est présenté dans le tableau 2.

| Token fusionné | Suggestion | Décision |
|---|---|---|
| sontécoulés | sont écoulés | o |
| peutêtre | peut être | o |
| ÉtatsGénéraux | États Généraux | o |
| procèsverbal | procès verbal | o |
| dommagesintérêts | dommages intérêts | o |

*Tableau 2. Extrait du TSV de validation du script 15, cycle 1 (47 cas, 0 refus).*

Le deuxième cycle n'a produit aucun nouveau cas : le modèle avait convergé en un seul passage. Sur un deuxième volume de la même série, ces 47 décisions seront appliquées automatiquement sans intervention humaine. Le modèle JSON est, en ce sens, une forme de mémoire savante : un registre structuré de décisions philologiques qui peut être inspecté, contesté et transféré.

### Script 14 : la connaissance disciplinaire encodée dans le code

Un dernier exemple illustre une dimension différente de la même pratique. Le script 14 restitue la ligature française œ (*oeuvre* → *œuvre*, *voeu* → *vœu*, etc.) — 79 corrections sur le corpus de développement, zéro faux positif. Mais le script contient aussi une règle qui est documentée et délibérément désactivée :

```
Pourquoi PAS « ae » → « æ » dans ce corpus :
  L'analyse exhaustive du corpus révèle que tous les mots contenant
  « ae » sont des noms propres souvent flamands et néerlandais :
      Jaequemyns (×40), Portugael (×11), Disraeli (×4), Zachariae (×3)...
  Ces noms NE prennent PAS la ligature æ — c'est l'orthographe correcte
  de ces patronymes (Rolin-Jaequemyns est l'un des fondateurs de
  l'Institut).
  La règle æ est donc désactivée pour ce corpus.
  Elle est documentée ci-dessous pour adaptation à d'autres corpus.
```

Savoir que Rolin-Jaequemyns est l'un des fondateurs de l'Institut de droit international, et que son nom ne prend pas de ligature, est une donnée historique qui n'a rien de computationnel. Sa présence dans le code source, comme justification d'une règle désactivée, est une instance concrète d'expertise disciplinaire conditionnant le comportement algorithmique.

### Le script annoté comme document méthodologique

Ces annotations ne s'adressent pas à un développeur qui a besoin de comprendre l'implémentation, mais à un historien qui a besoin de comprendre les engagements épistémologiques intégrés dans l'outil qu'il utilise. Elles documentent non seulement ce que fait le code mais ce qu'il affirme, et ce que le chercheur doit apporter que le code ne peut pas fournir. Cette pratique a un précédent dans la tradition de l'édition critique, où apparat et commentaire servent précisément cette fonction et rendent visibles les décisions qui ont produit le texte et les alternatives qui ont été envisagées et rejetées. Le script de pipeline annoté est, en ce sens, une forme d'apparat éditorial pour le travail philologique computationnel.

---

## 7. Conclusion

Cet article décrit des méandres. Les votes de LLM locaux ont révélé une erreur de conception. Un benchmark a exposé l'ampleur des variations de performance entre modèles et l'inadéquation de la correction brute par LLM pour un matériau historique dégradé. Une expérimentation latérale avec un LLM commercial a produit une analyse de la structure des erreurs qui a permis de rédiger des règles de correction déterministes. Le pipeline qui a émergé de ce processus applique ces règles dans une architecture qui calibre explicitement la supervision humaine à l'incertitude algorithmique, et documente chaque décision dans un code source conçu pour être lu comme un registre méthodologique autant que comme un document technique. Cela parce que dans le contexte de la recherche menée il convenait de préserver la capacité à reconstruire et justifier les transformations appliquées au texte.

L'exigence peut difficilement être tenue si l'on recourt à un dispositif fonctionnant comme une boîte noire. Elle est satisfaite, au moins en principe, par un pipeline dont chaque règle est documentée, chaque régime de supervision explicitement calibré, et la place du chercheur définie, sous une forme appropriée au niveau d'incertitude, à chaque étape du processus de correction.

C'est ce que nous avons appelé une philologie computationnelle explicite, dont la fonction est aussi pédagogique dans un contexte d'enseignement. L'expression ne vise pas à distinguer une érudition traditionnelle d'une érudition computationnelle mais à pointer le fait que certaines méthodes computationnelles achètent l'efficacité au prix des normes disciplinaires. Le pipeline décrit ici est sans doute moins rapide et moins immédiatement généralisable qu'une correction par LLM. Il requiert davantage d'investissement du chercheur, même si pas forcément plus de temps si l'on prend en compte les exigences du fine tuning. Il a de plus l'avantage de produire un corpus dont la qualité peut être caractérisée, dont les corrections peuvent être tracées, et dont le profil d'erreur peut être défini, tentant de répondre ainsi aux exigences d'une édition savante.

Deux conclusions peuvent être dégagées de l'expérience. Recourir à l'outil disponible le plus puissant et le plus générique est une décision compréhensible mais pas toujours optimale quand le matériau a des propriétés très spécifiques. La réponse la plus appropriée peut alors être de comprendre la structure du problème de façon à ajuster à celui-ci un mode de traitement ad hoc.

Cela revient à considérer que le bricolage numérique (Rygiel 2017) ou le *thinkering* (Fickers et van der Heijden 2020) peut encore avoir non seulement un sens mais une utilité pratique et permettre la construction d'un outil qui encode la connaissance disciplinaire, réfléchit sur ses propres limites, et reste conforme aux exigences épistémologiques du domaine. La chose du moins reste pensable et possible même dans un environnement qui voit surgir des outils génériques de plus en plus puissants.

Le pipeline est disponible sous forme de logiciel libre, avec la documentation complète et le corpus de développement, à l'adresse <https://github.com/Datashs/galica-postocr>. Une version archivée avec un identifiant pérenne est déposée sur Zenodo à <https://doi.org/10.5281/zenodo.20112806>. Les chercheurs travaillant sur des corpus similaires sont invités à adapter le pipeline à leur propre matériau, un script dédié permettant d'en évaluer les performances sur le corpus envisagé.

---

## Références



Bowker, Geoffrey C., et Susan Leigh Star. 1999. *Sorting Things Out: Classification and Its Consequences*. Cambridge, MA : MIT Press.

Chiron, Guillaume, Aurelie Levcopoulos, Bertrand Coüasnon et Alexis Viard. 2017. « Tools for OCR Post-Correction. » Dans *Proceedings of the 5th International Workshop on Historical Document Imaging and Processing*, 78–83.

Ellul, Jacques. 1954. *La Technique ou l'enjeu du siècle*. Paris : Armand Colin.

Evershed, Jonathan, et Kent Fitch. 2014. « Correcting OCR Errors in Historic Digitised Newspapers. » Dans *Proceedings of the Australasian Language Technology Association Workshop*, 19–27.

Fickers, Andreas, et Tim van der Heijden. 2020. « Inside the Trading Zone: Thinkering in a Digital History Lab. » *Digital Humanities Quarterly* 14 (3). <http://dhq.digitalhumanities.org/vol/14/3/000472/000472.html>

Kanerva, Jenna, Cassandra Ledins, Siiri Käpyaho et Filip Ginter. 2025. « OCR Error Post-Correction with LLMs in Historical Documents: No Free Lunches. » Dans *Proceedings of the Third Workshop on Resources and Representations for Under-Resourced Languages and Domains (RESOURCEFUL-2025)*, 38–47. Tallinn : University of Tartu Library. <https://aclanthology.org/2025.resourceful-1.8/>

Lévi-Strauss, Claude. 1962. *La Pensée sauvage*. Paris : Plon.

Lyu, Lijun, Maria Koutraki, Martin Krickl et Besnik Fetahu. 2021. « Neural OCR Post-Hoc Correction of Historical Corpora. » *Transactions of the Association for Computational Linguistics* 9 : 479–493. <https://aclanthology.org/2021.tacl-1.29/>

Pettersson, Eva. 2012. « Spelling Normalisation and Linguistic Analysis of Historical Text for Information Extraction. » Thèse de doctorat, Uppsala University.

Piotrowski, Michael. 2012. *Natural Language Processing for Historical Texts*. San Rafael : Morgan & Claypool.

Rygiel, Philippe. 2017. *Historien à l'âge numérique*. Villeurbanne : Presses de l'ENSSIB.

Rygiel, Philippe. 2021. *L'ordre des circulations ? L'Institut de droit international et la régulation des migrations (1870–1920)*. Paris : Éditions de la Sorbonne.

Sagot, Benoît. 2010. « The Lefff, a Freely Available and Large-Coverage Morphological and Syntactic Lexicon for French. » Dans *Proceedings of the 7th International Conference on Language Resources and Evaluation*, 2744–2751.

van Strien, Daniel, Kaspar Beelen, Mariona Coll Ardanuy, Kasra Hosseini, Barbara McGillivray et Giovanni Colavizza. 2020. « Assessing the Impact of OCR Quality on Downstream NLP Tasks. » Dans *Proceedings of the 12th International Conference on Agents and Artificial Intelligence*, 484–496. <https://doi.org/10.17863/CAM.52068>
