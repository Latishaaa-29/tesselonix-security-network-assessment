FROM postgres:16-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends iptables socat iproute2 tcpdump && rm -rf /var/lib/apt/lists/*
COPY lab/db/fw-entrypoint.sh /fw-entrypoint.sh
RUN chmod +x /fw-entrypoint.sh
ENTRYPOINT ["/fw-entrypoint.sh"]
CMD ["postgres"]
