#!/bin/bash
sudo apt install build-essential -y
sudo apt install erlang -y
sudo apt install sqlite3 -y
sudo apt install python3-pip -y
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y
wget https://github.com/rabbitmq/rabbitmq-server/releases/download/v3.10.8/rabbitmq-server_3.10.8-1_all.deb
sudo dpkg -i rabbitmq-server_3.10.8-1_all.deb