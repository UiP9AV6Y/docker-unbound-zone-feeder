#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
'''
import sys
import time
import schedule
import logging
import prometheus_client
import prometheus_client.core

import arguments
import feeder

if sys.version_info[0] == 2:
    reload(sys)
    sys.setdefaultencoding('utf-8')

def schedule_job(spoon, payload, days = None, hour = None, instant = False):
    daemon = any([days, hour])
    status = 1

    if instant or not daemon:
        if spoon.feed(payload):
            status = 0

    if not daemon:
        sys.exit(status)

    if days is None:
        schedule.every().days.at(hour).do(spoon.feed, payload)
    elif hour is None:
        schedule.every(days).days.do(spoon.feed, payload)
    else:
        schedule.every(days).days.at(hour).do(spoon.feed, payload)

    while 1:
        try:
            schedule.run_pending()
            time.sleep(1)
        except KeyboardInterrupt:
            break

    sys.exit(0)

def main():
    parser = arguments.parser('Feed Unbound zone information via the control interface')
    factory = arguments.Arguments(parser)

    try:
        factory.read_env()
        factory.read_argv()
        factory.read_stdin()
    except Exception as err:
        print(err)
        sys.exit(1)

    registry = prometheus_client.core.REGISTRY
    control = factory.control_client()
    provider = factory.provider()
    spoon = feeder.Feeder(control, provider)
    log_level = logging.INFO

    if factory.quiet:
        log_level = logging.WARNING
    elif factory.verbose:
        log_level = logging.DEBUG

    logging.basicConfig(format='%(message)s', level=log_level)
    provider.enable_logger()
    spoon.enable_logger()

    if factory.metrics:
        spoon.enable_metrics(registry)
        prometheus_client.start_http_server(factory.metrics_port, factory.metrics_bind, registry)

    schedule_job(spoon, factory.zone_type, factory.day, factory.time, factory.instant)

if __name__ == "__main__":
    main()
