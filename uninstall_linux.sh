#!/bin/bash

sudo systemctl stop networkd-resolver.service
sudo systemctl disable networkd-resolver.service

sudo rm -rf /etc/systemd/system/networkd-resolver

sudo systemctl daemon-reload
sudo systemctl reset-failed
