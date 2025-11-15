#!/usr/bin/env python3
"""
ProjectManager.py

Outil CLI pour la gestion de projets créatifs.
Version : Stockage AppData + Option de nommage (Client - Projet)
"""

import os
import sys
import json
import shutil
import subprocess
import configparser
from datetime import datetime
from typing import List, Dict, Optional

# --- GESTION DES CHEMINS SYSTÈME (APPDATA) ---

def get_app_data_dir() -> str:
    """
    Récupère le chemin du dossier de configuration utilisateur.
    Force l'utilisation de [USER]/.config/ProjectsManager sur tous les OS.
    """
    APP_NAME = "ProjectsManager" 
    
    try:
        # On récupère le dossier utilisateur (ex: C:\Users\Toi ou /home/toi)
        user_home = os.path.expanduser('~')
        
        # On construit le chemin : [USER]/.config/TemplateMaker
        config_dir = os.path.join(user_home, '.config', APP_NAME)
        
        # Création du dossier s'il n'existe pas
        os.makedirs(config_dir, exist_ok=True)
        return config_dir

    except (OSError, TypeError) as e:
        print(f"[WARNING] Impossible d'accéder au dossier système: {e}")
        return os.getcwd()

# --- CONSTANTES & FICHIERS ---

APP_DIR = get_app_data_dir()
SETTINGS_FILE = os.path.join(APP_DIR, "settings.json")
PROJECTS_DB = os.path.join(APP_DIR, "projects.ini")
TEMPLATE_MAKER_SCRIPT = "TemplateMaker.py"

# --- GESTION DE LA CONFIGURATION (settings.json) ---

def load_settings() -> dict:
    """Charge les paramètres ou lance l'initialisation si absent/incomplet."""
    if not os.path.exists(SETTINGS_FILE):
        return init_settings()
    
    try:
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # Vérifications de compatibilité (Mise à jour des clés manquantes)
            needs_save = False
            
            if "Projects_Directory" not in data:
                print("[CONFIG] Le chemin des projets est manquant.")
                data["Projects_Directory"] = prompt_for_projects_dir()
                needs_save = True
                
            if "Title_AddCustomer" not in data:
                print("[CONFIG] Option détectée : Préfixe Client.")
                data["Title_AddCustomer"] = prompt_for_title_option()
                needs_save = True

            if needs_save:
                save_settings(data)
                
            return data
    except json.JSONDecodeError:
        print(f"[ERREUR] {SETTINGS_FILE} est corrompu. Réinitialisation.")
        return init_settings()

def prompt_for_projects_dir() -> str:
    """Demande le dossier racine où seront créés les projets."""
    while True:
        path = input("Chemin du dossier de Production (Output des projets): ").strip()
        if os.path.isdir(path):
            return path
        print(f"[ERREUR] Le dossier '{path}' n'existe pas ou est invalide.")

def prompt_for_title_option() -> bool:
    """Demande si on doit ajouter le nom du client au titre du dossier."""
    return input("Ajouter le nom du client dans le nom du dossier final ? (y/n): ").lower().strip() == 'y'

def init_settings() -> dict:
    """Workflow d'initialisation complet."""
    print(f"\n--- Initialisation de Project Manager ---")
    print(f"(Les fichiers de config seront stockés dans : {APP_DIR})")
    
    # 1. Dossier de production
    proj_dir = prompt_for_projects_dir()

    customers = []
    # 2. Clients
    print("\n--- Configuration des Clients ---")
    first_cust = input("Entrez le nom du premier Client (Defaut: 'Customer 1'): ").strip()
    if not first_cust:
        first_cust = "Customer 1"
    customers.append(first_cust)
    
    while True:
        more = input("Ajouter un autre client ? (y/n): ").lower().strip()
        if more == 'y':
            c = input("Nom du client: ").strip()
            if c: customers.append(c)
        else:
            break
            
    # 3. Steps
    steps = []
    print("\n--- Configuration des Étapes ---")
    while True:
        step = input("Ajouter une étape (laisser vide pour finir): ").strip()
        if not step:
            break
        steps.append(step)
        
    # 4. Google API
    print("\n--- Configuration Google ---")
    use_google = input("Activer l'intégration Google API ? (y/n): ").lower().strip() == 'y'
    
    # 5. Options de Nommage (NOUVEAU)
    add_cust_title = prompt_for_title_option()
    
    settings = {
        "Projects_Directory": proj_dir,
        "Title_AddCustomer": add_cust_title, # Nouvelle clé
        "GoogleAPI": False,
        "User_Wants_Google": use_google,
        "Customers": customers,
        "Steps": steps
    }
    
    save_settings(settings)
    return settings

def save_settings(data: dict):
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    print(f"[INFO] Configuration sauvegardée : {SETTINGS_FILE}")

