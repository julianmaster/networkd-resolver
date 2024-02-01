# Networkd-Resolver

> Service bloqueur de site web pour machine Windows et Linux

## Installation du projet

Ce projet utilise [python3](https://www.python.org/) et [pip](https://pypi.org/). Allez les voir si vous ne les avez pas déjà installés localement.

```shell
pip install pywin32
pip install pyinstaller==5.13.2
```

### Création de l'exécutable Windows

```shell
pywin32_postinstall.py -install
pyinstaller --clean .\build_windows.spec
```

Le fichier exécutable final `webhost.exe` se trouve dans le dossier `dist` du projet.

### Installation sous Windows

Après avoir réalisé les étapes [Installation du projet](#installation-du-projet) et [Création de l'exécutable Windows](#création-de-lexécutable-windows), lancez le script `install_windows.ps1` avec un clique droit et `Exécuter avec PowerShell`.

### Installation sous Linux

Depuis un terminal :

```shell
chmod +x install_linux.sh
./install_linux.sh
history -cw # Effacer l'historique des commandes
```
### Désinstallation sous Windows

Lancez le script `uninstall_windows.ps1` avec un clique droit et `Exécuter avec PowerShell`.

### Désinstallation sous Linux

Depuis un terminal :

```shell
chmod +x uninstall_linux.sh
./uninstall_linux.sh
history -cw # Effacer l'historique des commandes
```

### Icone du programme

Extrait (avec 7-Zip) du dossier `ICON` dans le fichier `C:\Windows\SystemResources\imageres.dll.mun`. Transformation en un fichier `program.ico` multi-image au moyen du script `convert_and_build.ps1`.