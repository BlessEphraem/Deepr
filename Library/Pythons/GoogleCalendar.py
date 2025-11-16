#!/usr/bin/env python3
"""
GoogleCalendar.py
Version 2.5 : Token Management + Dynamic Preview + Project Picker Mode
"""

import os
import sys
import datetime
import calendar
import time
import copy
import tempfile

sys.dont_write_bytecode = True

# Gestion de l'input clavier sans bloquer (Cross-platform)
try:
    import msvcrt  # Windows
except ImportError:
    import tty, termios  # Linux/Mac

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# --- CONFIGURATION ---

SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/tasks' 
]
# Chemin vers vos identifiants (ID Client)
CREDENTIALS_PATH = r'Z:\Scripts\.credentials\googleCalendar.json' 

# --- GESTION COULEURS & ANSI ---

class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    INVERT = "\033[7m"      
    BLUE_BG = "\033[44m"
    RED_BG = "\033[41m"
    WHITE_TXT = "\033[97m"
    HEADER = "\033[95m"     
    GREEN = "\033[92m"      
    GREY = "\033[90m"
    CYAN = "\033[96m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    
    @staticmethod
    def hex_to_ansi(hex_color):
        if not hex_color or not hex_color.startswith('#'): return Colors.GREEN 
        hex_color = hex_color.lstrip('#')
        try:
            r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
            return f"\033[38;2;{r};{g};{b}m"
        except: return Colors.GREEN

# --- GESTION INPUT CLAVIER ---

class _Getch:
    def __init__(self):
        try: self.impl = _GetchWindows()
        except ImportError: self.impl = _GetchUnix()
    def __call__(self): return self.impl()

