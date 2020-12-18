from kivy.config import Config
Config.set('graphics', 'width', '1000')
Config.set('graphics', 'height', '700')
Config.set('graphics', 'resizable', False)
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
Config.set('kivy', 'exit_on_escape', 0)
Config.set('kivy', 'keyboard_mode', 'system')
from kivy.app import App
from kivy.uix import label, button, textinput, widget, scrollview, gridlayout, relativelayout, popup, togglebutton,\
    slider, tabbedpanel
from kivy.uix.behaviors import focus
from kivy.graphics import instructions, Color, Line, Point, Rectangle, RoundedRectangle, Triangle, texture
from kivy.core.window import Window
from kivy.core.text import Label as tl
from kivy.properties import StringProperty
from numpy import arange
import math
from func import Function_graph as Fg, Function_2d as F2d
from graphics_engine import con_v2 as line
import time
from math_plus import rhu as round_half_up, scientific_format as sci_format
import json
import values
from settings import configure, deconfigure
from copy import deepcopy


def multiple_executor(*args):
    to_return = []
    for statement in args:
        to_return.append(statement())
    return to_return


class CustomTabHeader(tabbedpanel.TabbedPanelHeader):
    def __init__(self, first=False, **kwargs):
        super(CustomTabHeader, self).__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = [.5, .5, .5, 1]
        self.color = [.7, .7, .7, 1]
        if first:
            self.canvas.before.add(Color(rgba=[.3, .3, .3, 1]))
            self.canvas.before.add(Rectangle(pos=[self.x, self.y - 20], size=[self.width, 20], size_hint=[None, None]))
            self.background_color = [.3, .3, .3, 3]

    def on_touch_down(self, touch):
        super(CustomTabHeader, self).on_touch_down(touch)
        print('=' * 20)
        print('called for', self.text, '\nstate:', self.state, '\ntouch data:', touch)
        self.canvas.before.clear()
        if self.state == 'normal':
            self.background_color = [.5, .5, .5, 1]
            self.canvas.before.clear()
        else:
            self.canvas.before.add(Color(rgba=[.3, .3, .3, 1]))
            self.canvas.before.add(Rectangle(pos=[self.x, self.y - 20], size=[self.width, 20], size_hint=[None, None]))
            self.background_color = [.3, .3, .3, 3]


class DefaultPopupLayout(relativelayout.RelativeLayout):
    def __init__(self, **kwargs):
        super(DefaultPopupLayout, self).__init__(**kwargs)
        self.cancel_bttn = button.Button(pos=[15, 5], size=[50, 30], text='cancel', background_color=[.6, .1, .1, 1],
                                         color=[.4, .05, .05, 1], size_hint=[None, None], background_normal='')
        self.add_bttn = button.Button(pos=[305, 5], size=[50, 30], text='add', background_color=[.1, .6, .1, 1],
                                      color=[.05, .4, .05, 1], size_hint=[None, None], background_normal='')
        self.add_widget(self.cancel_bttn)
        self.add_widget(self.add_bttn)
        self.popup = None

    def try_dismiss(self):
        print('.')
        if self.popup:
            self.popup.dismiss()
            self.popup = None
            return True
        else:
            return False


class BoolButton(togglebutton.ToggleButton):
    def __init__(self, start_value=True, **kwargs):
        kwargs['on_press'] = self.change_state
        kwargs['text'] = str(start_value)
        kwargs['background_down'] = 'atlas://data/images/defaulttheme/button'
        super(BoolButton, self).__init__(**kwargs)
        self.value = start_value
        if not self.value:
            self.state = 'down'

    def change_state(self, *args):
        self.value = not self.value
        self.text = str(self.value)


class ColorSlider(slider.Slider):
    def on_touch_move(self, touch):
        super(ColorSlider, self).on_touch_move(touch)
        self.parent.update_labels()


class ColorChooseLayout(relativelayout.RelativeLayout):
    def __init__(self, output, default=None, **kwargs):
        if not default:
            default = [0, 0, 0]
        self.output = output
        super(ColorChooseLayout, self).__init__(**kwargs)
        self.r_slider = ColorSlider(pos=[5, 100], min=0, max=255, size=[100, 30], size_hint=[None, None],
                                    value_track_color=[1, 0, 0, 1], value_track=True, value=default[0] * 255)
        self.add_widget(self.r_slider)
        self.g_slider = ColorSlider(pos=[5, 60], min=0, max=255, size=[100, 30], size_hint=[None, None],
                                    value_track_color=[0, 1, 0, 1], value_track=True, value=default[1] * 255)
        self.add_widget(self.g_slider)
        self.b_slider = ColorSlider(pos=[5, 20], min=0, max=255, size=[100, 30], size_hint=[None, None],
                                    value_track_color=[0, 0, 1, 1], value_track=True, value=default[2] * 255)
        self.add_widget(self.b_slider)
        self.r_label = label.Label(text=str(int(default[0] * 255)), pos=[110, 100],
                                   size=[30, 30], size_hint=[None, None])
        self.add_widget(self.r_label)
        self.g_label = label.Label(text=str(int(default[1] * 255)), pos=[110, 60],
                                   size=[30, 30], size_hint=[None, None])
        self.add_widget(self.g_label)
        self.b_label = label.Label(text=str(int(default[2] * 255)), pos=[110, 20],
                                   size=[30, 30], size_hint=[None, None])
        self.add_widget(self.b_label)
        self.color = Color(rgb=default)
        self.canvas.add(self.color)
        self.sample = Rectangle(pos=[145, 145], size=[30, 30], size_hint=[None, None])
        self.canvas.add(self.sample)

    def update_labels(self):
        self.r_label.text = str(int(self.r_slider.value))
        self.g_label.text = str(int(self.g_slider.value))
        self.b_label.text = str(int(self.b_slider.value))
        self.canvas.remove(self.color)
        self.canvas.remove(self.sample)
        self.color = Color(rgb=[self.r_slider.value / 255, self.g_slider.value / 255, self.b_slider.value / 255])
        self.canvas.add(self.color)
        self.sample = Rectangle(pos=[145, 145], size=[30, 30], size_hint=[None, None])
        self.canvas.add(self.sample)
        self.output(ColorChooseLayout.format_color(self.r_label.text, self.g_label.text, self.b_label.text))

    @staticmethod
    def format_color(r, g, b):
        score = str(hex(int(r))).replace('0x', '')
        if len(score) == 1:
            score = '0' + score
        score += str(hex(int(g))).replace('0x', '')
        if len(score) == 3:
            score = score[:2] + '0' + score[2:]
        score += str(hex(int(b))).replace('0x', '')
        if len(score) == 5:
            score = score[:4] + '0' + score[4:]
        return score


