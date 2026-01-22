import datetime
import os

FILENAME = "history.html"

def init_history_file():
    """Initialise le fichier (Version sans tableau des scores)."""
    # Si le fichier existe déjà, on ne touche à rien
    if os.path.exists(FILENAME):
        return

    html_content = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset='utf-8'>
    <title>MEDIEVALI - RAPPORT DE GUERRE</title>
    <link href="https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;700&family=Roboto:wght@400;900&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #0b0c15;
            --card-bg: rgba(20, 21, 30, 0.7);
            --cyan: #00f2ff;
            --magenta: #ff0055;
            --gold: #ffd700;
        }
        
        body {
            background-color: var(--bg);
            background-image: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), url('https://images.unsplash.com/photo-1542751371-adc38448a05e?ixlib=rb-1.2.1&auto=format&fit=crop&w=1920&q=80');
            background-size: cover;
            background-attachment: fixed;
            background-position: center;
            color: white;
            font-family: 'Roboto', sans-serif;
            margin: 0;
            padding: 40px;
            min-height: 100vh;
        }

        /* TITRE */
        h1 {
            font-family: 'Rajdhani', sans-serif;
            text-align: center;
            font-size: 3rem;
            letter-spacing: 10px;
            margin-bottom: 40px;
            color: var(--gold);
            text-transform: uppercase;
            text-shadow: 0 0 20px rgba(255, 215, 0, 0.3);
        }

        /* TIMELINE */
        .timeline { max-width: 900px; margin: 0 auto; display: flex; flex-direction: column-reverse; gap: 25px; }

        /* CARTE MATCH */
        .match-card {
            background: var(--card-bg);
            border: 1px solid rgba(255,255,255,0.05);
            border-radius: 12px;
            overflow: hidden;
            position: relative;
            transition: transform 0.2s;
            animation: slideIn 0.5s ease-out;
        }
        @keyframes slideIn { from { opacity:0; transform:translateY(20px); } to { opacity:1; transform:translateY(0); } }

        .match-card:hover { transform: scale(1.01); border-color: rgba(255,255,255,0.2); }

        .m-header {
            padding: 10px 20px;
            background: rgba(0,0,0,0.3);
            display: flex;
            justify-content: space-between;
            font-size: 0.8rem;
            color: #888;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .m-content { display: flex; align-items: center; padding: 20px; }
        .m-player { flex: 1; text-align: center; }
        .mp-name { font-weight: 900; font-size: 1.2rem; text-transform: uppercase; }
        .mp-info { font-size: 0.8rem; color: #888; margin-top: 4px; }
        .m-vs { font-family: 'Rajdhani'; font-weight: bold; font-size: 1.5rem; color: #444; margin: 0 20px; }

        .tag { padding: 4px 10px; border-radius: 4px; font-size: 0.7rem; font-weight: bold; text-transform: uppercase; display: inline-block; margin-top: 8px; }
        .tag-win { background: var(--gold); color: #000; box-shadow: 0 0 10px rgba(255, 215, 0, 0.3); }
        .tag-lose { border: 1px solid #444; color: #666; }

        .hp-bar { height: 4px; width: 100%; background: #222; display: flex; }
        .hp-fill-c { height: 100%; background: var(--cyan); box-shadow: 0 0 10px var(--cyan); }
        .hp-fill-m { height: 100%; background: var(--magenta); box-shadow: 0 0 10px var(--magenta); }

        .win-border-c { border-left: 4px solid var(--cyan); background: linear-gradient(90deg, rgba(0, 242, 255, 0.05), transparent); }
        .win-border-m { border-right: 4px solid var(--magenta); background: linear-gradient(-90deg, rgba(255, 0, 85, 0.05), transparent); }

        details { background: rgba(0,0,0,0.2); border-top: 1px solid rgba(255,255,255,0.05); }
        summary { padding: 10px; text-align: center; cursor: pointer; font-size: 0.75rem; color: #777; outline: none; list-style: none; }
        summary:hover { color: #fff; }
        
        .badge-list { padding: 0 20px 20px 20px; display: flex; flex-wrap: wrap; justify-content: center; gap: 5px; }
        .u-badge { padding: 2px 6px; border-radius: 3px; font-size: 0.7rem; font-family: monospace; border: 1px solid transparent; }
        .ub-c { background: rgba(0, 242, 255, 0.1); color: var(--cyan); border-color: rgba(0, 242, 255, 0.2); }
        .ub-m { background: rgba(255, 0, 85, 0.1); color: var(--magenta); border-color: rgba(255, 0, 85, 0.2); }
        .ub-icon { margin-right: 3px; }

    </style>
</head>
<body>

    <h1>MEDIEVALI <span style="font-weight:300; opacity:0.5">CHAMPIONSHIP</span></h1>

    <div class="timeline">
"""
    with open(FILENAME, "w", encoding="utf-8") as f:
        f.write(html_content)

def add_fight_history(p1_name, p2_name, ia1, ia2, u1_start, u2_start, winner, duration, survivors_data):
    # Sécurité : Si le fichier n'existe pas, on le crée
    if not os.path.exists(FILENAME):
        init_history_file()

    now = datetime.datetime.now().strftime("%H:%M")
    
    count_p1 = len([s for s in survivors_data if s[1] == p1_name])
    count_p2 = len([s for s in survivors_data if s[1] == p2_name])
    total = count_p1 + count_p2 if (count_p1 + count_p2) > 0 else 1
    pct_p1 = (count_p1 / total) * 100
    
    card_class = ""
    tag_p1, tag_p2 = "<span class='tag tag-lose'>DÉFAITE</span>", "<span class='tag tag-lose'>DÉFAITE</span>"
    winner_attr = "draw"

    if winner == p1_name:
        card_class = "win-border-c"
        tag_p1 = "<span class='tag tag-win'>👑 VICTOIRE</span>"
        winner_attr = "cyan"
    elif winner == p2_name:
        card_class = "win-border-m"
        tag_p2 = "<span class='tag tag-win'>👑 VICTOIRE</span>"
        winner_attr = "magenta"

    badges = ""
    if survivors_data:
        for symbol, team in survivors_data:
            css = "ub-c" if team == p1_name else "ub-m"
            icon = "♞" if "K" in str(symbol) else "♟"
            badges += f"<span class='u-badge {css}'><span class='ub-icon'>{icon}</span>{symbol}</span>"
    else:
        badges = "<span style='color:#555; font-size:0.8em'>☠️ Destruction Totale</span>"

    html = f"""
        <div class="match-card {card_class}" data-winner="{winner_attr}">
            <div class="m-header">
                <span>MATCH #{int(datetime.datetime.now().timestamp())%1000}</span>
                <span>⏱ {duration:.1f}s</span>
                <span>{now}</span>
            </div>
            
            <div class="hp-bar">
                <div class="hp-fill-c" style="width:{pct_p1}%"></div>
                <div class="hp-fill-m" style="width:{100-pct_p1}%"></div>
            </div>

            <div class="m-content">
                <div class="m-player">
                    <div class="mp-name" style="color:var(--cyan)">{p1_name}</div>
                    <div class="mp-info">{ia1} • {u1_start} Unités</div>
                    {tag_p1}
                </div>
                
                <div class="m-vs">VS</div>
                
                <div class="m-player">
                    <div class="mp-name" style="color:var(--magenta)">{p2_name}</div>
                    <div class="mp-info">{ia2} • {u2_start} Unités</div>
                    {tag_p2}
                </div>
            </div>

            <details>
                <summary>Forces Restantes ({count_p1 + count_p2}) ▼</summary>
                <div class="badge-list">
                    {badges}
                </div>
            </details>
        </div>
        """
    with open(FILENAME, "a", encoding="utf-8") as f:
        f.write(html)