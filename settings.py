import values


class Setting(object):
    def __init__(self, on_change=lambda: 1+1, user_name='', **kwargs):
        try:
            self.value = kwargs['value']
        except KeyError:
            raise TypeError('cannot find \'value\' or \'on_change\' argument')
        self.on_change = on_change
        self.user_name = user_name

    def set(self, new=None, **kwargs):
        try:
            if new != None:
                self.value = self.value.set(new)
            else:
                self.value = self.value.set(**kwargs)
        except (TypeError, ValueError):
            raise ValueError('invalid new value')
        else:
            self.on_change()


def configure(configuration):
    nv = {'view':{}, 'main':{}}
    try:
        print(configuration['view']['show_grid'])
        nv['view']['show_grid'] = Setting(value=values.BoolValue(configuration['view']['show_grid']),
                                                                 user_name='Show Grid')
        nv['view']['background_color'] = Setting(value=values.ColorValue(*configuration['view']['background_color']),
                                                                         user_name='Graph Background Color')
        nv['view']['axis_color'] = Setting(value=values.ColorValue(*configuration['view']['axis_color']),
                                                                         user_name='Graph Axis Color')
        nv['view']['x_axis_name'] = Setting(value=values.StringValue(configuration['view']['x_axis_name']),
                                            user_name='Name of x axis')
        nv['view']['y_axis_name'] = Setting(value=values.StringValue(configuration['view']['y_axis_name']),
                                            user_name='Name of y axis')
        nv['view']['show_axis_names'] = Setting(value=values.BoolValue(configuration['view']['show_axis_names']),
                                                user_name='Show axis\' names')
        nv['view']['debug_data'] = Setting(value=values.BoolValue(configuration['view']['debug_data']),
                                           user_name='Show Debug Data')
        nv['view']['quality'] = Setting(value=values.BoolValue(configuration['view']['quality']),
                                        user_name='Lines Quality')
        nv['main']['save_settings'] = Setting(value=values.BoolValue(configuration['main']['save_settings']),
                                              user_name='Save Settings When Closing')
    except KeyError as e:
        raise ValueError('incomplete configuration\n', e)
    return nv


def deconfigure(config):
    nv = {'view':{}, 'main':{}}
    for cat in config.keys():
        for setting in config[cat].keys():
            if isinstance(config[cat][setting].value, values.ColorValue):
                nv[cat][setting] = config[cat][setting].value.rgb()
            else:
                nv[cat][setting] = config[cat][setting].value.value
    return nv
