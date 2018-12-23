# -*- coding: utf-8 -*-
'''
'''
import errno
import socket
import select
import platform

try:
    import ssl
except ImportError:
    ssl = None

if platform.system() == 'Windows':
    EAGAIN = errno.WSAEWOULDBLOCK
else:
    EAGAIN = errno.EAGAIN

UNBOUND_CONTROL_VERSION = 1
UNBOUND_CONTROL_EOF = ''.join([chr(0x04), chr(0x0a)])

class ControlError(Exception):
    pass

class UnboundControlClient(object):
    def __init__(self, host = '127.0.0.1', port = 8953, key = None, cert = None, cas = None):
        self._host = host
        self._port = port
        self._key = key
        self._cert = cert
        self._cas = cas
        self._timeout = 10

        self._socket = None
        self._context = None

    def __del__(self):
        self.close()

    def open(self):
        """Connecto to a remote Unbound Control interfaceself."""

        if self._host is None or len(self._host) == 0:
            raise ValueError('Invalid host.')
        if self._port <= 0:
            raise ValueError('Invalid port number.')

        if self._key is None and self._cert is None:
            self._socket = self._create_socket()
        else:
            self._context = self._create_context()
            self._socket = self._create_socket(self._context)

    def close(self):
        """Close the connection to the server."""
        if self._socket is None:
            return

        sock = self._socket
        self._socket = None
        self._context = None
        sock.close()

    def send(self, command, *args):
        self._send_header(command)
        for arg in args:
            self._sendall(' ')
            self._sendall(arg)

        self._sendall("\n")

        return self._read_response()

    def send_lines(self, command, *args):
        self._send_header(command)
        self._sendall("\n")
        for arg in args:
            self._sendall(arg)
            self._sendall("\n")

        self._sendall(UNBOUND_CONTROL_EOF)

        return self._read_response()

    def local_zone(self, name, type):
        return self.send('local_zone', name, type)

    def local_zones(self, zones):
        return self.send_lines('local_zones', *zones)

    def _send_header(self, command):
        if self._socket is None:
            raise ValueError('SSL/TLS has already been configured.')

        # https://github.com/NLnetLabs/unbound/blob/023411f97505c8c7e375112ad853b6a40ef848a6/smallapp/unbound-control.c#L703
        # UBCT1  local_zone example.com always_nxdomain\n
        self._sendall('UBCT%d  %s' % (UNBOUND_CONTROL_VERSION, command))

    def _read_response(self):
        response = self._recvall()

        if response.startswith('error '):
            raise ControlError(response[6:])

        return response

    def _recvall(self):
        response = []

        while True:
            data = self._socket.recv(1024)
            if data:
                response.append(data.decode())
            else:
                break

        return ''.join(response)

    def _sendall(self, str):
        self._socket.sendall(str.encode())

    def _create_context(self):
        """Factory for secure communication contextself.

        Most settings are hardcoded and adapted from the
        control client implementation.
        (https://github.com/NLnetLabs/unbound/blob/023411f97505c8c7e375112ad853b6a40ef848a6/smallapp/unbound-control.c#L478)
        """

        if ssl is None:
            raise ValueError('This platform has no SSL/TLS.')

        if not hasattr(ssl, 'SSLContext'):
            raise ValueError('Python 2.7.9 and 3.2 are the minimum supported versions for TLS.')

        if self._cas is None and not hasattr(ssl.SSLContext, 'load_default_certs'):
            raise ValueError('CAs must be provided.')

        if self._cert is None and self._key is not None:
            raise ValueError('Cannot use certificate without a key.')

        if self._cert is not None and self._key is None:
            raise ValueError('Cannot use key without a certificate.')

        tls_version = ssl.PROTOCOL_SSLv23
        if hasattr(ssl, "PROTOCOL_TLS"):
            tls_version = ssl.PROTOCOL_TLS
        context = ssl.SSLContext(tls_version)

        context.verify_mode = ssl.CERT_REQUIRED
        context.options |= ssl.OP_NO_SSLv2
        context.options |= ssl.OP_NO_SSLv3

        if self._cert is not None:
            context.load_cert_chain(self._cert, self._key)

        if self._cas is not None:
            context.load_verify_locations(self._cas)
        else:
            context.load_default_certs()

        return context

    def _create_socket(self, ssl_context = None):
        self.close()

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        sock.settimeout(self._timeout)

        if ssl_context is None:
            sock.connect((self._host, self._port))
            return sock

        sock = ssl_context.wrap_socket(
            sock,
            do_handshake_on_connect=False,
        )

        sock.settimeout(self._timeout)
        sock.connect((self._host, self._port))
        sock.do_handshake()

        return sock
