import pytest

def test_pack_unpack():
    header = ('json', 301)
    from gpopup.ipc import _pack_header, _unpack_header
    header_bytes = _pack_header(*header)
    header_out = _unpack_header(header_bytes)
    assert header == header_out
    assert header[0] == header_out.type
    assert header[1] == header_out.length

def test_test_get_client(IpcServer):
    Client = IpcServer.get_client()
    c = Client()
    s = IpcServer()
    assert c.sock_name == s.sock_name

def test_ping(echo_client):
    assert echo_client.ping() == True

def test_pargs(echo_client):
    pargs = 9, 8, 7
    args, kw = echo_client.echo(*pargs)
    assert pargs == args
    assert {} == kw

def test_kwargs(echo_client):
    kwargs = {
        'a': [0,1,2],
        'b': 'some string',
        'c': print,
    }
    args, kw = echo_client.echo(**kwargs)
    assert () == args
    assert kwargs == kw

def test_adding_cmds(MathServer):
    Client = MathServer.get_client()
    assert 'cos' in Client.__dict__
    assert 'erf' in Client.__dict__

def test_calc(math_client):
    import math
    c = math_client
    assert c.cos(0.5) == pytest.approx(math.cos(0.5))
    assert c.erf(0.1) == pytest.approx(math.erf(0.1))

def test_json(IpcServer):
    assert IpcServer.serial_method == 'pickle'
    IpcServer.serial_method = 'json'
    assert IpcServer.serial_method == 'json'
    Client = IpcServer.get_client()
    assert Client.serial_method == 'json'
    c = Client()
    c.start_server_maybe()
    pargs, kwargs = c.echo(42)
    assert c.serial_method == 'json'
    assert kwargs == {}
    assert pargs == [42,]
    c.kill_server()

def test_no_server(IpcServer):
    Client = IpcServer.get_client()
    with pytest.raises(ConnectionError):
        Client().ping()

def test_busy(IpcServer):
    serv = IpcServer()
    serv2 = IpcServer()
    assert serv.sock_name == serv2.sock_name
    Client = serv.get_client()
    c = Client()
    with pytest.raises(ConnectionError):
        c.ping()
    serv.run(background=True)
    assert c.ping() == True
    assert serv2.run() == False
    c.kill_server()

def test_foreground(IpcServer):
    serv = IpcServer()
    Client = serv.get_client()
    c = Client()
    with pytest.raises(ConnectionError):
        c.ping()
    import threading
    run = lambda: serv.run(background=False)
    t = threading.Thread(target=run)
    t.start()
    assert c.ping() == True
    assert c.echo(37, wow='okay') == ((37,), {'wow': 'okay'})
    c.kill_server()
    t.join(1)

def test_fail_cmd(echo_client):
    assert echo_client.run_cmd('ping') == True
    with pytest.raises(AttributeError):
        echo_client.run_cmd('asdfasdf', 1, 3)

