import os
import shutil
import pathlib
import sys

def get_yes_no(prompt):
    """Demande une confirmation (y/n) à l'utilisateur."""
    while True:
        choice = input(f"{prompt} (y/n) : ").strip().lower()
        if choice == 'y':
            return True
        if choice == 'n':
            return False
        print("Veuillez répondre par 'y' (oui) ou 'n' (non).")

def main():
    """Fonction principale du script de sauvegarde."""
    print("--- Bienvenue dans Backup_Maker ---")
    print("\n")
    
    # 1. Demander le fichier Backup.txt
    print("Veuillez indiquer le chemin vers votre fichier 'Backup.txt'.")
    print("Ce fichier doit contenir un chemin de fichier ou de dossier par ligne.")
    print("Exemple de format :")
    print(r"  Z:\Scripts\MonScript.ahk")
    print(r"  C:\Users\Ephraem\Documents")
    print(r'  "Z:\Un autre\fichier.log"')
    print('\nLes guillemets (") au début et à la fin seront automatiquement ignorés.\n')
    
    backup_file_path_str = input("Chemin vers votre Backup.txt : ").strip().strip('"')
    
    backup_file_path = pathlib.Path(backup_file_path_str)
    
    if not backup_file_path.is_file():
        print(f"ERREUR : Le fichier '{backup_file_path}' n'a pas été trouvé.")
        print("Opération annulée.")
        sys.exit()

    # Lire les chemins depuis le fichier .txt
    try:
        with open(backup_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"ERREUR : Impossible de lire le fichier : {e}")
        sys.exit()

    # 2. Demander le dossier de sortie
    print("\n")
    print("Où souhaitez-vous enregistrer la sauvegarde ?")
    print("Indiquez le dossier parent. Un dossier nommé 'Backup' sera créé")
    print("automatiquement à l'intérieur de celui-ci pour contenir vos fichiers.")
    print(r"Exemple : Si vous indiquez 'Z:\Sauvegardes',")
    print(r"les fichiers iront dans 'Z:\Sauvegardes\Backup'")
    print("\n")
    
    output_parent_dir_str = input("Dossier de sortie (parent) : ").strip().strip('"')
    
    output_parent_dir = pathlib.Path(output_parent_dir_str)
    
    if not output_parent_dir.is_dir():
        print(f"ERREUR : Le dossier parent '{output_parent_dir}' n'existe pas.")
        print("Opération annulée.")
        sys.exit()

    # Définir le dossier de sauvegarde final
    backup_root = output_parent_dir / "Backup"
    
    try:
        backup_root.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"ERREUR : Impossible de créer le dossier de destination '{backup_root}': {e}")
        sys.exit()

    print(f"\nLa sauvegarde sera effectuée dans : {backup_root}")

    # Initialiser les listes pour le rapport final
    copied_items = []
    missing_items = []
    error_items = []
    
    # 3. Vérification et copie
    print("\n--- Démarrage de la vérification et de la copie ---")
    
    paths_to_process = []

    # Étape de vérification d'existence
    for line in lines:
        path_str = line.strip().strip('"')
        
        if not path_str:  # Ignorer les lignes vides
            continue
            
        source_path = pathlib.Path(path_str)
        
        if not source_path.exists():
            print(f"ATTENTION : Le chemin '{source_path}' n'a pas été trouvé.")
            missing_items.append(str(source_path))
            
            if not get_yes_no("Voulez-vous continuer en ignorant ce chemin ?"):
                print("Opération annulée par l'utilisateur.")
                sys.exit()
        else:
            paths_to_process.append(source_path)

    if not paths_to_process:
        print("Aucun fichier valide à copier n'a été trouvé.")
        sys.exit()

    print("\n--- Copie des fichiers en cours ---")

    # Étape de copie
    for source_path in paths_to_process:
        try:
            # Recréer la structure : Z:\Scripts\Fichier.txt -> Backup\Z\Scripts\Fichier.txt
            
            # 1. Obtenir le nom du lecteur (ex: 'Z')
            drive_name = source_path.parts[0].strip(':\\')
            
            # 2. Obtenir le reste du chemin (ex: 'Scripts', 'Fichier.txt')
            path_remainder = source_path.parts[1:]
            
            # 3. Construire le chemin de destination
            dest_path = backup_root.joinpath(drive_name, *path_remainder)

            if source_path.is_file():
                # Créer les dossiers parents pour le fichier
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                # Copier le fichier en préservant les métadonnées (date, etc.)
                shutil.copy2(source_path, dest_path)
                print(f"COPIÉ (Fichier) : {source_path}")
                copied_items.append(str(source_path))
                
            elif source_path.is_dir():
                # Copier l'arborescence complète du dossier
                shutil.copytree(source_path, dest_path, dirs_exist_ok=True)
                print(f"COPIÉ (Dossier) : {source_path}")
                copied_items.append(str(source_path))

        except Exception as e:
            print(f"ERREUR lors de la copie de '{source_path}' : {e}")
            error_items.append(str(source_path))

    # 4. Rapport final
    print("\n\n--- Rapport de sauvegarde terminé ---")
    print(f"Destination : {backup_root}")

    print(f"\nÉléments copiés avec succès ({len(copied_items)}) :")
    if copied_items:
        for item in copied_items:
            print(f"  - {item}")
    else:
        print("  (Aucun)")

    print(f"\nÉléments non trouvés et ignorés ({len(missing_items)}) :")
    if missing_items:
        for item in missing_items:
            print(f"  - {item}")
    else:
        print("  (Aucun)")

    print(f"\nÉléments ayant échoué lors de la copie ({len(error_items)}) :")
    if error_items:
        for item in error_items:
            print(f"  - {item}")
    else:
        print("  (Aucun)")

    print("\nOpération terminée.")

if __name__ == "__main__":
    main()