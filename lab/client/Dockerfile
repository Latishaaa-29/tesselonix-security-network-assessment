FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends nmap tcpdump postgresql-client netcat-openbsd socat iproute2 curl iptables ca-certificates && rm -rf /var/lib/apt/lists/*
CMD ["sleep", "infinity"]
