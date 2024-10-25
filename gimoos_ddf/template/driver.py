from gimoos_ddf import C4, PersistData


DEVICE_ID = C4.GetDeviceID()


@C4.pub_catch_exception()
@C4.pub_log_func()
def ReceivedFromScene(bindingId, sceneId, command, params):
    """场景变化"""
    match command:
        case 'PUSH_SCENE':
            pass
        case 'REMOVE_SCENE':
            pass
        case 'EXECUTE_SCENE':
            pass


@C4.pub_catch_exception()
def ReceivedFromProxy(id_binding, str_command, t_params={}):
    """接收 Proxy 消息"""


@C4.pub_catch_exception()
def ExecuteCommand(str_command, t_params: str | dict | None = None):
    """处理命令"""


@C4.pub_catch_exception()
def OnPropertyChanged(key: str, value: str):
    """属性改变事件"""
    C4.pub_set_PD(key, value)

    match key:
        case '日志级别':
            C4.pub_set_log_level(value)

    C4.pub_save_PD()


@C4.pub_catch_exception()
def OnBindingChanged(binding_id, connection_event, other_device_id, other_binding_id):
    """链接改变事件"""


@C4.pub_catch_exception()
def OnTimerExpird(id_timer):
    """定时器事件"""


@C4.pub_catch_exception()
def OnInit(**kwargs):
    """设备初始化事件"""
    C4.pub_init(PersistData, **kwargs)



@C4.pub_catch_exception()
def OnDestroy():
    """设备删除事件"""
