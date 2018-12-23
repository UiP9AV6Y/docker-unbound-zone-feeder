FROM alpine:latest

RUN set -xe; \
  apk add --no-cache \
    unbound

COPY unbound.conf /etc/unbound/

EXPOSE 53 8953
EXPOSE 53/udp
CMD [ "unbound", "-d" ]