class EditValueLayout(relativelayout.RelativeLayout):
    def __init__(self, save_to, call_to_destroy=None, **kwargs):
        self.save_to = save_to
        self.destroyer = call_to_destroy
        super(EditValueLayout, self).__init__(**kwargs)

    def bind(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class EditStringValueLayout(EditValueLayout):
    def __init__(self, **kwargs):
        super(EditStringValueLayout, self).__init__(**kwargs)
        self.value_entry = textinput.TextInput(pos=[35, 10], size=[100, 30], multiline=False, size_hint=[None, None])
        self.value_entry.bind(on_text_validate=lambda *x: self.save_to(self.value_entry.text))
        self.add_widget(self.value_entry)


class EditBoolValueLayout(EditValueLayout):
    def __init__(self, base_value=True, **kwargs):
        super(EditBoolValueLayout, self).__init__(**kwargs)
        self.value_bttn = BoolButton(pos=[20, 10], size=[40, 30], size_hint=[None, None], start_value=base_value)
        self.save_bttn = button.Button(pos=[120, 10], size=[40, 30], size_hint=[None, None], text='Save', on_press=
                                       lambda *x: multiple_executor(lambda: self.save_to(self.value_bttn.value),
                                                                 lambda: self.destroyer()))
        self.add_widget(self.value_bttn)
        self.add_widget(self.save_bttn)


class EditNumberValueLayout(EditStringValueLayout):
    def __init__(self, **kwargs):
        super(EditNumberValueLayout, self).__init__(**kwargs)
        self.remove_widget(self.value_entry)
        self.value_entry = textinput.TextInput(pos=[35, 10], size=[100, 30], multiline=False, size_hint=[None, None],
                                               on_text_validate=self.validate_input)
        self.add_widget(self.value_entry)

    def validate_input(self, *args):
        value = self.value_entry.text
        try:
            value = float(value)
        except ValueError:
            print('value is not a number')
            return
        if value in (float('inf'), float('nan')):
            print('value is not a valid number')
            return
        else:
            print('!')
            self.save_to(value)
            self.destroyer()


class SettingLabel(relativelayout.RelativeLayout):
    def __init__(self, value, name, key, call_to_update_hitboxes, background_col=None, **kwargs):
        self.call_to_update_hitboxes = call_to_update_hitboxes
        self.name = name
        self.value = value
        self.key = key
        super(SettingLabel, self).__init__(**kwargs)
        if background_col:
            self.canvas.before.add(Color(rgb=background_col))
            self.canvas.before.add(Rectangle(size=self.size, pos=self.pos))
        self.name_label = label.Label(text=self.name, pos=[2, 2], size=[180, 30], size_hint=[None, None])
        self.value_label = label.Label(text=str(self.value.value), pos=[182, 2], size=[100, 30], size_hint=[None, None])
        self.edit_bttn = button.Button(size=[30, 30], pos=[324, 3], on_press=self.edit_value, size_hint=[None, None],
                                       background_normal='images\\edit_icon.png',
                                       background_down='images\\edit_icon.png')
        self.add_widget(self.name_label)
        self.add_widget(self.value_label)
        self.add_widget(self.edit_bttn)
        self.popup = None

    def edit_value(self, *args):
        self.call_to_update_hitboxes()

    def close_popup(self):
        if self.popup:
            if hasattr(self.popup.content, 'try_dismiss'):
                self.popup.content.try_dismiss()
            else:
                self.popup.dismiss()
        self.parent.parent.parent.parent.parent.popup = None


class NumericSettingLabel(SettingLabel):
    def edit_value(self, *args):
        self.popup = popup.Popup(title='insert new value', content=EditNumberValueLayout(save_to=self.change),
                                 size=[200, 100], separator_height=0, size_hint=[None, None], title_align='center',
                                 on_dismiss=lambda x: setattr(self.parent.parent.parent.parent.parent, 'popup', None))
        self.popup.content.bind(destroyer=self.popup.dismiss)
        self.parent.parent.parent.parent.parent.popup = self.popup
        self.popup.open()
        super(NumericSettingLabel, self).edit_value()

    def change(self, new):
        self.value.set(new)
        self.value_label.text = str(new)
        self.parent.change_setting(self.key, self.value.value)


class BooleanSettingLabel(SettingLabel):
    def __init__(self, **kwargs):
        super(BooleanSettingLabel, self).__init__(**kwargs)
        self.value_label.text = str(bool(self.value.value))

    def edit_value(self, *args):
        self.popup = popup.Popup(title='insert new value', content=EditBoolValueLayout(save_to=self.change,
                                                                                       base_value=bool(self.value.value)
                                                                                       ),
                                 size=[200, 100], separator_height=0, size_hint=[None, None], title_align='center',
                                 on_dismiss=lambda x: setattr(self.parent.parent.parent.parent.parent, 'popup', None))
        self.popup.content.bind(destroyer=self.popup.dismiss)
        self.parent.parent.parent.parent.parent.popup = self.popup
        self.popup.open()
        super(BooleanSettingLabel, self).edit_value()

    def change(self, new):
        self.value.set(new=new)
        self.value_label.text = str(new)
        self.parent.change_setting(self.key, self.value.value)


class StringSettingLabel(SettingLabel):
    def edit_value(self, *args):
        self.popup = popup.Popup(title='insert new value', content=EditStringValueLayout(save_to=self.change),
                                 size=[200, 100], separator_height=0, size_hint=[None, None], title_align='center',
                                 on_dismiss=lambda x: setattr(self.parent.parent.parent.parent.parent, 'popup', None))
        self.popup.content.bind(destroyer=self.popup.dismiss)
        self.parent.parent.parent.parent.parent.popup = self.popup
        self.popup.open()
        super(StringSettingLabel, self).edit_value()

    def change(self, new):
        self.value.set(new=new)
        self.value_label.text = str(new)
        self.parent.change_setting(self.key, self.value.value)


class ColorSettingLabel(SettingLabel):
    def __init__(self, **kwargs):
        super(ColorSettingLabel, self).__init__(**kwargs)
        self.draw_color(first=True)
        self.value_label.text = values._ColorConversions.kivy_format_to_hex_string(*self.value.value.rgb())

    def draw_color(self, first=False):
        self.canvas.before.remove_group('indicator')
        self.canvas.before.add(Color(rgb=self.value.value.rgb(), group='indicator'))
        self.canvas.before.add(Rectangle(pos=[284, 3], size=[24, 24], size_hint=[None, None], group='indicator'))

    def edit_value(self, *args):
        self.popup = popup.Popup(title='pick a color', content=ColorChooseLayout(output=self.change,
                                                                                 default=self.value.value.rgb()),
                                 size_hint=[None, None], size=[200, 200], pos=[400, 250], separator_height=0,
                                 title_align='center', on_dismiss=lambda x: setattr(
                self.parent.parent.parent.parent.parent, 'popup', None))
        self.parent.parent.parent.parent.parent.popup = self.popup
        self.popup.open()
        super(ColorSettingLabel, self).edit_value()

    def change(self, new):
        self.value.set(fromhex=new)
        self.value_label.text = values._ColorConversions.kivy_format_to_hex_string(*self.value.value.rgb())
        self.parent.change_setting(self.key, new, mode='color')
        self.draw_color()


class SettingsListLayout(gridlayout.GridLayout):
    def __init__(self, settings_list, save_to, set_group, call_to_update_hitboxes, **kwargs):
        super(SettingsListLayout, self).__init__(**kwargs)
        self.bind(minimum_height=self.setter('height'))
        self.call_to_update_hitboxes = call_to_update_hitboxes
        self.settings_list = settings_list
        self.save_to = save_to
        self.set_group = set_group
        i = 0
        for setting, value in self.settings_list.items():
            if i % 2:
                bgc = [.5, .5, .5]
            else:
                bgc = None
            i += 1
            if isinstance(value.value, values.NumericValue):
                self.add_widget(NumericSettingLabel(value=value, name=value.user_name, size_hint=[None, None],
                                                    size=[390, 30], key=setting, background_col=bgc,
                                                    call_to_update_hitboxes=self.call_to_update_hitboxes))
            elif isinstance(value.value, values.BoolValue):
                self.add_widget(BooleanSettingLabel(value=value, name=value.user_name, size_hint=[None, None],
                                                    size=[390, 30], key=setting, background_col=bgc,
                                                    call_to_update_hitboxes=self.call_to_update_hitboxes))
            elif isinstance(value.value, values.StringValue):
                self.add_widget(StringSettingLabel(value=value, name=value.user_name, size_hint=[None, None],
                                                   size=[390, 30], key=setting, background_col=bgc,
                                                    call_to_update_hitboxes=self.call_to_update_hitboxes))
            elif isinstance(value.value, values.ColorValue):
                self.add_widget(ColorSettingLabel(value=value, name=value.user_name, size_hint=[None, None],
                                                  size=[390, 30], key=setting, background_col=bgc,
                                                    call_to_update_hitboxes=self.call_to_update_hitboxes))

    def change_setting(self, name, value, mode='default'):
        self.save_to(name, value, mode, self.set_group)
        if mode == 'default':
            self.settings_list[name].set(value)
        elif mode == 'color':
            self.settings_list[name].set(fromhex=value)


class SettingsLayout(relativelayout.RelativeLayout):
    def __init__(self, settings, save_to, call_to_destroy, call_to_update_hitboxes, **kwargs):
        self.call_to_update_hitboxes = call_to_update_hitboxes
        self.settings = settings
        self.changed_settings = {'main': {}, 'view': {}}
        self.popup = None
        super(SettingsLayout, self).__init__(**kwargs)
        self.close_bttn = button.Button(pos=[10, 2], size=[70, 30], size_hint=[None, None], text='cancel',
                                        on_press=call_to_destroy)
        self.proceed_bttn = button.Button(pos=[290, 2], size=[70, 30], size_hint=[None, None], text='proceed',
                                          on_press=lambda x: multiple_executor(lambda: save_to(self.changed_settings),
                                                                               call_to_destroy))
        self.panel = tabbedpanel.TabbedPanel(pos=[5, 35], size_hint=[None, None], size=[360, 320], tab_height=20,
                                             do_default_tab=False,
                                             tab_width=100)
        sw1 = scrollview.ScrollView(do_scroll=[False, True], size_hint_y=None, size=[390, 300])
        sw1.add_widget(SettingsListLayout(self.settings['main'],
                                         size_hint_y=None, spacing=10, cols=1, save_to=self.save, set_group='main',
                                                    call_to_update_hitboxes=self.call_to_update_hitboxes))
        sw2 = scrollview.ScrollView(do_scroll=[False, True], size_hint_y=None, size=[390, 300])
        sw2.add_widget(SettingsListLayout(self.settings['view'],
                                          size_hint_y=None, spacing=10, cols=1, save_to=self.save, set_group='view',
                                                    call_to_update_hitboxes=self.call_to_update_hitboxes))
        self.main_tab = CustomTabHeader(text='Main Settings', content=sw1, first=True)
        self.view_tab = CustomTabHeader(text='View', content=sw2)
        self.panel.add_widget(self.main_tab)
        self.panel.add_widget(self.view_tab)
        self.add_widget(self.panel)
        self.add_widget(self.close_bttn)
        self.add_widget(self.proceed_bttn)

    def try_dismiss(self):
        if self.popup:
            self.popup.dismiss()
            self.popup = None
            return True

    def save(self, name, value, mode, group):
        if mode == 'default':
            self.settings[group][name].set(value)
            if name in self.changed_settings[group].keys():
                self.changed_settings[group][name].set(value)
            else:
                self.changed_settings[group][name] = type(self.settings[group][name])\
                        (value=type(self.settings[group][name].value)(value), on_change=lambda: 1+1,
                         user_name=self.settings[group][name].user_name)
        elif mode == 'color':
            self.settings[group][name].set(fromhex=value)
            if name in self.changed_settings[group].keys():
                self.changed_settings[group][name].set(fromhex=value)
            else:
                self.changed_settings[group][name] = type(self.settings[group][name])\
                        (value=type(self.settings[group][name].value)(fromhex=value), on_change=lambda: 1+1,
                         user_name=self.settings[group][name].user_name)


class AddSeriesLayout(DefaultPopupLayout):
    def __init__(self, call_to_add, call_to_destroy, **kwargs):
        self.call_to_add = call_to_add
        self.call_to_destroy = call_to_destroy
        super(AddSeriesLayout, self).__init__(**kwargs)
        self.name_entry = textinput.TextInput(pos=[105, 300], size=[100, 30], size_hint=[None, None], multiline=False)
        self.min_range_entry = textinput.TextInput(pos=[105, 260], size=[100, 30], size_hint=[None, None],
                                                   multiline=False)
        self.max_range_entry = textinput.TextInput(pos=[105, 220], size=[100, 30], size_hint=[None, None],
                                                   multiline=False)
        self.formula_entry = textinput.TextInput(pos=[105, 140], size=[250, 30], size_hint=[None, None], multiline=False
                                                 )
        self.color_entry1 = textinput.TextInput(pos=[105, 100], size=[150, 30], size_hint=[None, None], multiline=False)
        self.color_entry2 = textinput.TextInput(pos=[105, 60], size=[150, 30], size_hint=[None, None], multiline=False)
        self.range_step_entry = textinput.TextInput(pos=[105, 180], size=[100, 30], size_hint=[None, None],
                                                    multiline=False)
        self.add_bttn.bind(on_press=self.accept)
        self.add_widget(self.name_entry)
        self.add_widget(self.min_range_entry)
        self.add_widget(self.max_range_entry)
        self.add_widget(self.formula_entry)
        self.add_widget(self.color_entry1)
        self.add_widget(self.color_entry2)
        self.add_widget(self.range_step_entry)
        self.add_widget(label.Label(pos=[15, 260], size=[70, 30], size_hint=[None, None], text='Range Min:'))
        self.add_widget(label.Label(pos=[10, 300], size=[85, 30], size_hint=[None, None], text='Variable Name:'))
        self.add_widget(label.Label(pos=[15, 220], size=[70, 30], size_hint=[None, None], text='Range Max:'))
        self.add_widget(label.Label(pos=[15, 180], size=[80, 30], size_hint=[None, None], text='range step:'))
        self.add_widget(label.Label(pos=[15, 140], size=[70, 30], size_hint=[None, None], text='Formula:'))
        self.add_widget(label.Label(pos=[15, 100], size=[80, 30], size_hint=[None, None], text='Color 1:'))
        self.add_widget(label.Label(pos=[15, 60], size=[80, 30], size_hint=[None, None], text='Color 2:'))
        self.add_widget(button.Button(pos=[255, 100], size=[25, 25], size_hint=[None, None],
                                      background_color=[1, 1, 1, 1], on_press=lambda x: self.pick_color(1),
                                      background_normal='images\\pick_icon.png',
                                      background_down='images\\pick_icon.png'))
        self.add_widget(button.Button(pos=[255, 60], size=[25, 25], size_hint=[None, None],
                                      background_color=[1, 1, 1, 1], on_press=lambda x: self.pick_color(2),
                                      background_normal='images\\pick_icon.png',
                                      background_down='images\\pick_icon.png'))

    def edit_color1(self, val):
        self.color_entry1.text = val

    def edit_color2(self, val):
        self.color_entry2.text = val

    def pick_color(self, n):
        if n == 1:
            self.popup = popup.Popup(title='pick a color', content=ColorChooseLayout(output=self.edit_color1),
                                     size_hint=[None, None], size=[200, 200], pos=[400, 250], separator_height=0,
                                     title_align='center', on_dismiss=lambda x: setattr(self, 'popup', None))
            self.popup.open()
        else:
            self.popup = popup.Popup(title='pick a color', content=ColorChooseLayout(output=self.edit_color2),
                                     size_hint=[None, None], size=[200, 200], pos=[400, 250], separator_height=0,
                                     title_align='center', on_dismiss=lambda x: setattr(self, 'popup', None))
            self.popup.open()

    def is_input_correct(self):
        try:
            float(self.name_entry.text)
        except ValueError:
            if self.name_entry.text in ('x', 'pi', 'e', 'tau'):
                return False
        else:
            return False
        try:
            float(self.min_range_entry.text)
            float(self.max_range_entry.text)
            float(self.range_step_entry.text)
        except ValueError:
            return False
        if not Fg.test_formula(self.formula_entry.text.replace(self.name_entry.text, self.min_range_entry.text)):
            return False
        if len(self.color_entry1.text) == 6:
            for char in self.color_entry1.text:
                if char.lower() not in '0123456789abcdef':
                    return False
        else:
            return False
        if len(self.color_entry2.text) == 6:
            for char in self.color_entry2.text:
                if char.lower() not in '0123456789abcdef':
                    return False
        else:
            return False
        return True

    def accept(self, *args):
        if self.is_input_correct():
            c1 = MainLayout.hex_to_kivy_color(self.color_entry1.text)
            c2 = MainLayout.hex_to_kivy_color(self.color_entry2.text)
            dr = c2[0] - c1[0]
            dg = c2[1] - c1[1]
            db = c2[2] - c1[2]
            x1 = float(self.min_range_entry.text)
            x2 = float(self.max_range_entry.text)
            dx = abs(x1 - x2)
            step = float(self.range_step_entry.text)
            for i in arange(x1, x2, step):
                self.call_to_add(formula=self.formula_entry.text.replace(self.name_entry.text, str(i)),
                                 color=[c1[0] + dr * i * abs(step) / dx, c1[1] + dg * i * abs(step) / dx,
                                        c1[2] + db * i * abs(step) / dx, 1])
            self.call_to_destroy()


class AddGuiLayout(DefaultPopupLayout):
    def __init__(self, **kwargs):
        super(AddGuiLayout, self).__init__(**kwargs)
        self.standard_color = '000000'
        self.add_bttn.disabled = True
        self.add_widget(label.Label(text='formula:', pos=[7, 300], size=[45, 25], size_hint=[None, None],
                                    color=[.7, .7, .7, 1]))
        self.formula_entry = textinput.TextInput(pos=[57, 300], size=[285, 25], multiline=False, size_hint=[None, None],
                                                 font_size=12)
        self.formula_entry.bind(text=self.update_bttn)
        self.add_widget(self.formula_entry)
        self.add_widget(label.Label(text='color (rgb):', pos=[7, 200], size=[65, 25], size_hint=[None, None],
                                    color=[.7, .7, .7, 1]))
        self.color_entry = textinput.TextInput(pos=[82, 200], size=[235, 25], multiline=False, size_hint=[None, None],
                                               font_size=12)
        self.color_entry.bind(text=self.update_bttn)
        self.add_widget(self.color_entry)
        self.pick_color_button = button.Button(pos=[320, 200], size=[25, 25], size_hint=[None, None],
                                               background_color=[1, 1, 1, 1], on_press=self.pick_color,
                                               background_normal='images\\pick_icon.png',
                                               background_down='images\\pick_icon.png')
        self.add_widget(self.pick_color_button)

    def update_bttn(self, *args):
        if self.formula_entry.text and self.color_entry.text:
            self.add_bttn.disabled = False
        else:
            self.add_bttn.disabled = True

    def pick_color(self, *args):
        if len(self.color_entry.text) == 6:
            try:
                int(self.color_entry.text, 16)
            except Exception:
                default = values._ColorConversions.hex_string_to_kivy_format(self.standard_color)
            else:
                default = values._ColorConversions.hex_string_to_kivy_format(self.color_entry.text)
        else:
            default = values._ColorConversions.hex_string_to_kivy_format(self.standard_color)
        self.popup = popup.Popup(title='pick a color', content=ColorChooseLayout(output=self.set_color_,
                                                                                 default=default),
                                 size_hint=[None, None], size=[200, 200], pos=[400, 250], separator_height=0,
                                 title_align='center', on_dismiss=lambda x: setattr(self, 'popup', None))
        self.popup.open()

    def set_color_(self, val):
        self.color_entry.text = val


class EditGuiLayout(AddGuiLayout):
    def __init__(self, formula, color, **kwargs):
        super(EditGuiLayout, self).__init__(**kwargs)
        self.standard_color = color
        self.add_bttn.text = 'modify'
        self.add_bttn.disabled = False
        self.color_entry.text = color
        self.formula_entry.text = formula


class DebugLayout(relativelayout.RelativeLayout):
    def __init__(self, data, **kwargs):
        super(DebugLayout, self).__init__(**kwargs)
        self.data = data
        self.last_render_label = label.Label(
            pos=[10, 10], size=[110, 20], text= 'last frame rendered in: ' + str(round(data['last_render'], 3)) + ' s')
        self.average_render_time_label = label.Label(
            pos=[10, 35], size=[110, 20], text='average render time: ' +  str(round(data['average_render'], 3)) + ' s')
        self.scale_label = label.Label(pos=[10, 60], size=[110, 20], text='scale: ' + str(round(data['scale'], 1)))
        self.position_label = label.Label(
            pos=[10, 85], size=[110, 20], text='x: ' + str(round(data['position'][0], 6)) +
                                               '    y: ' + str(round(data['position'][1], 6)))
        self.canvas.before.add(Color(rgba=[0, 0, 0, .3]))
        self.canvas.before.add(RoundedRectangle(pos=[0, 50], size=self.size))
        self.add_widget(self.last_render_label)
        self.add_widget(self.average_render_time_label)
        self.add_widget(self.scale_label)
        self.add_widget(self.position_label)

    def update(self, new_data):
        self.data.update(new_data)
        self.last_render_label.text = 'last frame rendered in: ' + str(round(self.data['last_render'], 3)) + ' s'
        self.average_render_time_label.text = 'average render time: ' + str(round(self.data['average_render'], 3)) +\
                                              ' s'
        self.scale_label.text = 'scale: ' + str(round(self.data['scale'], 1))
        self.position_label.text = 'x: ' + str(round(self.data['position'][0], 6)) +\
                                   '    y: ' + str(round(self.data['position'][1], 6))


class Frame(widget.Widget):
    def __init__(self, frame_size, color1, color2, item, before_instructions=None, **kwargs):
        self.item = item
        self.frame_size, self.color1, self.color2 = frame_size, color1, color2
        super(Frame, self).__init__(**kwargs)
        self.add_widget(self.item)
        if not before_instructions:
            self.draw_before = []
        else:
            self.draw_before = before_instructions
        self.draw(first=True)

    def draw(self, first=False):
        print('drawing')
        if not first:
            self.canvas.before.clear()
        with self.canvas.before:
            Color(rgb=self.color1)
            Rectangle(pos=self.pos, size=self.size)
            Color(rgb=self.color2)
            Rectangle(pos=[self.x + self.frame_size, self.y + self.frame_size],
                      size=[self.width - 2 * self.frame_size, self.height - 2 * self.frame_size])
        for cls, kwargs in self.draw_before:
            self.canvas.before.add(cls(**kwargs))


class FLabel(relativelayout.RelativeLayout):
    def __init__(self, function, **kwargs):
        self.function = function
        super(FLabel, self).__init__(**kwargs)
        self.title = label.Label(pos=[5, 50], size=[115, 20], text=self.function.formula, halign='left',
                                 color=self.function.color, size_hint_y=None)
        self.title.bind(size=self.title.setter('text_size'))
        self.add_widget(self.title)
        self.del_bttn = button.Button(pos=[120, 50], size=[30, 20], size_hint=[None, None],
                                      background_color=[.8, .2, .2, 1], text='del', color=[.6, .1, .1, 1],
                                      on_press=lambda x: self.parent.delete_function(self))
        self.add_widget(self.del_bttn)
        self.edit_bttn = button.Button(pos=[155, 50], size=[30, 20], size_hint=[None, None], text='edit',
                                       background_color=[.2, .8, .2, 2], color=[.1, .6, .1, 1],
                                       on_press=lambda x: self.parent.parent.parent.parent.edit_gui(self.function.id))
        self.hide_bttn = togglebutton.ToggleButton(pos=[120, 25], size=[65, 20], text='hide', size_hint=[None, None],
                                                   background_color=[.6, .6, .1, 1], color=[.4, .4, .05, 1],
                                                   background_down='', background_normal='')
        self.hide_bttn.bind(on_press=lambda x: multiple_executor(lambda: self.parent.parent.parent.parent.f.
                                                                 hide(self.function.id) if self.hide_bttn.
                                                                 state == 'down' else self.parent.
                                                                 parent.parent.parent.f.unhide(self.function.id),
                                                                 lambda: exec('b.background_color=[.6, .6, .1, 1]',
                                                                              {'b': self.hide_bttn}) if self.hide_bttn.
                                                                 state == 'normal' else exec
                                                                 ('b.background_color=[.3, .3, 0, 1]',
                                                                  {'b': self.hide_bttn})))
        self.add_widget(self.hide_bttn)
        self.add_widget(self.edit_bttn)
        self.update_canvas(first=True)

    def update_canvas(self, first=False):
        if not first:
            self.canvas.before.clear()
        with self.canvas.before:
            Color(rgb=[.1, .1, .1])
            Rectangle(pos=[self.x, self.y], size=[self.width, self.height])


class FLayout(gridlayout.GridLayout):
    def __init__(self, fdict, **kwargs):
        kwargs['size_hint_y'] = None
        kwargs['spacing'] = 10
        kwargs['cols'] = 1
        self.fdict = fdict
        super(FLayout, self).__init__(**kwargs)
        self.bind(minimum_height=self.setter('height'))
        self.update_list()

    def update_list(self):
        self.clear_widgets()
        for f in self.fdict.values():
            self.add_widget(FLabel(function=f, size_hint_y=None, size=[190, 75]))

    def delete_function(self, lab):
        label_id = lab.function.id
        del self.fdict[label_id]
        self.remove_widget(lab)
        self.parent.parent.parent.f.remove_graph(label_id)

    def add_function(self, f):
        self.fdict[f.id] = f
        self.add_widget(FLabel(function=f, size_hint_y=None, size=[190, 75]))

    def edit_function(self, label_id, formula=None, color=None):
        print('called "edit_function" in Flayout with args: ', label_id, formula, color)
        if formula:
            self.fdict[label_id].change_formula(formula)
        if color:
            self.fdict[label_id].change_color(color)
        self.update_list()


class FScrollView(scrollview.ScrollView):
    def __init__(self, child, **kwargs):
        self.child = child
        super(FScrollView, self).__init__(**kwargs)
        self.add_widget(self.child)


class FuncWidget(widget.Widget):

    def __init__(self, axis_color=None, show_grid=False, show_axis_names=False, x_name='', y_name='', **kwargs):
        super(FuncWidget, self).__init__()
        self.last_render = 0.0
        self.avrg_render_time = 0.0
        self.times_rendered = 0
        self.hidden = set()
        self.navigation_lines = show_grid
        self.show_axis_names = show_axis_names
        self.locked = False
        self.cam_pos = [0, 0]
        self.scale = -2.0
        self.width = kwargs['width']
        self.height = kwargs['height']
        self.pos = kwargs['pos']
        self.x_name = label.Label(pos=[self.x + self.width - 90, self.center_y + 10], size=[80, 30], text=x_name,
                                  color=[0, 0, 0, 1])
        self.y_name = label.Label(pos=[self.center_x + 20, self.y + self.height - 40], size=[80, 30], text=y_name,
                                  color=[0, 0, 0, 1])
        if self.show_axis_names:
            self.add_widget(self.x_name)
            self.add_widget(self.y_name)
        if not axis_color:
            self.c = [.5, .5, .5, 1]
        else:
            self.c = axis_color
        if 'frame_size' in kwargs.keys():
            self.frame_size = kwargs['frame_size']
        else:
            self.frame_size = 5
        try:
            self.f_obj = kwargs['obj']
        except KeyError:
            raise Exception('keyword argument "obj" is not set')
        self.tpl = None
        self.draw(start=True)

    def draw_graph_(self, flist='default'):
        mode = ['fast', 'rd']
        if flist == 'default':
            tfl = self.f_obj
        else:
            tfl = flist
        for f in tfl.values():
            if f.id not in self.hidden:
                prev = None
                self.fc = f.color[:]
                self.canvas.before.add(Color(rgba=self.fc, group=str(f.id)))
                self.tpl = []
                for point, value in f.generate(start=round(self.cam_pos[0] - (self.width / 2 - self.frame_size)
                                                           * 10
                                                           ** self.scale, -round(self.scale)),
                                        stop=round(self.cam_pos[0] + (self.width / 2 - self.frame_size)
                                                          * 10
                                                          ** self.scale, -round(self.scale)),
                                        step=10 ** self.scale).items():
                    if isinstance(value, float) or isinstance(value, int):
                        point = {'y': value / 10 ** self.scale, 'x': round(point / 10 ** self.scale)}
                        if prev:
                            if -(self.height / 2 - self.frame_size) <= point['y'] - self.cam_pos[1] / 10 \
                                    ** self.scale <= (self.height / 2 - self.frame_size) and \
                                    -(self.height / 2 - self.frame_size) <= prev['y'] \
                                    - self.cam_pos[1] / 10 ** self.scale <= (self.height / 2 - self.frame_size):
                                if abs(round(point['y'] + self.center_y - self.cam_pos[1] / 10 ** self.scale) -
                                       round(prev['y'] + self.center_y - self.cam_pos[1] / 10 ** self.scale)) > 1:
                                    if True:
                                        self.canvas.before.add(Line(points=[point['x'] + self.center_x - self.cam_pos[0] / 10
                                                                     ** self.scale,
                                                                     round(point['y'] + self.center_y -
                                                                           self.cam_pos[1] /
                                                                           10 ** self.scale), prev['x'] + self.center_x
                                                                     - self.cam_pos[0] / 10 ** self.scale,
                                                                     round(prev['y'] + self.center_y - self.cam_pos[1] /
                                                                           10 ** self.scale)],
                                                             width=1.2, group=str(f.id)))
                                    else:
                                        for pt in line([point['x'] + self.center_x - self.cam_pos[0] / 10
                                                                     ** self.scale,
                                                                     round(point['y'] + self.center_y -
                                                                           self.cam_pos[1] /
                                                                           10 ** self.scale)],
                                                       [prev['x'] + self.center_x
                                                       - self.cam_pos[0] / 10 ** self.scale,
                                                       round(prev['y'] + self.center_y - self.cam_pos[1] /
                                                             10 ** self.scale)]
                                                       ):
                                            self.tpl += pt
                                else:
                                    self.tpl += [point['x'] + self.center_x - self.cam_pos[0] / 10 ** self.scale,
                                                 round(point['y'] + self.center_y - self.cam_pos[1] /
                                                       10 ** self.scale)]
                        prev = point.copy()
                self.canvas.before.add(Point(points=self.tpl, group=str(f.id)))

    def draw_axes_(self):
        with self.canvas.before:
            Color(*self.c)
            n = 10 ** (round(self.scale) + 1)
            if n / 10 ** self.scale > 10:
                for i in arange(round(self.cam_pos[1], int(round_half_up(-self.scale - 1))) - 30 * n,
                                round(self.cam_pos[1], int(round_half_up(-self.scale - 1))) + 30 * n, n):
                    if -(self.height / 2 - self.frame_size - 20) < round(i - self.cam_pos[1],
                                                                         round(-self.scale - 1)) / 10 ** self.scale \
                            < (self.height / 2 - self.frame_size - 20) and (i / n) % 10:
                        num = round(i, round(-self.scale - 1))
                        if abs(num) >= 10 ** 5 and num // 10 ** 5 * 10 ** 5 == num:
                            num = sci_format(num, 0)
                        temp_label = tl(text=str(num), font_size=10, color=self.c)
                        temp_label.refresh()
                        t = temp_label.texture
                        Rectangle(pos=[self.center_x + 6, self.center_y +
                                       round((i - self.cam_pos[1]) / 10 ** self.scale)], texture=t, size=t.size)
                        Line(points=[self.center_x - 5, self.center_y + round((i - self.cam_pos[1]) /
                                                                              10 ** self.scale), self.center_x + 5,
                                     self.center_y + round((i - self.cam_pos[1]) / 10 ** self.scale)], width=1.1)
                        if self.navigation_lines:
                            Line(points=[self.pos[0], self.center_y + round((i - self.cam_pos[1]) / 10 ** self.scale),
                                         self.pos[0] + self.width, self.center_y + round((i - self.cam_pos[1]) /
                                                                                         10 ** self.scale)], width=0.7,
                                 group='navi_lines')
            n = 10 ** (round(self.scale) + 2)
            if n / 10 ** self.scale < (self.height / 2 - self.frame_size - 20):
                for i in arange(round(self.cam_pos[1], round(-self.scale - 2)) - 30 * n,
                                round(self.cam_pos[1], round(-self.scale - 2)) + 30 * n, n):
                    if -(self.height / 2 - self.frame_size - 20) < round((i - self.cam_pos[1]) / 10 ** self.scale) \
                            < (self.height / 2 - self.frame_size - 20):
                        num = round(i, round(-self.scale - 1))
                        if abs(num) >= 10 ** 5 and num // 10 ** 5 * 10 ** 5 == num:
                            num = sci_format(num, 0)
                        temp_label = tl(text=str(num), font_size=20, color=self.c)
                        temp_label.refresh()
                        t = temp_label.texture
                        Rectangle(pos=[self.center_x + 12, self.center_y +
                                       round((i - self.cam_pos[1]) / 10 ** self.scale)],
                                  texture=t, size=t.size)
                        Line(points=[self.center_x - 7, self.center_y +
                                     round((i - self.cam_pos[1]) / 10 ** self.scale), self.center_x + 7,
                                     self.center_y + round((i - self.cam_pos[1]) / 10 ** self.scale)], width=2)
                        if self.navigation_lines:
                            Line(points=[self.pos[0], self.center_y + round((i - self.cam_pos[1]) / 10 ** self.scale),
                                         self.pos[0] + self.width, self.center_y + round((i - self.cam_pos[1]) /
                                                                                         10 ** self.scale)], width=1.2,
                                 group='navi_lines')
            n = 10 ** (round(self.scale) + 1)
            step = 1
            if 5 * len(str(round(self.cam_pos[0], round(-self.scale - 1)) - 30 * n)) < n / \
                    10 ** self.scale:
                step = 1
            elif 2.5 * len(str(round(self.cam_pos[0], round(-self.scale - 1)) - 30 * n)) < n / \
                    10 ** self.scale:
                step = 2
            elif len(str(round(self.cam_pos[0], round(-self.scale - 1)) - 30 * n)) < n / \
                    10 ** self.scale:
                step = 5
            if n / 10 ** self.scale > (5 / step) * len(str(round(self.cam_pos[0],
                                                                 round(-self.scale - 1)) - 50 * n)):
                for i in arange(round(self.cam_pos[0], int(round_half_up(-self.scale - 2))) - 50 * n,
                                round(self.cam_pos[0], int(round_half_up(-self.scale - 2))) + 50 * n, n * step):
                    if -(self.width / 2 - self.frame_size) < round(i - self.cam_pos[0], round(-self.scale - 1)) / \
                            10 ** self.scale < (self.width / 2 - self.frame_size) and \
                            round(i, round(-self.scale - 1)) % (10 * n) > 1e-10:
                        num = round(i, round(-self.scale - 1))
                        if abs(num) >= 10 ** 5 and num // 10 ** 5 * 10 ** 5 == num:
                            num = sci_format(num, 0)
                        temp_label = tl(text=str(num), font_size=10, color=self.c)
                        temp_label.refresh()
                        t = temp_label.texture
                        Rectangle(pos=[self.center_x + round((i - self.cam_pos[0]) / 10 ** self.scale),
                                       self.center_y + 6], texture=t, size=t.size)
                        Line(points=[self.center_x + round((i - self.cam_pos[0]) / 10 ** self.scale), self.center_y
                                     - 5, self.center_x + round((i - self.cam_pos[0]) / 10 ** self.scale),
                                     self.center_y + 5], width=1.1)
                        if self.navigation_lines:
                            Line(points=[self.center_x + round((i - self.cam_pos[0]) / 10 ** self.scale), self.pos[1],
                                         self.center_x + round((i - self.cam_pos[0]) / 10 ** self.scale), self.pos[1] +
                                         self.height], width=0.7, group='navi_lines')
            n = 10 ** (round(self.scale) + 2)
            if n / 10 ** self.scale < (self.width / 2 - self.frame_size):
                for i in arange(round(self.cam_pos[0], int(-round_half_up(self.scale + 3))) - 30 * n,
                                round(self.cam_pos[0], int(-round_half_up(self.scale + 3))) + 30 * n, n):
                    if -(self.width / 2 - self.frame_size) < round((i - self.cam_pos[0]) / 10 ** self.scale) < \
                            (self.width / 2 - self.frame_size) and i:
                        num = round(i, round(-self.scale - 1))
                        if float(num).is_integer():
                            num = int(num)
                        if abs(num) >= 10 ** 5 and num // 10 ** 5 * 10 ** 5 == num:
                            num = sci_format(num, 0)
                        temp_label = tl(text=str(num), font_size=20, color=self.c)
                        temp_label.refresh()
                        t = temp_label.texture
                        Rectangle(pos=[self.center_x + round((i - self.cam_pos[0]) / 10 ** self.scale),
                                       self.center_y + 12],
                                  texture=t, size=t.size)
                        Line(points=[self.center_x + round((i - self.cam_pos[0]) / 10 ** self.scale),
                                     self.center_y - 7,
                                     self.center_x + round((i - self.cam_pos[0]) / 10 ** self.scale),
                                     self.center_y + 7], width=2)

                        if self.navigation_lines:
                            Line(points=[self.center_x + round((i - self.cam_pos[0]) / 10 ** self.scale), self.pos[1],
                                         self.center_x + round((i - self.cam_pos[0]) / 10 ** self.scale), self.pos[1] +
                                         self.height], width=1.2, group='navi_lines')

    def draw(self,  *args, start=False, **kwargs):
        s = time.time()
        with self.canvas.before:
            self.canvas.before.clear()
        self.draw_axes_()
        self.draw_graph_()
        self.avrg_render_time = (self.avrg_render_time * self.times_rendered + time.time() - s) / \
                                (self.times_rendered + 1)
        self.times_rendered += 1
        self.last_render = time.time() - s
        if not start:
            self.parent.parent.debug_layout.update({
                'last_render': self.last_render, 'average_render': self.avrg_render_time})
        print(time.time() - s, '%s')
        print(self.avrg_render_time, '%s')

    def resize(self, dif):
        self.scale -= dif
        self.parent.parent.debug_layout.update({'scale': self.scale})
        self.draw()

    def move_camera(self, dx=0.0, dy=0.0, move_to=None):
        if move_to:
            try:
                move_to = [float(move_to[0]), float(move_to[1])]
            except Exception as e:
                print('App>MainLayout>FuncWidget: Error when changing position of camera.\nError description:\t', e)
        try:
            dx, dy = float(dx), float(dy)
        except Exception as e:
            print('App>MainLayout>FuncWidget: Error when changing position of camera.\nError description:\t', e)
        try:
            if not move_to:
                self.cam_pos = [self.cam_pos[0] + dx * 10 ** self.scale, self.cam_pos[1] + dy * 10 ** self.scale]
            elif isinstance(move_to[0], float) and isinstance(move_to[1], float):
                self.cam_pos = move_to
        except Exception as e:
            print('App>MainLayout>FuncWidget: Error when changing position of camera.\nError description:\t', e)
        self.parent.parent.debug_layout.update({'position': self.cam_pos})
        self.draw()

    def generate_id(self):
        new_id = None
        prop = 0
        while new_id is None:
            if prop not in self.f_obj.keys():
                new_id = prop
            else:
                prop += 1
        return new_id

    def hide(self, fid):
        self.hidden.add(fid)
        self.draw()

    def unhide(self, fid):
        if fid in self.hidden:
            self.hidden.remove(fid)
            self.draw_graph_({fid: self.f_obj[fid]})

    def remove_graph(self, fid):
        self.canvas.remove_group(str(fid))

    def update_color(self, new):
        self.c = new

    def set_navigation_lines(self, state):
        print(state, self.navigation_lines)
        if self.navigation_lines and not state:
            self.canvas.remove_group('navi_lines')
            self.navigation_lines = False

        if not self.navigation_lines and state:
            self.navigation_lines = True
            self.draw()
            
    def set_axis_names(self, state=None, x_name=None, y_name=None):
        print(state, self.show_axis_names)
        if x_name != None:
            self.x_name.text = x_name
        if y_name != None:
            self.y_name.text = y_name
        if state and not self.show_axis_names:
            print(self.x_name.text, self.x_name.pos)
            self.add_widget(self.x_name)
            self.add_widget(self.y_name)
            self.show_axis_names = True
        elif state == False and self.show_axis_names:
            self.remove_widget(self.x_name)
            self.remove_widget(self.y_name)
            self.show_axis_names = False


class MainLayout(widget.Widget):
    def __init__(self, settings, **kwargs):
        self.settings, self.default_settings = settings
        self.settings_pattern = deepcopy(self.settings)
        self.settings_old = deepcopy(self.settings)
        self.activate_settings()
        self.popup = None
        self.has_active_entry = False
        self.entries_hitboxes = []
        super(MainLayout, self).__init__(**kwargs)
        self.f = FuncWidget(pos=[200, 0], obj={}, height=625, width=800, axis_color=self.settings['view']['axis_color'].
                            value.rgb() + [1], show_grid=self.settings['view']['show_grid'].value.value, x_name=
                            self.settings['view']['x_axis_name'].value.value, y_name=self.settings['view']
        ['y_axis_name'].value.value, show_axis_names=self.settings['view']['show_axis_names'].value.value)
        self.fframe = Frame(5, [.5, .5, .5], self.settings['view']['background_color'].value.rgb(), item=self.f,
                            pos=[200, 1], size=[800, 625],
                            before_instructions=[(Color, {'rgb': self.settings['view']['axis_color'].value.rgb()}),
                                                 (Line, {
                                                     'points': [self.f.pos[0] + self.f.frame_size + 3, self.f.center_y,
                                                                self.f.pos[0] + self.f.width
                                                                - self.f.frame_size - 3, self.f.center_y], 'width': 2}),
                                                 (Triangle, {
                                                     'points': [self.f.pos[0] + self.f.width - self.f.frame_size + 2,
                                                                self.f.center_y,
                                                                self.f.pos[0] + self.f.width - self.f.frame_size - 25,
                                                                self.f.center_y - 12,
                                                                self.f.pos[0] + self.f.width - self.f.frame_size - 25,
                                                                self.f.center_y + 12]}),
                                                 (Line, {
                                                     'points': [self.f.center_x, self.f.pos[1] + self.f.frame_size + 3,
                                                                self.f.center_x,
                                                                self.f.pos[1] + self.f.height - 3 - self.f.frame_size],
                                                     'width': 2}),
                                                 (Triangle, {'points': [self.f.center_x, self.f.pos[
                                                     1] + self.f.height - self.f.frame_size + 2,
                                                                        self.f.center_x - 12, self.f.pos[
                                                                            1] + self.f.height - self.f.frame_size - 25,
                                                                        self.f.center_x + 12, self.f.pos[
                                                                            1] + self.f.height - self.f.frame_size - 25]
                                                             })]
                            )
        self.add_widget(self.fframe)
        self.add_bttn = button.Button(pos=[3, 664], size=[80, 33], background_color=[.3, .3, .3, 1], text='Add',
                                      on_press=self.add_gui)
        self.add_widget(self.add_bttn)
        self.add_series_bttn = button.Button(pos=[3, 628], size=[80, 33], background_color=[.3, .3, .3, 1],
                                             text='Add series', on_press=self.add_series)
        self.add_widget(self.add_series_bttn)
        self.settings_bttn = button.Button(pos=[86, 664], size=[80, 33], background_color=[.3, .3, .3, 1],
                                           text='Settings', on_press=self.settings_popup)
        self.add_widget(self.settings_bttn)
        self.view_bttn = button.Button(pos=[86, 628], size=[80, 33], background_color=[.3, .3, .3, 1], text='View')
        self.add_widget(self.view_bttn)
        self.add_widget(label.Label(text='go to:', pos=[870, 670], height=30))
        self.navigation_entry = textinput.TextInput(pos=[870, 640], height=30,
                                                    on_text_validate=lambda x: multiple_executor(
                                                        lambda: self.f.move_camera(move_to=self.read_input(
                                                            entry=self.navigation_entry, func=lambda n: [
                                                                n.split(', ')[0], n.split(', ')[1]])),
                                                        self._set_keyboard), multiline=False)
        self.add_widget(self.navigation_entry)
        self.sw = FScrollView(size_hint=[1, None], size=[195, 615], child=FLayout(fdict=self.f.f_obj), pos=[5, 5])
        self.debug_layout = DebugLayout({'last_render': 0, 'average_render': 0, 'position': self.f.cam_pos,
                                         'scale': self.f.scale}, pos=[700, 400], size=[250, 170])
        if self.settings['view']['debug_data'].value.value:
            self.add_widget(self.debug_layout)
        self.add_widget(Frame(5, [.5, .5, .5], [0, 0, 0], self.sw, pos=[0, 0], size=[205, 625]))
        self._keyboard = Window.request_keyboard(self._kc, self)
        self._keyboard.bind(on_key_down=self._okd)
        self.draw(first=True)
        self.search_for_children(self, textinput.TextInput, first=True)

    def _set_keyboard(self):
        self._keyboard = Window.request_keyboard(self._kc, self)
        self._keyboard.bind(on_key_down=self._okd)

    def read_input(self, entry, func, *args, draw=True, **kwargs):
        try:
            score = func(entry.text)
        except Exception as e:
            score = None
        if draw:
            self.f.draw()
        return score

    def _kc(self):
        self._keyboard.unbind(on_key_down=self._okd)
        self._keyboard = None

    def _okd(self, keyboard, keycode, text, modifiers):
        if keycode[0] == 27 and self.popup:
            self.close_popup()
        return True

    def on_touch_up(self, touch):
        super(MainLayout, self).on_touch_down(touch)
        if touch.is_mouse_scrolling and self.f.pos[0] < touch.pos[0] < self.f.pos[0] + self.f.width and \
                self.f.pos[1] < touch.pos[1] < self.f.pos[1] + self.f.height and not self.f.locked:
            if touch.button == 'scrollup':
                self.f.resize(-0.1)
            elif touch.button == 'scrolldown':
                self.f.resize(0.1)

    def on_touch_down(self, touch):
        for entry in self.entries_hitboxes:
            if entry[0][0] <= touch.pos[0] <= entry[0][0] + entry[1][0] and entry[0][1] <= touch.pos[1] <=\
                    entry[0][1] + entry[1][1]:
                break
        else:
            self._set_keyboard()

    def on_touch_move(self, touch):
        if touch.button == 'left' and self.f.pos[0] < touch.pos[0] < self.f.pos[0] + self.f.width and \
                self.f.pos[1] < touch.pos[1] < self.f.pos[1] + self.f.height and not self.f.locked:
            self.f.move_camera(-touch.dx, -touch.dy)

    def draw(self, first=False):
        if not first:
            self.canvas.before.clear()
        with self.canvas.before:
            Color(rgb=[.45, .45, .45])
            Rectangle(pos=[0, 625], size=[500, 75])

    @staticmethod
    def hex_to_kivy_color(string):
        try:
            return [int(string[:2], 16) / 255, int(string[2:4], 16) / 255, int(string[4:], 16) / 255]
        except Exception:
            return [0, 0, 0]

    @staticmethod
    def kivy_to_hex_color(color):
        try:
            r = str(hex(round(color[0] * 255))).replace('0x', '')
            if r == '0':
                r = '00'
            g = str(hex(round(color[1] * 255))).replace('0x', '')
            if g == '0':
                g = '00'
            b = str(hex(round(color[2] * 255))).replace('0x', '')
            if b == '0':
                b = '00'
            return r + g + b
        except Exception as e:
            return '000000'

    def add_gui(self, *args):
        self.popup = popup.Popup(title='add new function', content=AddGuiLayout(), size=[400, 400],
                                 pos=[300, 150], size_hint=[None, None], separator_height=0, title_align='center',
                                 title_size=18, title_color=[.7, .7, .7, 1])
        self.add_widget(self.popup)
        self.popup.content.cancel_bttn.bind(on_press=self.close_popup)
        self.popup.content.add_bttn.bind(on_press=lambda x: self.add_function(F2d(
            formula=self.popup.content.formula_entry.text, id=self.f.generate_id(),
            color=MainLayout.hex_to_kivy_color(self.popup.content.color_entry.text) + [1])))
        self.f.locked = True

    def add_function(self, f):
        self.f.f_obj[f.id] = f
        self.f.draw_graph_({f.id: self.f.f_obj[f.id]})
        self.sw.child.add_function(f)
        self.close_popup()

    def edit_gui(self, fid, *args):
        self.popup = popup.Popup(title='edit function', content=EditGuiLayout(
            formula=self.f.f_obj[fid].formula, color=MainLayout.kivy_to_hex_color(self.f.f_obj[fid].color)),
                                 size=[400, 400], pos=[300, 150], size_hint=[None, None], separator_height=0,
                                 title_align='center', title_size=18, title_color=[.7, .7, .7, 1])
        self.add_widget(self.popup)
        self.popup.content.cancel_bttn.bind(on_press=self.close_popup)
        self.popup.content.add_bttn.bind(on_press=lambda x: self.edit_function(fid, formula=self.popup.content.
                                                                             formula_entry.text,
                                                                             color=
                                                                             MainLayout.hex_to_kivy_color(
                                                                                 self.popup.content.color_entry.text) +
                                                                             [1]))
        self.search_for_children(self, textinput.TextInput, first=True)
        self.f.locked = True

    def edit_function(self, fid, *args, formula=None, color=None):
        print("called 'edit_function' method for fid:", fid)
        if formula == self.f.f_obj[fid].formula or not Fg.test_formula(formula):
            formula = None
        if color == self.f.f_obj[fid].color:
            color = None
        self.sw.child.edit_function(fid, formula=formula, color=color)
        self.f.remove_graph(fid)
        self.f.draw_graph_({fid: self.f.f_obj[fid]})
        self.close_popup()

    def add_series(self, *args):
        self.popup = popup.Popup(title='Add series of functions',
                                 content=AddSeriesLayout(size=[400, 400], size_hint=[None, None],
                                                         call_to_add=self.create_function,
                                                         call_to_destroy=self.close_popup),
                                 size=[400, 400], pos=[300, 150], size_hint=[None, None], separator_height=0,
                                 title_align='center', title_size=18, title_color=[.7, .7, .7, 1])
        self.popup.content.cancel_bttn.bind(on_press=self.close_popup)
        self.add_widget(self.popup)
        self.search_for_children(self, textinput.TextInput, first=True)
        self.f.locked = True

    def create_function(self, formula, color):
        new_id = self.f.generate_id()
        self.f.f_obj[new_id] = F2d(formula=formula, id=new_id, color=color)
        self.f.draw_graph_({new_id: self.f.f_obj[new_id]})
        self.sw.child.update_list()

    def settings_popup(self, *args):
        self.popup = popup.Popup(title='Settings', content=SettingsLayout(self.settings_pattern.copy(), call_to_destroy=
                                                                          self.close_popup,
                                                                          save_to=self.proceed_settings,
                                                    call_to_update_hitboxes=lambda: self.search_for_children(
                                                        self, textinput.TextInput, first=True)),
                                 size=[400, 440], pos=[300, 150], size_hint=[None, None], separator_height=0,
                                 title_align='center', title_size=18, title_color=[.7, .7, .7, 1])
        self.add_widget(self.popup)
        self.search_for_children(self, textinput.TextInput, first=True)
        self.f.locked = True

    def activate_settings(self):
        self.settings['view']['axis_color'].on_change = lambda: multiple_executor(lambda: setattr(
            self.fframe, 'draw_before', [(Color, {'rgb': self.settings['view']['axis_color'].value.rgb()}),
                                                 (Line, {
                                                     'points': [self.f.pos[0] + self.f.frame_size + 3, self.f.center_y,
                                                                self.f.pos[0] + self.f.width
                                                                - self.f.frame_size - 3, self.f.center_y], 'width': 2}),
                                                 (Triangle, {
                                                     'points': [self.f.pos[0] + self.f.width - self.f.frame_size + 2,
                                                                self.f.center_y,
                                                                self.f.pos[0] + self.f.width - self.f.frame_size - 25,
                                                                self.f.center_y - 12,
                                                                self.f.pos[0] + self.f.width - self.f.frame_size - 25,
                                                                self.f.center_y + 12]}),
                                                 (Line, {
                                                     'points': [self.f.center_x, self.f.pos[1] + self.f.frame_size + 3,
                                                                self.f.center_x,
                                                                self.f.pos[1] + self.f.height - 3 - self.f.frame_size],
                                                     'width': 2}),
                                                 (Triangle, {'points': [self.f.center_x, self.f.pos[
                                                     1] + self.f.height - self.f.frame_size + 2,
                                                                        self.f.center_x - 12, self.f.pos[
                                                                            1] + self.f.height - self.f.frame_size - 25,
                                                                        self.f.center_x + 12, self.f.pos[
                                                                            1] + self.f.height - self.f.frame_size - 25]
                                                             })]), self.fframe.draw, lambda: self.f.update_color(
            self.settings['view']['axis_color'].value.rgb() + [1]), self.f.draw)
        self.settings['view']['background_color'].on_change = lambda: multiple_executor(
            lambda: setattr(self.fframe, 'color2', self.settings['view']['background_color'].value.rgb()),
            self.fframe.draw
        )
        self.settings['view']['show_grid'].on_change = lambda: self.f.set_navigation_lines(
            self.settings['view']['show_grid'].value.value)
        self.settings['view']['show_axis_names'].on_change = lambda: self.f.set_axis_names(state=self.settings['view'
        ]['show_axis_names'].value.value)
        self.settings['view']['x_axis_name'].on_change = lambda: self.f.set_axis_names(x_name=self.settings['view'][
            'x_axis_name'].value.value)
        self.settings['view']['y_axis_name'].on_change = lambda: self.f.set_axis_names(y_name=self.settings['view'][
            'y_axis_name'].value.value)
        self.settings['view']['debug_data'].on_change = lambda: self.update_debug(self.settings['view']['debug_data'].
                                                                                  value.value)

    def proceed_settings(self, new):
        for cat in self.settings.keys():
            for setting in self.settings[cat].keys():
                if setting in new[cat].keys():
                    if not isinstance(self.settings[cat][setting].value, values.ColorValue):
                        self.settings[cat][setting].set(new[cat][setting].value.value)
                    else:
                        self.settings[cat][setting].set(fromhex=values._ColorConversions.kivy_format_to_hex_string(
                            *new[cat][setting].value.rgb()))

    def close_popup(self, *args):
        if not self.popup.content.try_dismiss():
            self.remove_widget(self.popup)
            self.popup = None
            self.f.locked = False
        self.search_for_children(self, textinput.TextInput, first=True)

    def update_debug(self, state):
        print(state, self.debug_layout in self.children)
        if not state and self.debug_layout in self.children:
            self.remove_widget(self.debug_layout)
        elif state and self.debug_layout not in self.children:
            self.add_widget(self.debug_layout)
            self.debug_layout.update({
                'last_render': self.f.last_render, 'average_render': self.f.avrg_render_time,
                'position': self.f.cam_pos, 'scale': self.f.scale})

    def search_for_children(self, obj, cls, first=False):
        if first:
            self.entries_hitboxes = []
        if isinstance(obj, cls):
            self.entries_hitboxes.append([obj.pos, obj.size])
        if hasattr(obj, 'popup'):
            if obj.popup:
                self.search_for_children(obj.popup.content, cls, first=False)
        for child in obj.children:
            self.search_for_children(child, cls, first=False)


class FuncApp(App):
    def __init__(self, **kwargs):
        super(FuncApp, self).__init__(**kwargs)
        self.title = 'function'

    def build(self):
        self.layout = MainLayout(settings=FuncApp.import_settings())
        return self.layout

    @staticmethod
    def import_settings():
        default = json.load(open('settings_default.json'))
        actual = default.copy()
        actual.update(json.load(open('settings.json')))
        print(actual)
        return configure(actual), configure(default)

    def stop(self, *largs):
        self.save_settings()
        super(FuncApp, self).stop(*largs)

    def save_settings(self):
        if self.layout.settings['main']['save_settings'].value.value:
            f = open('settings.json', 'w')
            deco = deconfigure(self.layout.settings)
            print(deco)
            json.dump(deco, f)
            f.close()
        else:
            f = open('settings.json', 'w')
            s = self.layout.settings_old
            s['main']['save_settings'].set(False)
            deco = deconfigure(s)
            deco['main']['save_settings'] = 0
            json.dump(deco, f)
            f.close()


if __name__ == '__main__':
    FuncApp().run()
