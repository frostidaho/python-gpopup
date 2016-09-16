#!/usr/bin/env python
from gpopup import notifier
from gpopup import message_types as mtypes
from time import sleep


SOCK_NAME = 'gpopup_example/notifier_socket'
def data_file(name):
    from os import path
    ex_dir = path.dirname(path.dirname(path.realpath(__name__)))
    return path.join(ex_dir, 'data', name)


server = notifier.NotifierServer(sock_name=SOCK_NAME, force_bind=True)
server.run(background=True)

client = notifier.NotifierClient(sock_name=SOCK_NAME)
print(client.echo('Testing server'))

simp_msg = mtypes.Simple(
    summary='Summary text',
    body='And here is some body text.\nLine two.',
)

print('Displaying window with a message_types.Simple msg')
print(simp_msg)
w_id = client.new_window(simp_msg)

sleep(2.0)
print('Destroying window with id', w_id)
client.destroy(w_id)

print('Creating a new window with a simple msg and a table msg.')
print('The table msg is created from a json data file')
with open(data_file('pizza.json'), 'rt') as fjson:
          table_msg = mtypes.Table.from_json(fjson.read())
print(table_msg)

w_id = client.new_window(simp_msg, table_msg)

from gpopup.window_utils import Position
for position in Position.choices:
    print('Moving window to position: ', position)
    client.movewin(position, notification_id=w_id)
    sleep(1.0)


print('Destroying window', w_id)
client.destroy(w_id)

print('Shutting down server')
client.kill_server()

