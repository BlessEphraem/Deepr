#Requires AutoHotkey v2.0

/**
 * @function ClipGain
 * Sets the audio gain value for the currently selected clip(s) in Adobe Premiere Pro.
 * It sends the shortcut to open the Audio Gain dialog, inputs the desired value, and confirms.
 * NOTE: This function relies on an external definition: KS_Premiere.AudioGain.
 * @param {string|number} value The desired audio gain value (e.g., '3' for +3dB, '-6' for -6dB).
 * @returns {void}
 * @platform Adobe Premiere Pro
 */
ClipGain(value) {
    ; Send the hotkey/command to open the 'Audio Gain' dialog box in Premiere Pro.
    ; KS_Premiere.AudioGain is expected to be defined elsewhere (e.g., 'g').
    SendInput KS_Premiere.AudioGain
    sleep 1 ; Minimal delay after opening the dialog.
    
    ; Input the numerical value directly into the focused field (expected to be the gain adjustment).
    Send value
    sleep 1 ; Minimal delay after inputting the value.
    
    ; Send {Enter} to confirm the operation, applying the gain change to the selected clip(s).
    SendInput "{Enter}"
    return
}