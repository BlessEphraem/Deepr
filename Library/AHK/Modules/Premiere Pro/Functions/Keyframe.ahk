/**
 * @fileoverview AutoHotkey v2.0 Class for managing Keyframe operations in Premiere Pro.
 * * This class provides methods to select and perform actions related to keyframes
 * within the Adobe Premiere Pro application, specifically targeting the
 * "EffectControls" panel.
 */
class Keyframe {

    static _switch(action, choice, subchoice := '') {
        Switch action {
            Case 'Add': Switch choice
                {
                    Case 'Video': return SelChoice := KS_Premiere.Keyframe.Perform.Video.Add
                    Case 'Audio': return SelChoice := KS_Premiere.Keyframe.Perform.Audio.Add
                }

            Case 'Remove': Switch choice
                {
                    Case 'Video': return SelChoice := KS_Premiere.Keyframe.Perform.Video.Del
                    Case 'Audio': return SelChoice := KS_Premiere.Keyframe.Perform.Audio.Del
                }

            Case 'Select': Switch choice
                {
                    Case 'Next': return SelChoice := KS_Premiere.Keyframe.SelNext
                    Case 'Prev': return SelChoice := KS_Premiere.Keyframe.SelPrev
                }

            Case 'Move': Switch choice
                {
                    Case 'Video': Switch subchoice
                        {
                            Case '+1f': return SelChoice := KS_Premiere.Keyframe.Move.Video.Forw.1
                            Case '+10f': return SelChoice := KS_Premiere.Keyframe.Move.Video.Forw.10
                            Case '-1f': return SelChoice := KS_Premiere.Keyframe.Move.Video.Back.1
                            Case '-10f': return SelChoice := KS_Premiere.Keyframe.Move.Video.Back.10
                        }

                    Case 'Audio': Switch subchoice
                        {
                            Case '+1f': return SelChoice := KS_Premiere.Keyframe.Move.Audio.Forw.1
                            Case '+10f': return SelChoice := KS_Premiere.Keyframe.Move.Audio.Forw.10
                            Case '-1f': return SelChoice := KS_Premiere.Keyframe.Move.Audio.Back.1
                            Case '-10f': return SelChoice := KS_Premiere.Keyframe.Move.Audio.Back.10
                        }
                }
            Case 'Default':
                return msgbox("Error: 2 Params needed")
        }
    }

    /**
     * @static
     * @method Keyframe - Executes the chosen keyframe action in Premiere Pro.
     * * 1. **Focuses Panel:** Ensures the "EffectControls" panel in Premiere Pro has focus 
     * using a hypothetical `Panel.Focus()` function.
     * 2. **Selects Hotkey:** Calls the private `_switch` method to retrieve the correct hotkey sequence.
     * 3. **Sends Input:** Sends the selected hotkey sequence using `SendInput`.
     * * @param {string} choice - The action string (e.g., 'Next', 'Prev', 'Add', 'Del').
     */
    static Perform(action, choice, subchoice := '') {
        ; Sets focus to the "EffectControls" panel in Premiere Pro.
        Panel.Focus("EffectControls")
        ; Gets the corresponding AHK key sequence for the requested action.
        sleep 150
        SelChoice := this._switch(action, choice, subchoice := '')
        return SelChoice
    }
}