# --- GESTION DE LA BASE DE DONNÉES (projects.ini) ---

def load_projects_db() -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    if not os.path.exists(PROJECTS_DB):
        with open(PROJECTS_DB, 'w', encoding='utf-8') as f:
            f.write("") 
    config.read(PROJECTS_DB, encoding='utf-8')
    return config

def save_projects_db(config: configparser.ConfigParser):
    with open(PROJECTS_DB, 'w', encoding='utf-8') as f:
        config.write(f)

# --- COMMANDES ---

def command_view():
    """Affiche les projets triés par client."""
    settings = load_settings()
    db = load_projects_db()
    
    print("\n--- TABLEAU DE BORD PROJETS ---")
    customers = settings.get("Customers", [])
    
    all_projects = []
    for section in db.sections():
        proj_data = {
            "Title": section,
            "Customer": db.get(section, "Customer", fallback="Inconnu"),
            "Deadline": db.get(section, "Deadline", fallback="--")
        }
        all_projects.append(proj_data)

    if not all_projects:
        print("Aucun projet en cours.")
    else:
        for cust in customers:
            cust_projects = [p for p in all_projects if p['Customer'] == cust]
            if cust_projects:
                print(f"\n[{cust.upper()}]")
                print(f"{'PROJET':<30} | {'DEADLINE':<15}")
                print("-" * 45)
                for p in cust_projects:
                    print(f"{p['Title']:<30} | {p['Deadline']:<15}")
                    
        orphans = [p for p in all_projects if p['Customer'] not in customers]
        if orphans:
            print(f"\n[AUTRES / INCONNUS]")
            for p in orphans:
                print(f"{p['Title']:<30} | {p['Deadline']:<15}")

    print("\n[Actions] (a)jouter, (d)elete, (q)uitter")
    choice = input(">> ").lower().strip()
    if choice == 'a':
        command_add()
    elif choice == 'd':
        command_delete()
    elif choice == 'q':
        sys.exit(0)
    else:
        command_view()

def command_add():
    """Workflow de création de projet."""
    settings = load_settings()
    
    print("\n--- NOUVEAU PROJET ---")
    
    # Phase 1: Data Collection
    customers = settings.get("Customers", [])
    if not customers:
        print("Aucun client configuré. Vérifiez settings.json.")
        return

    print("Sélectionnez un client :")
    for i, c in enumerate(customers):
        print(f"[{i+1}] {c}")
    
    while True:
        try:
            idx = int(input("Choix: ")) - 1
            if 0 <= idx < len(customers):
                selected_cust = customers[idx]
                break
            print("Numéro invalide.")
        except ValueError:
            print("Entrez un nombre.")

    project_title = input("Titre du projet (Nom du dossier): ").strip()
    while not project_title:
        print("Le titre ne peut pas être vide.")
        project_title = input("Titre du projet: ").strip()

    deadline = ""
    send_to_google = False
    
    if settings.get("GoogleAPI", False):
        date_str = input("Deadline (JJ-MM-AA) [Laisser vide pour ignorer]: ").strip()
        if date_str:
            try:
                datetime.strptime(date_str, "%d-%m-%y")
                deadline = date_str
                send_to_google = True
            except ValueError:
                print("Format de date invalide. Google Calendar ignoré.")
    
    # Phase 2: Review
    print("\n--- RÉSUMÉ ---")
    print(f"Client   : {selected_cust}")
    print(f"Projet   : {project_title}")
    print(f"Deadline : {deadline if deadline else 'Aucune'}")
    
    confirm = input("Confirmer ? (y/n/retry): ").lower().strip()
    if confirm == 'n':
        return
    elif confirm == 'retry':
        command_add()
        return

    # Phase 3: Google Integration (Stub)
    if send_to_google:
        print("[GOOGLE API] Fonctionnalité désactivée temporairement (Mock).")

    # Phase 4: Database Update
    db = load_projects_db()
    
    # Note : On utilise ici le titre "court" pour la base de données (plus lisible)
    # Mais si tu préfères que la clé DB soit aussi "Client - Projet", dis-le moi.
    # Pour l'instant je garde la logique du TDD initial : [Projet] Customer = X
    
    if db.has_section(project_title):
        print(f"[ATTENTION] Le projet '{project_title}' existe déjà dans la base de données.")
        choice = input("Écraser l'entrée DB ? (y/n): ")
        if choice.lower() != 'y':
            print("Annulation.")
            return
    else:
        db.add_section(project_title)
    
    db.set(project_title, "Customer", selected_cust)
    db.set(project_title, "Deadline", deadline if deadline else "N/A")
    save_projects_db(db)
    print("[DB] Base de données mise à jour.")

    # Phase 5: File System Generation
    projects_root = settings.get("Projects_Directory")
    
    if not projects_root or not os.path.isdir(projects_root):
        print(f"[ERREUR] Dossier de production introuvable: {projects_root}")
        return
    
    client_dir_path = os.path.join(projects_root, selected_cust)
    if not os.path.exists(client_dir_path):
        try:
            os.makedirs(client_dir_path)
            print(f"[FS] Dossier client créé : {client_dir_path}")
        except OSError as e:
            print(f"[ERREUR] Impossible de créer le dossier client: {e}")
            return

    # 2. Intégration Template_Maker.py
    print("\n[TEMPLATE] Lancement du générateur de structure...")
    
    try:
        if not os.path.exists(TEMPLATE_MAKER_SCRIPT):
            print(f"[ERREUR] Le script {TEMPLATE_MAKER_SCRIPT} est introuvable.")
        else:
            # --- NOUVELLE LOGIQUE : FORMATAGE DU TITRE ---
            final_folder_name = project_title
            
            # On vérifie si l'option est activée
            if settings.get("Title_AddCustomer", False):
                # Format : "Client - Projet"
                final_folder_name = f"{selected_cust} - {project_title}"
                print(f"[INFO] Nom du dossier adapté : '{final_folder_name}'")
            
            # Appel du script avec le nom final (court ou long selon l'option)
            subprocess.run([sys.executable, TEMPLATE_MAKER_SCRIPT, client_dir_path, final_folder_name])
            
    except Exception as e:
        print(f"[ERREUR] Échec lors de l'appel à Template_Maker: {e}")

    print("\nOpération terminée.")
    input("Appuyez sur Entrée pour revenir au menu...")
    command_view()

