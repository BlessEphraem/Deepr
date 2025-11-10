#Requires AutoHotkey v2.0
#SingleInstance Force
/**
 * ```
 * Volume.Change(Action := '', ExeName := '', Value, ExePath := "")
 * ```
 * 
 * @Description - Can change, set or mute application sound volume using NirCmd utility.
 * 
 * @param {'Change'|'Set'|'Mute'} Action  -  Action to do on the app.
 * * `ChangeAppVolume` : Add/Subtract volume from specific app.
 * * `SetAppVolume` : Set precise volume for specific app.
 * * `MuteAppVolume` : Toggle mute for specific app.
 * 
 * @param {'{exeName}.exe'} ExeName  -  The Exe name.
 * 
 * @param {(Primitive)} Value
 * * Positive or Negative number between 0 and 1.
 * * Positive number increases the volume, Negative number decreases the volume.
 * 
 * @param {(String)} ExePath - A string param
 * 
 * @example 
 * ; Decrease Microsoft Edge volume by 2%.
 * Volume.Change("ChangeAppVolume", "msedge.exe", -0.02)
 * 
**/
class Volume {
    static Change(Action, ExeName, Value := "", ExePath := "Z:\Scripts\Tools\nircmd.exe") {
        try {
            Run('' ExePath ' ' Action ' ' ExeName ' ' Value '',, "Hide")
        } catch as e {
            return MsgBox('Error while trying to open "nircmd.exe".')  
        }   
    }

    /**
     * @class
     * Manages the launch, positioning, and sizing of the Windows Volume Mixer (SndVol.exe).
     * It uses WinWait and WinMove to control the target window.
     * * **CONFIGURATION**: All positioning parameters (MONITOR_INDEX, SndVol_WIDTH, etc.) 
     * are now passed directly to the Init() and Toggle() methods, making the behavior 
     * fully dynamic per call.
     * * @methods
     * Init() | Launches and positions the window based on provided parameters.
     * Toggle() | Closes the window if visible, or calls Init() with parameters if hidden.
     * * @example
     * ; Launches SndVol on monitor 2 (index 1), 600px wide, centered at the top.
     * ^s:: SndVol.Toggle(1, 600, 250, 50, 5)
     */
    class SndVol {
    
        ; --- WINDOW PROPERTIES ---
        ; The Title and Class of the target window (Volume Mixer)
        static WINDOW_TITLE := 'Volume Mixer'
        static WINDOW_CLASS := '#32770'
    
        /**
         * @static
         * **TOGGLE METHOD:** Closes the SndVol window if it is visible,
         * or calls Init() to launch and position it if it is not found.
         * * @param MONITOR_INDEX (Optional) The 0-based index of the target monitor. Defaults to 0 (primary).
         * @param SndVol_WIDTH (Optional) The desired width of the window. Defaults to 1000.
         * @param SndVol_HEIGHT (Optional) The desired height of the window. Defaults to 200.
         * @param SCREEN_MARGIN_EDGE (Optional) The margin (in pixels) from the monitor edge. Defaults to 80.
         * @param LOCATION (Optional) Code for positioning (1-8). Defaults to 5 (Top, Centered).
         * @returns True if the window was closed, False if it was launched.
         * * @example
         * SndVol.Toggle(1, 800, 200, 50, 8) ; Launch/Toggle on monitor 2, 800px wide, Bottom Centered (8).
         */
        static Toggle(MONITOR_INDEX := 0, SndVol_WIDTH := 1000, SndVol_HEIGHT := 200, SCREEN_MARGIN_EDGE := 80, LOCATION := 5) {
            ; Use partial title matching to ensure the window is found regardless of dynamic title changes.
            SetTitleMatchMode(2) 
        
            Local WindowTarget := this.WINDOW_TITLE ' ahk_class ' this.WINDOW_CLASS
            
            ; Checks if the window exists
            if (WinExist(WindowTarget)) {
                ; If the window exists, close it.
                WinClose(WindowTarget)
                Return True ; Indicates the window was closed
            } else {
                ; If the window doesn't exist, launch it via Init(), passing all current parameters.
                ; Note: 'this.Init()' is called, not 'Init()'.
                this.Init(MONITOR_INDEX, SndVol_WIDTH, SndVol_HEIGHT, SCREEN_MARGIN_EDGE, LOCATION)
                Return False ; Indicates the window was launched
            }
        }
    
