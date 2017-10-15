#!/bin/bash

apt-get remove --purge hostapd -yqq
apt-get update -yqq
apt-get upgrade -yqq

sudo apt-get install -y hostapd dnsmasq nginx
sudo pip install gunicorn

sudo cp system/nginx--print-a-bot /etc/nginx/sites-available/print-a-bot
sudo rm -f /etc/nginx/sites-enabled/default
sudo ln -s /etc/nginx/sites-available/print-a-bot /etc/nginx/sites-enabled/

sudo cp system/gunicorn_bot.service /etc/systemd/system/gunicorn_bot.service
sudo systemctl daemon-reload
sudo systemctl start gunicorn_bot

sudo service nginx restart


sudo pip install -r Print_A_Bot/requirements-pi.txt

