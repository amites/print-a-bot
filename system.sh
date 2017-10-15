#!/bin/bash

sudo cp system/nginx--print-a-bot /etc/nginx/sites-available/print-a-bot
sudo rm -f /etc/nginx/sites-enabled/default
sudo ln -s /etc/nginx/sites-available/print-a-bot /etc/nginx/sites-enabled/

sudo cp system/gunicorn_bot.service /etc/systemd/system/gunicorn_bot.service
sudo systemctl daemon-reload
sudo systemctl start gunicorn_bot

sudo service nginx restart

