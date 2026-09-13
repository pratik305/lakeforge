#!/bin/bash
set -euxo pipefail
dnf install -y docker git
systemctl enable --now docker
curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
git clone https://github.com/pratik305/lakeforge.git /opt/lakeforge
