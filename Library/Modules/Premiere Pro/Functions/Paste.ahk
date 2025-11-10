#Requires AutoHotkey v2.0

; I'm very proud of this one.
; I noticed, using clipboard analysis tools, that when decrypting information
; copied in Premiere Pro that are only usable within it (If you try to copy/paste keyframes 
; into some text app, it will paste nothing), we could distinguish one copied element from another.

; More precisely, we can decrypt and deduce if the copied element is:
;   A timeline item (clip)
;   A "Bin" panel item (project item)
;   One or more keyframes

; The final goal of this function is to be able to copy/paste keyframes without needing
; to be focused on the effects panel. We will force the focus and paste the keyframes.

; USE CASE :
; You have a Transform effect, premade with custom velocity on keyframes, and you want to copy paste it.
; Select and copy your keyframe, use "LButton" (which is for me another ahk script that move my playhead on the mouse)
; and now, you can "^v" as you move on the timeline with your mouse to set up your keyframe
; without needing another input from you to put focus on "Effect Controls", which is needed to copy/paste keyframes.

/**
 * @function Paste
 * Smart Paste function for Adobe Premiere Pro. It detects the type of content
 * currently in the clipboard (Keyframes, Clip, or Project Item) based on the presence 
 * of custom clipboard formats. It forces focus to the 'Effect Controls' panel 
 * ONLY if keyframes are detected, allowing the user to paste keyframes without
 * manually focusing the panel.
 * NOTE: Relies on the external method Panel.Focus().
 * @returns {void}
 * @platform Adobe Premiere Pro
 */
Paste() {
    ; Custom clipboard format strings used by Premiere Pro to identify non-standard copied content.
    TrackItem := "PProAE/Exchange/TrackItem" ; Clipboard format for a selected clip on the timeline.
    ProjectItem := "PProAE/Exchange/ProjectItem" ; Clipboard format for an item in the Project/Bin panel.
    
    ; 1. Register the IDs of the formats to check
    ; DllCall("RegisterClipboardFormat") returns the ID associated with the format name.
    TrackItemID := DllCall("RegisterClipboardFormat", "Str", TrackItem)
    ProjectItemID := DllCall("RegisterClipboardFormat", "Str", ProjectItem)
    
    ; 2. Check for the presence of the formats
    ; IsClipboardFormatAvailable() returns 1 (True) if the format is present, 0 (False) otherwise.
    
    IsTrackItem := DllCall("IsClipboardFormatAvailable", "UInt", TrackItemID)
    IsProjectItem := DllCall("IsClipboardFormatAvailable", "UInt", ProjectItemID)
    
    ; Check the unique signature for keyframes: Absence of both TrackItem and ProjectItem.
    If (!IsTrackItem && !IsProjectItem)
    {
        ; Keyframes detected: The system clipboard contains a Premiere-specific keyframe format 
        ; that is NOT flagged by the clip or project item formats.
        
        Tooltip "Keyframe Detected"
        ; Force focus to the Effect Controls panel, as keyframe pasting requires it.
        Panel.Focus("EffectControls")
        sleep(5)

        ; Send the paste command (Ctrl+V). Use SendEvent for better timing control.
        SendEvent("{Ctrl Down}v{Ctrl Up}")
        return
    }
    Else
    {
        ; If either format is present, the content is a standard clip or project item. Paste normally.
        SendEvent("{Ctrl Down}v{Ctrl Up}")
        return
    }
}