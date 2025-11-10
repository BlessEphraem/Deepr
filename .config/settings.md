# ⚙️ Guide de Configuration (Settings.json)

Le fichier `settings.json` est le cœur de ce projet. Il sert de plan directeur que le script Python (`main.py`) utilise pour exécuter deux tâches principales :

1.  **Générer la structure des dossiers** : Il crée tous les dossiers et sous-dossiers de votre projet.
2.  **Générer le script AHK** : Il construit le fichier `.includes.ahk` (ou le nom que vous avez défini), qui contient :
    * Des variables de chemin statiques dans une classe (`A_Path`) pour un accès facile dans AHK.
    * Toutes les directives `#include` pour vos scripts AHK, automatiquement groupées par contexte (`#HotIf WinActive(...)`).

## Explication des Clés (Keys)

Chaque objet dans la `structure` peut contenir les clés suivantes :

| Clé | Obligatoire ? | Description |
| :--- | :--- | :--- |
| **`RootName`** | **Oui (Racine)** | (Présent une seule fois, à la racine) Le nom de votre projet. Sera utilisé pour générer le script AHK final (ex: `"Deepr"` crée `Deepr.ahk`). |
| **`type`** | **Oui** | L'identifiant logique de l'élément. **Utilisé comme nom de dossier** si `name` n'est pas fourni. **Utilisé comme nom de variable** dans la classe `A_Path` (ex: `A_Path.Library`). |
| **`name`** | Non | Si présent, ce sera le **nom du dossier physique** utilisé, à la place de `type`. Le `type` restera le nom de la variable AHK. |
| **`is_include`** | Non | (Défaut: `"true"`) Contrôle l'inclusion des scripts AHK. Si `"false"`, les scripts `.ahk` dans ce dossier **et ses sous-dossiers** ne seront PAS ajoutés au fichier `#include`. |
| **`is_path`** | Non | (Défaut: `"true"`) Contrôle la génération de la variable de chemin. Si `"false"`, `A_Path.MonType` ne sera pas créé, et ses enfants seront rattachés au parent (ex: `A_Path.Parent.Enfant` au lieu de `A_Path.Parent.MonType.Enfant`). |
| **`Active`** | Non | Définit le contexte `WinActive` pour les `#include` de ce dossier et de ses enfants. (ex: `"ahk_exe Adobe Premiere Pro.exe"`). Si la valeur est `"Windows"` ou absente, les scripts sont globaux. |
| **`children`** | Non | Un tableau `[]` contenant d'autres objets (dossiers) imbriqués. |

### Note Importante sur le Dossier de Configuration

Votre structure **doit** contenir un objet de configuration principal. Le script `main.py` est codé pour le rechercher (par défaut `CONFIG_TYPE = "Configuration"`). C'est dans ce dossier que le `settings.json` sera déplacé après la première exécution.

```json
{
    "rootName": "MyScripts",
    "structure": [
        {       
            "name": "config",
            "type": "Configuration",
            "is_include": "true"
        }
    ]
}
```

My personnal template :

```json
{
    "RootName": "Deepr",
    "structure": [
        {
            "name": ".config",
            "type": "Configuration",
            "is_include": "true"
        },
        {
            "type": "SupportFiles",
            "is_include": "false",
            "children": [
                {
                    "type": "AHK",
                    "is_include": "false"
                },
                {
                    "type": "Icons",
                    "is_include": "false"
                },
                {
                    "type": "Images",
                    "is_include": "false"
                },
                {
                    "type": "ImageSearch",
                    "is_include": "false"
                },
                {
                    "type": "Pythons",
                    "is_include": "false"
                },
                {
                    "type": "Sounds",
                    "is_include": "false"
                }
            ]
        },
        {
            "type": "Library",
            "is_include": "true",
            "children": [
                {
                    "type": "Core",
                    "Active": "Windows",
                    "description": "Scripts essentiels au fonctionnement global.",
                    "is_include": "true",
                    "children": [
                        {
                            "type": "Classes",
                            "is_include": "true"
                        },
                        {
                            "type": "Functions",
                            "is_include": "true"
                        }
                    ]
                },
                {
                    "type": "GUIs",
                    "is_include": "true",
                    "children":[
                        {
                            "type": "SupportFiles",
                            "is_path": "false",
                            "is_include": "true"
                        }
                    ] 
                },
                {
                    "type": "Modules",
                    "description": "Logiciels ou contextes spécifiques.",
                    "is_include": "true",
                    "children": [
                        {
                            "type": "Windows",
                            "Active": "Windows",
                            "is_include": "true",
                            "children": [
                                {
                                    "type": "Classes",
                                    "is_path": "false",
                                    "is_include": "true"
                                },
                                {
                                    "type": "Functions",
                                    "is_path": "false",
                                    "is_include": "true"
                                }
                            ]
                        },
                        {
                            "name": "Premiere Pro",
                            "type": "PremierePro",
                            "Active": "ahk_exe Adobe Premiere Pro.exe",
                            "is_include": "true",
                            "children": [
                                {
                                    "type": "Classes",
                                    "is_path": "false",
                                    "is_include": "true"
                                },
                                {
                                    "type": "Functions",
                                    "is_path": "false",
                                    "is_include": "true"
                                }
                            ]
                        },
                        {
                            "name": "After Effects",
                            "type": "AfterFx",
                            "Active": "ahk_exe AfterFX.exe",
                            "is_include": "true",
                            "children": [
                                {
                                    "type": "Classes",
                                    "is_path": "false",
                                    "is_include": "true"
                                },
                                {
                                    "type": "Functions",
                                    "is_path": "false",
                                    "is_include": "true"
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    ]
}
```