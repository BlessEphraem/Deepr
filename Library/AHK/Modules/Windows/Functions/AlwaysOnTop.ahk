

AlwaysOnTop(Sound := true)
{
    ; WS_EX_TOPMOST est le style étendu pour AlwaysOnTop.
    ; Sa valeur est 0x8.
    HWND := WinGetID("A")
    ExStyle := WinGetExStyle(HWND)
    IsOnTop := (ExStyle & 0x8)
    
    If IsOnTop
    {
        ; Actuellement AlwaysOnTop, on le désactive (0)
        WinSetAlwaysOnTop 0, HWND
        ; Bip pour indiquer la désactivation
        if Sound
            SoundPlay A_Path.Sounds "\Button3.wav"
    }
    Else
    {
        ; N'est pas AlwaysOnTop, on l'active (1)
        WinSetAlwaysOnTop 1, HWND
        ; Bip pour indiquer l'activation
        if Sound
            SoundPlay A_Path.Sounds "\Button1.wav"
    }
}