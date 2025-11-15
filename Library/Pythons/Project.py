import os
import sys
import json
import shutil
import subprocess
import configparser
import platform # <-- 1. AJOUTER CET IMPORT
from datetime import datetime, timedelta
from typing import List, Dict, Optional

try:
    import receiver_GoogleApi
except ImportError:
    receiver_GoogleApi = None # Gestion gracieuse si le module manque

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

# --- MODIFICATION ---
# On récupère le chemin absolu du dossier où se trouve Project.py
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# On construit le chemin complet vers Template.py
TEMPLATE_MAKER_SCRIPT = os.path.join(SCRIPT_DIR, "Template.py")
# --- FIN MODIFICATION ---

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
        "GoogleAPI": use_google,
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

# --- 2. AJOUTER CETTE NOUVELLE FONCTION ---
def open_file_explorer(path: str):
    """
    Ouvre le gestionnaire de fichiers à l'emplacement spécifié,
    de manière multi-plateforme.
    """
    if not os.path.isdir(path):
        print(f"[ERREUR] Impossible d'ouvrir le dossier, chemin introuvable : {path}")
        return
        
    try:
        # os.path.realpath() résout les liens symboliques et normalise le chemin
        real_path = os.path.realpath(path)
        
        if sys.platform == "win32":
            os.startfile(real_path)
        elif sys.platform == "darwin": # macOS
            subprocess.run(["open", real_path])
        else: # Linux
            subprocess.run(["xdg-open", real_path])
        print(f"[INFO] Ouverture de {real_path}...")
    except Exception as e:
        print(f"[ERREUR] Impossible d'ouvrir le gestionnaire de fichiers : {e}")
