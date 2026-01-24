# src/data_exporter.py
import os

def save_battle_report(filename, battle, args):
    """
    Exporte les données finales de la bataille dans un fichier HTML.
    """
    
    winner_name = battle.winner.name if battle.winner else "Match Nul"
    color_win = "#2ecc71" if battle.winner else "#95a5a6" 
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <title>Export Données - {args.scenario}</title>
        <style>
            body {{ font-family: 'Consolas', 'Monaco', monospace; background-color: #1e1e1e; color: #d4d4d4; padding: 20px; }}
            .container {{ max-width: 900px; margin: 0 auto; background: #252526; padding: 20px; border: 1px solid #333; }}
            h1 {{ color: #569cd6; border-bottom: 1px solid #333; padding-bottom: 10px; }}
            .summary {{ background-color: #333333; padding: 15px; margin-bottom: 20px; border-left: 4px solid {color_win}; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 0.9em; }}
            th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #333; }}
            th {{ background-color: #0e639c; color: white; }}
            tr:nth-child(even) {{ background-color: #2d2d2d; }}
            .unit-alive {{ color: #4ec9b0; }}
            .unit-dead {{ color: #f44747; text-decoration: line-through; opacity: 0.6; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>💾 EXPORT DE DONNÉES DE BATAILLE</h1>
            
            <div class="summary">
                <p><strong>SCENARIO :</strong> {args.scenario}</p>
                <p><strong>IA 1 :</strong> {args.ai_a}</p>
                <p><strong>IA 2 :</strong> {args.ai_b}</p>
                <p><strong>RÉSULTAT :</strong> <span style="color:{color_win}">{winner_name}</span></p>
                <p><strong>DURÉE :</strong> {battle.time:.2f}s</p>
            </div>

            <h2>📋 LISTE DES UNITÉS</h2>
    """

    for player in battle.players:
        alive_count = len([u for u in player.squad if u.is_alive])
        html_content += f"""
            <h3 style="color: #ce9178;">{player.name} ({alive_count} vivants)</h3>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Type</th>
                        <th>PV</th>
                        <th>Pos X</th>
                        <th>Pos Y</th>
                        <th>Statut</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for u in player.squad:
            state_class = "unit-alive" if u.is_alive else "unit-dead"
            hp_text = f"{u.current_hp:.1f}" if u.is_alive else "0.0"
            status = "ACTIF" if u.is_alive else "ÉLIMINÉ"
            
            type_name = u.type.name if hasattr(u, 'type') else "UNIT"

            html_content += f"""
                    <tr class="{state_class}">
                        <td>#{id(u) % 10000}</td>
                        <td>{type_name}</td>
                        <td>{hp_text}</td>
                        <td>{u.x:.2f}</td>
                        <td>{u.y:.2f}</td>
                        <td>{status}</td>
                    </tr>
            """
        html_content += "</tbody></table>"

    html_content += "</div></body></html>"

    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"✅ Données exportées vers : {os.path.abspath(filename)}")
    except Exception as e:
        print(f"❌ Erreur export : {e}")