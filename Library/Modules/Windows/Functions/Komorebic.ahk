#Requires AutoHotkey v2.0

/**
 * @function Komorebic
 * Executes a command using 'komorebic.exe', the command-line client for the Komorebi tiling window manager.
 * The execution is performed hidden and silently on success.
 * @param {String} cmd The command string to be passed as an argument to komorebic.exe (e.g., 'focus-left').
 * @param {ByRef String} [Result] An optional output variable to store a success message.
 * @returns {void}
 */
Komorebic(cmd, &Result?) {
    try {
        ; Attempts to execute the command via komorebic.exe, hiding the command window.
        Run(format("komorebic.exe {}", cmd), , "Hide")
        ; If successful, store a confirmation message in the optional Result variable.
        Result := 'Komorebic => ' cmd
    } catch as e {
        ; If an error occurs (e.g., komorebic.exe not found in PATH), display an error message.
        return MsgBox('Error while trying to open "komorebic.exe".')
    }
}