# --- FIN DE L'AJOUT ---


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
    """Workflow de création de projet avec planification étape par étape."""
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

    # --- INITIALISATION VARIABLES ---
    deadline_str = ""
    deadline_obj = None # Sera calculé automatiquement basé sur la date la plus lointaine
    send_to_google = False
    
    # Liste qui contiendra les événements à créer : [{'title': '...', 'date': datetime}, ...]
    events_to_create = [] 

    # --- BLOC PLANIFICATION (BOUCLE SUR LES ÉTAPES) ---
    if settings.get("GoogleAPI", False):
        receiver_script_path = os.path.join(SCRIPT_DIR, "receiver_GoogleApi.py")
        exchange_file = os.path.join(SCRIPT_DIR, "selected_date.txt")

        if not os.path.exists(receiver_script_path):
             print("[AVERTISSEMENT] Script 'receiver_GoogleApi.py' introuvable.")
        else:
            steps = settings.get("Steps", [])
            
            # Liste des "choses" à planifier
            # Si aucune étape config, on planifie juste une "Deadline"
            items_to_schedule = steps if steps else ["DEADLINE"]
            
            print(f"\n[PLANIFICATION] {len(items_to_schedule)} événement(s) à définir.")
            
            for step_name in items_to_schedule:
                # Nettoyage fichier échange
                if os.path.exists(exchange_file): os.remove(exchange_file)
                
                # On prépare le titre affiché dans l'interface calendrier pour guider l'utilisateur
                # Ex: "MonProjet (Etape: Review)"
                display_title = f"{project_title} ({step_name})"
                
                print(f"\n--> Sélection de la date pour : {step_name}")
                try:
                    # Lancement TUI pour CETTE étape
                    cmd = [sys.executable, receiver_script_path, display_title, selected_cust]
                    subprocess.run(cmd)
                    
                    # Lecture date
                    if os.path.exists(exchange_file):
                        with open(exchange_file, "r") as f:
                            date_str = f.read().strip()
                        
                        if date_str:
                            d_obj = datetime.strptime(date_str, "%d-%m-%y")
                            print(f"    Date choisie : {date_str}")
                            
                            # On construit le nom final de l'event Google
                            if step_name == "DEADLINE":
                                final_event_name = f"{selected_cust} - {project_title} - DEADLINE"
                            else:
                                final_event_name = f"{selected_cust} - {project_title} - {step_name}"
                                
                            events_to_create.append({
                                "title": final_event_name,
                                "date": d_obj,
                                "raw_date_str": date_str # Pour l'affichage résumé
                            })
                            send_to_google = True # Au moins une date a été choisie
                        else:
                            print(f"    [IGNORE] Aucune date pour '{step_name}'")
                    else:
                        print(f"    [IGNORE] Annulé pour '{step_name}'")
                        
                except Exception as e:
                    print(f"Erreur lancement calendrier : {e}")

    # --- CALCUL DE LA DEADLINE DU PROJET ---
    # La deadline est la date la plus lointaine parmi tous les events choisis
    if events_to_create:
        # On trie par date
        events_to_create.sort(key=lambda x: x['date'])
        # Le dernier est le plus loin
        latest_event = events_to_create[-1]
        deadline_obj = latest_event['date']
        deadline_str = latest_event['raw_date_str']
    
    # Phase 2: Review
    print("\n--- RÉSUMÉ ---")
    print(f"Client   : {selected_cust}")
    print(f"Projet   : {project_title}")
    print(f"Deadline : {deadline_str if deadline_str else 'Non définie'}")
    if events_to_create:
        print("Planning :")
        for evt in events_to_create:
            print(f"  - {evt['date'].strftime('%d-%m-%y')} : {evt['title']}")
    
    confirm = input("\nConfirmer création ? (y/n/retry): ").lower().strip()
    if confirm == 'n': return
    elif confirm == 'retry': command_add(); return

    # Drapeaux de succès
    google_op_success = True
    template_op_success = True 
    final_project_path = None

    # --- Phase 3: Google Integration (ENVOI DES EVENTS) ---
    if send_to_google and events_to_create:
        print("\n--- GOOGLE CALENDAR INTEGRATION ---")
        try:
            # 1. Authentification
            service = receiver_GoogleApi.get_calendar_service(APP_DIR)
            if not service:
                print("[ERREUR] Auth échouée.")
                google_op_success = False
            else:
                # 2. Choix du calendrier (Une seule fois pour tous les events)
                cals = receiver_GoogleApi.get_writable_calendars(service)
                cal_id = None
                
                if not cals:
                    print("[ERREUR] Aucun calendrier inscriptible.")
                    google_op_success = False
                else:
                    print("Sélectionnez le calendrier pour ajouter le planning :")
                    for i, cal in enumerate(cals):
                        print(f"[{i+1}] {cal['summary']}")
                    
                    while True:
                        try:
                            c_idx = int(input("Choix (0 pour annuler): "))
                            if c_idx == 0: google_op_success = False; break
                            if 0 <= c_idx - 1 < len(cals):
                                cal_id = cals[c_idx - 1]['id']
                                break
                        except ValueError: pass

                # 3. Création en masse
                if google_op_success and cal_id:
                    print(f"Création de {len(events_to_create)} événement(s)...")
                    all_ok = True
                    for item in events_to_create:
                        # Appel API
                        if not receiver_GoogleApi.create_event(service, cal_id, item['title'], item['date']):
                            all_ok = False
                    
                    if not all_ok: print("[ATTENTION] Certains événements n'ont pas été créés.")
                    else: print("[SUCCÈS] Planning exporté vers Google Agenda.")

        except Exception as e:
            print(f"[ERREUR CRITIQUE] : {e}")
            google_op_success = False
    
    # Si Google échoue, on annule tout
    if not google_op_success:
        print("\n[ANNULATION] Problème Google Calendar. Projet non créé.")
        return

    # --- Phase 4: File System Generation ---
    projects_root = settings.get("Projects_Directory")
    
    if not projects_root or not os.path.isdir(projects_root):
        print(f"[ERREUR] Dossier racine introuvable: {projects_root}")
        template_op_success = False 
    else:
        client_dir_path = os.path.join(projects_root, selected_cust)
        if not os.path.exists(client_dir_path):
            try: os.makedirs(client_dir_path)
            except OSError: template_op_success = False
        
        if template_op_success:
            print("[TEMPLATE] Génération des dossiers...")
            try:
                if not os.path.exists(TEMPLATE_MAKER_SCRIPT):
                    print(f"[ERREUR] Script Template introuvable.")
                    template_op_success = False
                else:
                    final_folder_name = project_title
                    if settings.get("Title_AddCustomer", False):
                        final_folder_name = f"{selected_cust} - {project_title}"
                    
                    final_project_path = os.path.join(client_dir_path, final_folder_name)
                    
                    result = subprocess.run([sys.executable, TEMPLATE_MAKER_SCRIPT, client_dir_path, final_folder_name])
                    
                    if result.returncode != 0:
                        template_op_success = False
                        final_project_path = None
                    
            except Exception as e:
                print(f"[ERREUR] Template: {e}")
                template_op_success = False
                final_project_path = None

    # --- Phase 5: Database Update ---
    if template_op_success:
        db = load_projects_db()
        if not db.has_section(project_title): db.add_section(project_title)
        
        db.set(project_title, "Customer", selected_cust)
        db.set(project_title, "Deadline", deadline_str if deadline_str else "N/A")
        save_projects_db(db)
        
        print("\n[SUCCÈS] Projet créé et sauvegardé.")
        
        if final_project_path:
            open_q = input(f"Ouvrir le dossier ? (Y/n): ").lower().strip()
            if open_q != 'n': open_file_explorer(final_project_path)
    else:
        print("\n[ECHEC] La création des dossiers a échoué.")
    
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



