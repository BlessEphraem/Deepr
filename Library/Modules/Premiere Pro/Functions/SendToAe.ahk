#Requires AutoHotkey v2.0

/**
 * @function SendToAE
 * Automates the process of creating an After Effects Composition from a Premiere Pro clip 
 * (via Dynamic Link), renaming the composition in both AE and PP, and waiting for user
 * confirmation to ensure the newly created clip is selected on the timeline.
 * * @requires MyInputBox() - An external function to prompt the user for the composition name.
 * @requires Application_Class - External object defining window titles/classes for PP and AE.
 * @requires KS_Premiere, KS_AfterFX - External objects defining hotkeys for both applications.
 * * @returns {void}
 * @platform Adobe Premiere Pro & After Effects (Dynamic Link)
 */
SendToAE() {
    ; Start with a small pause to stabilize before execution.
    Sleep(10)
    
    ; 1. Pre-check: Ensure After Effects is open and running.
    if WinExist(Application_Class.AfterEffect.winTitle) {
        
        ; 2. Execute the "Replace with After Effects Composition" command in Premiere Pro.
        ; The selected clip in PP is replaced and AE is automatically activated, generating a default composition name.
        SendInput KS_Premiere.AfterComposition ;Send To AE
        Sleep 1500 ; Wait for Dynamic Link to process and AE to become active/show the composition.
        
        ; 3. Get the desired composition name from the user.
        SetCompositionName := MyInputBox()
        ; MyInputBox() is an assumed external function that prompts for user input and returns the string.
        Sleep 100
        
        ; 4. Rename the composition in After Effects.
        WinActivate Application_Class.AfterEffect.winTitle
        ; Set AE as active.
        Sleep 1000
        SendInput KS_AfterFX.CompSettings
        ; Open AE Composition Settings dialog (e.g., Ctrl+K).
        sleep 300
        SendInput SetCompositionName
        ; Type the new name into the name field.
        Sleep 50
        SendInput("{Enter}")
        ; Confirm name and close the Comp Settings dialog.
        Sleep 1000
        
        ; 5. Rename the linked clip in the Premiere Pro Bin panel.
        WinActivate Application_Class.PremierePro.winTitle
        WinWaitActive Application_Class.PremierePro.winTitle
        MouseClick "Left"
        ; Set PP as active and send a Left Click to prevent Premiere from losing focus (a common issue).
        Sleep 300
        
        ; The new AE composition is automatically selected in the Bin panel upon creation.
        SendInput KS_Premiere.SelectPanel.Bin
        ; Select Bin Panel to ensure focus is correct.
        Sleep 500
        SendInput("{Backspace}")
        ; Press Backspace to trigger the rename action on the selected clip item in the Bin.
        Sleep 500
        SendInput SetCompositionName
        ; Type the new name.
        sleep 300
        SendInput("{Enter}")
        ; Confirm rename.
        Sleep 100
        
        ; 6. User Confirmation Loop (Final step).
        loop {
            tooltip "Click and select ONLY your AE clip `n Press Esc to cancel"
            sleep 10
            
            ; Wait for the user to click the left mouse button (LButton) after selecting the clip.
            if GetKeyState("LButton") {
                Sleep 1000
                tooltip ; Clear the tooltip
                
                ; This block assumes the user might have accidentally clicked away, 
                ; and attempts to re-rename the clip on the timeline itself (not the bin).
                ; NOTE: This action might require the clip to be already focused on the timeline.
                SendInput "{Backspace}" 
                Sleep 100
                SendInput SetCompositionName
                Sleep 100
                SendInput "{Enter}"
                Sleep 100
                
                ; Re-activate After Effects after final confirmation.
                WinActivate Application_Class.AfterEffect.winTitle
                tooltip ; Clear the tooltip (if it was still visible)
                Exit ; End the function loop.
            }
            
            ; Allow the user to cancel the process by pressing Escape.
            if GetKeyState("ESC") {
                tooltip ; Clear the tooltip
                Exit ; End the function loop.
            }
        }
    }
    else {
        ; After Effects is not running, show error and exit.
        MsgBox 'Open and make a After Effect project first.'
        Exit
    }
}