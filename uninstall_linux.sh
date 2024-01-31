#!/bin/bash

sudo systemctl stop networkd-resolver.service
sudo systemctl disable networkd-resolver.service

sudo rm /etc/systemd/system/networkd-resolver

systemctl daemon-reload
systemctl reset-failed
