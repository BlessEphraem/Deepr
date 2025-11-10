#Requires AutoHotkey v2.0

/**
 * @function TrueFullscreen
 * Toggles the "True Fullscreen" view in Premiere Pro for the currently focused panel.
 * This is typically the unmodifiable Adobe shortcut (Ctrl + Backslash on US keyboards).
 * It automatically switches the keyboard layout to English (en) before sending the hotkey,
 * and restores the original layout afterward, ensuring the hotkey executes correctly
 * regardless of the user's current keyboard language (e.g., French Azerty).
 * * @param {string} VKSC_Code - The Virtual Key/Scan Code string representing the backslash/asterisk key 
 * on a US keyboard (e.g., "SC02B" for the key that sends Backslash/Asterisk).
 * @returns {void}
 * @requires Panel.Focus() - To ensure the target panel (e.g., Effect Controls/Player) is active.
 * @requires Language.Set(), Language.Get.ID(), Language.Get.Name() - External functions for keyboard language management.
 * @platform Adobe Premiere Pro
 */
TrueFullscreen(VKSC_Code) {
    ; 0. Ensure a panel is focused, often Effect Controls (Program Monitor).
    Panel.Focus("EffectControls")
    sleep 33
    
    ; 1. Save the current keyboard language ID and Name.
    prevLangRaw := Language.Get.ID()
    prevLangName := Language.Get.Name(prevLangRaw)
    
    ; 2. Switch the keyboard layout to English (US) to guarantee the hotkey is recognized by Premiere.
    Language.Set("en")
    sleep 5
    newLangRaw := Language.Get.ID()
    newLangName := Language.Get.Name(newLangRaw)
    tooltip "Keyboard Switched to: " newLangName
    sleep 5
    
    ; 3. Execute the True Fullscreen hotkey: {LCtrl} + {*}
    ; The code "<^{" VKSC_Code "}" sends LCtrl + the specified key code,
    ; which Premiere Pro expects from an English layout (e.g., Backslash / Asterisk key).
    Send "<^{" VKSC_Code "}"
    sleep 650
    ; Send it again to exit fullscreen immediately if needed, or just to ensure the first command registered.
    Send "<^{" VKSC_Code "}"
    sleep 5
    ; Note: The sleep time (650ms) is crucial to allow the screen to switch.


    
    ; 4. Restore the previous keyboard language layout.
    Language.Set(prevLangRaw)
    
    ; 5. Debug tooltip for restored language confirmation.
    tooltip "Keyboard restored to: " prevLangName
}