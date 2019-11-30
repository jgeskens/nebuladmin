#!/bin/bash

set -e

systemctl stop nebula || true
systemctl disable nebula

echo "Nebula disabled."

echo "OK"
