#!/bin/bash

set -e

systemctl stop nebula || true

cat >/etc/nebula.yaml << "EOF"
{% include "nebula/config.yaml" with member=member network=member.network %}
EOF

systemctl start nebula

echo "Nebula settings updated."

echo "OK"
