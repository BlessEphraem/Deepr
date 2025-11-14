#Requires AutoHotkey v2.0

/**
 * @class Motion
 * Provides methods for controlling and manipulating the 'Motion' effect properties
 * within the Effect Controls panel in Adobe Premiere Pro, primarily using image and pixel searching.
 * NOTE: Relies heavily on external functions/classes like Panel.ClassNN, FileNameConstructor, 
 * FindImage, fpath.ImageSearch, KS_Premiere, and WaitForUserConfirm.
 */
class Motion{
    /**
     * @static
     * Initializes the Motion effect for manipulation by finding its location, checking its state (Open/Closed),
     * and toggling it if needed. It uses image search within the Effect Controls panel.
     * @param {string} prefix - Part of the image filename constructor (e.g., application name).
     * @param {string} theme - Part of the image filename constructor (e.g., 'Dark' theme).
     * @param {string} name - The specific name to search for (e.g., 'Motion').
     * @param {string} format - The image file extension (e.g., 'png').
     * @param {string} [picturePath=fpath.ImageSearch] - The directory where search images are located.
     * @param {string} [NewState="Open"] - The desired state for the Motion effect ("Open" or "Close").
     * @param {number} [attempts=3] - Number of times to retry finding the image/effect.
     * @returns {Object|void} An object containing the Effect Controls panel dimensions (x, y, w, h) on success, or void on failure.
     */
    static Initialize(prefix, theme, name, format, picturePath := A_Path.ImageSearch, NewState := "Open", attempts := 3) {
        ; Set coordinate modes to 'Window' for all functions operating within the Premiere window.
        CoordMode "Mouse", "Window"
        CoordMode "ToolTip", "Window"
        CoordMode "Pixel", "Window"
        DllCall("SetProcessDPIAware") ; Ensure DPI scaling compatibility.
        
        imageName := FileNameConstructor(prefix, theme, name, format) ; Construct the name of the image file to search for.

        Sleep(33)
        ClassPanel := Panel.ClassNN("EffectControls") ; Get coordinates and info for the Effect Controls panel.

        Restart:
        sleep 66
        ; Search for the 'Motion' text/icon image within the Effect Controls panel area.
        MotionPos := FindImage(imageName, ClassPanel.x, ClassPanel.y, ClassPanel.w, ClassPanel.h, 150, picturePath)
        
        if !MotionPos {
            attempts--
            sleep 5
            ; Toggle "Selection Follows Playhead" to try and refresh the panel content/selection.
            SendInput KS_Premiere.Timeline.Selection_Follow_Playhead
            sleep 5
            SendInput KS_Premiere.Timeline.Selection_Follow_Playhead
            if attempts = 0 {
                MsgBox("Failed : Make sure you got a Target Track active `n with a layer under playhead", Err)
                Exit
            }
            else
                goto Restart ; Retry image search.
        } else {
            ; Calculate the position of the disclosure triangle (arrow) relative to the found image.
            ArrowPos := {
                X : MotionPos.X-27,
                Y : MotionPos.Y+6
            }
            ;MouseMove ArrowPos.X, ArrowPos.Y, 0
            
            ; Check the pixel color at the arrow position to determine if the effect is open or closed.
            PixelCheck := PixelGetColor(ArrowPos.X, ArrowPos.Y)
            sleep 5
            
            ; Pixel color checks based on Premiere's "Darkest" theme (standard UI colors).
            if (PixelCheck = "0x2E2E2E") {
                ; 0x2E2E2E is the closed/dark state color.
                sleep 5
                ;tooltip "Motion // Twirl : Closed", +200
                state := "Motion // Twirl : Closed"
                }
            if (PixelCheck = "0xC1C1C1") {
                ; 0xC1C1C1 is the opened/light state color.
                sleep 5
                ;tooltip "Motion // Twirl : Opened", +200
                state := "Motion // Twirl : Opened"
                }

            try {
                ; Toggle the state if the current state does not match the desired NewState.
                if NewState = "Close" AND state = "Motion // Twirl : Opened" {
                    BlockInput("MouseMove")
                    Sleep(33)
                    Click "Left", ArrowPos.X, ArrowPos.Y
                    
                }
                else if NewState = "Open" AND state = "Motion // Twirl : Closed" {
                    BlockInput("MouseMove")
                    Sleep(33)
                    Click "Left", ArrowPos.X, ArrowPos.Y
                }
                
                BlockInput("MouseMoveOff") ; Release mouse block after the click, if it occurred.
                
                ; Return the panel coordinates for subsequent operations (e.g., HotBar).
                return {
                    x: ClassPanel.x,
                    y: ClassPanel.y,
                    w: ClassPanel.w,
                    h: ClassPanel.h,
                }
            } catch {
                BlockInput("MouseMoveOff")
                tooltip "Failed : PixelGetColor Error"
                Exit
            }
        }    
    }

