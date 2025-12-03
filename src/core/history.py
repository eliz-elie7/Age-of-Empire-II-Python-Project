from datetime import datetime

def init_history_file():
    """Crée le fichier HTML d'historique au lancement du jeu."""
    content = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Historique des combats</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f4f4f4;
            padding: 20px;
        }
        h1 { text-align: center; }
        .log-entry {
            background: white;
            padding: 15px 20px;
            margin: 15px 0;
            border-left: 5px solid #0074D9;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .date { color: #666; font-size: 0.85em; }
        .players { font-size: 1.1em; margin-bottom: 5px; }
        .winner { font-weight: bold; color: #2ECC40; }
        .duration { color: #555; }
    </style>
</head>

<body>
    <h1>Historique des combats</h1>
    <div id="logs"></div>
</body>
</html>
"""
    with open("history.html", "w", encoding="utf-8") as f:
        f.write(content)


def add_fight_history(player1, player2, duration, winner, details=""):
    """Ajoute un combat dans l'historique HTML."""
    with open("history.html", "r", encoding="utf-8") as f:
        html = f.read()

    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    entry = f"""
    <div class="log-entry">
        <div class="date">{timestamp}</div>
        <div class="players">⚔️ {player1} vs {player2}</div>
        <div class="duration">⏳ Durée : {duration} sec</div>
        <div class="winner">🏆 Vainqueur : {winner}</div>
        <div>{details}</div>
    </div>
    """

    # On insère l'entrée juste avant la fin du bloc logs
    html = html.replace("</div>", entry + "\n</div>", 1)

    with open("history.html", "w", encoding="utf-8") as f:
        f.write(html)
