import os
try:
    os.remove("history.html")
    print("✅ Historique supprimé avec succès. Le prochain combat en créera un nouveau.")
except FileNotFoundError:
    print("⚠️ Aucun historique trouvé.")