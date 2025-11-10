#Requires AutoHotkey v2.0

/**
 * @function ClipClear
 * Clears the attributes of the selected clip(s) assuming a predefined sequence of shortcuts.
 * NOTE: This function relies on external definitions: Panel.Focus and KS_Premiere.Attributes.Sub.
 * @returns {void}
 */
ClipClear() {
    ; Ensure the Timeline panel is focused before sending clip-related commands.
    ; NOTE: Panel.Focus is expected to be an external function/method.
    Panel.Focus("Timeline")
    sleep 33 ; Short delay to ensure focus change is complete.
    
    ; Send the hotkey/command sequence to open the 'Remove Attributes' or equivalent dialog.
    ; KS_Premiere.Attributes.Sub is expected to contain the required shortcut (e.g., Alt+Shift+/)
    Send(KS_Premiere.Attributes.Sub)
    
    ; Send {Enter} to confirm the default action in the dialog (typically "OK" or "Apply"), 
    ; effectively clearing the default set of attributes.
    Send("{Enter}")
    return
}