import gpopup.notifier as _noti
import gpopup.message_types as _mtypes

def show(message='', columns=(), display_time=5.0, position='northeast'):
    client = _noti.NotifierClient()
    client.start_server_maybe()
    table_msg = _mtypes.Table(body=message, columns=columns)
    n_id = client.new_window(table_msg)
    client.timeout(timeout=display_time, notification_id=n_id)
    return n_id

