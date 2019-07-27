
[microbadger]: https://microbadger.com/images/uip9av6y/unbound-zone-feeder
[docker library]: https://store.docker.com/images/python
[MIT]: https://opensource.org/licenses/MIT

[![](https://images.microbadger.com/badges/image/uip9av6y/unbound-zone-feeder.svg)][microbadger]
[![](https://images.microbadger.com/badges/version/uip9av6y/unbound-zone-feeder.svg)][microbadger]
[![](https://images.microbadger.com/badges/commit/uip9av6y/unbound-zone-feeder.svg)][microbadger]

# how to use this image

this image is intended to be used in combination with an external/linked
unbound instance. as such, it is not operational on its own.

the *examples/* directory contains a suggested deployment setup
using docker-compose.

## using a customized image

```dockerfile
FROM unbound-zone-feeder:latest
COPY hosts.blacklist /data/
CMD [ "-f", "/data/hosts.blacklist" ]
```

the image takes no build arguments and can be built running
`docker build -t my-unbound-zone-feeder .`

if the customized image does **not** spawn an unbound server,
you must link it to the container or make it otherwise accessible.

`docker run -d --name my-running-unbound-zone-feeder
  --add-host=unbound:10.180.0.1
  --env UZF_HOST=unbound
  my-unbound-zone-feeder`

you may need to publish the ports the prometheus webserver is
listening on to the host by specifying the -p option, for example
*-p 80:8080* to publish port 80 from the container host to port
8080 in the container. make sure the port you're using is free.

## using commandline arguments

`docker run -d --name my-running-unbound-zone-feeder
  --link some-unbound:unbound
  unbound-zone-feeder:latest
  --host unbound`

* *--quiet*

  Reduce output verbosity

* *--verbose*

  Increase output verbosity

* *--zone-type*

  Used zone type

* *--retry*

  Number of retries for data retrieval and remote connection

* *--retry-wait*

  Time to wait between retries

* *--metrics*

  Start webserver exposing Prometheus compatible metrics

* *--metrics-port*

  Port binding for metrics listener

* *--metrics-bind*

  Interface for metrics listener

* *--time*

  Time of day to run job. If absent, will run at midnight

* *--day*

  Day of month to run job. If absent, will run every day


* *--instant*

  Run a job immediately in addition to the schedule

* *--host*

  Remote Unbound server host name

* *--port*

  Remote Unbound server port number

* *--keyfile*

  SSL key file

* *--certfile*

  SSL certificate file

* *--cacerts*

  CA certificate chain file

* *--blacklist*

  Domain to add

* *--blacklist-url*

  Remote location containing hosts-style domain list

* *--blacklist-file*

  File with blacklisted domains per line

* *--whitelist*

  Domain to exclude from adding

* *--whitelist-file*

  File with whitelisted domains per line

* *--blacklist-stdin*

  Read domains to add from stdin

* *--whitelist-stdin*

  Read domains to exclude from stdin

## using environment variables

`docker run -d --name my-running-unbound-zone-feeder
  --env UZF_HOST=unbound
  --link some-unbound:unbound
  unbound-zone-feeder:latest`

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

`docker run -d --name my-running-unbound-zone-feeder
  --link some-unbound:unbound
  unbound-zone-feeder:latest
  --host unbound`

to get more information about the supported commandlines,
run the image with the *-h* option

`docker run --rm -it unbound-zone-feeder:latest -h`

## directly via bind mount

`docker run -d --name my-running-unbound-zone-feeder
  -v /path/to/hosts:/data:ro
  unbound-zone-feeder:latest
  --blacklist-file /data/hosts.blacklist`

note that your host's `/path/to/hosts` folder should be populated with a file
named `hosts.blacklist`. the content of it is formatted with one blacklisted
host per line.

# input processing

hosts can be read from various sources using different
retrieval strategies.

## commandline

input provided via the commandline interface is forwarded
without modifications and **not** filtered.

## file

files are read line by line ignoring empty ones and those
starting with *#*. no filtering is applied.

## url

remote files are parsed for values following the *hosts file*
syntax. processing involves:

* accepting lines starting with *127.0.0.1*
* accepting lines starting with *0.0.0.0*
* stripping port numbers from hostnames
* removing trailing comments
* lowercase conversion

```
# ignored
127.0.0.1 localhost
# valid entries
127.0.0.1 localhost.test
0.0.0.0 all.interfaces.test
127.127.127.127 again.localhost.test # comment
127.0.0.1 port.localhost.test:8080
127.0.0.1	tab.localhost.test
127.0.0.1 utf-8.localhost.test # 😄 unicode character
::1 ipv6.localhost.test #[IPv6]
```

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
