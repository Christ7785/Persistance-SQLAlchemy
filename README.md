# Jeu Loups et Villageois avec SQLAlchemy

Ce projet est une implémentation d'un jeu de plateau où des loups et des villageois s'affrontent. Il utilise SQLAlchemy pour la persistance des données.

## Installation

```bash
# Cloner le dépôt
git clone <url-du-repo>
cd <dossier-du-repo>

# Installer les dépendances
pip install -r requirements.txt
```

## Fonctionnalités

- Plateau de jeu 2D avec des loups (W) et villageois (O)
- Système de tour par tour
- Persistance des données via SQLAlchemy
- Gestion des mouvements et collisions entre joueurs
- Règles de jeu configurables (taille du plateau, nombre de tours, etc.)

## Utilisation

Pour lancer le test du jeu:

```bash
python sa.db.py
```

## Structure du code

- `sa_model.py` : Contient les modèles SQLAlchemy (Game, Player, GameBoard, Cell, etc.)
- `sa.db.py` : Script de test pour démontrer le fonctionnement du jeu


## Dépendances

- SQLAlchemy 2.0+
- typing-extensions
- greenlet