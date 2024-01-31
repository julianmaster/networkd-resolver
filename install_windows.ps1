if (!([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator))
{
    Start-Process PowerShell -Verb RunAs "-NoProfile -ExecutionPolicy Bypass -Command `"cd '$pwd'; & '$PSCommandPath';`"";
    exit;
}

if (-not(Test-Path "./dist/webhost.exe" -PathType leaf))
{
    Write-Host "Ce fichier d'installation ne fonctionne que si le l'exécutable à préalablement été créer. Voir les sections 'Installation du projet' et 'Création de l'exécutable Windows'"
    Write-Host "Press any key to continue..."
    $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    Exit
}

Copy-Item "./dist/webhost.exe" -Destination "C:\Windows\System32"
Set-Location "C:\Windows\System32"
./webhost.exe --startup=auto install


$start = Read-Host -Prompt "Voulez-vous démarrer le programme maintenant ? (oui|o ou non|n)"
switch -Regex ($start)
{
    "oui|o" {./webhost.exe start}
}

Write-Host "Installation terminé !"
Write-Host -NoNewLine "Appuyez sur n'importe quelle touche pour continuer...";
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown");