#!/bin/bash

sudo rm -rf /etc/systemd/system/networkd-resolver/

sudo install -dv /etc/systemd/system/networkd-resolver/{sbin,conf}
sudo install -D -m 0700 -o root sbin/networkd-resolver.py /etc/systemd/system/networkd-resolver/sbin/networkd-resolver
sudo install -D -m 0700 -o root sbin/settings_linux.ini /etc/systemd/system/networkd-resolver/sbin/settings
sudo install -D -m 0700 -o root conf/* /etc/systemd/system/networkd-resolver/conf/

sudo install -D -m 0644 -o root systemd/networkd-resolver.service /etc/systemd/system/

sudo systemctl daemon-reload
sudo systemctl enable networkd-resolver.service
sudo systemctl start networkd-resolver.service
