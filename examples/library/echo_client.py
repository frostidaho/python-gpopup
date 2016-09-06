#!/usr/bin/env python
from gpopup import ipc

class Client(ipc.BaseClient):
    command_server = ipc.Server


pargs = 9,8,7
kwargs = {
    'a': [0,1,2],
    'b': 'some string',
    'c': print,
}

c = Client(sock_name='ipc/echo_client_example')
try:
    out = c.echo(*pargs, **kwargs)
    print(out)
except ConnectionError:
    print("Couldn't connect to server")
    c.start_server_maybe()
    out = c.echo(*pargs, **kwargs)
    print(out)


