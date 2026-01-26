# save_system.py
# Gère la sauvegarde et le chargement des batailles

import pickle #sert à transformer un objet Python en fichier (et inversement)
import os
from datetime import datetime #Sert à obtenir la date et l’heure actuelle

SAVE_FOLDER = "saves" #Nom du dossier où seront stockées les sauvegardes.

# Creayion automatique du dossier des sauvegardes
os.makedirs(SAVE_FOLDER, exist_ok=True)

#Sauvegarder l’objet GameState dans un fichier
def save_game(game_state):
    """
    Sauvegarde un objet GameState contenant Battle.
    """

    # Création d'un nom à partir de date + heure
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{SAVE_FOLDER}/save_{timestamp}.sav"

    #Écriture du fichier binaire
    with open(filename, "wb") as f:
        pickle.dump(game_state, f)

    print(f"[SAUVEGARDE] Partie enregistrée : {filename}")


def load_game():
    """
    Charge la sauvegarde la plus récente.
    Retourne un GameState ou None.
    """

    # Liste des sauvegardes
    saves = [f for f in os.listdir(SAVE_FOLDER) if f.endswith(".sav")]

    # Si aucune sauvegarde on dit qu'on n'a rien trovué
    if not saves:
        print("[CHARGEMENT] Aucune sauvegarde trouvée.")
        return None

    # Trie par date
    saves.sort()

    # Sélectionne la plus récente
    latest = saves[-1]
    path = os.path.join(SAVE_FOLDER, latest)

    # Lecture du fichier
    with open(path, "rb") as f:
        game_state = pickle.load(f)

    print(f"[CHARGEMENT] Sauvegarde restaurée : {path}")
    return game_state
