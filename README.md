# Projet RPA de Mise en Qualité de Données

## Description

Ce projet utilise Python et Selenium pour automatiser la mise en qualité des données sur un site web interne de l'entreprise. Le script traite les numéros de contrat depuis un fichier Excel, interagit avec différentes modales sur le site web et met à jour les informations selon des règles prédéfinies.

## Prérequis

- Python 3.x
- pip (pour installer les packages Python)

## Installation

1. **Cloner le dépôt** :
   ```bash
   git clone https://github.com/ton-repo/rpa-mise-en-qualite.git
   cd rpa-mise-en-qualite
   ```

2. **Créer et activer un environnement virtuel** (optionnel mais recommandé) :
   ```bash
   python -m venv venv
   source venv/bin/activate  # Sur Windows: venv\Scripts\activate
   ```

3. **Installer les dépendances** :
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurer les variables d'environnement** :
   Créer un fichier `.env` à la racine du projet et y ajouter vos identifiants :
   ```env
   IDENTIFIANT=ton_identifiant
   MOT_DE_PASSE=ton_mot_de_passe
   ```

## Usage

1. **Préparer le fichier Excel** :
   Placement du fichier Excel contenant les numéros de contrat dans le répertoire du projet et assurez-vous qu'il est nommé `MEQ - Fichier test pour le robot.xlsx`.

2. **Exécuter le script** :
   ```bash
   python main.py
   ```

## Structure du Projet

- **main.py** : Point d'entrée principal du script.
- **affranchigo_forfait_case.py, affranchigo_lib_case.py, destineo_case.py, frequenceo_case.py, proxicompte_case.py, collecte_remise.py** : Modules pour la gestion de différents types de cas de contrat.
- **data_processing.py** : Contient les fonctions pour le traitement des fichiers de données.
- **debug.py** : Contient les fonctions de logging et de capture de screenshots en cas d'erreur.

## Fonctionnalités

- **Connexion** : Le script se connecte automatiquement au site web en utilisant les identifiants fournis.
- **Gestion des Modales** : Le script gère automatiquement les différentes modales qui apparaissent sur le site.
- **Traitement des Contrats** : Le script soumet les numéros de contrat, navigue dans les différentes sections du site, et met à jour les informations.
- **Enregistrement des Résultats** : Les numéros de contrat traités et non modifiables sont enregistrés dans des fichiers JSON.

## Dépendances

Les dépendances nécessaires sont listées dans `requirements.txt` :
- `selenium`
- `pandas`
- `openpyxl`
- `pip`
- `python-dotenv`

## Contribuer

Les contributions sont les bienvenues ! Veuillez soumettre des pull requests avec des descriptions claires des changements apportés.

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

--------------------------------

### Exécuter le script

Pour exécuter le script, utilisez la commande suivante :

```bash
python main.py
```