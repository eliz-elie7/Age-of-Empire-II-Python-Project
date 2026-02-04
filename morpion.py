#!/usr/bin/env python3
"""
Jeu de Morpion (Tic-Tac-Toe) avec interface graphique
Tic-Tac-Toe game with graphical interface using tkinter
"""

import tkinter as tk
from tkinter import messagebox


class MorpionGame:
    """Classe principale pour le jeu de morpion"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Jeu de Morpion - Tic-Tac-Toe")
        self.root.resizable(False, False)
        
        # État du jeu
        self.current_player = "X"
        self.board = [""] * 9
        self.buttons = []
        self.score_x = 0
        self.score_o = 0
        self.game_active = True
        
        # Créer l'interface
        self.create_widgets()
        
    def create_widgets(self):
        """Créer tous les widgets de l'interface"""
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg="#2c3e50", padx=20, pady=20)
        main_frame.pack()
        
        # Titre
        title_label = tk.Label(
            main_frame,
            text="🎮 JEU DE MORPION 🎮",
            font=("Arial", 24, "bold"),
            bg="#2c3e50",
            fg="#ecf0f1"
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # Indicateur du joueur actuel
        self.player_label = tk.Label(
            main_frame,
            text=f"Joueur actuel: {self.current_player}",
            font=("Arial", 16),
            bg="#2c3e50",
            fg="#ecf0f1"
        )
        self.player_label.grid(row=1, column=0, columnspan=3, pady=(0, 10))
        
        # Frame pour le plateau de jeu
        game_frame = tk.Frame(main_frame, bg="#34495e", padx=5, pady=5)
        game_frame.grid(row=2, column=0, columnspan=3, pady=(0, 10))
        
        # Créer les 9 boutons pour le plateau
        for i in range(9):
            btn = tk.Button(
                game_frame,
                text="",
                font=("Arial", 32, "bold"),
                width=5,
                height=2,
                bg="#ecf0f1",
                fg="#2c3e50",
                activebackground="#bdc3c7",
                command=lambda idx=i: self.make_move(idx)
            )
            row = i // 3
            col = i % 3
            btn.grid(row=row, column=col, padx=2, pady=2)
            self.buttons.append(btn)
        
        # Frame pour les scores
        score_frame = tk.Frame(main_frame, bg="#2c3e50")
        score_frame.grid(row=3, column=0, columnspan=3, pady=(10, 10))
        
        self.score_label = tk.Label(
            score_frame,
            text=f"Score - X: {self.score_x}  |  O: {self.score_o}",
            font=("Arial", 14),
            bg="#2c3e50",
            fg="#ecf0f1"
        )
        self.score_label.pack()
        
        # Boutons de contrôle
        control_frame = tk.Frame(main_frame, bg="#2c3e50")
        control_frame.grid(row=4, column=0, columnspan=3)
        
        reset_btn = tk.Button(
            control_frame,
            text="Nouvelle Partie",
            font=("Arial", 12, "bold"),
            bg="#3498db",
            fg="white",
            activebackground="#2980b9",
            padx=15,
            pady=8,
            command=self.reset_game
        )
        reset_btn.pack(side=tk.LEFT, padx=5)
        
        reset_score_btn = tk.Button(
            control_frame,
            text="Réinitialiser Score",
            font=("Arial", 12, "bold"),
            bg="#e74c3c",
            fg="white",
            activebackground="#c0392b",
            padx=15,
            pady=8,
            command=self.reset_score
        )
        reset_score_btn.pack(side=tk.LEFT, padx=5)
        
        quit_btn = tk.Button(
            control_frame,
            text="Quitter",
            font=("Arial", 12, "bold"),
            bg="#95a5a6",
            fg="white",
            activebackground="#7f8c8d",
            padx=15,
            pady=8,
            command=self.root.quit
        )
        quit_btn.pack(side=tk.LEFT, padx=5)
        
    def make_move(self, index):
        """Gérer un coup joué"""
        if not self.game_active:
            return
            
        if self.board[index] == "":
            # Mettre à jour le plateau
            self.board[index] = self.current_player
            
            # Mettre à jour le bouton avec la couleur appropriée
            color = "#e74c3c" if self.current_player == "X" else "#3498db"
            self.buttons[index].config(
                text=self.current_player,
                fg=color,
                state=tk.DISABLED
            )
            
            # Vérifier si quelqu'un a gagné
            if self.check_winner():
                self.game_active = False
                self.show_winner(self.current_player)
                if self.current_player == "X":
                    self.score_x += 1
                else:
                    self.score_o += 1
                self.update_score()
                return
            
            # Vérifier le match nul
            if "" not in self.board:
                self.game_active = False
                self.show_draw()
                return
            
            # Changer de joueur
            self.current_player = "O" if self.current_player == "X" else "X"
            self.update_player_label()
    
    def check_winner(self):
        """Vérifier s'il y a un gagnant"""
        # Toutes les combinaisons gagnantes possibles
        winning_combinations = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Lignes
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Colonnes
            [0, 4, 8], [2, 4, 6]              # Diagonales
        ]
        
        for combo in winning_combinations:
            if (self.board[combo[0]] == self.board[combo[1]] == 
                self.board[combo[2]] != ""):
                # Mettre en évidence la combinaison gagnante
                for idx in combo:
                    self.buttons[idx].config(bg="#2ecc71")
                return True
        return False
    
    def show_winner(self, winner):
        """Afficher le message de victoire"""
        message = f"🎉 Le joueur {winner} a gagné! 🎉"
        messagebox.showinfo("Victoire!", message)
    
    def show_draw(self):
        """Afficher le message de match nul"""
        messagebox.showinfo("Match nul!", "🤝 Match nul! Aucun gagnant. 🤝")
    
    def update_player_label(self):
        """Mettre à jour l'indicateur du joueur actuel"""
        self.player_label.config(text=f"Joueur actuel: {self.current_player}")
    
    def update_score(self):
        """Mettre à jour l'affichage du score"""
        self.score_label.config(text=f"Score - X: {self.score_x}  |  O: {self.score_o}")
    
    def reset_game(self):
        """Réinitialiser le jeu pour une nouvelle partie"""
        self.current_player = "X"
        self.board = [""] * 9
        self.game_active = True
        
        for btn in self.buttons:
            btn.config(
                text="",
                state=tk.NORMAL,
                bg="#ecf0f1",
                fg="#2c3e50"
            )
        
        self.update_player_label()
    
    def reset_score(self):
        """Réinitialiser les scores"""
        self.score_x = 0
        self.score_o = 0
        self.update_score()
        self.reset_game()


def main():
    """Fonction principale pour lancer le jeu"""
    root = tk.Tk()
    game = MorpionGame(root)
    
    # Centrer la fenêtre
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()


if __name__ == "__main__":
    main()
