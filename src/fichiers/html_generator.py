import os
import sys
import subprocess
import shutil
import webbrowser

def generate_snapshot_html(players, game_time):
    """
    Génère un Dashboard HTML 'Ultimate HUD' et force l'ouverture sur Linux.
    """
    filename = os.path.abspath("game_state.html")
    
    # --- CALCULS STATISTIQUES AVANCÉS ---
    p1, p2 = players[0], players[1]
    
    # Fonction locale pour les stats
    def get_stats(player):
        alive = [u for u in player.squad if u.is_alive]
        total = len(player.squad)
        current_hp = sum(u.current_hp for u in alive)
        max_total_hp = sum(u.max_hp for u in player.squad)
        avg_hp = (current_hp / len(alive)) if alive else 0
        return alive, total, current_hp, max_total_hp, avg_hp

    u1_alive, u1_total, hp1_curr, hp1_max, hp1_avg = get_stats(p1)
    u2_alive, u2_total, hp2_curr, hp2_max, hp2_avg = get_stats(p2)

    # Calcul domination (basé sur les PV restants totaux)
    total_hp_pool = hp1_curr + hp2_curr if (hp1_curr + hp2_curr) > 0 else 1
    domination_p1 = (hp1_curr / total_hp_pool) * 100
    domination_p2 = (hp2_curr / total_hp_pool) * 100

    # --- HTML & CSS DESIGN ULTIME ---
    html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset='utf-8'>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>TACTICAL OVERVIEW T={game_time:.2f}s</title>
    <link href="https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-deep: #030508;
            --grid-color: rgba(30, 144, 255, 0.05);
            --glass: rgba(20, 30, 40, 0.6);
            --border: rgba(255, 255, 255, 0.1);
            
            /* Player 1: Cyan Tech */
            --p1-main: #00e5ff;
            --p1-glow: rgba(0, 229, 255, 0.4);
            
            /* Player 2: Crimson Neon */
            --p2-main: #ff1744;
            --p2-glow: rgba(255, 23, 68, 0.4);
        }}
        
        * {{ box-sizing: border-box; }}

        body {{
            font-family: 'Rajdhani', sans-serif;
            background-color: var(--bg-deep);
            background-image: 
                linear-gradient(var(--grid-color) 1px, transparent 1px),
                linear-gradient(90deg, var(--grid-color) 1px, transparent 1px);
            background-size: 40px 40px;
            color: #fff;
            margin: 0;
            padding: 20px;
            min-height: 100vh;
            overflow-x: hidden;
        }}

        /* Animation d'entrée */
        @keyframes slideIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        /* --- HEADER & HUD --- */
        .hud-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 30px;
            background: rgba(10, 10, 10, 0.8);
            border-bottom: 2px solid #333;
            backdrop-filter: blur(10px);
            margin-bottom: 30px;
            border-radius: 0 0 15px 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }}
        
        .hud-title h1 {{ margin: 0; font-weight: 700; letter-spacing: 3px; font-size: 2em; text-transform: uppercase; }}
        .hud-title span {{ color: var(--p1-main); }}
        .hud-time {{ font-size: 1.5em; font-weight: 600; color: #fbbf24; font-variant-numeric: tabular-nums; }}

        /* --- BATTLE BALANCE BAR --- */
        .balance-container {{
            max-width: 1200px;
            margin: 0 auto 30px auto;
            text-align: center;
            animation: slideIn 0.5s ease-out;
        }}
        .balance-label {{ margin-bottom: 5px; color: #888; text-transform: uppercase; letter-spacing: 2px; font-size: 0.8em; }}
        
        .balance-bar {{
            height: 20px;
            background: #111;
            border-radius: 10px;
            overflow: hidden;
            display: flex;
            box-shadow: 0 0 15px rgba(0,0,0,0.8);
            border: 1px solid #333;
        }}
        .bar-segment {{ height: 100%; transition: width 1s ease-in-out; display: flex; align-items: center; justify-content: center; font-size: 0.7em; font-weight: bold; text-shadow: 0 1px 2px black; }}
        .seg-p1 {{ background: linear-gradient(90deg, #00acc1, var(--p1-main)); width: {domination_p1}%; }}
        .seg-p2 {{ background: linear-gradient(90deg, var(--p2-main), #b71c1c); width: {domination_p2}%; }}

        /* --- GRID LAYOUT --- */
        .tactical-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            max-width: 1600px;
            margin: 0 auto;
        }}

        /* --- PLAYER CARD --- */
        .player-panel {{
            background: var(--glass);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
            backdrop-filter: blur(15px);
            animation: slideIn 0.8s ease-out;
            position: relative;
            overflow: hidden;
        }}
        
        /* Effet de lueur sur les bords */
        .panel-p1 {{ border-top: 4px solid var(--p1-main); box-shadow: 0 0 30px rgba(0, 229, 255, 0.1); }}
        .panel-p2 {{ border-top: 4px solid var(--p2-main); box-shadow: 0 0 30px rgba(255, 23, 68, 0.1); }}

        .panel-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            padding-bottom: 10px;
        }}
        .p-name {{ font-size: 1.8em; font-weight: 700; text-transform: uppercase; }}
        .p-ai {{ background: rgba(255,255,255,0.1); padding: 2px 8px; border-radius: 4px; font-size: 0.8em; }}

        /* Stats Blocks */
        .stats-row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 20px; }}
        .stat-box {{ background: rgba(0,0,0,0.3); padding: 10px; border-radius: 6px; text-align: center; }}
        .stat-val {{ font-size: 1.4em; font-weight: bold; display: block; }}
        .stat-lbl {{ font-size: 0.7em; color: #aaa; text-transform: uppercase; }}

        /* --- UNIT LIST --- */
        .unit-scroll {{ max-height: 600px; overflow-y: auto; padding-right: 5px; }}
        
        .unit-row {{
            display: flex;
            align-items: center;
            background: rgba(255,255,255,0.03);
            margin-bottom: 8px;
            padding: 10px;
            border-radius: 6px;
            transition: all 0.2s;
            border-left: 3px solid transparent;
        }}
        .unit-row:hover {{ background: rgba(255,255,255,0.08); transform: translateX(5px); }}
        
        .unit-icon {{ font-size: 1.2em; width: 40px; text-align: center; opacity: 0.8; }}
        .unit-info {{ flex-grow: 1; }}
        .unit-id {{ font-size: 0.8em; color: #666; font-family: monospace; }}
        
        .hp-track {{ width: 100%; height: 4px; background: #333; margin-top: 5px; border-radius: 2px; }}
        .hp-fill {{ height: 100%; border-radius: 2px; box-shadow: 0 0 5px currentColor; }}
        
        .unit-action {{ font-size: 0.75em; font-weight: bold; padding: 3px 8px; border-radius: 4px; min-width: 70px; text-align: center; }}
        
        .act-attack {{ color: #ff5252; border: 1px solid #ff5252; box-shadow: 0 0 5px rgba(255,82,82,0.3); animation: pulse 1s infinite; }}
        .act-move {{ color: #40c4ff; border: 1px solid #40c4ff; }}
        .act-idle {{ color: #78909c; border: 1px solid #546e7a; }}

        @keyframes pulse {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0.6; }} 100% {{ opacity: 1; }} }}
    </style>
</head>
<body>

<div class="hud-header">
    <div class="hud-title"><h1>MEDIEVALI <span>OPS</span></h1></div>
    <div class="hud-time">T + {game_time:.2f}s</div>
</div>

<div class="balance-container">
    <div class="balance-label">Estimation de la Domination du Champ de Bataille</div>
    <div class="balance-bar">
        <div class="bar-segment seg-p1">{int(domination_p1)}%</div>
        <div class="bar-segment seg-p2">{int(domination_p2)}%</div>
    </div>
</div>

<div class="tactical-grid">
"""

    # --- GENERATION DES CARTES JOUEURS ---
    players_data = [
        (p1, u1_alive, u1_total, hp1_avg, "panel-p1", "var(--p1-main)"),
        (p2, u2_alive, u2_total, hp2_avg, "panel-p2", "var(--p2-main)")
    ]

    for p, alive, total, avg_hp, panel_class, color_var in players_data:
        ai_name = getattr(p, "general", None).__class__.__name__ if hasattr(p, "general") else "IA"
        
        html_content += f"""
    <div class="player-panel {panel_class}">
        <div class="panel-header">
            <div>
                <div class="p-name" style="color: {color_var}">{p.name}</div>
                <span class="p-ai">{ai_name}</span>
            </div>
        </div>

        <div class="stats-row">
            <div class="stat-box">
                <span class="stat-val" style="color: {color_var}">{len(alive)} <span style="font-size:0.5em; color:#666">/{total}</span></span>
                <span class="stat-lbl">Unités Actives</span>
            </div>
            <div class="stat-box">
                <span class="stat-val" style="color: #fff">{int(avg_hp)}%</span>
                <span class="stat-lbl">Santé Moyenne</span>
            </div>
        </div>

        <div class="unit-scroll">
        """
        
        if not alive:
             html_content += f"<div style='text-align:center; padding:40px; color:#555; font-style:italic'>// SIGNAL PERDU - ARMÉE DÉTRUITE //</div>"

        for u in alive:
            hp_pct = (u.current_hp / u.max_hp) * 100 if u.max_hp > 0 else 0
            
            # Couleur dynamique HP
            hp_color = "#00e676" # Vert
            if hp_pct < 60: hp_color = "#ffea00" # Jaune
            if hp_pct < 30: hp_color = "#ff1744" # Rouge
            
            # Status
            order_str = str(u.current_order).lower() if hasattr(u, 'current_order') else "none"
            act_class = "act-idle"
            act_txt = "EN ATTENTE"
            
            if "attack" in order_str: 
                act_class = "act-attack"
                act_txt = "COMBAT"
            elif "move" in order_str: 
                act_class = "act-move"
                act_txt = "MARCHE"

            icon = "◆" 
            if "knight" in str(u.get_symbol()).lower(): icon = "♞"
            elif "p" in str(u.get_symbol()).lower(): icon = "♟"

            html_content += f"""
            <div class="unit-row" style="border-left-color: {hp_color}">
                <div class="unit-icon" style="color:{color_var}">{icon}</div>
                <div class="unit-info">
                    <div style="font-weight:600">UNITÉ <span class="unit-id">#{id(u)%1000}</span></div>
                    <div class="hp-track"><div class="hp-fill" style="width:{hp_pct}%; background:{hp_color}; color:{hp_color}"></div></div>
                </div>
                <div style="text-align:right; margin-left:10px;">
                    <div class="unit-action {act_class}">{act_txt}</div>
                    <div style="font-size:0.7em; color:#555; margin-top:4px;">POS: {int(u.x)}, {int(u.y)}</div>
                </div>
            </div>
            """
        
        html_content += "</div></div>" # Fin panel

    html_content += """
</div>
</body>
</html>
"""

    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"✨ HUD Généré : {filename}")

    # --- OUVERTURE FORCEE (Spécial Linux/Sudo) ---
    # Le problème avec sudo est qu'il lance les commandes en tant que root,
    # et les navigateurs modernes refusent de se lancer en root pour des raisons de sécurité.
    
    # 1. On cherche le navigateur
    browser_cmd = None
    if shutil.which('firefox'): browser_cmd = 'firefox'
    elif shutil.which('google-chrome'): browser_cmd = 'google-chrome'
    elif shutil.which('chromium'): browser_cmd = 'chromium'
    elif shutil.which('xdg-open'): browser_cmd = 'xdg-open'

    if browser_cmd:
        print(f"🚀 Tentative d'ouverture avec {browser_cmd}...")
        try:
            # On essaie d'ouvrir le fichier
            subprocess.Popen([browser_cmd, filename], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        except OSError:
            print(f"⚠️ Échec de l'ouverture automatique. Le mode 'sudo' bloque peut-être le navigateur.")
            print(f"👉 CLIQUEZ ICI : file://{filename}")
    else:
        # Fallback Python standard
        webbrowser.open('file://' + filename)