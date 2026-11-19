Option Explicit
Dim shell, fso, folder, command
Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
folder = fso.GetParentFolderName(WScript.ScriptFullName)
' Script lives in scripts\startup — repo root is two levels up.
repoRoot = fso.GetParentFolderName(fso.GetParentFolderName(folder))
command = "cmd.exe /c """ & folder & "\START_TALENTBRIDGEAI.bat"""
shell.CurrentDirectory = repoRoot
shell.Run command, 0, False
