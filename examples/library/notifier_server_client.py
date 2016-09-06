#!/usr/bin/env python
import gpopup.notifier
from gpopup.utils import format_msg
from time import sleep
TIME_PAUSE = 0.5

def data_file(name):
    from os import path
    ex_dir = path.dirname(path.dirname(path.realpath(__name__)))
    return path.join(ex_dir, 'data', name)

client = gpopup.notifier.NotifierClient(sock_name='gpopup_example/notifier_socket')
# Start the server associated with client if not already running
client.start_server_maybe()

with open(data_file('pizza.json'), 'rt') as fjson:
    w_id = client.new_from_markup(fjson.read(), position='southwest', parser='json')

sleep(TIME_PAUSE)
# Explicitly passing notification_id is only necessary
# if the notification you want to use is not the most recently created
# notification by the server.
client.movewin(position='south', notification_id=w_id)
sleep(TIME_PAUSE)
client.movewin(position='southeast', notification_id=w_id)
sleep(TIME_PAUSE)
client.hide(notification_id=w_id)
sleep(TIME_PAUSE)

with open(data_file('wiki_gdp.html'), 'rt') as wiki_gdp:
    client.new_from_markup(wiki_gdp.read(), position='north', parser='html')

client.show(w_id)    # Showing the pizza.json window
sleep(TIME_PAUSE*2)

client.destroy()                # Destroying the wiki_gdp.html window
sleep(TIME_PAUSE)

client.destroy(w_id)            # Destroying the pizza.json window
sleep(TIME_PAUSE)

client.kill_server()
