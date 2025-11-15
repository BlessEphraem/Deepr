    /**
     * @param {string} Title - The custom title for the Windows Terminal instance.
     * @param {string} Exe - The path to the Windows Terminal executable (e.g., 'wt.exe').
     * @param {Integer} [Position=3] - Screen position (1: Top-Left, 2: Top-Right, 3: Bottom-Left, 4: Bottom-Right).
     * @param {Integer} [Width=500] - The desired width of the window.
     * @param {Integer} [Height=300] - The desired height of the window.
     * @param {Integer} [CheckInterval=300] - Timer interval in ms to check focus.
     */
class Terminal {

    __new(title, exe, position := 3, width := 500, height := 300, checkInterval := 300, profilePath := "") {
        ; Call the initialization function
        this.Init(title, exe, position, width, height, checkInterval, profilePath)
    }

    /**
     * Initializes and positions the Windows Terminal window.
     * @private
     * @param {string} Title - The custom title for the Windows Terminal instance.
     * @param {string} Exe - The path to the Windows Terminal executable (e.g., 'wt.exe').
     * @param {Integer} Position - Screen position.
     * @param {Integer} Width - The desired width of the window.
     * @param {Integer} Height - The desired height of the window.
     * @param {Integer} CheckInterval - Timer interval in ms.
     */
    init(Title, Exe, Position, Width, Height, CheckInterval, profilePath) {
        ; Check if the terminal window already exists
        this.hwnd := WinExist(Title)
        
        if (!this.hwnd) {

            if (ProfilePath != "") {
                ; Explication de la commande :
                ; 1. wt.exe ... --title "..." : Lance le terminal avec le titre.
                ; 2. powershell.exe : L'application à lancer DANS le terminal.
                ; 3. -NoExit : Empêche la fenêtre de se fermer après l'exécution du script.
                ; 4. -Command ". 'chemin'" : Le point (.) signifie "Dot Source". 
                ;    Cela charge les variables/fonctions du script dans la session actuelle.
                
                ; Note : Les doubles quotes ('') autour du path dans le Format() deviennent des simples quotes dans la string finale pour PowerShell.
                RunStr := Format('{} -w 0 nt --title "{}" powershell.exe -NoExit -Command . `"{}"` ', Exe, Title, ProfilePath)

            } 
            else {
                ; Comportement par défaut si aucun profil n'est donné
                RunStr := Format('{} -w 0 nt -p "PowerShell" --title "{}"', Exe, Title)
            }

            Run(RunStr)

            ; Wait for the window with the title to appear
            this.hwnd := WinWait(Title, , 5) ; Wait max 5 seconds
            
            if (!this.hwnd) {
                MsgBox("Failed to detect the Windows Terminal window.")
                return
            }
        }

        ; Get the primary screen size
        MonitorWidth := A_ScreenWidth
        MonitorHeight := A_ScreenHeight
        
        ; Calculate X and Y coordinates based on the Position parameter
        X := 0
        Y := 0
        
        if (Position = 1) { ; Top-Left
            X := 0
            Y := 0
        } else if (Position = 2) { ; Top-Right
            X := MonitorWidth - Width
            Y := 0
        } else if (Position = 3) { ; Bottom-Left
            X := 0
            Y := MonitorHeight - Height
        } else if (Position = 4) { ; Bottom-Right
            X := MonitorWidth - Width
            Y := MonitorHeight - Height
        } else {
            ; Invalid value, default to Bottom-Right
            X := MonitorWidth - Width
            Y := MonitorHeight - Height
        }

        ; Position and show the window
        WinShow "ahk_id " this.hwnd
        WinMove X, Y, Width, Height, "ahk_id " this.hwnd
        WinSetAlwaysOnTop True, "ahk_id " this.hwnd
        WinActivate "ahk_id " this.hwnd

        ; Start monitoring the focus
        SetTimer this.Watch.Bind(this), CheckInterval
    }

    /**
     * Minimizes the window if it loses focus. Used as a SetTimer function.
     * @private
     */
    watch() {
        ; Ensure the window still exists
        if (!WinExist("ahk_id " this.hwnd)) {
            ; Stop the timer if the window is gone
            SetTimer , 0
            return
        }

        ; Check if the window is no longer active
        if (WinActive("A") != this.hwnd) {
            WinMinimize "ahk_id " this.hwnd
            ; Stop the timer as the window is minimized
            SetTimer , 0
        }
    }
}

/**  Example Usage (Optional, for context)
@example 
Term := Terminal("MyCustomTerminalTitle", "wt.exe", 3, 500, 300, 300)
        ; OR
Terminal("MyCustomTerminalTitle", "wt.exe", 3, 500, 300, 300)
*/
