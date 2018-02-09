import pytest
import gpopup.window_utils as wu

def test_monitor_geometry():
    geom = wu.monitor_geometry()
    assert isinstance(geom, wu.MonitorGeometry)

def test_notifier_ping(notifier_client):
    assert notifier_client.ping() is True

def test_notifier_echo(notifier_client):
    pargs, kwargs = notifier_client.echo('asdf', wow=9)
    assert pargs == ('asdf',)
    assert kwargs == {'wow': 9}

def test_notifier_msg(notifier_client, message_types):
    Simple = message_types.Simple
    s_msg = Simple(
        summary='Some summary',
        body='some body txt',
    )
    n_id = notifier_client.new_window(s_msg)
    assert isinstance(n_id, int)
    notifier_client.destroy(n_id)


@pytest.mark.filterwarnings('ignore::Warning')
@pytest.mark.parametrize('position', wu.Position.choices)
def test_notifier_msg_cmds(notifier_client, message_types, position):
    nc = notifier_client
    Simple = message_types.Simple
    s_msg = Simple(
        summary='Some summary',
        body='some body txt',
    )
    n_id = nc.new_window(s_msg)
    assert isinstance(n_id, int)
    nc.hide(notification_id=n_id)
    nc.show(notification_id=n_id)
    pos = nc.movewin(position=position, notification_id=n_id)
    assert pos == position
    nc.hide(notification_id=n_id)
    nc.timeout(3.0, notification_id=n_id)
    nc.destroy(n_id)

