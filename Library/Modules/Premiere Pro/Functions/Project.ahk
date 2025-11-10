#Requires AutoHotkey v2.0

/**
 * @class Project
 * Class to manage and interact with Premiere Pro Project-level functions,
 * primarily focusing on project name extraction and activation.
 * NOTE: Assumes Application_Class.PremierePro.winClass is defined elsewhere.
 */
class Project {

    /**
     * @static
     * Gets the name of the main active project in Premiere Pro.
     * The Bin panel is focused before extraction to ensure the correct window is active/targeted.
     *
     * @returns {string} The base name of the active project file (e.g., "ActiveOpenedProject").
     */
    static A_ThisProject {
        get {
            Panel.Focus("Bin") ; Ensure the Bin panel is active before reading the window title.
            return this.GetActive()
        }
    }

    /**
     * @static
     * Gets the active Premiere Pro project's base name from the main window title.
     * This relies on the main Premiere Pro window title format.
     *
     * @returns {string|number} The base project name, or an error message box result if extraction fails.
     */
    static GetActive() {
        ; Get the main Premiere Pro window handle using its defined class.
        /** @type {number} */
        Premiere := WinExist(Application_Class.PremierePro.winClass)
        /** @type {string} */
        FullTitle := WinGetTitle(Premiere)
        ; Expected format example: "Adobe Premiere Pro {VER} - D:\User\Projects\ActiveOpenedProject.prproj *"
        
        ; RegEx to extract the project name without the extension.
        ; .*: Matches the beginning of the title.
        ; \\: Matches the final backslash preceding the filename path separator.
        ; (.+?): Capture group 1. Captures one or more characters non-greedily (the project name).
        ; \.prproj: Matches the file extension.
        ; \s*\**$: Matches optional spaces and the optional asterisk (*), followed by the end of the string.
        /** @type {string} */
        RegEx := ".*\\(.+?)\.prproj\s*\**$"
        
        ; Match the pattern against the window title.
        if RegExMatch(FullTitle, RegEx, &Match) {
            /** @type {string} */
            ActiveProject := Match[1]
            return ActiveProject
            ; Returns: "ActiveOpenedProject"
        } else {
            return MsgBox("Error: Could not extract active project name from window title.")
        }
    }

    /**
     * @static
     * Cycles through the Bin controls (open projects/shortcuts) in the Project Panel 
     * using the 'Bin' panel hotkey to find and focus the bin corresponding to the specified project name.
     *
     * @param {string} [ProjName=A_ThisProject] The base name of the project/bin to activate.
     * @returns {string|number} Returns a text string indicating success or failure, potentially with debug info.
     */
    static Activate(ProjName := this.A_ThisProject) {
        
        ; 1. Focus the Bin panel to start the focus cycle.
        Panel.Focus("Bin")
        Sleep(50)
        
        ; Array to store the ClassNN of visited controls to detect a full cycle (end of list).
        /** @type {string[]} */
        AllBins := []
        
        Loop {
            ; 2. Get the ClassNN of the currently focused control.
            /** @type {string} */
            CurrentBinClassNN := ControlGetClassNN(ControlGetFocus("A"))
            
            ; 3. Cycle check: If this ClassNN is already in AllBins, we've completed a full cycle.
            for _, StoredBin in AllBins {
                if (CurrentBinClassNN == StoredBin) {
                    ; Cycle detected, bin not found.
                    /** @type {string} */
                    ResultText := "Failure: Bin cycle is complete. The bin '" ProjName "' was not found."
                    ResultText .= "`n`nClassNN at failure: " CurrentBinClassNN
                    ResultText .= "`nNumber of Bins visited: " AllBins.Length
                    return ResultText
                }
            }
            
            ; Add the current ClassNN to the list of visited bins.
            AllBins.Push(CurrentBinClassNN)
            
            ; 4. Get the name of the active project/bin (based on the window title)
            /** @type {string|number} */
            ActiveName := this.GetActive()
            
            ; 5. Check the return from GetActive(). If it's an error message, stop.
            if (!ActiveName || InStr(ActiveName, "Error:")) {
                ; If GetActive returned an error message, treat it as a failure.
                /** @type {string} */
                ResultText := "Failure: Project.GetActive() encountered an error during name extraction. Stopping search."
                ResultText .= "`nLast ClassNN: " CurrentBinClassNN
                return ResultText
            }
            
            ; 6. Success check
            if (ActiveName == ProjName) {
                /** @type {string} */
                ResultText := "Success: Bin '" ProjName "' found and focused!"
                ResultText .= "`n`nClassNN found: " CurrentBinClassNN
                ResultText .= "`nNumber of Bins visited: " AllBins.Length
                return ResultText
            }
            
            ; 7. Move to the next bin
            Sleep(5)
            ; Use Panel.Focus("Bin", false) to send the hotkey again without the reset, 
            ; which in Premiere Pro cycles focus among controls within the panel (the opened bins/projects).
            Panel.Focus("Bin", false)
            Sleep(100)
        }
    }

}


