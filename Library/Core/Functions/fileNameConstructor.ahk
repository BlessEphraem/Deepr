#Requires AutoHotkey v2.0

FileNameConstructor(Params*) {
    fileName := ""
    for each, part in Params
        fileName .= part
    return fileName
}
