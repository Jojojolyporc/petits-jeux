# Brèche — rapports de test

## 16/11/2026 — version 1
Verdict : livrable avec réserves (équilibrage mesuré avec un robot seulement, rien de vérifié sur iPhone).

Environnement : Chromium (google-chrome) via Playwright, viewport 390 × 844, DPR 3, tactile. Scripts : `outils/qa/breche_qa.py` (simulations, fps, captures), `outils/qa/breche_flow.py` (parcours, ergonomie), `outils/qa/breche_eval.py` (expressions ponctuelles). Graines 1 à 50.

### Équilibrage (50 parties, robot simple)
| Valeur | Cible | Mesure | Écart |
|---|---|---|---|
| Victoire | 30 à 70 % | 32 % (±14) | dans la cible, limite basse |
| Mort avant 4:00 | < 30 % | 18 % | OK |
| Durée d'une victoire | 4:45 à 5:45 | 4:42 à 5:21, médiane 4:59 | OK |
| Combat contre le colosse | 45 à 90 s | 42 à 81 s, médiane 59 s | OK |
| Niveau à 4:00 | 18 à 26 | 22 | OK |
| Pic d'ennemis | 150 à 400 | 226 | OK |

Réglages passés pendant la mise au point (le robot perdait 100 % des parties avec les valeurs d'origine) : dégâts des diablotins 5 → 2, invulnérabilité 0,5 → 0,7 s, brutes 12 → 10 dégâts et 45 → 40 de vitesse, PV ennemis (1 + t/150) → (1 + t/240), XP par niveau 5 + 4(n−1) → 5 + 12(n−1) (le robot finissait au niveau 45, tout au maximum), colosse 9000 → 7000 PV, apparitions 18/s → 16/s au maximum, encerclements 70/100 → 80/140.
Dégâts subis dans les défaites : diablotins et brutes ~80 %, colosse au contact ~15 %, coup au sol ~3 %.

### Fluidité
| Mesure | Résultat |
|---|---|
| Scène à ~500 ennemis, 10 s | médiane 60 i/s, pire seconde 57 |
| Même scène, processeur ralenti ×4 (test de résistance) | 14 i/s |
| Rendu | canevas plafonné à DPR 2 |

### Robustesse et ergonomie
| Sévérité | Constat | Mesure |
|---|---|---|
| — | Parcours titre → partie → niveau → pause → export → purge → import → reprise | OK, partie retrouvée au même instant (4,2 s) |
| — | Passage en arrière-plan en pleine partie | pause automatique + sauvegarde |
| — | Rechargement hors ligne | écran titre OK depuis le cache |
| — | Paysage | message « Tourne ton téléphone » affiché |
| — | Erreurs console, échecs réseau, requêtes externes | 0, 0, 0 |
| — | Cibles tactiles < 44 px | aucune |
| mineur | Textes secondaires sous 16 px | inventaire 14 px, étiquettes de carte 15 px, numéro de version 13 px |
| mineur | Le joystick n'a pas d'emplacement fixe | voulu (il apparaît sous le pouce) |

### À vérifier sur l'iPhone
1. Fluidité réelle avec la horde à 3:00–4:00.
2. Le joystick ne déclenche ni défilement ni geste iOS, y compris près du bas de l'écran (barre d'accueil).
3. Lisibilité de la horde et des orbes roses du colosse sur l'écran du téléphone.
4. Copier le code de sauvegarde (presse-papier Safari).
5. Son après le premier toucher.
