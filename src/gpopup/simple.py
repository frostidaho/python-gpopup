import gpopup.message_types as _mtypes

new_messages = _mtypes.new_messages
def show(summary='', body='', table='', table_cols=(),
         post_summary='', post_body='', display_time=5.0,
         position='northeast'):
    import gpopup.notifier as _noti
    client = _noti.NotifierClient()
    client.start_server_maybe()
    pre_msg = _mtypes.Simple(summary=summary, body=body)
    table_msg = _mtypes.Table(body=table, columns=table_cols, max_rows=6)
    post_msg = _mtypes.Simple(summary=post_summary, body=post_body)
    n_id = client.new_window(pre_msg, table_msg, post_msg, position=position)
    client.timeout(timeout=display_time, notification_id=n_id)
    return n_id


def show_blocking(summary='', body='', table='', table_cols=(),
         post_summary='', post_body='', display_time=5.0,
         position='northeast'):
    import gpopup.message_widgets as _mwidgets
    pre_msg = _mtypes.Simple(summary=summary, body=body)
    table_msg = _mtypes.Table(body=table, columns=table_cols, max_rows=6)
    post_msg = _mtypes.Simple(summary=post_summary, body=post_body)
    win = _mwidgets.MainWindow(pre_msg, table_msg, post_msg)
    win.position = position
    win.timeout_destroy(display_time)
    _mwidgets.Gtk.main()
    return True

