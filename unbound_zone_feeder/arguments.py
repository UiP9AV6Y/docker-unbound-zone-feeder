# -*- coding: utf-8 -*-
'''
'''
import os
import sys
import argparse

import provider
import client
import utils

try:
    # python2
    from urlparse import urlparse
except:
    # python3
    from urllib.parse import urlparse

UNBOUND_ZONE_TYPES = ["static", "deny", "refuse", "redirect", "transparent", "typetransparent", "inform", "inform_deny", "always_transparent", "always_refuse", "always_nxdomain", "noview", "nodefault"]

def syntactic_url(value):
    try:
        result = urlparse(value)
        if all([result.scheme, result.netloc, result.path]):
            return value

        raise argparse.ArgumentTypeError("Incomplete URL: %s" % value)
    except Exception as err:
        raise argparse.ArgumentTypeError(str(err))

def file_path(value):
    if not os.path.isfile(value):
        raise argparse.ArgumentTypeError("No such file: %s" % value)

    return os.path.abspath(value)

def day_of_month(value):
    try:
        day = int(value)

        if 1 > day or 31 < day:
            raise argparse.ArgumentTypeError("DoM must be between [1, 31], not '%s'" % value)
    except argparse.ArgumentTypeError:
        raise
    except ValueError:
        raise argparse.ArgumentTypeError("Malformed Dom: %s" % value)

    return day

def time_of_day(value):
    if 1 != value.count(':'):
        raise argparse.ArgumentTypeError("ToD must be given in HH:MM format not '%s'" % value)

    hour, minute = value.split(':', 2)
    m = int(minute)
    h = int(hour)

    if 0 > h or 23 < h:
        raise argparse.ArgumentTypeError("Hour must be between [0, 23], not '%s'" % hour)

    if 0 > m or 59 < h:
        raise argparse.ArgumentTypeError("Minute must be between [0, 59], not '%s'" % minute)

    return value

def port_number(value):
    try:
        port = int(value)

        if 1 > port or 65535 < port:
            raise argparse.ArgumentTypeError("Post must be between [1, 65535], not '%s'" % value)
    except argparse.ArgumentTypeError:
        raise
    except ValueError:
        raise argparse.ArgumentTypeError("Malformed port: %s" % value)

    return port

def host_address(value):
    if not utils.is_domain(value) and not utils.is_address(value):
        raise argparse.ArgumentTypeError("Malformed host/address: %s" % value)

    return value

def zone_name(value):
    if not utils.is_domain(value):
        raise argparse.ArgumentTypeError("Malformed zone name: %s" % value)

    return value

def binding_address(value):
    if not utils.is_address(value):
        raise argparse.ArgumentTypeError("Malformed bind address: %s" % value)

def parser(description):
    parser = argparse.ArgumentParser(description=description)
    verbosity = parser.add_mutually_exclusive_group()
    input = parser.add_mutually_exclusive_group()

    verbosity.add_argument("--quiet", "-q", help="Reduce output verbosity", action="store_true")
    verbosity.add_argument("--verbose", "-v", help="Increase output verbosity", action="store_true")

    parser.add_argument("--zone-type", "-z", choices=UNBOUND_ZONE_TYPES, help="Used zone type")
    parser.add_argument("--retry", "-r", type=int, help="Number of retries for data retrieval and remote connection", metavar="COUNT")
    parser.add_argument("--retry-wait", "-R", type=int, help="Time to wait between retries", metavar="SECONDS")

    parser.add_argument("--metrics", help="Start webserver exposing Prometheus compatible metrics", action="store_true")
    parser.add_argument("--metrics-port", type=port_number, help="Port binding for metrics listener", metavar="PORT")
    parser.add_argument("--metrics-bind", type=binding_address, help="Interface for metrics listener", metavar="ADDRESS")

    parser.add_argument("--time", "-t", type=time_of_day, help="Time of day to run job. If absent, will run at midnight")
    parser.add_argument("--day", "-d", type=day_of_month, help="Day of month to run job. If absent, will run every day.")
    parser.add_argument("--instant", "-i", help="Run a job immediately in addition to the schedule", action="store_true")

    parser.add_argument("--host", "-H", type=host_address, help="Host name")
    parser.add_argument("--port", "-p", type=port_number, help="Port number")
    parser.add_argument("--keyfile", "-k", type=file_path, help="SSL key file", metavar="FILE")
    parser.add_argument("--certfile", "-c", type=file_path, help="SSL certificate file", metavar="FILE")
    parser.add_argument("--cacerts", "-C", type=file_path, help="CA certificate chain file", metavar="FILE")

    parser.add_argument("--blacklist", "-b", type=zone_name, help="Domain to add", action="append", metavar="HOST")
    parser.add_argument("--blacklist-url", "-u", type=syntactic_url, help="Remote location containing hosts-style domain list", action="append", metavar="URL")
    parser.add_argument("--blacklist-file", "-f", type=file_path, help="File with blacklisted domains per line", action="append", metavar="FILE")

    parser.add_argument("--whitelist", "-w", type=zone_name, help="Domain to exclude from adding", action="append", metavar="HOST")
    parser.add_argument("--whitelist-file", "-F", type=file_path, help="File with whitelisted domains per line", action="append", metavar="FILE")

    input.add_argument("--blacklist-stdin", "-B", help="Read domains to add from stdin", action="store_true")
    input.add_argument("--whitelist-stdin", "-W", help="Read domains to exclude from stdin", action="store_true")

    return parser

