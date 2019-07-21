# -*- coding: utf-8 -*-
'''
'''
import os
import time
import dnsblackhole

import utils

class ProviderWrapper(utils.Loggable):
    def __init__(self, blacklists, whitelists = [], retries = 0, wait_retry = 1):
        super(ProviderWrapper, self).__init__()

        self.retries = retries
        self.wait_retry = wait_retry

        self._blacklists = blacklists
        self._whitelists = whitelists

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

class HostProvider(object):
    def retrieve(self):
        pass

class RemoteHostsProvider(HostProvider):
    def __init__(self, urls):
        self._urls = urls

    def retrieve(self):
        zone_data = '{domain}'

        return dnsblackhole.process_host_file_url([], [], zone_data, self._urls)

class FileLinesProvider(HostProvider):
    def __init__(self, files):
        self._files = files

    def retrieve(self):
        hosts = []

        for file in self._files:
            with open(os.path.abspath(file), 'rb') as f:
                for line in f:
                    try:
                        host = line.decode('utf-8').strip()
                    except:
                        continue

                    if host == '' or line.startswith(b'#'):
                        continue

                    hosts.append(host)

        return hosts

class ListProvider(HostProvider):
    def __init__(self, hosts):
        self._hosts = hosts

    def retrieve(self):
        return self._hosts
