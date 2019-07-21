# -*- coding: utf-8 -*-
'''
'''
import time
import prometheus_client
import prometheus_client.core

import utils

class Feeder(utils.Loggable):

    def __init__(self, client, provider):
        super(Feeder, self).__init__()

        self._provider = provider
        self._client = client
        self._metrics = None

        self._failure_counter = None
        self._transmission_gauge = None

    def enable_metrics(self, registry=None):
        """Enables metrics reporting"""
        if registry is None:
            if self._metrics is not None:
                # dont replace existing registry
                return
            registry = prometheus_client.core.REGISTRY
        self._metrics = registry
        self._recreate_metrics(registry)

    def disable_metrics(self):
        self._metrics = None

    def feed(self, data):
        hosts = self._provider.retrieve()
        report = 0
        failure = True

        if not hosts:
            self._info('No hosts available, skipping operation')
            failure = False
        elif self._transmit_hosts(data, hosts, self._provider.retries, self._provider.wait_retry):
            report = len(hosts)
            failure = False

        if self._metrics:
            self._debug('Reporting metrics: Failure=%r, Transmission=%d' % (failure, report))
        if failure and self._failure_counter is not None:
            self._failure_counter.inc()
        if self._transmission_gauge is not None:
            self._transmission_gauge.set(report)

        return not failure

    def _transmit_hosts(self, zone_data, hosts = [], retries = 0, wait_retry = 1):
        while True:
            try:
                self._client.open()
                break
            except Exception as err:
                self._error('Unable to establish connection: %s', err)

                if 0 < retries:
                    retries -= 1
                    self._info('Retrying to connect')
                    time.sleep(wait_retry)
                else:
                    self._warning('Unable to connect, giving up')
                    self._client.close()
                    return False

        zones = map(lambda host: '%s %s' % (host, zone_data), hosts)

        try:
            answer = self._client.local_zones(zones)
            self._info('Transmission complete: %s', answer)
            return True
        except Exception as err:
            self._error('Unable to transmit zones: %s', err)
        finally:
            self._client.close()

        return False

    def _recreate_metrics(self, registry):
        self._failure_counter = prometheus_client.Counter('transmission_failures', 'Number of failed transmissions', registry=registry)
        self._transmission_gauge = prometheus_client.Gauge('zone_transmissions', 'Transmissions during the last job', registry=registry)
