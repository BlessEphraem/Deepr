#Requires AutoHotkey v2.0

MyInputBox() {
	IB := InputBox("Please enter a value."), UserInput := IB.Value, ErrorLevel := IB.Result="OK" ? 0 : IB.Result="CANCEL" ? 1 : IB.Result="Timeout" ? 2 : "ERROR"
	if ErrorLevel {
		MsgBox("CANCEL was pressed.")
		Exit()
	}
	else {
		return UserInput
	}
}