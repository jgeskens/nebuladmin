#!/bin/bash

set -e

yum install -y wget
cd /tmp
rm nebula-linux-amd64.tar.gz || true
rm nebula || true
rm nebula-cert || true
wget https://github.com/slackhq/nebula/releases/download/v1.0.0/nebula-linux-amd64.tar.gz
tar -zxvf nebula-linux-amd64.tar.gz
systemctl stop nebula || true
mkdir -p /usr/local/bin
cp nebula /usr/local/bin
cat >/etc/nebula.yaml << "EOF"
{% include "nebula/config.yaml" with member=member network=member.network %}
EOF
cat >/etc/systemd/system/nebula.service << "EOF"
[Unit]
Description=Nebula
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root
ExecStart=/usr/local/bin/nebula -config /etc/nebula.yaml
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

systemctl enable nebula
systemctl start nebula

echo "OK"

