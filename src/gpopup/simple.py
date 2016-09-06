import gpopup.notifier as _noti
import gpopup.utils as _utils

def show(message='', columns=(), display_time=5.0, position='northeast'):
    client = _noti.NotifierClient()
    client.start_server_maybe()
    n_id = client.new_window(
        formatted_msg=_utils.format_msg(message, columns),
        position=position,
    )
    client.timeout(timeout=display_time, notification_id=n_id)
    return n_id