class _GetchUnix:
    def __init__(self): import tty, termios
    def __call__(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
            if ch == '\x1b':
                seq = sys.stdin.read(2)
                if seq == '[A': return 'UP'
                if seq == '[B': return 'DOWN'
                if seq == '[C': return 'RIGHT'
                if seq == '[D': return 'LEFT'
            return ch
        finally: termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

class _GetchWindows:
    def __init__(self): import msvcrt
    def __call__(self):
        ch = msvcrt.getch()
        if ch == b'\xe0':
            ch = msvcrt.getch()
            if ch == b'H': return 'UP'
            if ch == b'P': return 'DOWN'
            if ch == b'M': return 'RIGHT'
            if ch == b'K': return 'LEFT'
        try: return ch.decode('utf-8')
        except: return ch

getch = _Getch()

def input_text_tui(prompt):
    sys.stdout.write(f"\r{Colors.CYAN}{prompt}{Colors.RESET} ")
    sys.stdout.flush()
    try:
        if os.name != 'nt':
            import tty, termios
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            termios.tcsetattr(fd, termios.TCSADRAIN, termios.tcgetattr(sys.stdout))
        user_input = input()
        if os.name != 'nt': termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return user_input.strip()
    except: return ""

# --- API SERVICES & LOGIQUE MÉTIER ---

def get_services(config_dir):
    creds = None
    base_cred_dir = os.path.dirname(os.path.abspath(CREDENTIALS_PATH))
    token_dir = os.path.join(base_cred_dir, "_token")
    token_filename = "googleCalendar_token.json"
    token_path = os.path.join(token_dir, token_filename)

    if not os.path.exists(token_dir):
        try: os.makedirs(token_dir, exist_ok=True)
        except OSError: token_path = os.path.join(config_dir, 'token.json')

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if os.path.exists(CREDENTIALS_PATH):
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            elif os.path.exists('credentials.json'):
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            else: return None, None
            creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as token: token.write(creds.to_json())
    
    cal_service = build('calendar', 'v3', credentials=creds)
    task_service = build('tasks', 'v1', credentials=creds)
    return cal_service, task_service

def get_writable_calendars(service):
    res = service.calendarList().list().execute()
    return [{'id': c['id'], 'summary': c['summary']} for c in res.get('items', []) if c.get('accessRole') in ['owner', 'writer']]

def get_task_lists(service):
    res = service.tasklists().list().execute()
    return [{'id': t['id'], 'title': t['title']} for t in res.get('items', [])]

# --- OPERATIONS API AVANCÉES (CRUD) ---

def build_event_body(data):
    """Construit le corps JSON de l'événement."""
    body = {
        'summary': data['title'],
        'description': data.get('description', ''),
        'location': data.get('location', ''),
        'transparency': 'opaque' if data.get('busy', True) else 'transparent',
        'visibility': data.get('visibility', 'default'),
    }
    date_obj = data['date']
    if data['all_day']:
        end_date = date_obj + datetime.timedelta(days=1)
        body['start'] = {'date': date_obj.strftime('%Y-%m-%d')}
        body['end'] = {'date': end_date.strftime('%Y-%m-%d')}
    else:
        sh, sm = map(int, data.get('start_time', '09:00').split(':'))
        eh, em = map(int, data.get('end_time', '10:00').split(':'))
        start_dt = datetime.datetime(date_obj.year, date_obj.month, date_obj.day, sh, sm)
        end_dt = datetime.datetime(date_obj.year, date_obj.month, date_obj.day, eh, em)
        body['start'] = {'dateTime': start_dt.isoformat(), 'timeZone': 'Europe/Paris'}
        body['end'] = {'dateTime': end_dt.isoformat(), 'timeZone': 'Europe/Paris'}
    
    # Recurrence
    rrule = None
    if data.get('recurrence') and data['recurrence'] != 'NONE':
        if data['recurrence'] == 'CUSTOM':
            if data.get('custom_rrule'): rrule = data['custom_rrule']
        else: rrule = f"RRULE:FREQ={data['recurrence']}"
    if rrule: body['recurrence'] = [rrule]

    if data.get('color_id') and data['color_id'] != 'DEFAULT': body['colorId'] = data['color_id']
    
    if data.get('reminders_use_default'): body['reminders'] = {'useDefault': True}
    else:
        min_before = int(data.get('reminders_min', 10))
        body['reminders'] = {'useDefault': False, 'overrides': [{'method': 'popup', 'minutes': min_before}]}
    return body

def create_google_event(service, calendar_id, data):
    body = build_event_body(data)
    try:
        service.events().insert(calendarId=calendar_id, body=body).execute()
        return True
    except Exception as e:
        print(f"Err Create: {e}"); time.sleep(2); return False

def update_google_event(service, calendar_id, event_id, data, scope='THIS'):
    body = build_event_body(data)
    if scope == 'THIS' and 'recurrence' in body: del body['recurrence']

    try:
        service.events().update(calendarId=calendar_id, eventId=event_id, body=body).execute()
        return True
    except Exception as e:
        print(f"Err Update: {e}"); time.sleep(2); return False

def delete_google_event(service, calendar_id, event_id, scope='THIS'):
    try:
        service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
        return True
    except Exception as e:
        print(f"Err Delete: {e}"); time.sleep(2); return False

def get_events_with_colors(service, calendar_map, start_date, end_date):
    t_min, t_max = start_date.isoformat() + 'Z', end_date.isoformat() + 'Z'
    all_events = []
    for cal_id, hex_color in calendar_map.items():
        try:
            res = service.events().list(calendarId=cal_id, timeMin=t_min, timeMax=t_max, singleEvents=True, orderBy='startTime').execute()
            ansi = Colors.hex_to_ansi(hex_color)
            for item in res.get('items', []):
                item['_ui_color'] = ansi
                item['_cal_id'] = cal_id
                all_events.append(item)
        except: continue
    all_events.sort(key=lambda x: x['start'].get('dateTime', x['start'].get('date')))
    return all_events


# --- UTILITAIRES UI ---

def prompt_scope(action_name):
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"\n{Colors.RED_BG}{Colors.WHITE_TXT}  CONFIRMATION {action_name.upper()}  {Colors.RESET}")
    print(f"{Colors.YELLOW}Cet événement est une répétition.{Colors.RESET}")
    print("Appliquer à :")
    print(f"  1. {Colors.BOLD}Cet événement uniquement{Colors.RESET}")
    print(f"  2. {Colors.BOLD}Cet événement et les suivants{Colors.RESET}")
    print(f"  3. {Colors.BOLD}Tous les événements de la série{Colors.RESET}")
    print("\n(ECHAP pour annuler)")
    while True:
        k = getch()
        if k == '1': return 'THIS'
        if k == '2': return 'ALL'
        if k == '3': return 'ALL'
        if k == '\x1b': return None

def prompt_confirm(msg):
    print(f"\n{Colors.RED}{msg}{Colors.RESET} (ENTRÉE: Oui / ECHAP: Non)")
    while True:
        k = getch()
        if k == '\r' or k == '\n': return True
        if k == '\x1b': return False

# --- FORMULAIRES ---

