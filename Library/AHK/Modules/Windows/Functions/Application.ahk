#Requires AutoHotkey v2.0

/************************************************************************
 * @description - Functions to run/focus/minimize applications based on window titles or criteria.
 * Original from JuanmaMenendez (https://github.com/JuanmaMenendez/AutoHotkey-script-Open-Show-Apps/blob/master/Open-Apps-and-Switch-opened-windows.ahk)
 * @STILL_IN_PROGRESS (BrowserApp untested yet, Title can be hard to use)
 ***********************************************************************/


; example:
; Application.Window("ahk_exe Adobe Premiere Pro.exe", "C:\Program Files\Adobe\Adobe Premiere Pro 2025\Adobe Premiere Pro.exe")

/**
 * @class Application
 * Provides static methods for managing application windows (launch, focus, minimize)
 * based on window criteria or specific application types (e.g., browsers, Explorer).
 */
class Application {
    /**
     * @description Toggles between Run/Minimize/Focus for a Chrome-based browser app (e.g., as a PWA).
     * This method currently relies on the more generic `Window` method.
     * @param {string} titlePart - A partial window title to match the existing window.
     * @param {string} url - The URL to open in app mode (e.g., 'https://mail.google.com/mail/').
     * @param {string} appPath - The full path to the browser executable (e.g., 'C:\Program Files\Google\Chrome\Application\chrome.exe').
     * @returns {void}
     * @example
     * Application.BrowserApp('Gmail', 'https://mail.google.com/mail/', 'C:\Program Files\Google\Chrome\Application\chrome.exe')
     */
    static BrowserApp(titlePart, url, appPath)
    {
        ; SetTitleMatchMode 2 is the default value for AHK v2.0 (TitleMatchMode "Contains").
        ; Construct the full command line to run the browser in PWA/App mode.
        compose := appPath . ' --app=' url
        ; Calls the generic Window method, using 'titlePart' as the window criterion and 'appPath' as the run command.
        ; NOTE: This call is likely intended to use `compose` as the run command for launching,
        ; but currently uses `appPath`, which runs the browser without the PWA argument unless
        ; the intention is to only match the running process.
        this.Window(titlePart, appPath) ; Note: titlePart is used here as winCriteria, which might be too broad.
    }


