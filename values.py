class NumericValue(float):
    def __new__(self, value, *args, **kwargs):
        return float.__new__(NumericValue, value)

    def __init__(self, value, value_range=None, floating=True):
        self.is_float = floating
        if not self.is_float and not self.is_integer():
            raise ValueError('only integers accepted')
        if not value_range:
            self.value_range = [None, None]
        else:
            try:
                if len(value_range) >= 2:
                    if isinstance(value_range[0], (int, float, type(None))) and \
                            isinstance(value_range[1], (int, float, type(None))):
                        if isinstance(value_range[0], (int, float)) and isinstance(value_range[1], (int, float)):
                            if value_range[0] >= value_range[1]:
                                raise ValueError('Invalid Value range')
                        self.value_range = value_range
                    else:
                        raise ValueError('invalid value range')
                else:
                    raise ValueError('invalid value range')
            except TypeError:
                raise ValueError('invalid value range')

    def set(self, new_value):
        if self.value_range[0]:
            if new_value <= self.value_range[0]:
                raise ValueError('Invalid Value')
        if self.value_range[1]:
            if new_value >= self.value_range[1]:
                raise ValueError('Invalid Value')
        return NumericValue(new_value, self.value_range, floating=self.is_float)


class FromListValue(object):
    def __init__(self, group, value):
        try:
            if value not in group:
                raise ValueError('start value not in possible values group')
        except TypeError:
            raise TypeError('invalid value of \'group\' argument')
        self.value = value
        self.group = group

    def set(self, new_group, new_value):
        return FromListValue(new_group, new_value)


class StringValue(str):
    def __new__(self, value):
        if not isinstance(value, str):
            raise TypeError('value must be string')
        return super(StringValue, self).__new__(StringValue, value)

    def __init__(self, value):
        self.value = value

    def set(self, new_value):
        return StringValue(new_value)


class ColorValue(object):
    def __init__(self, r=1, g=1, b=1, a=1.0, fromhex=None):
        self.r = r
        self.g = g
        self.b = b
        self.a = a
        if fromhex:
            self.r, self.g, self.b = _ColorConversions.hex_string_to_kivy_format(fromhex)

    def set(self, rgb=None, a=None, fromhex=None):
        if rgb:
            r, g, b = rgb
        else:
            r = g = b = 1
        if not a:
            a = 1
        return ColorValue(r, g, b, a, fromhex)

    def rgb(self):
        return [self.r, self.g, self.b]

    def rgba(self):
        return self.rgb() + [self.a]

    def __repr__(self):
        return str([self.r, self.g, self.b, self.a])

    def __str__(self):
        return self.__repr__()

    def __add__(self, other):
        if not isinstance(other, ColorValue):
            raise TypeError('cannot add ' + str(type(other)) + ' object')
        else:
            return ColorValue((self.r + other.r) / 2, (self.g + other.g) / 2, (self.b + other.b) / 2,
                              (self.a + other.a) / 2)

    def __mul__(self, other):
        try:
            return ColorValue((self.r * other - 1) * (self.r * other - 1 <= 0) + 1,
                              (self.g * other - 1) * (self.g * other - 1 <= 0) + 1,
                              (self.b * other - 1) * (self.b * other - 1 <= 0) + 1, self.a)
        except (TypeError, NotImplementedError) as e:
            raise TypeError(e)

    def __truediv__(self, other):
        return self * (1 / other)

    def __sub__(self, other):
        try:
            return ColorValue((self.r - other) * (self.r - other >= 0),
                              (self.g - other) * (self.g - other >= 0),
                              (self.b - other) * (self.b - other >= 0), self.a)
        except (TypeError, NotImplementedError) as e:
            raise TypeError(e)


class BoolValue(int):
    def __new__(self, value, alternative_desc=None):
        if not alternative_desc:
            return super(BoolValue, self).__new__(BoolValue, value)

    def __init__(self, value, alternative_desc=None):
        if value not in (True, False):
            raise TypeError('value can only be True or False')
        if alternative_desc:
            self.state_names = alternative_desc
        self.value = value

    def set(self, new):
        return BoolValue(new)


class _ColorConversions(object):
    @staticmethod
    def hex_string_to_kivy_format(string):
        return [int(string[:2], 16) / 255, int(string[2:4], 16) / 255, int(string[4:], 16) / 255]

    @staticmethod
    def kivy_format_to_hex_string(r, g, b):
        result = ''
        for col in (r, g, b):
            to_add = str(hex(int(col * 255)))
            to_add = to_add.replace('0x', '')
            if len(to_add) == 1:
                to_add = '0' + to_add
            result += to_add
        return result
