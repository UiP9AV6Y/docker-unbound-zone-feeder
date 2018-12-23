
[microbadger]: https://microbadger.com/images/uip9av6y/unbound-control-feeder
[docker library]: https://store.docker.com/images/python
[MIT]: https://opensource.org/licenses/MIT

[![](https://images.microbadger.com/badges/image/uip9av6y/unbound-control-feeder.svg)][microbadger]
[![](https://images.microbadger.com/badges/version/uip9av6y/unbound-control-feeder.svg)][microbadger]
[![](https://images.microbadger.com/badges/commit/uip9av6y/unbound-control-feeder.svg)][microbadger]

# how to use this image

this image is intended to be used in combination with an external/linked
unbound instance. as such, it is not operational on its own.

the *examples/* directory contains a suggested deployment setup
using docker-compose.

## using a customized image

```dockerfile
FROM unbound-control-feeder:latest
COPY hosts.blacklist /data/
CMD [ "-f", "/data/hosts.blacklist" ]
```

the image takes no build arguments and can be built running
`docker build -t my-unbound-control-feeder .`

if the customized image does **not** spawn an unbound server,
you must link it to the container or make it otherwise accessible.

`docker run -d --name my-running-unbound-control-feeder
  --add-host=unbound:10.180.0.1
  --env UZF_HOST=unbound
  my-unbound-control-feeder`

you may need to publish the ports the prometheus webserver is
listening on to the host by specifying the -p option, for example
*-p 80:8080* to publish port 80 from the container host to port
8080 in the container. make sure the port you're using is free.

## using environment variables

`docker run -d --name my-running-unbound-control-feeder
  --env UZF_HOST=unbound
  --link some-unbound:unbound
  unbound-control-feeder:latest`

* *UZF_ZONE_TYPE*

  Used zone type (equivalent to `--zone-type`)

* *UZF_QUIET*

  if defined, reduces verbosity (equivalent to `--quiet`)

* *UZF_VERBOSE*

  if defined, increases verbosity (equivalent to `--verbose`)

* *UZF_INSTANT*

  if defined, runs a job immediately in addition to the schedule (equivalent to `--instant`)

* *UZF_METRICS*

  enable the prometheus metrics webserver (equivalent to `--metrics`)

* *UZF_METRICS_BIND*

  address to bind the webserver to (equivalent to `--metrics-bind`)

* *UZF_METRICS_PORT*

  port number the webserver will listen on (equivalent to `--metrics-port`)

* *UZF_RETRY*

  Number of retries for data retrieval and remote connection (equivalent to `--retry`)

* *UZF_RETRY_WAIT*

  time to wait between retries (equivalent to `--retry-wait`)

* *UZF_KEYFILE*

  SSL key file (equivalent to `--keyfile`)

* *UZF_CERTFILE*

  SSL certificate file (equivalent to `--certfile`)

* *UZF_CACERTS*

  CA certificate chain file (equivalent to `--cacerts`)

* *UZF_DAY*

  day of month to run update job (equivalent to `--day`)

* *UZF_TIME*

  time of day to run update job (equivalent to `--time`)

* *UZF_HOST*

  remote unbound control address (equivalent to `--host`)

* *UZF_PORT*

  remote unbound control port (equivalent to `--port`)

## with custom instructions via commandline

`docker run -d --name my-running-unbound-control-feeder
  --link some-unbound:unbound
  unbound-control-feeder:latest
  --host unbound`

to get more information about the supported commandlines,
run the image with the *-h* option

`docker run --rm -it unbound-control-feeder:latest -h`

## directly via bind mount

`docker run -d --name my-running-unbound-control-feeder
  -v /path/to/hosts:/data:ro
  unbound-control-feeder:latest
  --blacklist-file /data/hosts.blacklist`

note that your host's `/path/to/hosts` folder should be populated with a file
named `hosts.blacklist`. the content of it is formatted with one blacklisted
host per line.

# image setup

the image is based on the **3-alpine** tagged **python** image from
the [docker library][].

# license

the software contained in this image is licensed under the
[MIT][].

as with all Docker images, these likely also contain other
software which may be under other licenses (such as Bash, etc
from the base distribution, along with any direct or indirect
dependencies of the primary software being contained).
it is the image user's responsibility to ensure that any use of
this image complies with any relevant licenses for all software
contained within.