    /**
     * @static
     * Searches for a specific text/icon image within the Motion effect section of the Effect Controls panel.
     * This is used to locate a specific property bar (e.g., 'Position', 'Scale').
     * @param {string} prefix - Part of the image filename constructor.
     * @param {string} theme - Part of the image filename constructor.
     * @param {string} name - The specific name of the property bar to search for.
     * @param {string} format - The image file extension.
     * @returns {Object|void} An object containing the coordinates (x, y) and expected dimensions (w: 250, h: 18) of the property bar.
     */
    static HotBar(prefix, theme, name, format) { ; searches for text inside of the Motion effect. requires an actual image.
        CoordMode "Pixel", "Window"
        CoordMode "ToolTip", "Window"
        CoordMode "Mouse", "Window"
        imageName := FileNameConstructor(prefix, theme, name, format)
        attempts := 3

        Restart:
        ; First, ensure the 'Motion' effect is initialized (and opened by default).
        MotionPanel := this.Initialize(prefix, theme, "Motion", format)
        sleep 66

        ; Search for the specific property bar image within the Motion panel's bounds.
        HotbarPos := FindImage(imageName, MotionPanel.x, MotionPanel.y, MotionPanel.w, MotionPanel.h, 150)
        ;sleep(1500)
        if !FindImage{
            attempts--
            if attempts = 0 {
                Exit MsgBox("Failed : FindImage Not Found", Err)
            }
            else
                goto Restart
        } else {
            ;tooltip "FindImage Found"
            ; Move the mouse cursor to the found position.
            MouseMove HotbarPos.X, HotbarPos.Y, 0
            ; Return the position and expected size of the property bar for further actions.
            return { x: HotbarPos.X, y: HotbarPos.Y, w: 250, h: 18}
        }
    }

    /**
     * @static
     * Finds and initiates interaction (click-and-drag) on the numerical value within a Motion property bar
     * (e.g., the 'X' or 'Y' Position value). It uses PixelSearch to find the blue highlight color.
     * @param {string} prefix - Part of the image filename constructor.
     * @param {string} theme - Part of the image filename constructor.
     * @param {string} name - The name of the property bar (e.g., 'Position') to use in HotBar search.
     * @param {string} format - The image file extension.
     * @returns {void}
     */
    static HotValue(prefix, theme, name, format) { ; searches for value inside of the Motion effect. requires an actual image, inside Pr.Focus.HotBar
        CoordMode "Pixel", "Window"
        CoordMode "ToolTip", "Window"
        CoordMode "Mouse", "Window"
        attempts := 3

        MouseGetPos &xStart, &yStart ; Save starting mouse position.
        
        ; Send the hotkey to activate the Transform overlay in the Program Monitor (if defined).
        SendInput KS_Premiere.Player.Transform
        BlockInput "MouseMove" ; Block user mouse movement during search and setup.
        
        ; Find the location of the target property bar (e.g., Position).
        FoobarPos := this.HotBar(prefix, theme, name, format)
        Sleep(5)

        Restart:
        ; Search for the blue color (0x5eaaf7) used to highlight active numerical values in Premiere's UI.
        ; The search area is limited to the property bar found by HotBar.
        FindColor := PixelSearch(&Px, &Py, FoobarPos.x, FoobarPos.y, FoobarPos.x + FoobarPos.w, FoobarPos.y + FoobarPos.h, 0x5eaaf7, 30)
        ;MouseMove Px, Py, 0
        ;sleep(1500)

        if !FindColor{
            attempts--
            if attempts = 0 {
                SendInput KS_Premiere.Player.Transform ; Deactivate the Transform tool.
                BlockInput("MouseMoveOff")
                MsgBox("Failed : FindColor Not Found", Err)
                Exit
            }
            else
                goto Restart
        } else {
            ;tooltip "FindColor Found"
            ; Move the mouse to the center of the found colored pixel (value).
            MouseMove Px+5, Py+5, 0 
            Sleep(5)
            
            ; Simulate a left click down (starting a drag operation for value scrubbing).
            Click "Left", , , , "Down"
            Sleep(12)
            
            BlockInput("MouseMoveOff") ; Allow user mouse movement now that the drag is initiated.
            
            ; Wait for the user to confirm (Enter) or cancel (Escape/Click) the drag-scrubbing.
            WaitForUserConfirm("Enter", "Escape", "LButton", "RButton", "MButton")
            
            ; Toggle the Transform tool off.
            SendInput KS_Premiere.Player.Transform
            Sleep(100)
            
            ; Release the mouse button (if still held down from the Click "Down" command)
            Click "Left", , , , "Up" 
            ; Restore the initial mouse position and return.
            return MouseMove(xStart, yStart)
        }
    }

