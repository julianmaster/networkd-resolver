if (!([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator))
{
    Start-Process PowerShell -Verb RunAs "-NoProfile -ExecutionPolicy Bypass -Command `"cd '$pwd'; & '$PSCommandPath';`"";
    exit;
}

Set-Location "C:\Windows\System32"
./webhost.exe stop
./webhost.exe remove
Remove-Item -Path "webhost.exe" -Force

Write-Host "Désinstallation terminé !"
Write-Host -NoNewLine "Appuyez sur n'importe quelle touche pour continuer...";
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown");