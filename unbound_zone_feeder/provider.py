# -*- coding: utf-8 -*-
'''
'''
import os
import time
import requests

import utils

class ProviderWrapper(utils.Loggable):
    def __init__(self, blacklists, whitelists = [], retries = 0, wait_retry = 1):
        super(ProviderWrapper, self).__init__()

        self.retries = retries
        self.wait_retry = wait_retry

        self._blacklists = blacklists
        self._whitelists = whitelists

    def enable_logger(self, logger=None):
        for list in self._blacklists:
            list.enable_logger(logger)

        for list in self._whitelists:
            list.enable_logger(logger)

        super(ProviderWrapper, self).enable_logger(logger)

    def retrieve(self):
        black = []
        white = []
        zones = []

        for list in self._blacklists:
            hosts = self._retrieve('blacklist', list, self.retries, self.wait_retry)
            black.extend(hosts)

        for list in self._whitelists:
            hosts = self._retrieve('whitelist', list, self.retries, self.wait_retry)
            white.extend(hosts)

        for zone in black:
            if zone not in white:
                self._debug('Blacklisted zone: %s', zone)
                zones.append(zone)
            else:
                self._debug('Zone is whitelisted: %s', zone)

        return zones

    def _retrieve(self, purpose, provider, retries = 0, wait_retry = 1):
        while True:
            try:
                return provider.retrieve()
            except Exception as err:
                self._error('Unable to fetch %s hosts: %s', purpose, err)

                if 0 < retries:
                    retries -= 1
                    self._info('Retrying to fetch %s host list', purpose)
                    time.sleep(wait_retry)
                else:
                    self._warning('Unable to fetch %s hosts, giving up', purpose)
                    break

        return []

class HostProvider(utils.Loggable):
    def __init__(self):
        super(HostProvider, self).__init__()

    def retrieve(self):
        pass

class RemoteHostsProvider(HostProvider):
    def __init__(self, urls):
        super(RemoteHostsProvider, self).__init__()

        self._urls = urls

    def retrieve(self):
        hosts = []

        self._info('Retrieving hosts from %d URLs', len(self._urls))

        for url in self._urls:
            try:
                self._debug('Retrieving hosts from %s', url)
                hosts.extend(self._retrieve(url))
            except Exception as e:
                self._warning('Failed to retrieve hosts from %s: %s', url, str(e))

        return hosts

    def _retrieve(self, url):
        hosts = []
        r = requests.get(url)

        if r.status_code != 200:
            return hosts

        for line in r.iter_lines():
            line = line.decode('utf-8').strip()

            # supported lines include:
            # 127.0.0.1 domain.name # comment
            # 0.0.0.0   domain.name:port
            # ::1       domain.name

            if not line.startswith(('127.', '0.', '::1')):
                continue

            fragments = line.split()

            if len(fragments) < 2:
                continue

            # convert to lower case and remove :port
            host = fragments[1].lower().split(':')[0]

            if host == 'localhost.localdomain' or host == 'localhost':
                continue

            hosts.append(host)

        return hosts

class FileLinesProvider(HostProvider):
    def __init__(self, files):
        super(FileLinesProvider, self).__init__()

        self._files = files

    def retrieve(self):
        hosts = []

        self._info('Reading hosts from %d files', len(self._files))

        for file in self._files:
            try:
                self._debug('Reading hosts from %s', file)
                hosts.extend(self._retrieve(file))
            except Exception as e:
                self._warning('Failed to read hosts from %s: %s', file, str(e))

        return hosts

    def _retrieve(self, file):
        hosts = []

        with open(os.path.abspath(file), 'rb') as f:
            for line in f:
                host = line.decode('utf-8').strip()

                if host and not host.startswith('#'):
                    hosts.append(host)

        return hosts

class ListProvider(HostProvider):
    def __init__(self, hosts):
        super(ListProvider, self).__init__()

        self._hosts = hosts

    def retrieve(self):
        self._debug('Returning %d hosts', len(self._hosts))

        return self._hosts