    /**
     * @description Toggles between Run/Minimize/Focus for an app using its window Title.
     * This method specifically enforces RegEx matching for the Title parameter.
     * @param {string} Title - The window title to match. Uses RegEx syntax (e.g., 'Microsoft.*Edge').
     * @param {string} AppAddress - The path/command to run the application (e.g., 'msedge.exe').
     * @returns {void}
     * @example
     * Application.Title('Microsoft.*Edge', 'msedge.exe')
     */
    static Title(Title, AppAddress)
    {
        ; A_TitleMatchMode defaults to "2" (Contains). Setting it explicitly to "2" here is redundant
        ; but included for clarity/legacy.
        A_TitleMatchMode := "2"
        SetTitleMatchMode "regEx" ; Temporarily switch to RegEx mode for Title matching.

        ; Check if the process exists (a rough proxy for the application being open).
        If ProcessExist(AppAddress) {
            ; If process exists, check if the window is currently active (using RegEx match on Title).
            If WinActive(Title) {
                WinMinimize(Title) ; Minimize if active.
            } else {
                WinActivate(Title) ; Activate if open but inactive.
            }
        } 
        ; If the process does not exist, attempt to run the application.
        else try {
            ; After running, activation will be handled automatically by the OS or the process itself.
            run AppAddress
        } catch as e {
            ; Display an error if the application cannot be launched.
            msgbox e . AppAddress
        }
        ; SetTitleMatchMode is NOT automatically reverted here; be cautious of side effects.
    }

/**
 * @description Toggles between Run/Minimize/Focus for an application based on a window criterion.
 * This is the core function for application toggling.
 * @param {string} winCriteria - The base criterion (e.g., 'ahk_exe Discord.exe', 'ahk_class CabinetWClass').
 * @param {string} runCommand - The command/path to run, also used to refine the window title search for Explorer.
 * @param {boolean} [force=false] - If true, ignores existing windows and forces a new application launch.
 * @returns {string|void} The action taken ("Minimize", "Activate", "Launch") or void on error.
 */
static Window(winCriteria, runCommand, force := false) {
    
    ; --- 1. DEFINE THE FULL WINDOW CRITERIA ---
    ; This section attempts to refine the criteria, especially for File Explorer windows.
    
    ; Build precise WinTitle criteria (especially for Explorer)
    WinTitleCriteria := ""
    ; Check if criteria includes Explorer class AND runCommand is a valid file/folder path.
    if (InStr(winCriteria, "CabinetWClass") && FileExist(runCommand)) {
        ; Extract the folder/file name for the title matching (Explorer window title usually contains this).
        SplitPath(runCommand, &FileName)
        WinTitleCriteria := FileName ; Search for a window title containing the folder name.
    }

    ; Combine the criteria: Base criterion OR the specific Explorer class.
    FullWinCriteria := (WinTitleCriteria ? 'ahk_class CabinetWClass' : winCriteria) ; The Title/Criteria for WinExist
    ; WinText is used for the folder name search (if it's an Explorer path).
    WinTextCriteria := WinTitleCriteria ? WinTitleCriteria : "" ; The partial title (WinText) for WinExist

    ; --- 2. CHECK FOR EXISTENCE / TOGGLE (unless forced) ---
    if !force && WinExist(FullWinCriteria, WinTextCriteria) {
        if WinActive(FullWinCriteria, WinTextCriteria) {
            WinMinimize(FullWinCriteria, WinTextCriteria)
            return "Minimize"
        } else {
            WinActivate(FullWinCriteria, WinTextCriteria)
            return "Activate"
        }
    } 
    
    ; --- 3. LAUNCH (if non-existent or forced) ---
    else try {
        ; NOTE: For Explorer (runCommand = a path), Run opens this path in a new window.
        Run(runCommand) ; Launch the application/path.
        
        ; Activation logic for the newly launched window.
        
        ; WinWait and activate only if NOT forced AND the command is not 'edge.exe' (specific exclusion).
        if (!force && !InStr(runCommand, 'edge.exe')) {
            WinWait(FullWinCriteria, WinTextCriteria) ; Wait for the window to appear.
            WinActivate(FullWinCriteria, WinTextCriteria) ; Activate the found window.
        }
        return "Launch"
    } catch as e {
        MsgBox('Error launching: ' . runCommand . '`nMessage: ' . e.Message)
        return
    }
}


    /**
     * @description Toggles between Run/Minimize/Focus for File Explorer, with an option to open a specific Path or find it in an existing tab.
     * NOTE: Requires Application_Class.Explorer.winClass and Application_Class.Explorer.path to be defined externally.
     * @param {string} [Path=""] - The path to open (file, folder, or drive). If empty, it toggles the default Explorer window.
     * @param {boolean|string} [NewTab=false] - If true, tries to open the path in a new tab. If "Actual", opens in the current tab. Defaults to false (new window or find existing).
     * @param {boolean} [ForceOpen=false] - If true, skips tab searching and forces opening the path (new tab or current tab).
     * @returns {void}
     * @example
     * Application.Explorer("Z:\Scripts", false) ; Toggle or open in new window
     * Application.Explorer("C:\Users\Name\Documents", true) ; Open path in a new tab
     */
    static Explorer(Path := "", NewTab := false, ForceOpen := false) {
        ; NOTE: Requires the existence of a global Application_Class object.
        local winCriteria := Application_Class.Explorer.winClass ; Expected to be 'ahk_class CabinetWClass'
        local runCommand := Application_Class.Explorer.path ; Expected to be 'explorer.exe' or default path
        local winID := WinExist(winCriteria)
        
        if (winID) {
            ; --- BASE LOGIC (Focus/Minimize) ---
            if (Path == "") {
                if WinActive(winCriteria) {
                    WinMinimize(winCriteria) ; <-- Minimize if already active
                    return
                } else {
                    WinActivate(winCriteria) ; <-- Activate if open but inactive
                    return
                }
            } else {

                ; If Path is NOT empty, continue with activation/tab management logic.
                ; Ensure the window is active for subsequent SendInput commands.
                if WinActive(winCriteria) {
                    ; If active and a path is specified, it seems the intention is to minimize it (exit 1).
                    ; This logic might be intended for a different workflow.
                    WinMinimize(winCriteria)
                    return msgbox("exit 1")
                } else {
                    WinActivate(winCriteria)
                    WinWaitActive(winCriteria)
                }

                ; If a path is specified, check if it's an existing tab
                local FullTitle := WinGetTitle(winID)
                
                ; 1. Tab Count Detection using RegEx.
                local Match := []
                ; Checks for the " and X more tabs" suffix in the title.
                local found := RegExMatch(FullTitle, " and (\d+) more tabs - File Explorer", &Match)
                
                ; numExtraTabs = Number of additional tabs. totalTabs = Total number of tabs (numExtraTabs + 1).
                local numExtraTabs := found ? Match[1] : 0 
                local totalTabs := numExtraTabs + 1

                ; Extract the last folder/file name from the Path.
                local folderName := RegExReplace(Path, ".*[\\/](.+)", "$1")
                
                ; Send a Tab press, often used to ensure the window is ready for hotkeys after activation/minimization.
                SendInput "{Tab}"
                BlockInput true ; Block user input during SendInput sequence.

                ; --- FORCE OPEN LOGIC ---
                if ForceOpen {
                    if NewTab = true {
                        ; Open path in a NEW tab (Ctrl+T, Alt+D for address bar, paste, Enter)
                        SendInput "^{t}"
                        Sleep 600 ; Wait for new tab to open
                        SendInput "!{d}"
                        
                        Sleep 200
                        SendInput Path
                        Sleep 100
                        SendInput "{Enter}"
                        BlockInput false
                        return
                    }

                    if NewTab = "Actual" {
                        ; Open path in the ACTUAL tab (Alt+D for address bar, paste, Enter)
                        SendInput "!{d}"
                        sleep 200
                        SendInput Path
                        Sleep 100
                        SendInput "{Enter}"
                        BlockInput false
                        return
                    }
                }
                
                ; --- TAB SEARCH LOGIC (if not forced and multiple tabs exist) ---
                if (totalTabs > 1) {
                    local targetFound := false
                    
                    ; Loop through all tabs (totalTabs times).
                    Loop totalTabs
                    {
                        ; 2. Get the ACTIVE tab's title (must be retrieved after each ^Tab).
                        local currentTitle := WinGetTitle(winCriteria)
                        
                        ; Clean the title: Remove multi-tab suffix and single-tab suffix.
                        local cleanTitle := RegExReplace(currentTitle, " and \d+ more tabs - File Explorer", "")
                        cleanTitle := RegExReplace(cleanTitle, " - File Explorer", "") 
                        
                        ; 3. Compare the active tab name with the searched path (folderName).
                        if (InStr(cleanTitle, folderName)) {
                            targetFound := true
                            WinActivate(winCriteria) ; Ensure the found tab remains active.
                            WinWaitActive(winCriteria)
                            break 
                        }

                        ; 4. Switch to the next tab (N-1 times).
                        if (A_Index < totalTabs) {
                            SendInput "^{Tab}" ; Ctrl+Tab
                            Sleep 200 ; Essential: Wait for the window title to update after tab switch.
                        }
                    }
                    
                    if (targetFound) {
                        BlockInput false
                        return ; Tab was found and activated.
                    } else {
                        ; Tab was not found in the loop. Open the path (new window/tab).
                        if NewTab = true {
                            ; Open path in a NEW tab
                            SendInput "^{t}"
                            Sleep 600
                            SendInput "!{d}"
                            
                            Sleep 200
                            SendInput Path
                            Sleep 100
                            SendInput "{Enter}"
                            BlockInput false
                            return
                        }

                        if NewTab = "Actual" {
                            ; Open path in the ACTUAL tab (overwrite current path)
                            SendInput "!{d}"
                            sleep 200
                            SendInput Path
                            Sleep 100
                            SendInput "{Enter}"
                        }

                        ; Fallback: Open in a NEW WINDOW (if NewTab was false/unspecified).
                        Run("explorer.exe " . Path)
                        BlockInput false
                        return
                    }
                    
                } else {
                    ; --- SINGLE-TAB MODE (totalTabs = 1) ---
                    BlockInput false
                    local singleTabName := RegExReplace(FullTitle, " - File Explorer", "")
                    
                    ; Check if the single active tab matches the path name.
                    if (InStr(singleTabName, folderName)) {
                        WinActivate(winCriteria) 
                        WinWaitActive(winCriteria)
                        BlockInput false
                        return ; Correct folder is already active.
                    } else {
                        ; Not the correct folder, open the path (new window/tab logic repeats).
                        if NewTab = true {
                            ; Open path in a NEW tab
                            SendInput "^{t}"
                            Sleep 600
                            SendInput "!{d}"

                            Sleep 200
                            SendInput Path
                            Sleep 100
                            SendInput "{Enter}"
                            BlockInput false
                            return
                        }
                        if NewTab = "Actual" {
                            ; Open path in the ACTUAL tab
                            SendInput "!{d}"
                            sleep 200
                            SendInput Path
                            Sleep 100
                            SendInput "{Enter}"
                        }
                        
                        ; Fallback: Open in a NEW WINDOW
                        Run("explorer.exe " . Path)
                        WinActivate(winCriteria) ; Activate the newly opened window/tab
                        WinWaitActive(winCriteria)
                        BlockInput false
                        return
                    }
                }
            }
        } 
        ; --- LAUNCH (if window does not exist) ---
        else try {
            ; Window does not exist, run the command (Path takes precedence for launching).
            local commandToRun := (Path != "") ? "explorer.exe " . Path : runCommand
            
            Run(commandToRun) ; Launch if not found
            
            ; Wait and activate the new window.
            WinWait(winCriteria)
            WinActivate(winCriteria)
            WinWaitActive(winCriteria)
            
            return
        } catch as e {
            MsgBox('Error launching: ' . (Path != "" ? Path : runCommand) . '`nMessage: ' . e.Message)
            return
        }
    }

}