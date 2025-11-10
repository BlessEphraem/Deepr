#Requires AutoHotkey v2.0
;by Moo-GH : https://github.com/moo-gh/windows-auto-language-switcher/blob/main/keyboard_language_switcher.ahk
;I only need the Keyboard Detection and Set Language part, it's insanely good.

/**
 * @class Language
 * Manages the setting, getting, and switching of the active keyboard input language.
 */
class Language {
    /**
     * @static
     * Sets the keyboard input language for the active window.
     * Note: This method currently uses a generic PostMessage that might not reliably set a specific language
     * based on the LanguageCode parameter for all contexts in AHK v2.0.
     * The original implementation likely had a different intent or context for the PostMessage.
     * @param {String} LanguageCode The hexadecimal string representation of the language ID (e.g., '409' for English).
     * @returns {void}
     */
    static Set(LanguageCode) {
        ; Adjusting the code to switch input languages
        ; NOTE: This specific PostMessage (0x50, 0, 0) is WM_INPUTLANGCHANGEREQUEST, which usually
        ; triggers a change to the *next* installed language, not necessarily the one specified by LanguageCode.
        ; The 'LanguageCode' parameter is currently unused in this implementation.
        PostMessage(0x50, 0, 0, , "A")  ; Send WM_INPUTLANGCHANGEREQUEST message to the active window (WinTitle "A")
    }

    /**
     * @static
     * Cycles through a list of languages, switching the active input language to the next one in the list.
     * @param {...String} Params A variadic array of hexadecimal language code strings to cycle through (e.g., '409', '40c').
     * @returns {void}
     */
    static Switch(Params*) {
        ; Retrieves the ID of the current active language layout.
        currentLang := this.Get.ID()
        if !currentLang
            return 0 ; Unable to retrieve the language ID, aborting switch.

        ; Creates an array from the language codes provided as parameters.
        langs := []
        for index, lang in Params
            langs.Push(lang)

        ; Finds the index of the current language in the array to determine the next one.
        nextIndex := 1  ; Default index (the first language) if the current language is not in the list.
        for index, lang in langs {
            if (lang = currentLang) {
                ; Move to the next language in the list, or wrap around to the beginning (index 1).
                nextIndex := (index < langs.MaxIndex()) ? index + 1 : 1
                break
            }
        }

        ; Changes the language to the next one in the determined sequence.
        this.Set(langs[nextIndex]) ; Calls the Set method to perform the actual switch.
        return
    }
    

    /**
     * @class Get
     * Provides static methods to retrieve information about the current keyboard layout/language.
     */
    class Get {
        /**
         * @static
         * Retrieves the hexadecimal ID of the active keyboard layout (HKL) for a given window.
         * The ID is masked to isolate the Language Identifier (LOWORD) part.
         * @param {AHK_Window} [hWnd=''] The window handle (Ptr) to check. Defaults to the active window.
         * @returns {String} The hexadecimal language ID string (e.g., '409'), or an empty string on failure.
         */
        static ID(hWnd := '') {
            (!hWnd) && hWnd := WinActive('A') ; Use the active window if no handle is provided.
            ; Get the thread ID of the window handle.
            threadId := DllCall('GetWindowThreadProcessId', 'Ptr', hWnd, 'UInt', 0)
            if (threadId = 0) {
                MsgBox("Failed to retrieve thread ID.")
                return ""
            }
            ; Get the keyboard layout handle (HKL) associated with the thread.
            lyt := DllCall('GetKeyboardLayout', 'Ptr', threadId, 'UInt')
            if (lyt = 0) {
                MsgBox("Failed to retrieve keyboard layout.")
                return ""
            }
            ; Mask the HKL (lyt) to extract the Language Identifier (LANGID), which is the low 16 bits,
            ; then format it as a hexadecimal string. (0x3FFF is used to mask the relevant bits).
            Return Format('{:#x}', lyt & 0x3FFF)
        }

        /**
         * @static
         * Retrieves the English name of the language associated with a given Language ID.
         * @param {UInt} langId The numerical Language Identifier (LANGID).
         * @returns {String} The English name of the language (e.g., 'English'), or an empty string if the call fails.
         */
        static Name(langId)  {
            LOCALE_SENGLANGUAGE := 0x1001 ; Constant for the language name in English.
            ; Get the required buffer size for the language name string.
            charCount := DllCall('GetLocaleInfo', 'UInt', langId, 'UInt', LOCALE_SENGLANGUAGE, 'UInt', 0, 'UInt', 0)
            ; Create a buffer with the necessary size (charCount * 2 bytes for WCHAR).
            localeSig := Buffer(size := charCount << 1)
            ; Get the actual language name string into the buffer.
            DllCall('GetLocaleInfo', 'UInt', langId, 'UInt', LOCALE_SENGLANGUAGE, 'Ptr', localeSig, 'UInt', size)
            ; Convert the buffer content (UTF-16 string) to an AHK string and return it.
            Return StrGet(localeSig)
        }


    }
}