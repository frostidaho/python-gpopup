import pytest
import math

@pytest.fixture(scope='function')
def IpcServer():
    from gpopup import ipc
    from random import randint
    val = ipc.Server._default_sock_name()
    rando = '_' + '{:d}'.format(randint(0, int(1e6)))
    class _IpcServer(ipc.Server):
        @classmethod
        def _default_sock_name(cls):
            return val + rando
    return _IpcServer

@pytest.fixture(scope='function')
def echo_client(IpcServer):
    Client = IpcServer.get_client()
    c = Client()
    c.start_server_maybe()
    yield c
    c.kill_server()

@pytest.fixture(scope='function')
def MathServer(IpcServer):
    class _MathServer(IpcServer):
        def cmd_cos(self, *pargs, **kwargs):
            return math.cos(*pargs, **kwargs)

        def cmd_erf(self, x):
            "Calculate the error function of x"
            return math.erf(x)
    return _MathServer

@pytest.fixture(scope='function')
def math_client(MathServer):
    Client = MathServer.get_client()
    c = Client()
    c.start_server_maybe()
    yield c
    c.kill_server()

@pytest.fixture(scope='function')
def message_types():
    from gpopup import message_types
    return message_types

@pytest.fixture(scope='function')
def gpopup_server():
    from subprocess import Popen
    p = Popen(['gpopup-server', '--force-bind'])
    yield p
    p.terminate()
    p.kill()

@pytest.fixture(scope='function')
def notifier_server():
    from gpopup.notifier import NotifierServer
    from threading import Thread
    t = Thread(target=lambda: NotifierServer().run(background=False))
    t.start()
    yield t
    t.join(timeout=2.0)

@pytest.fixture(scope='function')
def notifier_client(notifier_server):
    from gpopup.notifier import NotifierClient
    c = NotifierClient()
    yield c
    c.kill_server()