def command_delete():
    """Workflow de suppression."""
    settings = load_settings()
    db = load_projects_db()
    
    print("\n--- SUPPRESSION PROJET ---")
    
    projects_list = []
    customers = settings.get("Customers", [])
    
    counter = 1
    for cust in customers:
        print(f"\nClient: {cust}")
        found = False
        for section in db.sections():
            if db.get(section, "Customer") == cust:
                print(f" [{counter}] {section}")
                projects_list.append(section)
                counter += 1
                found = True
        if not found:
            print(" (Aucun projet)")
            
    if not projects_list:
        print("Rien à supprimer.")
        return

    try:
        idx_str = input("\nEntrez le numéro du projet à supprimer (ou 0 pour annuler): ")
        idx = int(idx_str) - 1
        if idx == -1:
            return
        if 0 <= idx < len(projects_list):
            proj_name = projects_list[idx]
        else:
            print("Index invalide.")
            return
    except ValueError:
        print("Entrée invalide.")
        return

    print(f"\n[ATTENTION] Vous allez supprimer le projet : '{proj_name}'")
    sure = input("Êtes-vous sûr ? (Taper 'DELETE' pour confirmer): ").strip()
    
    if sure == 'DELETE':
        # 1. Suppression Fichiers
        projects_root = settings.get("Projects_Directory")
        customer_name = db.get(proj_name, "Customer")
        
        # IMPORTANT : Pour supprimer, il faut deviner le nom du dossier réel
        # Si l'option "Title_AddCustomer" est active, le dossier est "Client - Projet"
        # Si elle ne l'est pas, c'est "Projet".
        # MAIS l'utilisateur a pu changer l'option entre temps...
        # Le plus sûr est de vérifier les deux possibilités.
        
        target_path_simple = os.path.join(projects_root, customer_name, proj_name)
        target_path_full = os.path.join(projects_root, customer_name, f"{customer_name} - {proj_name}")
        
        path_to_delete = None
        
        if os.path.exists(target_path_simple):
            path_to_delete = target_path_simple
        elif os.path.exists(target_path_full):
            path_to_delete = target_path_full
            
        if path_to_delete:
            try:
                shutil.rmtree(path_to_delete)
                print(f"[FS] Dossier supprimé : {path_to_delete}")
            except OSError as e:
                print(f"[ERREUR] Impossible de supprimer le dossier : {e}")
        else:
            print(f"[FS] Aucun dossier trouvé ({proj_name} ou {customer_name} - {proj_name}).")
            
        # 2. Suppression DB
        db.remove_section(proj_name)
        save_projects_db(db)
        print("[DB] Entrée supprimée.")
        
    else:
        print("Suppression annulée.")

    input("Appuyez sur Entrée pour continuer...")
    command_view()

# --- MAIN ---

def main():
    if not os.path.exists(SETTINGS_FILE):
        init_settings()

    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg == 'view':
            command_view()
        elif arg == 'add':
            command_add()
        elif arg == 'delete':
            command_delete()
        else:
            print(f"Commande inconnue: {arg}")
            print("Usage: ProjectManager.py [View|Add|Delete]")
    else:
        command_view()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterruption utilisateur.")
        sys.exit(0)