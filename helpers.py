from enum import Enum
import operator
import cexprtk
import math
import re

relative = lambda landmark, shape: (int(landmark.x * shape[1]), int(landmark.y * shape[0]))
relativeT = lambda landmark, shape: (int(landmark.x * shape[1]), int(landmark.y * shape[0]), 0)
relative3D = lambda landmark, shape: (landmark.x * shape[1], landmark.y* shape[0], landmark.z)

relativeCoord = lambda point, shape: (int(point[0] * shape[1]), int(point[1] * shape[0]))
relativeTCoord = lambda point, shape: (int(point[0] * shape[1]), int(point[1] * shape[0]), 0)
relative3DCoord = lambda point, shape: (point[0] * shape[1], point[1]* shape[0], point[3])

def tag(tag_name):
    def tags_decorator(func):
        func._tag = tag_name
        return func
    return tags_decorator

class ExampleClass:
    @tag('foo')
    def method_a(self):
        """does stuff"""

    @tag('foo')
    def method_b(self):
        """does stuff"""

    def method_c(self):
        """does stuff"""

    @tag('bar')
    def method_d(self):
        """does stuff"""

    @tag('bar')
    def method_e(self):
        """does stuff"""

def find_methods(cls, label):
    """Searches through the class namespace
        returns all methods with the correct label"""
    return [getattr(cls, func) for func in dir(cls) if '_tag' in dir(getattr(cls, func)) and getattr(cls, func)._tag == label]

#print(ExampleClass.method_a._tag)
#
#print(find_methods(ExampleClass,'foo')[0].__name__)
#print(find_methods(ExampleClass,'bar'))
#print(find_methods(ExampleClass,'qwe')) #--> Fail to call non-existent tag example

class RETURN_TYPE(Enum):
    PAIR_2D = 0
    PAIR_3D = 1
    DICTIONARY = 2

#face_landmarks_name_to_idx_list = None
#face_landmarks_idx_to_name_list = None
#file1 = open('face_landmarks_list.txt', 'r')
#Lines = file1.readlines()
#  
#for line in Lines:
#    line_nonewline = line.strip()
#    line_splitted = line_nonewline.split(',')
#    if face_landmarks_name_to_idx_list is None:
#        face_landmarks_name_to_idx_list = {line_splitted[1]:line_splitted[0]}
#    else:
#        face_landmarks_name_to_idx_list[line_splitted[1]] = line_splitted[0]
#
#    if face_landmarks_idx_to_name_list is None:
#        face_landmarks_idx_to_name_list = {line_splitted[0]:line_splitted[1]}
#    else:
#        face_landmarks_idx_to_name_list[line_splitted[0]] = line_splitted[1]
#
#for key, value in helpers.face_landmarks_name_to_idx_list.items():
#    print(key, '->', value)

#for key, value in helpers.face_landmarks_idx_to_name_list.items():
#    print(key, '->', value)

ops = {
    '+' : operator.add,
    '-' : operator.sub,
    '*' : operator.mul,
    '/' : operator.truediv,  # use operator.div for Python 2
    '%' : operator.mod,
    '^' : operator.xor,
    'and' : operator.and_,
    'or' : operator.or_,
    '<' : operator.lt,
    '<=' : operator.le,
    '==' : operator.eq,
    '>=' : operator.ge,
    '>' : operator.gt,
    '!=' : operator.ne,
    'not' : operator.neg
}

def isint(num):
    try:
        int(num)
        return True
    except ValueError:
        return False

def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False

def get_float(num: str, other_options: dict = None):
    tmp_result = None
    if isfloat(num):
        return float(num)
    else:
        if isint(num):
            return float(int(num))
        else:
            if other_options is not None:
#                print(other_options)
#                print(other_options.get(num))
                tmp_result = other_options.get(num)
                print(tmp_result)
                return tmp_result
            else:
                return None

def get_int(num: str, other_options: dict = None):
    if isint(num):
        return int(num)
    else:
        if other_options is not None:
            return other_options.get(num)
        else:
            return None

def test_evaluate_expression(expression_string, st):
    try:
#        st = cexprtk.Symbol_Table(self.handler.input_options)
        expression = cexprtk.Expression(expression_string, st)
        result = expression()
        return True, result
    except cexprtk._exceptions.ParseException:
        return False, None

def get_time_from_frame(current_fps, frame_fps):
    if current_fps is None:
        return None
#        current_fps = self.vs.get(cv2.CAP_PROP_POS_FRAMES)
    current_hour = math.floor(current_fps / (frame_fps * 3600))
    current_minute = math.floor((current_fps - current_hour * 60 * 60 * frame_fps)/(frame_fps * 60))
    current_second = math.floor((current_fps - current_hour * 60 * 60 * frame_fps - current_minute * frame_fps * 60)/(frame_fps))
    return str(current_hour) + ":" + str(current_minute) + ":" + str(current_second)

def get_frame_from_time(value: str, frame_fps):
    if value is None:
        return None
    splitted_var = value.split(':')
    if splitted_var is None:
        return None
    if len(splitted_var) != 3:
        return None
    hour, minute, second = splitted_var
    return (60*60*int(hour) + 60*int(minute) + int(second)) * frame_fps

def get_substring_before_first_digit_underscore_from_string(s1: str) -> str:
    if s1 is None:
        return None
    m = re.search(r"\d", s1)
    if m is None:
        return s1
    if m.start() > 0:
        return s1[0:m.start()-1]
    else:
        return s1
#    if m:
#        print("Digit found at position", m.start())
#    else:
#        print("No digit in that string")    