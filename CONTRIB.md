python -m vnv .venv
. .venv/bin/activate
pip install -r requirements.txt

sudo raspi-config
|_
   Interface Options
   |_
      I2C
      |_Yes
   |_
      1-Wire
      |_Yes
sudo reboot now

sudo ln -s /home/pi/Projects/moonshine-5/services/moonshine.service /etc/systemd/system/moonshine.service
sudo systemctl enable moonshine.service
sudo systemctl start moonshine.service
sudo systemctl status moonshine.service