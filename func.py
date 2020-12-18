from numpy import arange
import math
import mpmath
from mpmath import *
from math import *


AXIS_NAMES = ['x', 'y', 'z', 'w', '5th', '6th', '7ht', '8th', '9th', '10th']


class nd_dict(object):
    def __init__(self, dimensions):
        self.structure_ = {}
        try:
            dimensions = float(dimensions)
        except TypeError:
            raise ValueError('dimension argument must be convertible to integer')
        if 1 <= dimensions and float(dimensions).is_integer():
            self.d = dimensions
        else:
            raise ValueError('dimension argument must be equal or bigger than 1 and must be integer')

    def __getitem__(self, path):
        if len(path) > 1:
            try:
                return self.structure_[path[0]].\
                    __getitem__(path[1:])
            except KeyError:
                self.structure_[path[0]] = nd_dict(self.d - 1)
                return self.structure_[path[0]]. \
                    __getitem__(path[1:])
        else:
            try:
                return self.structure_[path[0]]
            except KeyError:
                raise KeyError('value with this key seems not to exist')

    def __repr__(self):
        return repr(self.structure_)

    def __setitem__(self, path, value):
        if self.d == 1:
            if len(path) > self.d:
                raise KeyError('too long path')
            self.structure_[path[0]] = value
        elif len(path) == 1:
            if isinstance(value, nd_dict):
                if value.d == self.d - 1:
                    self.structure_[path[0]] = value
                else:
                    raise ValueError('Incompatible value')
            else:
                raise ValueError('Incompatible value')
        else:
            try:
                self.structure_[path[0]].__setitem__(path[1:], value)
            except KeyError:
                self.structure_[path[0]] = nd_dict(self.d - 1)
                self.structure_[path[0]].__setitem__(path[1:], value)

    def __delitem__(self, path):
        if len(path) == 1:
            try:
                del self.structure_[path[0]]
            except KeyError:
                raise KeyError('value with this key seems not to exist')
        else:
            try:
                self.structure_[path[0]].__delitem__(path[1:])
            except KeyError:
                raise KeyError('value with this key seems not to exist')


class Function_graph(object):
    handler_base = mpmath.__dict__
    handler_base.update(math.__dict__)
    def __init__(self, formula, d, id, axis_names=None, color=None):
        self.id = id
        self.formula = formula
        print('initialized function object with formula:', self.formula)
        self.points = nd_dict(d)
        self.d = d
        if not axis_names or len(axis_names) != d + 1:
            self.axis_names = AXIS_NAMES[:d + 1]
        else:
            self.axis_names = axis_names
        if not color:
            self.color = [1., 0., 0., 1.]
        else:
            self.color = color

    def generate(self, starts, stops, step_length, path_=None):
        if not path_:
            first_call = True
            path_ = {}
        else:
            first_call = False
        if len(starts) != len(stops) or len(stops) + len(path_) != self.d:
            raise ValueError('starts and stops should be defined for all dimensions')
        if len(starts) == 1:
            try:
                for independent_variable in arange(list(starts.values())[0], list(stops.values())[0], step_length):
                    tp = path_.copy()
                    tp.update({list(starts.keys())[0]: independent_variable})
                    try:
                        score = self.points[list(tp.values())[::-1]]
                        tp.update({self.axis_names[-1]: score})
                        yield tp
                    except KeyError:
                        score = {self.axis_names[-1]: self.execute(tp), list(starts.keys())[0]: independent_variable}
                        self.points[list(tp.values())] = score[self.axis_names[-1]]
                        yield score
            except KeyError:
                raise ValueError('starts and stops should be defined for all dimensions')
        else:
            for independent_variable in arange(list(starts.values())[0], list(stops.values())[0], step_length):
                try:
                    tp = path_.copy()
                    tp.update({list(starts.keys())[0]: independent_variable})
                    nstarts = starts.copy()
                    nstarts.pop(list(nstarts.keys())[0])
                    nstops = stops.copy()
                    nstops.pop(list(nstops.keys())[0])
                    for dependent_variable in self.generate(nstarts, nstops, step_length, tp):
                        dependent_variable.update({list(starts.keys())[0]: independent_variable})
                        if first_call:
                            tdp = dependent_variable.copy()
                            s = tdp.pop(self.axis_names[-1])
                        yield dependent_variable
                except KeyError:
                    raise ValueError('starts and stops should be defined for all dimensions')

    def execute(self, cords):
        handler = Function_graph.handler_base
        handler['score'] = 'err'
        temporary_formula = self.formula
        for dim, value in cords.items():
            temporary_formula = temporary_formula.replace(dim, str((value)))
        try:
            exec('score = ' + temporary_formula, handler)
        except Exception as e:
            print(e)
            handler['score'] = 'err'
        else:
            if isinstance(handler['score'], mpmath.mpf):
                handler['score'] = float(handler['score'])
            if not math.isfinite(handler['score']):
                handler['score'] = 'err'
        finally:
            return handler['score']

    def change_formula(self, new):
        self.formula = new
        self.points = nd_dict(self.d)

    def change_color(self, new_color):
        self.color = new_color

    @staticmethod
    def test_formula(formula):
        try:
            y = eval(formula.replace('x', '1'), Function_graph.handler_base)
        except Exception as e:
            if isinstance(e, ZeroDivisionError) or e.args[0] == 'math domain error':
                return True
            else:
                return False
        else:
            return True


class Function_2d(object):
    def __init__(self, formula, color, id):
        self.formula = formula
        self.executable = eval('lambda x: ' + formula.replace('x', '(x)'))
        self.color = color
        self.id = id
        self.saved = {}

    def generate(self, start, stop, step):
        to_return = {}
        for x in arange(start, stop, step):
            if x in self.saved.keys():
                to_return[x] = self.saved[x]
            else:
                try:
                    score = self.executable(x)
                    if not isinstance(score, (int, float)):
                        score = float(score)
                except Exception as e:
                    score = 'err'
                to_return[x] = self.saved[x] = score
        return to_return

    def change_formula(self, new):
        print('called "change_formula" in instance of Function_2d with id: ', self.id)
        if new != self.formula:
            self.formula = new
            self.saved = {}

    def change_color(self, new):
        self.color = new