    /**
     * @static
     * Activates the Transform control overlay in the Program Monitor, confines the mouse to the monitor,
     * and waits for the user to stop the interaction.
     * @returns {void}
     */
    static Transform() {
        CoordMode "Pixel", "Window"
        CoordMode "ToolTip", "Window"
        CoordMode "Mouse", "Window"

        MouseGetPos &xStart, &yStart ; Save initial mouse position.

        ClassPanel := Panel.ClassNN("Player") ; Get coordinates of the Program Monitor panel.
        Sleep(33)

        ; Move the mouse to the center of the Program Monitor.
        MouseMove ClassPanel.x + ClassPanel.w // 2, ClassPanel.y + ClassPanel.h // 2
        ; Activate the Transform overlay (shows handles for Position/Scale/Rotation).
        SendInput KS_Premiere.Player.Transform

        Loop {
            ; Confine the mouse cursor strictly to the Program Monitor area during the transform operation.
            ClipCursor({ x1: ClassPanel.x, y1: ClassPanel.y, x2: ClassPanel.x + ClassPanel.w, y2: ClassPanel.y + ClassPanel.h })
            ToolTip "Appuie sur ESC/ENTER pour stop." ; User instruction (in French, should be translated).
            
            ; Exit the loop if the user presses Escape or Enter.
            if GetKeyState("Esc") OR GetKeyState("Enter")
                break
            sleep(33)
        }
        
        ClipCursor() ; Release the cursor confinement.
        ToolTip ; Hide the instruction tooltip.
        Sleep(5)
        
        MouseMove xStart, yStart ; Restore the mouse position.
        SendInput KS_Premiere.Player.Transform ; Deactivate the Transform overlay.
        Sleep(66)
        return
    }
}

/**
 * @function FindImage
 * Performs an image search within a specified window area using the provided image file.
 * NOTE: This function is expected to be defined globally or within the class scope.
 * @param {string} imageName - The name of the image file (e.g., 'Position.png').
 * @param {number} x - The starting X-coordinate for the search area (Window relative).
 * @param {number} y - The starting Y-coordinate for the search area (Window relative).
 * @param {number} w - The width of the search area.
 * @param {number} h - The height of the search area.
 * @param {number} [shade=100] - The allowed color variation/shading for the search (*N option).
 * @param {string} [picturePath=fpath.ImageSearch] - The path to the image directory.
 * @param {number} [attempts=3] - Number of search attempts (currently unused inside the function).
 * @returns {Object|void} An object containing the image's X/Y coordinates on success, or void on failure.
 */
FindImage(imageName, x, y, w, h, shade := 100, picturePath := A_Path.ImageSearch, attempts := 3){
    ; ImageSearch returns 0 (found), 1 (not found), or 2 (error).
    FindImage := ImageSearch(&ImageX, &ImageY, x, y, x + w, y + h, "*" shade " " picturePath "\" imageName)
    if !FindImage {
        MsgBox("Failed finding picture.", Err)
        Exit
    }
    else {
        ImagePos := {X: ImageX, Y: ImageY}
        return ImagePos
    }
}