        /**
         * @static
         * Launches SndVol.exe, waits for its window to appear, and then positions and sizes it
         * according to the provided parameters.
         * * @param MONITOR_INDEX The 0-based index of the target monitor.
         * @param SndVol_WIDTH The desired width of the window.
         * @param SndVol_HEIGHT The desired height of the window.
         * @param SCREEN_MARGIN_EDGE The margin (in pixels) from the monitor edge.
         * @param LOCATION Code for positioning (1-8).
         * @returns Nothing. Returns early on error (e.g., WinWait failure).
         * * @example
         * ; Launch SndVol on the primary monitor (0), Top-Left (1), with a 50px margin.
         * SndVol.Init(0, 500, 300, 50, 1)
         */
        static Init(MONITOR_INDEX, SndVol_WIDTH, SndVol_HEIGHT, SCREEN_MARGIN_EDGE, LOCATION) {
            ; * * LOCATION Codes:
            ; * 1: TopLeft, 2: TopRight, 3: BottomLeft, 4: BottomRight
            ; * 5: Top (Centered), 6: Left (Centered), 7: Right (Centered), 8: Bottom (Centered)
            
            SetTitleMatchMode(2) 
            
            ; 1. Launch SndVol.exe
            Run('SndVol.exe')
        
            ; 2. Wait for the Volume Mixer window to appear
            Local WindowTarget := this.WINDOW_TITLE ' ahk_class ' this.WINDOW_CLASS
            if (!WinWait(WindowTarget, , 5)) {
                MsgBox('Error: Could not find the "' this.WINDOW_TITLE '" window within 5 seconds.')
                return
            }
        
            ; 3. Calculate Monitor Coordinates (using WorkArea to exclude the taskbar)
            ; Monitor IDs are 1-based, so we add 1 to the 0-based MONITOR_INDEX.
            Local MonitorLeft, MonitorTop, MonitorRight, MonitorBottom
            try {
                MonitorGetWorkArea(MONITOR_INDEX + 1, &MonitorLeft, &MonitorTop, &MonitorRight, &MonitorBottom)
            } catch {
                ; Fallback to the primary screen (Monitor ID 1) if the index is invalid
                MonitorGetWorkArea(1, &MonitorLeft, &MonitorTop, &MonitorRight, &MonitorBottom)
            }
            
            ; Fallback check...
            if (MonitorRight == '') {
                MsgBox('Error: Could not retrieve monitor dimensions.')
                return
            }
        
            ; 4. Calculate SndVol Window Position (X, Y)
            
            Local MonitorWidth := MonitorRight - MonitorLeft
            Local MonitorHeight := MonitorBottom - MonitorTop
        
            ; Adjust the window size if it exceeds monitor dimensions
            Local SndVol_WIDTH_Actual := SndVol_WIDTH, SndVol_HEIGHT_Actual := SndVol_HEIGHT
            
            if (SndVol_WIDTH_Actual > MonitorWidth) {
                SndVol_WIDTH_Actual := MonitorWidth
            }
            if (SndVol_HEIGHT_Actual > MonitorHeight) {
                SndVol_HEIGHT_Actual := MonitorHeight
            }
        
            Local Target_X := 0, Target_Y := 0
            
            ; --- Calculate X Coordinates ---
            if (LOCATION = 1 or LOCATION = 3) ; TopLeft or BottomLeft
                Target_X := MonitorLeft + SCREEN_MARGIN_EDGE
            else if (LOCATION = 2 or LOCATION = 4) ; TopRight or BottomRight
                Target_X := MonitorRight - SndVol_WIDTH_Actual - SCREEN_MARGIN_EDGE
            ; Centered X for Top/Bottom/Left/Right placements (5, 6, 7, 8)
            else
                Target_X := MonitorLeft + (MonitorWidth // 2) - (SndVol_WIDTH_Actual // 2)
            
            ; --- Calculate Y Coordinates ---
            if (LOCATION = 1 or LOCATION = 2 or LOCATION = 5) ; TopLeft, TopRight, Top (Centered)
                Target_Y := MonitorTop + SCREEN_MARGIN_EDGE
            else if (LOCATION = 3 or LOCATION = 4 or LOCATION = 8) ; BottomLeft, BottomRight, Bottom (Centered)
                Target_Y := MonitorBottom - SndVol_HEIGHT_Actual - SCREEN_MARGIN_EDGE
            ; Centered Y for Left/Right placements (6, 7)
            else if (LOCATION = 6 or LOCATION = 7)
                Target_Y := MonitorTop + (MonitorHeight // 2) - (SndVol_HEIGHT_Actual // 2)
            
            ; 5. Position and Size the Window
            ; A second WinWait is sometimes needed to ensure the window is ready for WinMove/Activate
            WinWait(WindowTarget, , 5)
            Sleep 100
            WinMove(Target_X, Target_Y, SndVol_WIDTH_Actual, SndVol_HEIGHT_Actual, WindowTarget)
            
            ; 6. Ensure the window is active and visible
            WinActivate(WindowTarget)
        }
    }
}
