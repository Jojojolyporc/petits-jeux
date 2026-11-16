# Brèche — conception

## Intention
Tenir seul, en exo-armure, face à une marée de démons qui déferle par une brèche, monter en puissance en quelques minutes, puis abattre le colosse qui garde le centre de la carte.

## Prise en main
- Portrait, une main (pouce).
- Joystick virtuel : il apparaît là où le pouce se pose, le personnage avance dans la direction donnée. Aucune autre commande en partie : les armes tirent seules.
- Durée cible d'une partie : environ 5 minutes (éveil du boss à 4:00, boss abattu vers 5:00).
- Pause : bouton en haut à droite. Pause automatique quand l'appli passe en arrière-plan.

## Boucle de jeu
- **Action (secondes)** : se déplacer pour garder les hordes à distance pendant que les armes frappent ; ramasser les gemmes d'expérience.
- **Partie (5 min)** : chaque niveau gagné propose 3 améliorations (nouvelle arme, niveau d'arme, bonus passif). La densité monte jusqu'à 4:00, où le colosse s'éveille au centre. Victoire : colosse abattu. Défaite : PV à zéro.
- **Progression entre parties** : pas dans cette version (voulue plus tard). Seuls les records sont conservés.

## Règles
- Carte fermée 2400 × 2400, colosse endormi et invulnérable au centre jusqu'à 4:00. Le joueur part 500 unités au sud du centre.
- Contact d'un ennemi : dégâts, puis 0,7 s d'invulnérabilité.
- Gemmes : lâchées par chaque ennemi tué, aspirées dans le rayon d'aimant. Au-delà de 350 gemmes au sol, les plus anciennes fusionnent.
- Plafonds : 4 armes, 4 bonus passifs, niveau 5 pour chacun. Quand tout est au maximum, le choix devient « soin 30 PV ».
- Flèche au bord de l'écran vers le colosse quand il est hors champ.

## Contenu
### Ennemis (valeurs de base ; PV multipliés par 1 + t/240 avec t en secondes)
| Ennemi | Rôle | Rayon | PV | Vitesse | Dégâts contact | XP |
|---|---|---|---|---|---|---|
| Diablotin | la horde, partout | 9 | 6 | 72 → 95 | 2 | 1 |
| Brute | plus lourd, encaisse, ralentit le passage | 20 | 70 | 40 | 10 | 6 |
| Bourreau (élite) | gros morceau, ponctuel | 30 | 500 | 55 | 20 | 40 |
| Colosse (boss) | fin de partie, au centre | 70 | 7000 | 34 | 25 | — |

Attaques du colosse éveillé : coup au sol annoncé 1 s à l'avance (rayon 170, 30 dégâts, toutes les 6 s) ; salve de 16 orbes (12 dégâts, toutes les 4,5 s) ; appel de 24 diablotins en cercle (toutes les 9 s).

### Chronologie
| Temps | Événement |
|---|---|
| 0:00 | diablotins seuls, 3 par seconde |
| 1:00 | les brutes arrivent (8 % des apparitions, 15 % à 3:00) ; premier bourreau |
| 1:30 | encerclement : anneau de 80 diablotins autour du joueur |
| 2:30 | bourreau |
| 3:00 | encerclement de 140 diablotins |
| 3:30 | bourreau |
| 3:50 | alerte « Le colosse s'éveille » |
| 4:00 | colosse actif ; apparitions normales réduites de moitié |

Apparitions : 3/s à 0:00 → 16/s à 4:00 (linéaire). Plafond 500 ennemis vivants (élites exceptés).

### Armes (niveau 1 → 5)
| Arme | Effet | Dégâts | Recharge | Évolution par niveau |
|---|---|---|---|---|
| Grande lame (départ) | balayage en arc de 150° devant soi | 16 → 36 | 1,0 → 0,7 s | portée 75 → 110 ; niv. 4 : balaie aussi derrière |
| Fusil à rafale | tirs vers l'ennemi le plus proche | 9 → 17 | 1,0 s | 2 → 5 balles, perforation 1 → 3 |
| Grenades | explosion sur un ennemi au hasard à l'écran | 22 → 46 | 2,2 → 1,5 s | 1 → 3 grenades, rayon 50 → 80 |
| Brasier | aura autour de soi, toutes les 0,4 s | 4 → 10 | — | rayon 55 → 95 |
| Arc électrique | éclair qui rebondit d'ennemi en ennemi | 14 → 26 | 1,6 → 1,1 s | 3 → 7 cibles |

### Bonus passifs (par niveau)
Puissance +10 % dégâts · Cadence −8 % recharge · Servomoteurs +8 % vitesse · Blindage +20 PV max · Régénération +0,4 PV/s · Aimant +35 % rayon · Amplitude +10 % zone.

### Expérience
XP pour passer du niveau n au n+1 : 5 + 12 × (n − 1).

## Équilibrage
Mesures du 16/11/2026 : 50 parties simulées, robot simple (esquive de près, tourne autour de la horde, armes avant bonus). Marge ±14 points sur les pourcentages.
| Valeur | Cible | Mesure | Statut |
|---|---|---|---|
| Durée d'une partie gagnée | 4:45 à 5:45 | médiane 4:59 (4:42 à 5:21) | mesurée |
| Combat contre le colosse | 45 à 90 s | médiane 59 s (42 à 81 s) | mesurée |
| Victoire, robot | 30 à 70 % | 32 % (16/50) | mesurée, limite basse |
| Mort avant 4:00, robot | moins de 30 % | 18 % (9/50) | mesurée |
| Niveau du joueur à 4:00 | 18 à 26 | médiane 22 | mesurée |
| Pic d'ennemis vivants par partie | 150 à 400 | médiane 226 | mesurée |
| Images par seconde, ~500 ennemis (Chromium) | médiane ≥ 55 | médiane 60, pire seconde 57 | mesurée |

Le ressenti humain (difficulté, lisibilité de la horde) reste à valider sur le téléphone.

## Décisions
- 16/11/2026 — Survivors-like, univers original (pas de Warhammer 40K). Portrait, joystick, parties de 5 minutes pour commencer. Hordes très denses de petits démons, ennemis plus imposants, méga-boss au centre de la carte. Progression entre parties voulue, mais pas dans ce MVP.

## Questions ouvertes
- Moment du combat contre le boss : éveil à 4:00 (version actuelle), ou attaquable dès le début ?
- « Grosse épée » : prise comme arme de départ. À confirmer.
- Ce qui se passe si le boss n'est pas tué : rien pour l'instant (la partie continue). Option : enragement après 2 minutes.
- Évolutions d'armes, coffres, objets de soin au sol : non inclus, à proposer plus tard.
