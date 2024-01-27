# Networkd-Resolver

> Service bloqueur de site web pour machine Windows et Linux

## Installation

Ce projet utilise [python3](https://www.python.org/) et [pip](https://pypi.org/). Allez les voir si vous ne les avez pas
déjà installés localement.

```shell
pip install pywin32
pip install pyinstaller
```

### Création de l'installeur Windows

```shell
pywin32_postinstall.py -install
pyinstaller --clean .\install_windows.spec
```

### Icone du programme

Extrait (avec 7-Zip) du dossier `ICON` dans le fichier `C:\Windows\SystemResources\imageres.dll.mun`. Transformation en un fichier `program.ico` multi-image au moyen du script `convert_and_build.ps1`.