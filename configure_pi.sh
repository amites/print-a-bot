#!/bin/bash

# setup packages
apt-get remove --purge hostapd -yqq
apt-get update -yqq
apt-get upgrade -yqq

sudo apt-get install -y hostapd dnsmasq nginx
sudo pip install gunicorn

sudo pip install -r Print_A_Bot/requirements-pi.txt

# setup web server nginx
sudo cp system/nginx--print-a-bot /etc/nginx/sites-available/print-a-bot
sudo rm -f /etc/nginx/sites-enabled/default
sudo ln -s /etc/nginx/sites-available/print-a-bot /etc/nginx/sites-enabled/

# setup python wsgi server gunicorn
sudo cp system/gunicorn_bot.service /etc/systemd/system/gunicorn_bot.service
sudo systemctl daemon-reload
sudo systemctl start gunicorn_bot

sudo service nginx restart

# setup running check network script at boot
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "@reboot root python $DIR/system/check_network.py" > /etc/cron.d/ap_check
cat > /etc/network/if-down.d/ap_check.sh << EOF
#!/bin/bash
python "$SYSTEM_DIR/check_network.py"
EOF
