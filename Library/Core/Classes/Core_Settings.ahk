#Requires AutoHotkey v2.0

#SingleInstance force
Persistent
InstallKeybdHook
InstallMouseHook
#UseHook
SendMode "Input"
/*
    Very important too, we need a better control of our computer and input, "InstallKeybdHook" il really needed
    for the alt-menu accelleration, and SendMode "Input" is just better. No need an explanation here, just
    use SendMode "Input" in your script, you will have a better control.
*/

#WinActivateForce ; For Faster response. Used for "\lib\Modules\Windows\Class\ApplicationClass.ahk" and "\Functions\WindowMover.ahk"

;false is the default settings, but I put it because it's very important.
;If you put it on, the class "Application" will no longer work. It can Run/Focus/Minimize an app.
DetectHiddenWindows false

SetWinDelay 2
SetKeyDelay 0, 2
SetMouseDelay 0
SetControlDelay 0
A_HotkeyInterval := 0