/**
 * @class Bin
 * Class to manage and interact with Premiere Pro Bins (or project panels/shortcuts).
 * Works with imported Shortcut Projects as well.
 */
class Bin {
    /**
     * @static
     * Attempts to cycle the focus to a specific Bin (or opened project shortcut) index in the Project Panel.
     *
     * @param {number} Index The 1-based index of the Bin to focus. Must be 1 or higher.
     * @returns {number|void} Returns an error message box if the index is invalid, otherwise void.
     */
    static Focus(Index) {
        if (Index < 1) {
            return MsgBox("Error: Index must be 1 or higher.")
        }

        /** @type {string[]} */
        AllBins := []

        ; 1. Ensure the Bin panel is focused. (Panel.Focus is assumed to be defined elsewhere.)
        Panel.Focus("Bin")
        Sleep(50)

        ; Get the ClassNN of the control currently focused (expected to be Bin 1).
        /** @type {string} */
        FirstBin := ControlGetClassNN(ControlGetFocus("A"))
        AllBins.Push(FirstBin)

        ; Cycle focus (Index - 1) times to reach the target Bin index.
        Loop (Index - 1) {
            /** @type {string} */
            PrevBin := ControlGetClassNN(ControlGetFocus("A"))
            ; Store the current control's ClassNN for cycle detection later.
            AllBins.Push(PrevBin)
            
            Sleep(5)
            ; Cycle focus to the next Bin control without resetting the main Bin panel focus.
            Panel.Focus("Bin", false)
            Sleep(100) ; Small pause between key presses
        }
    
        ; Get the ClassNN of the final focused control.
        /** @type {string} */
        FinalBin := ControlGetClassNN(ControlGetFocus("A"))

        /** @type {boolean} */
        IsUnique := true

        ; Check if the FinalBin control is a duplicate of any previously visited control,
        ; indicating a failure to move to a new unique control (e.g., end of the list/cycle).
        for _, StoredBin in AllBins {
            ; Strict comparison of values
            if (FinalBin == StoredBin) {
                IsUnique := false ; FinalBin is NOT unique, a cycle/failure is detected.
                break ; Exit the loop as soon as a duplicate is found.
            }
        }
    
        /** @type {string} */
        /** @type {string} */
        ControlList := "FirstBin: " FirstBin '`n'
        ControlList .= "FinalBin: " FinalBin '`n' 
        ControlList .= "Index demandé: " Index '`n'
        
        if (IsUnique) {
            ; Success: FinalBin is different from all previously recorded controls.
            MsgBox("Success (UNIQUE Final Control):`n" ControlList)
        } else {
            ; Failure: FinalBin is identical to an earlier control (cycle detected).
            MsgBox("Failure (NON-UNIQUE Final Control - Cycle Detected): `n" ControlList)
        }
    }
}