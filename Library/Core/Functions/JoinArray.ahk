#Requires AutoHotkey v2.0

/**
 * @param arr An Array object (or any enumerable collection) whose elements will be joined.
 * @param sep The string to insert between elements. Defaults to " / ".
 * @returns A string containing all elements of 'arr' joined by 'sep'.
 * * Joins all elements of an array (or object implementing __Enum) into a single string,
 * separated by the specified delimiter.
 */
JoinArray(arr, sep := " / ") {
    ; Initializes the output string to be built.
    out := ""
    
    ; Iterates over the array elements. 'i' is the 1-based index (key), 'val' is the value.
    for i, val in arr {
        ; Appends the separator *before* the current value, but only if it's not the first element (i > 1).
        ; This is a common pattern to avoid a trailing separator.
        out .= (i > 1 ? sep : "") val
    }
    ; Returns the final joined string.
    return out
}