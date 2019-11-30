#!/bin/bash

set -e

sv stop nebula || true

cat >/etc/nebula.yaml << "EOF"
{% include "nebula/config.yaml" with member=member network=member.network %}
EOF

sv start nebula

echo "Nebula settings updated."

echo "OK"
