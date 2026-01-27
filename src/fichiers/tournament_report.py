import datetime
import os

FILENAME = "tournament_results.html"

def generate_tournament_report(stats, generals, scenarios):
    """
    Génère un rapport HTML complet basé sur les statistiques du tournoi.
    """
    css = """
    <style>
        body { background: #1a1b26; color: #a9b1d6; font-family: sans-serif; padding: 20px; line-height: 1.5; }
        h1, h2 { color: #7aa2f7; text-align: center; border-bottom: 2px solid #414868; padding-bottom: 10px; }
        table { width: 100%; border-collapse: collapse; margin-bottom: 40px; background: #24283b; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
        th, td { border: 1px solid #414868; padding: 12px; text-align: center; }
        th { background: #16161e; color: #7aa2f7; text-transform: uppercase; letter-spacing: 1px; }
        tr:hover { background: #2e344e; }
        .win-high { background: rgba(158, 206, 106, 0.2); color: #9ece6a; font-weight: bold; }
        .win-med { color: #bb9af7; }
        .win-low { background: rgba(247, 118, 118, 0.2); color: #f7768e; }
        .draw-cell { color: #565f89; font-style: italic; }
        .self-match { background: #1f2335; color: #565f89; opacity: 0.6; }
        .stats-detail { font-size: 0.85em; color: #565f89; margin-top: 4px; border-top: 1px solid #414868; padding-top: 4px; }
    </style>
    """

    html = f"""<!DOCTYPE html>
<html>
<head><meta charset='utf-8'><title>Rapport de Tournoi IA</title>{css}</head>
<body>
    <h1>🏆 RÉSULTATS DU TOURNOI AUTOMATISÉ</h1>
    <p style='text-align:center'>Généré le {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
    """

    # --- PARTIE 1 : CLASSEMENT GÉNÉRAL ---
    # Cette section agrège tous les résultats de la matrice pour donner un score global.
    html += "<h2>1. Classement Général (Toutes maps confondues)</h2>"
    html += "<table><tr><th>Général</th><th>Victoires</th><th>Nuls</th><th>Matchs Joués</th><th>% Victoire</th></tr>"
    
    global_stats = {g: {'wins': 0, 'draws': 0, 'total': 0} for g in generals}
    for sc in scenarios:
        for g1 in generals:
            for g2 in generals:
                if g2 in stats[sc][g1]:
                    d = stats[sc][g1][g2]
                    global_stats[g1]['wins'] += d['wins']
                    global_stats[g1]['draws'] += d.get('draws', 0)
                    global_stats[g1]['total'] += d['matches']

    # Tri par taux de victoire décroissant
    sorted_gens = sorted(generals, key=lambda g: (global_stats[g]['wins']/global_stats[g]['total'] if global_stats[g]['total']>0 else 0), reverse=True)

    for g in sorted_gens:
        s = global_stats[g]
        pct = (s['wins'] / s['total'] * 100) if s['total'] > 0 else 0
        color = "win-high" if pct > 60 else "win-low" if pct < 40 else "win-med"
        html += f"<tr><td><strong>{g}</strong></td><td>{s['wins']}</td><td class='draw-cell'>{s['draws']}</td><td>{s['total']}</td><td class='{color}'>{pct:.1f}%</td></tr>"
    html += "</table>"

    # --- PARTIE 2 : MATRICE CROISÉE ---
    # C'est ici que l'on voit les duels directs (Ligne vs Colonne).
    html += "<h2>2. Matrice Croisée (Général vs Général)</h2>"
    html += "<table><tr><th>VS</th>" + "".join([f"<th>{g}</th>" for g in generals]) + "</tr>"
    
    for g1 in generals:
        html += f"<tr><th>{g1}</th>"
        for g2 in generals:
            w, d, t = 0, 0, 0
            # On cumule les résultats de ce duel sur tous les scénarios
            for sc in scenarios:
                if g2 in stats[sc][g1]:
                    w += stats[sc][g1][g2]['wins']
                    d += stats[sc][g1][g2].get('draws', 0)
                    t += stats[sc][g1][g2]['matches']
            
            pct = (w / t * 100) if t > 0 else 0
            # Style visuel selon la performance
            cls = "self-match" if g1 == g2 else ("win-high" if pct > 55 else "win-low" if pct < 45 else "")
            html += f"<td class='{cls}'><strong>{pct:.1f}%</strong><div class='stats-detail'>Nuls: {d} | Total: {t}</div></td>"
        html += "</tr>"
    html += "</table>"

    # --- PARTIE 3 : PERFORMANCE PAR SCÉNARIO ---
    # Pour voir quelle IA est la meilleure sur "lanchester" vs "skirmish".
    html += "<h2>3. Performance par Scénario</h2>"
    html += "<table><tr><th>Général</th>" + "".join([f"<th>{sc}</th>" for sc in scenarios]) + "</tr>"
    
    for g in generals:
        html += f"<tr><th>{g}</th>"
        for sc in scenarios:
            # On calcule le taux de victoire de g contre TOUS les opposants sur ce scénario précis
            w = sum(stats[sc][g][opp]['wins'] for opp in generals if opp in stats[sc][g])
            t = sum(stats[sc][g][opp]['matches'] for opp in generals if opp in stats[sc][g])
            pct = (w/t*100) if t > 0 else 0
            html += f"<td>{pct:.1f}%</td>"
        html += "</tr>"
    html += "</table>"

    html += "</body></html>"
    
    with open(FILENAME, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"📊 Rapport HTML généré avec succès : {FILENAME}")