class Arguments(object):
    def __init__(self, parser):
        self._parser = parser

        self.quiet = False
        self.verbose = False
        self.instant = False

        self.metrics = False
        self.metrics_bind = '0.0.0.0'
        self.metrics_port = 8080

        self.host = '127.0.0.1'
        self.port = 8953
        self.keyfile = None
        self.certfile = None
        self.cacerts = None

        self.zone_type = UNBOUND_ZONE_TYPES[0]
        self.retry = 0
        self.retry_wait = 5

        self.blacklist = []
        self.blacklist_url = []
        self.blacklist_file = []
        self.whitelist = []
        self.whitelist_file = []

        self.blacklist_stdin = False
        self.whitelist_stdin = False

        self.day = None
        self.time = None

    def control_client(self):
        return client.UnboundControlClient(self.host,
            self.port,
            self.keyfile,
            self.certfile,
            self.cacerts
        )

    def whitelist_providers(self):
        list = []

        if self.whitelist:
            list.append(provider.ListProvider(self.whitelist))

        if self.whitelist_file:
            list.append(provider.FileLinesProvider(self.whitelist_file))

        return list

    def blacklist_providers(self):
        list = []

        if self.blacklist:
            list.append(provider.ListProvider(self.blacklist))

        if self.blacklist_file:
            list.append(provider.FileLinesProvider(self.blacklist_file))

        if self.blacklist_url:
            list.append(provider.RemoteHostsProvider(self.blacklist_url))

        return list

    def provider(self):
        blacklists = self.blacklist_providers()
        whitelists = self.whitelist_providers()

        return provider.ProviderWrapper(blacklists, whitelists, self.retry, self.retry_wait)

    def read_argv(self):
        self._parser.parse_args(namespace=self)

    def read_stdin(self):
        domains = []

        if not any([self.blacklist_stdin, self.whitelist_stdin]):
            return

        for line in sys.stdin:
            domain = line.strip()

            if domain and is_domain_or_address(domain):
                domains.append(domain)

        if self.blacklist_stdin:
            self.blacklist.extend(domains)
        elif self.whitelist_stdin:
            self.whitelist.extend(domains)

    def read_env(self):
        zone_type = os.getenv('UZF_ZONE_TYPE', self.zone_type)

        if zone_type in UNBOUND_ZONE_TYPES:
            self.zone_type = zone_type
        else:
            raise ValueError('Invalid zone type: %s' % zone_type)

        if os.environ.get('UZF_QUIET'):
            self.quiet = True
        if os.environ.get('UZF_VERBOSE'):
            self.verbose = True
        if os.environ.get('UZF_INSTANT'):
            self.instant = True
        if os.environ.get('UZF_METRICS'):
            self.metrics = True
        if os.environ.get('UZF_METRICS_BIND'):
            self.metrics_bind = binding_address(os.environ.get('UZF_METRICS_BIND'))
        if os.environ.get('UZF_METRICS_PORT'):
            self.metrics_port = port_number(os.environ.get('UZF_METRICS_PORT'))
        if os.environ.get('UZF_RETRY'):
            self.retry = int(os.environ.get('UZF_RETRY'))
        if os.environ.get('UZF_RETRY_WAIT'):
            self.retry_wait = int(os.environ.get('UZF_RETRY_WAIT'))
        if os.environ.get('UZF_KEYFILE'):
            self.keyfile = file_path(os.environ.get('UZF_KEYFILE'))
        if os.environ.get('UZF_CERTFILE'):
            self.certfile = file_path(os.environ.get('UZF_CERTFILE'))
        if os.environ.get('UZF_CACERTS'):
            self.cacerts = file_path(os.environ.get('UZF_CACERTS'))
        if os.environ.get('UZF_DAY'):
            self.day = day_of_month(os.environ.get('UZF_DAY'))
        if os.environ.get('UZF_TIME'):
            self.time = time_of_day(os.environ.get('UZF_TIME'))

        self.host = host_address(os.getenv('UZF_HOST', self.host))
        self.port = port_number(os.getenv('UZF_PORT', self.port))
