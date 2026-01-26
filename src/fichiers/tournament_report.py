# src/fichiers/tournament_report.py
import datetime
import os

FILENAME = "tournament_results.html"

def generate_tournament_report(stats, generals, scenarios):
    """
    Génère un rapport HTML complet avec matrices de scores.
    stats = {scenario: {g1: {g2: {'wins': x, 'matches': y}}}}
    """
    
    css = """
    <style>
        body { background: #1a1b26; color: #a9b1d6; font-family: sans-serif; padding: 20px; }
        h1, h2 { color: #7aa2f7; text-align: center; }
        table { width: 100%; border-collapse: collapse; margin-bottom: 30px; background: #24283b; }
        th, td { border: 1px solid #414868; padding: 10px; text-align: center; }
        th { background: #16161e; color: #fff; }
        .win-high { background: rgba(0, 255, 0, 0.2); color: #fff; }
        .win-med { color: #eee; }
        .win-low { background: rgba(255, 0, 0, 0.2); color: #fff; }
        .self-match { background: #2e3c64; font-style: italic; }
    </style>
    """

    html = f"""<!DOCTYPE html>
<html>
<head><meta charset='utf-8'><title>Rapport de Tournoi</title>{css}</head>
<body>
    <h1>🏆 RÉSULTATS DU TOURNOI AUTOMATISÉ</h1>
    <p style='text-align:center'>Généré le {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
    """

    # --- 1. CLASSEMENT GÉNÉRAL (GLOBAL SCORE) ---
    html += "<h2>1. Classement Général (Toutes maps confondues)</h2>"
    html += "<table><tr><th>Général</th><th>Victoires</th><th>Matchs Joués</th><th>% Victoire</th></tr>"
    
    global_stats = {g: {'wins': 0, 'total': 0} for g in generals}
    
    for sc in scenarios:
        for g1 in generals:
            for g2 in generals:
                if g2 in stats[sc][g1]:
                    data = stats[sc][g1][g2]
                    global_stats[g1]['wins'] += data['wins']
                    global_stats[g1]['total'] += data['matches']

    # Tri par pourcentage
    sorted_gens = sorted(generals, key=lambda g: (global_stats[g]['wins']/global_stats[g]['total'] if global_stats[g]['total']>0 else 0), reverse=True)

    for g in sorted_gens:
        w = global_stats[g]['wins']
        t = global_stats[g]['total']
        pct = (w / t * 100) if t > 0 else 0
        color = "win-high" if pct > 60 else "win-low" if pct < 40 else "win-med"
        html += f"<tr><td>{g}</td><td>{w}</td><td>{t}</td><td class='{color}'><strong>{pct:.1f}%</strong></td></tr>"
    html += "</table>"

    # --- 2. MATRICE GÉNÉRAL vs GÉNÉRAL (Cross-table) ---
    html += "<h2>2. Matrice Croisée (Général vs Général)</h2>"
    html += "<table><tr><th>VS</th>" + "".join([f"<th>{g}</th>" for g in generals]) + "</tr>"
    
    for g1 in generals:
        html += f"<tr><th>{g1}</th>"
        for g2 in generals:
            # Aggréger sur tous les scénarios
            w, t = 0, 0
            for sc in scenarios:
                if g2 in stats[sc][g1]:
                    w += stats[sc][g1][g2]['wins']
                    t += stats[sc][g1][g2]['matches']
            
            pct = (w / t * 100) if t > 0 else 0
            cls = "self-match" if g1 == g2 else ("win-high" if pct > 55 else "win-low" if pct < 45 else "")
            
            # Pour le "self-match" (g1 vs g1), on veut voir ~50%
            txt = f"{pct:.1f}%"
            if g1 == g2:
                # Alerte si déséquilibre en miroir (> 55 ou < 45 c'est louche)
                if t > 0 and (pct > 60 or pct < 40): txt += " ⚠️ BIAIS"
            
            html += f"<td class='{cls}'>{txt}<br><small>{w}/{t}</small></td>"
        html += "</tr>"
    html += "</table>"

    # --- 3. PERFORMANCE PAR SCÉNARIO ---
    html += "<h2>3. Performance par Scénario</h2>"
    html += "<table><tr><th>Général</th>" + "".join([f"<th>{sc}</th>" for sc in scenarios]) + "</tr>"
    
    for g in generals:
        html += f"<tr><th>{g}</th>"
        for sc in scenarios:
            w = sum(stats[sc][g][opp]['wins'] for opp in generals)
            t = sum(stats[sc][g][opp]['matches'] for opp in generals)
            pct = (w/t*100) if t > 0 else 0
            html += f"<td>{pct:.1f}%</td>"
        html += "</tr>"
    html += "</table>"

    html += "</body></html>"
    
    with open(FILENAME, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"📊 Rapport détaillé généré : {os.path.abspath(FILENAME)}")