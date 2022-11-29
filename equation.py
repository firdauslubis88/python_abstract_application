import tkinter as tki
from tkinter import ttk
from .helpers import get_float, ops
import cexprtk

class Equation:
    def __init__(self, parent, handler, is_negation: bool, input: str, multiplier: float, addition: float, equality_signs: str, comparator: float, input_options: dict):
        self.parent = parent
        self.handler = handler
        self.is_negation = is_negation
#        self.input_options = input_options

        if is_negation is None or input is None or multiplier is None or addition is None or equality_signs is None or comparator is None:
            return None

        self.value_inside_input = tki.StringVar()
        self.value_inside_input.set(input)

        self.value_inside_multiplier = tki.StringVar(parent)
        self.value_inside_multiplier.set(str(multiplier))

        self.value_inside_addition = tki.StringVar(parent)
        self.value_inside_addition.set(str(addition))

        self.value_inside_comparator = tki.StringVar(parent)
        self.value_inside_comparator.set(str(comparator))

#        self.input_entry = ttk.Combobox(self.parent, textvariable = value_inside_input)
#        self.multiplier_entry = ttk.Combobox(self.parent, textvariable = value_inside_multiplier)
#        self.addition_combobox = ttk.Combobox(self.parent, textvariable = value_inside_addition)
        self.equality_signs_combobox = ttk.Combobox(self.parent, textvariable = equality_signs)
#        self.comparator_combobox = ttk.Combobox(self.parent, textvariable = value_inside_comparator)

        self.input_entry = ttk.Entry(self.parent, textvariable = self.value_inside_input, width=150)
        self.multiplier_entry = ttk.Entry(self.parent, textvariable = self.value_inside_multiplier)
        self.addition_combobox = ttk.Entry(self.parent, textvariable = self.value_inside_addition)
#        self.equality_signs_combobox = ttk.Entry(self.parent, textvariable = equality_signs)
        self.comparator_combobox = ttk.Entry(self.parent, textvariable = self.value_inside_comparator)
        self.btn_remove_self = tki.Button(parent, text="Remove", command=self.on_remove_self)

#        self.input_entry["values"] = available_input_options
#        self.multiplier_entry["values"] = available_input_options
#        self.addition_combobox["values"] = available_input_options
#        self.comparator_combobox["values"] = available_input_options
        self.equality_signs_combobox["values"] = ['<','<=','==','>=','>','!=']
        self.equality_signs_combobox.current(2)

        self.multiplier_label = tki.Label(parent, text="x")
        self.addition_label = tki.Label(parent, text="+")
        self.result_label = tki.Label(parent, text="None")
        
    def get_is_negation(self):
        return self.is_negation
        
    def get_input(self):
        return self.input_entry.get()

#    def set_input(self,value):
#        self.input_entry.insert(0,value)
        
    def get_multiplier(self):
        return self.multiplier_entry.get()
        
    def set_multiplier(self,value):
        self.multiplier_entry.insert(0,value)

    def get_addition(self):
        return self.addition_combobox.get()
        
    def get_equality_signs(self):
        return self.equality_signs_combobox.get()
        
    def get_comparator(self):
        return self.comparator_combobox.get()

    def grid(self, row: int, column: int):
        self.input_entry.grid(row = row, column = column, columnspan=7, sticky='nsew')
#        self.multiplier_label.grid(row = row, column = column + 1)
#        self.multiplier_entry.grid(row = row, column = column + 2)
#        self.addition_label.grid(row = row, column = column + 3)
#        self.addition_combobox.grid(row = row, column = column + 4)
#        self.equality_signs_combobox.grid(row = row, column = column + 5)
#        self.comparator_combobox.grid(row = row, column = column + 6)
        self.result_label.grid(row = row, column = column + 7)
        self.btn_remove_self.grid(row=row,column=column + 8,sticky='nsew')

        return row, row, column, column + 7
        
    def on_remove_self(self):
        if self.handler is not None:
            self.handler.on_remove_equation(self)

    def calculate(self):
#        print('hii0')
        if self.is_negation is None or self.get_input() is None or self.get_multiplier() is None or self.get_addition() is None or self.get_equality_signs() is None or self.get_comparator() is None:
            self.result_label.config(text='None')
            return None
#        print('hii1')
#        if self.get_float(self.get_input()) is None or self.get_float(self.get_multiplier()) is None or self.get_float(self.get_addition()) is None or self.get_float(self.get_comparator()) is None:
#            self.result_label.config(text='None')
#            return None

#        print(self.get_input())
        evaluation_result, tmp_calculate = self.evaluate_expression()
        self.result_label.config(text=str(tmp_calculate))
        return tmp_calculate
#        return 0.
        
#        tmp_calculate = (self.get_float(self.get_input())*self.get_float(self.get_multiplier()))+self.get_float(self.get_addition())
#        print(tmp_calculate)
#        tmp_calculate_after_equality = False
#        if self.get_equality_signs() in ops:
#            tmp_calculate_after_equality = ops[self.get_equality_signs()](tmp_calculate,self.get_float(self.get_comparator()))
#        else:
#            self.result_label.config(text='None')
#            return None
#        if self.is_negation is True:
#            self.result_label.config(text=str(tmp_calculate))
##            self.result_label.config(text=str(not tmp_calculate_after_equality))
#            return (not tmp_calculate_after_equality)
#        else:
#            self.result_label.config(text=str(tmp_calculate))
##            self.result_label.config(text=str(tmp_calculate_after_equality))
#            return tmp_calculate_after_equality

#    def isint(self,num):
#        try:
#            int(num)
#            return True
#        except ValueError:
#            return False
#
#    def isfloat(self,num):
#        try:
#            float(num)
#            return True
#        except ValueError:
#            return False
#
#    def get_float(self,num: str):
##        tmp_result = None
#        if self.isfloat(num):
#            return float(num)
#        else:
#            if self.isint(num):
#                return float(int(num))
#            else:
#                if self.handler.input_options is not None:
#    #                print(other_options)
#    #                print(other_options.get(num))
##                    tmp_result = self.handler.input_options.get(num)
##                    print(tmp_result)
#                    return self.handler.input_options.get(num)
#                else:
#                    return None
#
#    def get_int(self,num: str):
#        if self.isint(num):
#            return int(num)
#        else:
#            if self.handler.input_options is not None:
#                return self.handler.input_options.get(num)
#            else:
#                return None
#
    
    def evaluate_expression(self):
        try:
#            print(self.get_input())
            if self.handler.input_options is None:
                return False, None
#            print(self.handler.input_options)
            st = cexprtk.Symbol_Table(self.handler.input_options)
            expression = cexprtk.Expression(self.get_input(), st)
            result = expression()
            return True, result
        except cexprtk._exceptions.ParseException:
#            print(self.get_input())
            return False, None
