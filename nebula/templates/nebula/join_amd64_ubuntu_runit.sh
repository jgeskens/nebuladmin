#!/bin/bash

set -e

apt-get update
apt-get install -y runit
apt-get install -y runit-systemd || true
mkdir -p /etc/sv/nebula /etc/service
cd /tmp
sv stop nebula || true
rm nebula-linux-amd64.tar.gz || true
rm nebula || true
rm nebula-cert || true
wget https://github.com/slackhq/nebula/releases/download/v1.0.0/nebula-linux-amd64.tar.gz
tar -zxvf nebula-linux-amd64.tar.gz
mkdir -p /usr/local/bin
cp nebula /usr/local/bin
cat >/etc/nebula.yaml << "EOF"
{% include "nebula/config.yaml" with member=member network=member.network %}
EOF
cat >/etc/sv/nebula/run << "EOF"
#!/bin/bash
exec /usr/local/bin/nebula -config /etc/nebula.yaml
EOF
chmod +x /etc/sv/nebula/run
ln -s /etc/sv/nebula /etc/service/nebula || true
sleep 5
sv start nebula
echo "OK"
