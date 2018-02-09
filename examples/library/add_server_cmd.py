#!/usr/bin/env python
from gpopup import ipc
import math

class MathServer(ipc.Server):
    def cmd_cos(self, *pargs, **kwargs):
        return math.cos(*pargs, **kwargs)

    def cmd_erf(self, x):
        "Calculate the error function of x"
        return math.erf(x)

class Client(ipc.BaseClient):
    command_server = MathServer

c = Client(sock_name='gpopup_example/add_server_cmd')
c.start_server_maybe()
print('c.cos(0.0) =', c.cos(0.0))
print('c.cos(pi / 4) =', c.cos(math.pi / 4.0))
print('c.erf(0.5) =', c.erf(0.5))

print('Available client commands:')
print(c.commands)

c.kill_server()
