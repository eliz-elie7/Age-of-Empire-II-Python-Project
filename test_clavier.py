# test_clavier.py
import sys
import termios
import tty
import select

def test_input():
    print("=== TEST CLAVIER ===")
    print("Appuie sur des touches (TAB, P, A, etc.).")
    print("Appuie sur 'Q' pour quitter.")
    
    # Vérification TTY
    if not sys.stdin.isatty():
        print("❌ ERREUR FATALE : Ce terminal ne supporte pas le mode interactif.")
        print("   Solution : Lance ce script depuis un VRAI terminal (Gnome Terminal, cmd.exe).")
        return

    print("✅ Terminal compatible détecté.")

    old_settings = termios.tcgetattr(sys.stdin)
    try:
        tty.setcbreak(sys.stdin.fileno())
        
        while True:
            # On attend qu'une touche soit pressée
            if select.select([sys.stdin], [], [], 0)[0]:
                key = sys.stdin.read(1)
                code = ord(key)
                print(f"--> Touche reçue : '{key}' (Code ASCII: {code})")
                
                if key == '\t' or code == 9:
                    print("    VICTOIRE ! La touche TAB est bien détectée !")
                
                if key.lower() == 'q':
                    break
    except Exception as e:
        print(f"❌ Erreur : {e}")
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        print("Fin du test.")

if __name__ == "__main__":
    test_input()