FROM python:3-alpine

RUN set -xe; \
    addgroup -g 1000 unbound \
    && adduser -u 1000 -G unbound -s /bin/sh -D unbound

WORKDIR /src

COPY requirements.txt ./
RUN set -xe; \
  pip install \
    --no-cache-dir \
    -r requirements.txt

COPY . .

EXPOSE 8080
ENTRYPOINT [ "python", "unbound_zone_feeder" ]
CMD [ "--help" ]

ARG BUILD_DATE="1970-01-01T00:00:00Z"
ARG VCS_URL="http://localhost/"
ARG VCS_REF="master"
ARG VERSION="1.0.0"
LABEL org.label-schema.build-date=$BUILD_DATE \
    org.label-schema.name="Unbound Zone Feeder" \
    org.label-schema.description="Zone data provider for Unbound DNS servers" \
    org.label-schema.url="https://www.github.com/UiP9AV6Y/docker-unbound-zone-feeder" \
    org.label-schema.vcs-url=$VCS_URL \
    org.label-schema.vcs-ref=$VCS_REF \
    org.label-schema.vendor="Gordon Bleux" \
    org.label-schema.version=$VERSION \
    org.label-schema.schema-version="1.0" \
    com.microscaling.docker.dockerfile="/Dockerfile" \
    com.microscaling.license="MIT"
