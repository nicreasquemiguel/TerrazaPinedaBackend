#!/usr/bin/bash 

sed -i 's/\[]/\["3.82.128.229"]/' /home/ubuntu/terraza/terraza/settings.py

python3 manage.py migrate 
python3 manage.py makemigrations     
python3 manage.py collectstatic
python3 manage.py runserver 0.0.0.0:8000
sudo service gunicorn restart
sudo service nginx restart
#sudo tail -f /var/log/nginx/error.log
#sudo systemctl reload nginx
#sudo tail -f /var/log/nginx/error.log
#sudo nginx -t
#sudo systemctl restart gunicorn
#sudo systemctl status gunicorn
#sudo systemctl status nginx
# Check the status
#systemctl status gunicorn
# Restart:
#systemctl restart gunicorn
#sudo systemctl status nginx