class CustomRecurrenceForm:
    def __init__(self, calendar_instance):
        self.calendar_instance = calendar_instance
        self.data = {
            "freq_num": 1, "freq_type": "WEEKLY",
            "days": {"MO": False, "TU": False, "WE": False, "TH": False, "FR": False, "SA": False, "SU": False},
            "end_mode": "NEVER", "end_date": "", "end_count": 13
        }
        self.selected_row = 0
        self.freq_opts = ["DAILY", "WEEKLY", "MONTHLY", "YEARLY"]
        self.day_keys = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]

    def generate_rrule(self):
        parts = [f"FREQ={self.data['freq_type']}"]
        if self.data['freq_num'] > 1: parts.append(f"INTERVAL={self.data['freq_num']}")
        if self.data['freq_type'] == "WEEKLY":
            active_days = [d for d in self.day_keys if self.data['days'][d]]
            if active_days: parts.append(f"BYDAY={','.join(active_days)}")
        if self.data['end_mode'] == "COUNT": parts.append(f"COUNT={self.data['end_count']}")
        elif self.data['end_mode'] == "DATE" and self.data['end_date']:
            parts.append(f"UNTIL={self.data['end_date']}T235959Z")
        return "RRULE:" + ";".join(parts)

    def get_rows(self):
        rows = [("Répéter tous les", "freq"), ("Se termine", "end_mode")]
        if self.data['end_mode'] == "DATE": rows.insert(2, ("   Le", "end_date_val"))
        elif self.data['end_mode'] == "COUNT": rows.insert(2, ("   Nb Occurrences", "end_count_val"))
        if self.data['freq_type'] == "WEEKLY": rows.append(("Jours", "days_selector"))
        rows.append(("---", "sep")); rows.append(("[ TERMINÉ ]", "done"))
        return rows

    def draw(self, editing_days=False, day_cursor=0):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{Colors.INVERT} RÉCURRENCE PERSONNALISÉE {Colors.RESET}")
        print("─" * 50)
        rows = self.get_rows()
        if self.selected_row >= len(rows): self.selected_row = len(rows) - 1
        for idx, (label, key) in enumerate(rows):
            if key == "sep": print("─" * 50); continue
            marker = f"{Colors.CYAN}➜{Colors.RESET}" if idx == self.selected_row else " "
            style = f"{Colors.INVERT}" if idx == self.selected_row and not editing_days else ""
            val_str = ""
            if key == "freq": val_str = f"{self.data['freq_num']} {self.data['freq_type']}"
            elif key == "end_mode": val_str = self.data['end_mode']
            elif key == "end_date_val": val_str = self.data['end_date'] or "..."
            elif key == "end_count_val": val_str = str(self.data['end_count'])
            elif key == "days_selector":
                for i, d in enumerate(self.day_keys):
                    ds = f"{Colors.INVERT}{d}{Colors.RESET}" if (editing_days and i==day_cursor) else (f"{Colors.BLUE_BG}{d}{Colors.RESET}" if self.data['days'][d] else d)
                    val_str += ds + " "
            
            if key == "days_selector": print(f"   {marker} {label:<20} : {val_str}")
            elif key == "done": print(f"   {marker} {style} {label} {Colors.RESET}")
            else: print(f"   {marker} {label:<20} : {style}{val_str}{Colors.RESET}")
        print("─" * 50)

    def run_day_selector(self):
        cur = 0
        while True:
            self.draw(True, cur)
            k = getch()
            if k == '\x1b': return
            if k == 'LEFT': cur = (cur-1)%7
            if k == 'RIGHT': cur = (cur+1)%7
            if k in ['\r','\n',' ']: self.data['days'][self.day_keys[cur]] = not self.data['days'][self.day_keys[cur]]

    def run(self):
        while True:
            self.draw()
            k = getch()
            if k == 'UP': self.selected_row -= 1
            elif k == 'DOWN': self.selected_row += 1
            elif k == ' ':
                _, key = self.get_rows()[self.selected_row]
                if key == "done": return self.generate_rrule()
                if key == "freq": self.data['freq_type'] = self.freq_opts[(self.freq_opts.index(self.data['freq_type'])+1)%4]
                if key == "end_mode": self.data['end_mode'] = ["NEVER","DATE","COUNT"][(["NEVER","DATE","COUNT"].index(self.data['end_mode'])+1)%3]
                if key == "days_selector": self.run_day_selector()
                if key == "end_date_val":
                    d = self.calendar_instance.run_date_picker_mode()
                    if d: self.data['end_date'] = d.strftime('%Y%m%d')
            elif k in ['RIGHT', 'LEFT']: 
                _, key = self.get_rows()[self.selected_row]
                delta = 1 if k == 'RIGHT' else -1
                if key == "freq": self.data['freq_num'] = max(1, self.data['freq_num'] + delta)
                if key == "end_count_val": self.data['end_count'] = max(1, self.data['end_count'] + delta)
            elif k in ['\r', '\n']:
                _, key = self.get_rows()[self.selected_row]
                if key == "done": return self.generate_rrule()
            elif k == '\x1b': return None

