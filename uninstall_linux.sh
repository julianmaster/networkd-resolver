#!/bin/bash

sudo systemctl stop networkd-resolver.service
sudo systemctl disable networkd-resolver.service

sudo rm -rf /etc/systemd/system/networkd-resolver
sudo rm /etc/systemd/system/networkd-resolver.service
sudo rm -rf /var/log/networkd-resolver

sudo systemctl daemon-reload
sudo systemctl reset-failed

read -p "Voulez-vous effacer tout l'historique des commandes ? (oui|o ou non|n) " clr
if [[ $clr == "oui" || $clr == "o" ]]
then
  history -cw
fi

echo "Désinstallation terminé !"