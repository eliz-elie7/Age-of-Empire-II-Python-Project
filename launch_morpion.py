#!/usr/bin/env python3
"""
Lanceur du jeu de Morpion
Tic-Tac-Toe Game Launcher

Ce script lance le jeu de morpion dans le navigateur web par défaut.
This script launches the tic-tac-toe game in the default web browser.
"""

import webbrowser
import http.server
import socketserver
import os
import sys
from pathlib import Path
import threading
import time


def find_free_port(start_port=8000, max_attempts=10):
    """Trouve un port libre pour le serveur HTTP"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socketserver.TCPServer(("", port), None) as _:
                return port
        except OSError:
            continue
    return None


def main():
    """Lance le jeu de morpion dans le navigateur"""
    # Obtenir le chemin du fichier HTML
    script_dir = Path(__file__).parent.absolute()
    html_file = script_dir / "morpion.html"
    
    if not html_file.exists():
        print(f"❌ Erreur: Le fichier {html_file} n'existe pas!")
        print(f"❌ Error: File {html_file} does not exist!")
        sys.exit(1)
    
    # Trouver un port libre
    port = find_free_port()
    if port is None:
        print("❌ Erreur: Impossible de trouver un port libre!")
        print("❌ Error: Could not find a free port!")
        sys.exit(1)
    
    # Changer vers le répertoire contenant le fichier HTML
    os.chdir(script_dir)
    
    # Créer le serveur HTTP
    Handler = http.server.SimpleHTTPRequestHandler
    
    def start_server():
        with socketserver.TCPServer(("", port), Handler) as httpd:
            print(f"🌐 Serveur HTTP démarré sur le port {port}")
            print(f"🌐 HTTP Server started on port {port}")
            print(f"📍 URL: http://localhost:{port}/morpion.html")
            print("\n🎮 Le jeu va s'ouvrir dans votre navigateur...")
            print("🎮 The game will open in your browser...\n")
            print("⏹️  Appuyez sur Ctrl+C pour arrêter le serveur")
            print("⏹️  Press Ctrl+C to stop the server\n")
            httpd.serve_forever()
    
    # Démarrer le serveur dans un thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Attendre que le serveur démarre
    time.sleep(1)
    
    # Ouvrir le navigateur
    url = f"http://localhost:{port}/morpion.html"
    try:
        webbrowser.open(url)
        print("✅ Navigateur ouvert avec succès!")
        print("✅ Browser opened successfully!")
    except Exception as e:
        print(f"⚠️  Impossible d'ouvrir le navigateur automatiquement: {e}")
        print(f"⚠️  Could not open browser automatically: {e}")
        print(f"🔗 Veuillez ouvrir manuellement: {url}")
        print(f"🔗 Please open manually: {url}")
    
    try:
        # Garder le script en cours d'exécution
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n👋 Arrêt du serveur...")
        print("👋 Stopping server...")
        print("✅ Au revoir! / Goodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()
