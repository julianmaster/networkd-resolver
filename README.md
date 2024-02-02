# Networkd-Resolver

> Service bloqueur de site web pour machine Windows et Linux

## Table des matières

- [Windows](#windows)
  - [Installation du projet](#installation-du-projet)
  - [Création de l'éxécutable](#création-de-lexécutable)
  - [Installation](#installation)
  - [Fonctionnement](#fonctionnement)
  - [Logs](#logs)
  - [Désinstallation](#désinstallation)
- [Linux](#linux)
  - [Prérequis](#prérequis)
  - [Installation](#installation)
  - [Fonctionnement](#fonctionnement-1)
  - [Logs](#logs)
  - [Désinstallation](#désinstallation-1)
- [Icone du programme](#icone-du-programme)
- [Mainteneurs](#mainteneurs)

## Windows

### Installation du projet

Ce projet utilise [python3](https://www.python.org/) et [pip](https://pypi.org/). Allez les voir si vous ne les avez pas déjà installés localement.

```shell
pip install pywin32
pip install pyinstaller==5.13.2
```

### Création de l'exécutable

```shell
pywin32_postinstall.py -install
pyinstaller --clean .\build_windows.spec
```

Le fichier exécutable final `webhost.exe` se trouve dans le dossier `dist` du projet.

### Installation

Après avoir réalisé les étapes [Installation du projet](#installation-du-projet) et [Création de l'exécutable Windows](#création-de-lexécutable-windows), lancez le script `install_windows.ps1` avec un clique droit et `Exécuter avec PowerShell`.
Si la fenêtre vous demande de modifier la stratégie d'exécution, ecrivez `O` (`o` majuscule) puis appuyez sur la touche `Entrée`.
Lorsque le programme vous demande d'autoriser cette application à modifier votre appareil, cliquez sur `Oui`.  
L'installation terminée, le programme vous demande si vous souhaitez démarrer le service maintenant.

### Fonctionnement

Ouvrez la fenêtre `Exécuter` avec le raccourci `Windows+R`. Ecrivez `services.msc` et cliquez sur le bouton `OK`.
Le service se nomme `Windows Routing Service`. Vous pouvez le démarrer/arrêter avec un clique droit sur le nom du service.

### Logs

Les logs du service sont disponible dans le fichier `C:/Windows/System32/config/systemprofile/AppData/Local/webhostsvc/process.log`

### Désinstallation

Lancez le script `uninstall_windows.ps1` avec un clique droit et `Exécuter avec PowerShell`.
Si la fenêtre vous demande de modifier la stratégie d'exécution, ecrivez `O` (`o` majuscule) puis appuyez sur la touche `Entrée`.
Lorsque le programme vous demande d'autoriser cette application à modifier votre appareil, cliquez sur `Oui`.


## Linux

### Prérequis

Ce programme nécessite que [python3](https://www.python.org/) soit intallé.

### Installation

```shell
chmod +x install_linux.sh
./install_linux.sh
history -cw # Effacer l'historique des commandes
```

Le service `networkd-resolver` est automatiquement démarré !

### Fonctionnement

Pour démarrer le service :

```shell
sudo service networkd-resolver start
```

Pour arrêter le service :

```shell
sudo service networkd-resolver stop
```

### Logs

Les logs du service sont disponible dans le fichier `/var/log/networkd-resolver/process.log`

### Désinstallation

```shell
chmod +x uninstall_linux.sh
./uninstall_linux.sh
history -cw # Effacer l'historique des commandes
```

## Icone du programme

Extrait (avec 7-Zip) depuis le dossier `ICON` du fichier `C:/Windows/SystemResources/imageres.dll.mun`. Transformation en un fichier `program.ico` multi-image au moyen du script `icon/convert_and_build.ps1`.

## Mainteneurs

[@JulienMaitre](https://gitlab.univ-lr.fr/jmaitr03).