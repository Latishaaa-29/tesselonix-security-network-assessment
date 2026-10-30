#!/bin/sh
set -eu
iptables -F INPUT
iptables -P INPUT ACCEPT
if [ "${FW_MODE:-secure}" = secure ]; then
  iptables -A INPUT -i lo -j ACCEPT
  iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
  for source in 172.28.20.11 172.28.20.60; do
    iptables -A INPUT -s "$source" -p tcp --dport 5432 -j ACCEPT
  done
  iptables -A INPUT -s 172.28.20.60 -p udp --dport 5353 -j ACCEPT
  iptables -P INPUT DROP
fi
socat UDP4-RECVFROM:5353,reuseaddr,fork EXEC:/bin/cat &
exec /usr/local/bin/docker-entrypoint.sh "$@"
