import os

def find_and_list_files(directory=".", extension=".ahk"):
    """
    Parcourt le répertoire spécifié (et ses sous-répertoires) 
    pour trouver tous les fichiers avec l'extension donnée et 
    enregistre leurs noms dans un fichier 'foundFiles.txt'.
    """
    found_files = []
    
    # Parcourt récursivement le répertoire
    # root est le chemin du dossier courant
    # dirs est la liste des sous-dossiers dans root
    # files est la liste des fichiers dans root
    for root, dirs, files in os.walk(directory):
        for file in files:
            # Vérifie si le fichier se termine par l'extension spécifiée (insensible à la casse)
            if file.lower().endswith(extension.lower()):
                # Construit le chemin complet du fichier
                full_path = os.path.join(root, file)
                found_files.append(full_path)

    # Écrit les noms de fichiers dans foundFiles.txt
    output_filename = "foundFiles.txt"
    try:
        with open(output_filename, 'w') as f:
            for filepath in found_files:
                f.write(filepath + '\n')
        print(f"✅ Opération terminée. {len(found_files)} fichiers '{extension}' trouvés.")
        print(f"Les noms de fichiers ont été enregistrés dans : **{output_filename}**")
    except IOError as e:
        print(f"❌ Erreur lors de l'écriture dans le fichier {output_filename}: {e}")

# Exécute la fonction pour le dossier courant ('.') et l'extension '.ahk'
if __name__ == "__main__":
    find_and_list_files(extension=".ahk")