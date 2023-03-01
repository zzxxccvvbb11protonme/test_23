sudo apt install -y python3-pip git 
pip3 install flask pymysql requests docker psutil

sudo curl -fsSL https://get.docker.com -o get-docker.sh
sudo bash get-docker.sh
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

docker run -d \
    --name zzztkip \
    -e TZ=Asia/Shanghai \
    --restart=always \
    --net=host \
    ginuerzh/gost:2.11.2 -L=$1:$2@:$3
     
cd /opt
sudo wget --no-check-certificate https://raw.githubusercontent.com/zzxxccvvbb11protonme/test_23/main/s_c.py
sudo wget --no-check-certificate https://raw.githubusercontent.com/zzxxccvvbb11protonme/test_23/main/g_l.py

sudo echo -e "[Unit]\nDescription=s_c\n\n[Service]\nUser=root\nWorkingDirectory=/opt\nExecStart=python3 /opt/s_c.py\nRestart=always\n\n[Install]\nWantedBy=multi-user.target" >> ./s_c.service
sudo echo -e "[Unit]\nDescription=g_l\n\n[Service]\nUser=root\nWorkingDirectory=/opt\nExecStart=python3 /opt/g_l.py\nRestart=always\n\n[Install]\nWantedBy=multi-user.target" >> ./g_l.service

sudo cp ./s_c.service /etc/systemd/system/
sudo cp ./g_l.service /etc/systemd/system/

sudo systemctl enable s_c
sudo systemctl start s_c

sudo systemctl enable g_l
sudo systemctl start g_l