class AdvancedFormTUI:
    def __init__(self, cal_service, task_service, date, calendar_instance, existing_event=None):
        self.cal_service = cal_service
        self.task_service = task_service
        self.date = date
        self.calendar_instance = calendar_instance
        self.existing_event = existing_event 
        self.calendars = get_writable_calendars(cal_service)
        self.tasklists = get_task_lists(task_service)
        self.data = {
            "type": "EVENT", "title": "Nouvel événement", "description": "",
            "all_day": True, "start_time": "09:00", "end_time": "10:00",
            "location": "", "cal_idx": 0, "recurrence": "NONE", "custom_rrule": "",
            "visibility": "default", "busy": True, "color_id": "DEFAULT",
            "reminders_use_default": True, "reminders_min": 10, "tasklist_idx": 0
        }
        if existing_event:
            self.data["title"] = existing_event.get('summary', 'Sans titre')
            self.data["description"] = existing_event.get('description', '')
            self.data["location"] = existing_event.get('location', '')
            start = existing_event.get('start')
            if 'date' in start:
                self.data['all_day'] = True
                self.date = datetime.datetime.strptime(start['date'], '%Y-%m-%d').date()
            elif 'dateTime' in start:
                self.data['all_day'] = False
                dt = datetime.datetime.fromisoformat(start['dateTime'].replace('Z', '+00:00'))
                self.date = dt.date()
                self.data['start_time'] = dt.strftime('%H:%M')
                if 'end' in existing_event:
                    end_dt = datetime.datetime.fromisoformat(existing_event['end']['dateTime'].replace('Z', '+00:00'))
                    self.data['end_time'] = end_dt.strftime('%H:%M')
            if 'colorId' in existing_event: self.data['color_id'] = existing_event['colorId']
            cid = existing_event.get('_cal_id')
            for i, c in enumerate(self.calendars):
                if c['id'] == cid: self.data['cal_idx'] = i; break

        self.selected_row = 0
        self.recurrence_opts = ["NONE", "DAILY", "WEEKLY", "MONTHLY", "YEARLY", "CUSTOM"]
        self.colors_ids = ["DEFAULT", "1", "2", "3", "4", "5", "6", "8", "11"]

    def get_fields(self):
        fields = [("Titre", "title")]
        if self.data["type"] == "EVENT":
            fields.extend([("Horaire", "all_day")])
            if not self.data["all_day"]: fields.extend([("Début", "start_time"), ("Fin", "end_time")])
            if not self.existing_event: 
                fields.extend([("Récurrence", "recurrence")])
                if self.data["recurrence"] == "CUSTOM": fields.append(("   Paramètres", "recurrence_settings"))
            fields.extend([("Lieu", "location"), ("Desc", "description"), ("Calendrier", "cal_idx"), ("Couleur", "color_id"), ("Notifs", "reminders")])
            if not self.data["reminders_use_default"]: fields.append(("Minutes", "reminders_min"))
        else:
            fields.extend([("Desc", "description"), ("Liste", "tasklist_idx")])
        fields.append(("---", "sep"))
        fields.append(("[ SAUVEGARDER ]", "save"))
        if self.existing_event: fields.append(("[ SUPPRIMER ]", "delete"))
        fields.append(("[ ANNULER ]", "cancel"))
        return fields

    def draw(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{Colors.BLUE_BG if self.data['type']=='EVENT' else Colors.GREEN} {('MODIFIER' if self.existing_event else 'NOUVEAU')} {self.data['type']} {Colors.RESET}")
        print(f"Date: {self.date.strftime('%d/%m/%Y')}"); print("─" * 50)
        rows = self.get_fields()
        if self.selected_row >= len(rows): self.selected_row = len(rows) - 1
        for idx, (label, key) in enumerate(rows):
            if key == "sep": print("─" * 50); continue
            mk = f"{Colors.CYAN}➜{Colors.RESET}" if idx == self.selected_row else " "
            st = f"{Colors.INVERT}" if idx == self.selected_row else ""
            val = str(self.data.get(key, ""))
            if key == "all_day": val = "Journée entière" if self.data['all_day'] else "Heures précises"
            if key == "cal_idx" and self.calendars: val = self.calendars[self.data['cal_idx']]['summary']
            if key == "reminders": val = "Défaut" if self.data['reminders_use_default'] else "Custom"
            if key in ["save", "delete", "cancel"]: print(f"   {mk} {st} {label} {Colors.RESET}")
            else: print(f"   {mk} {label:<12} : {st}{val}{Colors.RESET}")
        print("\nSPACE: Changer | ENTER: Valider | ECHAP: Retour")

    def save_action(self):
        print(f"\n{Colors.YELLOW}Traitement...{Colors.RESET}")
        scope = 'THIS'
        if self.existing_event and self.data['type'] == 'EVENT':
            is_recurring = ('recurrence' in self.existing_event) or ('recurringEventId' in self.existing_event)
            if is_recurring:
                scope = prompt_scope("MODIFICATION")
                if not scope: return 
        cid = self.calendars[self.data['cal_idx']]['id']
        if self.existing_event:
            eid = self.existing_event['id']
            target_id = eid
            if scope == 'ALL' and 'recurringEventId' in self.existing_event:
                target_id = self.existing_event['recurringEventId']
            ok = update_google_event(self.cal_service, cid, target_id, {**self.data, 'date': self.date}, scope)
        else:
            ok = create_google_event(self.cal_service, cid, {**self.data, 'date': self.date})
        if ok: print(f"{Colors.GREEN}OK{Colors.RESET}"); time.sleep(0.5); return True
        else: input("Erreur."); return False

    def delete_action(self):
        if not self.existing_event: return
        scope = 'THIS'
        is_recurring = ('recurrence' in self.existing_event) or ('recurringEventId' in self.existing_event)
        if is_recurring:
            scope = prompt_scope("SUPPRESSION")
            if not scope: return
            print(f"\n{Colors.RED}Êtes-vous sûr de vouloir supprimer cette série/instance ?{Colors.RESET} (Entrée/Echap)")
            k = getch()
            if k not in ['\r','\n']: return
        else:
            if not prompt_confirm("Supprimer cet événement ?"): return
        print(f"\n{Colors.YELLOW}Suppression...{Colors.RESET}")
        cid = self.calendars[self.data['cal_idx']]['id']
        eid = self.existing_event['id']
        target_id = eid
        if scope == 'ALL' and 'recurringEventId' in self.existing_event:
            target_id = self.existing_event['recurringEventId']
        ok = delete_google_event(self.cal_service, cid, target_id, scope)
        if ok: return True
        else: input("Erreur."); return False

    def run(self):
        while True:
            self.draw()
            k = getch()
            if k == 'UP': self.selected_row -= 1
            elif k == 'DOWN': self.selected_row += 1
            elif k == '\x1b': return False
            elif k == ' ': 
                rows = self.get_fields()
                key = rows[self.selected_row][1]
                if key == "all_day": self.data["all_day"] = not self.data["all_day"]
                elif key == "recurrence": 
                    i = self.recurrence_opts.index(self.data["recurrence"])
                    self.data["recurrence"] = self.recurrence_opts[(i+1)%len(self.recurrence_opts)]
                elif key == "recurrence_settings":
                    f = CustomRecurrenceForm(self.calendar_instance)
                    r = f.run()
                    if r: self.data['custom_rrule'] = r
                elif key == "reminders": self.data["reminders_use_default"] = not self.data["reminders_use_default"]
                elif key == "cal_idx": self.data['cal_idx'] = (self.data['cal_idx']+1)%len(self.calendars)
                elif key == "color_id": 
                     i = self.colors_ids.index(self.data['color_id']) if self.data['color_id'] in self.colors_ids else 0
                     self.data['color_id'] = self.colors_ids[(i+1)%len(self.colors_ids)]
                elif key in ["title", "description", "location"]:
                    res = input_text_tui(f"{key} >")
                    if res: self.data[key] = res
                elif key in ["start_time", "end_time"]:
                    res = input_text_tui("HH:MM >")
                    if ":" in res: self.data[key] = res
            elif k in ['\r', '\n']:
                rows = self.get_fields()
                key = rows[self.selected_row][1]
                if key == "save": 
                    if self.save_action(): return True
                elif key == "delete":
                    if self.delete_action(): return True
                elif key == "cancel": return False

# --- CALENDRIER PRINCIPAL ---

class CalendarTUI:
    def __init__(self, cal_service, task_service, calendar_ids, picker_mode=False, picker_title=""):
        self.cal_service = cal_service
        self.task_service = task_service
        self.target_cal_ids = calendar_ids 
        
        # CONFIGURATION MODE "PROJECT PICKER"
        self.picker_mode = picker_mode
        self.picker_title = picker_title
        
        now = datetime.datetime.now()
        self.year = now.year; self.month = now.month; self.day = now.day
        
        # États de navigation
        self.active_panel = 0 
        self.showing_day_preview = False
        self.side_cursor = 0
        self.scroll_offset = 0 
        self.cursor_in_header = False 
        
        self.selected_date = now.date()
        self.events_cache = {} 
        self.all_month_events_flat = [] 
        self.last_fetch_month = None
        self.cal_colors = {}
        self._init_colors()

    def _init_colors(self):
        try:
            items = self.cal_service.calendarList().list().execute().get('items', [])
            for c in items:
                if c['id'] in self.target_cal_ids: self.cal_colors[c['id']] = c.get('backgroundColor', '#00FF00')
        except: pass

    def fetch_month_events(self):
        if (self.year, self.month) == self.last_fetch_month: return
        start_date = datetime.datetime(self.year, self.month, 1)
        _, last_day = calendar.monthrange(self.year, self.month)
        end_date = datetime.datetime(self.year, self.month, last_day, 23, 59, 59)
        
        raw = get_events_with_colors(self.cal_service, self.cal_colors, start_date, end_date)
        
        self.events_cache = {}
        self.all_month_events_flat = [] 

        for e in raw:
            self.all_month_events_flat.append(e)
            start = e['start'].get('dateTime', e['start'].get('date'))
            dt_obj = datetime.datetime.fromisoformat(start.replace('Z', '+00:00'))
            d_key = dt_obj.strftime("%Y-%m-%d")
            if d_key not in self.events_cache: self.events_cache[d_key] = []
            self.events_cache[d_key].append(e)
        
        self.last_fetch_month = (self.year, self.month)

    def get_side_items(self):
        if self.active_panel == 0:
            if self.showing_day_preview:
                d_key = self.selected_date.strftime("%Y-%m-%d")
                return self.events_cache.get(d_key, [])
            else:
                return self.all_month_events_flat
        elif self.active_panel == 1:
            d_key = self.selected_date.strftime("%Y-%m-%d")
            return self.events_cache.get(d_key, [])
        elif self.active_panel == 2:
            return self.all_month_events_flat
        return []

    def draw(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        self.fetch_month_events()
        try:
            _, max_days = calendar.monthrange(self.year, self.month)
            self.day = min(self.day, max_days)
            self.selected_date = datetime.date(self.year, self.month, self.day)
        except: pass

        # Header Gauche
        cal_obj = calendar.Calendar(firstweekday=0)
        month_days = cal_obj.monthdayscalendar(self.year, self.month)
        m_name = calendar.month_name[self.month].upper()
        
        head_grid = f"{m_name} {self.year}".center(22)
        if self.active_panel == 0 and self.cursor_in_header: head_grid = f"{Colors.INVERT}{head_grid}{Colors.RESET}"
        else: head_grid = f"{Colors.HEADER}{head_grid}{Colors.RESET}"
        
        # Header Droite Logic
        if self.picker_mode:
            # Mode Picker : On affiche le titre demandé (Ex: "Projet (Review)")
            head_side = f"{Colors.YELLOW}{self.picker_title}{Colors.RESET}"
        else:
            # Mode Normal
            if self.active_panel == 0:
                if self.showing_day_preview:
                    head_side = f"{Colors.BOLD}Événements: {self.selected_date.strftime('%d/%m')}{Colors.RESET}"
                else:
                    head_side = f"{Colors.BOLD}Événements du Mois{Colors.RESET}"
            elif self.active_panel == 1:
                head_side = f"{Colors.INVERT} {self.selected_date.strftime('%d/%m')} {Colors.RESET}"
            elif self.active_panel == 2:
                head_side = f"{Colors.INVERT} Événements du Mois {Colors.RESET}"

        print(f"{head_grid}   |   {head_side}")
        print(f"|L |M |M |J |V |S |D |   |")
        
        # --- Construction Liste Latérale ---
        side_evts = self.get_side_items()
        raw_lines = []
        
        if not side_evts:
             raw_lines.append(f"{Colors.GREY}(Aucun){Colors.RESET}")
        else:
            for i, e in enumerate(side_evts):
                col = e.get('_ui_color', Colors.GREEN)
                start = e['start'].get('dateTime', e['start'].get('date'))
                dt_obj = datetime.datetime.fromisoformat(start.replace('Z', '+00:00'))
                d_str = dt_obj.strftime("%d/%m")
                
                txt = f"{d_str} {e.get('summary','(Sans titre)')[:20]}"
                
                is_selected = (self.active_panel in [1, 2] and i == self.side_cursor)
                style = f"{Colors.INVERT}{txt}{Colors.RESET}" if is_selected else f"{col}{txt}{Colors.RESET}"
                raw_lines.append(style)
        
        # Bouton Ajouter (seulement si mode interactif et PAS en mode picker)
        if self.active_panel != 0 and not self.picker_mode:
            limit_idx = len(side_evts)
            add_btn_txt = "[ + Ajouter ]"
            if self.active_panel in [1, 2] and self.side_cursor == limit_idx:
                raw_lines.append(f"{Colors.INVERT}{add_btn_txt}{Colors.RESET}")
            else:
                raw_lines.append(f"{Colors.YELLOW}{add_btn_txt}{Colors.RESET}")

        # --- Viewport ---
        fixed_height = 9 
        if self.active_panel == 0: self.scroll_offset = 0

        if self.active_panel != 0:
            if self.side_cursor >= self.scroll_offset + fixed_height:
                self.scroll_offset = self.side_cursor - fixed_height + 1
            elif self.side_cursor < self.scroll_offset:
                self.scroll_offset = self.side_cursor
        
        total_items = len(raw_lines)
        if self.scroll_offset > total_items - fixed_height:
             self.scroll_offset = max(0, total_items - fixed_height)

        visible_side = raw_lines[self.scroll_offset : self.scroll_offset + fixed_height]

        can_scroll_up = self.scroll_offset > 0
        can_scroll_down = (self.scroll_offset + fixed_height) < total_items

        for i in range(fixed_height):
            # Grid
            row_str = ""
            if i < len(month_days):
                for d_num in month_days[i]:
                    if d_num == 0: row_str += "|  "
                    else:
                        ds = f"{d_num:02d}"
                        dk = f"{self.year}-{self.month:02d}-{d_num:02d}"
                        has_evt = (dk in self.events_cache)
                        
                        is_today_cursor = (d_num == self.day)
                        
                        if self.active_panel == 0 and not self.cursor_in_header and is_today_cursor:
                            # Curseur sur la grille
                            cell = f"{Colors.BLUE_BG}{Colors.WHITE_TXT}{ds}{Colors.RESET}"
                        elif self.active_panel == 1 and is_today_cursor: 
                            # Focus ailleurs, mais on montre la sélection grisée
                            cell = f"{Colors.INVERT}{ds}{Colors.RESET}"
                        elif has_evt:
                            c = self.events_cache[dk][0].get('_ui_color', Colors.GREEN)
                            cell = f"{c}{Colors.BOLD}{ds}{Colors.RESET}"
                        else: cell = ds
                        row_str += f"|{cell}"
                row_str += "|"
            else: row_str = " " * 22 
            
            # Side
            if i < len(visible_side):
                content = visible_side[i]
                indicator = " "
                if self.active_panel != 0: 
                    if i == 0 and can_scroll_up: indicator = f"{Colors.GREY}▲{Colors.RESET}"
                    elif i == fixed_height - 1 and can_scroll_down: indicator = f"{Colors.GREY}▼{Colors.RESET}"
                print(f"{row_str}   | {indicator} {content}")
            else:
                print(f"{row_str}   |")

        print("-" * 60)
        if self.picker_mode:
            print(f"NAV: Flèches | {Colors.INVERT}ENTER: Valider la date{Colors.RESET} | ECHAP: Annuler")
        else:
            if self.active_panel == 0: print(f"NAV: Flèches | {Colors.BOLD}'e': Events Mois{Colors.RESET} | ENTER: Events Jour")
            elif self.active_panel == 1: print("JOUR: HAUT/BAS | ENTER: Éditer | ECHAP: Retour")
            elif self.active_panel == 2: print("MOIS: HAUT/BAS | ENTER: Éditer | ECHAP: Retour")

    def run_date_picker_mode(self):
        temp_active = self.active_panel
        self.active_panel = 0
        while True:
            self.draw()
            k = getch()
            if k == '\x1b': self.active_panel = temp_active; return None
            if k in ['\r','\n']: 
                self.active_panel = temp_active
                return self.selected_date
            # Basic Navigation
            if k == 'UP':
                if not self.cursor_in_header:
                    self.day -= 7
                    if self.day < 1: self.cursor_in_header = True; self.day += 7
            elif k == 'DOWN':
                if self.cursor_in_header: self.cursor_in_header = False
                else: self.day += 7
            elif k == 'LEFT': self.day -= 1
            elif k == 'RIGHT': self.day += 1

    def save_and_exit_picker(self):
        """Ecrit la date dans un fichier temporaire et quitte (Pour Project.py)"""
        # On utilise le dossier temp du système pour éviter de polluer le dossier du script
        temp_dir = tempfile.gettempdir()
        output_file = os.path.join(temp_dir, "ProjectManager_date.tmp")
        
        date_str = self.selected_date.strftime("%d-%m-%y")
        try:
            with open(output_file, "w") as f:
                f.write(date_str)
        except Exception as e:
            print(f"Erreur écriture date: {e}")
            time.sleep(2)
        return True # Exit signal

    def run(self):
        while True:
            self.draw()
            k = getch()

            # --- GLOBAL EXIT ---
            if k == '\x1b':
                if self.active_panel != 0 and not self.picker_mode: 
                    self.active_panel = 0 
                    self.scroll_offset = 0
                    self.showing_day_preview = False
                else: 
                    if self.showing_day_preview and not self.picker_mode:
                        self.showing_day_preview = False 
                    else:
                        return None # Quit

            # --- PANEL 0 (GRID) ---
            elif self.active_panel == 0:
                if k == 'e' and not self.picker_mode: # Desactivé en mode picker
                    self.active_panel = 2
                    self.side_cursor = 0
                    self.scroll_offset = 0
                
                elif k == 'UP':
                    if not self.picker_mode: self.showing_day_preview = True
                    if not self.cursor_in_header:
                        self.day -= 7
                        if self.day < 1: self.cursor_in_header = True; self.day += 7 
                elif k == 'DOWN':
                    if not self.picker_mode: self.showing_day_preview = True
                    if self.cursor_in_header: self.cursor_in_header = False
                    else:
                        self.day += 7
                        _, max_d = calendar.monthrange(self.year, self.month)
                        if self.day > max_d: self.day = max_d
                elif k == 'LEFT':
                    if not self.picker_mode: self.showing_day_preview = True
                    if self.cursor_in_header:
                        self.month -= 1
                        if self.month < 1: self.month = 12; self.year -= 1
                        self.last_fetch_month = None
                    else:
                        self.day -= 1
                        if self.day < 1:
                            self.month -= 1
                            if self.month < 1: self.month = 12; self.year -= 1
                            _, max_prev = calendar.monthrange(self.year, self.month)
                            self.day = max_prev
                            self.last_fetch_month = None
                elif k == 'RIGHT':
                    if not self.picker_mode: self.showing_day_preview = True
                    if self.cursor_in_header:
                        self.month += 1
                        if self.month > 12: self.month = 1; self.year += 1
                        self.last_fetch_month = None
                    else:
                        _, max_d = calendar.monthrange(self.year, self.month)
                        self.day += 1
                        if self.day > max_d:
                            self.month += 1
                            if self.month > 12: self.month = 1; self.year += 1
                            self.day = 1
                            self.last_fetch_month = None
                
                elif k in ['\r', '\n']:
                    if self.picker_mode:
                        # MODE PICKER : VALIDATION DATE
                        if self.save_and_exit_picker(): return
                    else:
                        # MODE NORMAL : SWITCH VERS JOUR
                        self.active_panel = 1
                        self.side_cursor = 0 
                        self.scroll_offset = 0 

            # --- PANEL 1 & 2 (NON ACCESSIBLES EN PICKER MODE) ---
            elif self.active_panel in [1, 2]:
                evts = self.get_side_items()
                limit = len(evts) 
                
                if k == 'UP':
                    self.side_cursor = max(0, self.side_cursor - 1)
                elif k == 'DOWN':
                    self.side_cursor = min(limit, self.side_cursor + 1)
                elif k in ['\r', '\n']:
                    if self.side_cursor == limit:
                        form = AdvancedFormTUI(self.cal_service, self.task_service, self.selected_date, self, None)
                        if form.run(): self.last_fetch_month = None
                    else:
                        target_evt = evts[self.side_cursor]
                        form = AdvancedFormTUI(self.cal_service, self.task_service, self.selected_date, self, target_evt)
                        if form.run(): self.last_fetch_month = None


# --- EXPORT FUNCTIONS FOR PROJECT.PY ---

def get_calendar_service(config_dir):
    """Helper for external scripts to get service"""
    cal, _ = get_services(config_dir)
    return cal

def create_event(service, calendar_id, title, date_obj):
    """Helper for external scripts to create event"""
    body = {
        'summary': title,
        'start': {'date': date_obj.strftime('%Y-%m-%d')},
        'end': {'date': (date_obj + datetime.timedelta(days=1)).strftime('%Y-%m-%d')},
        'transparency': 'transparent'
    }
    try:
        service.events().insert(calendarId=calendar_id, body=body).execute()
        return True
    except: return False


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # --- DETECTION MODE PICKER VIA ARGUMENTS ---
    # Project.py sends: script.py --title "Display Title" "Customer Name"
    is_picker = False
    pick_title = ""
    
    # Argument parsing logic
    args = sys.argv[1:]
    if "--title" in args:
        try:
            # Find the index of --title and get the next argument
            t_index = args.index("--title")
            if t_index + 1 < len(args):
                is_picker = True
                pick_title = args[t_index + 1]
        except ValueError:
            pass
    elif len(args) > 0:
        # Fallback: If arguments exist but no --title flag, assume index 0 is title (Legacy behavior)
        is_picker = True
        pick_title = args[0]

    try:
        cal_service, task_service = get_services(current_dir)
        if not cal_service: 
            print("Auth Error.")
            time.sleep(2)
            sys.exit(1)
        
        # Calendar Retrieval
        cals_result = cal_service.calendarList().list().execute()
        target_ids = [c['id'] for c in cals_result.get('items', []) if c.get('selected', True)]
        
        # Launch App with Configuration
        app = CalendarTUI(cal_service, task_service, target_ids, picker_mode=is_picker, picker_title=pick_title)
        app.run()
        
    except Exception as e:
        print(f"Critical Error: {e}")
        time.sleep(3)