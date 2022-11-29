import tkinter as tki
from tkinter import ttk
from .equation import Equation
from .helpers import ops

class Classification:
#    def __init__(self, parent, handler, class_name,  mathematical_operations: list[Equation] = None, boolean_operations: list = None, input_options: dict = None):
    def __init__(self, parent, handler, class_name,  mathematical_operations: list[str] = None, boolean_operations: list = None, input_options: dict = None):
        self.class_name = class_name
        self.parent = parent
        self.handler = handler
        self.mathematical_operations = mathematical_operations
        self.boolean_operations = boolean_operations
        self.input_options = input_options

        if mathematical_operations is None:
            self.mathematical_operations = [Equation(parent = parent, handler = self, is_negation = False, input = '0.', multiplier = 1., addition = 0., equality_signs = '==', comparator = 0., input_options=input_options)]
        else:
            self.mathematical_operations = []
            for current_mathematical_expression in mathematical_operations:
                self.mathematical_operations.append(Equation(parent = parent, handler = self, is_negation = False, input = current_mathematical_expression, multiplier = 1., addition = 0., equality_signs = '==', comparator = 0., input_options=input_options))

        self.separator = ttk.Separator(self.parent,orient=tki.HORIZONTAL)

        self.value_inside_class_name = tki.StringVar()
        self.value_inside_class_name.set(str(self.class_name))

        self.current_class_label = tki.Entry(parent, textvariable = self.value_inside_class_name)
        self.btn_add_equation = tki.Button(parent, text="Add Equation", command=self.on_add_equation)
        self.btn_remove_self = tki.Button(parent, text="Remove Class", command=self.on_remove_self)

    def get_class_name(self):
        return self.current_class_label.get()

    def set_class_name(self, value):
        self.class_name = value
        self.value_inside_class_name.set(str(self.class_name))

    def get_mathematical_operations(self):
        return self.mathematical_operations

    def set_mathematical_operations(self, value):
        self.mathematical_operations = value

    def get_boolean_operations(self):
        return self.boolean_operations

    def set_boolean_operations(self, value):
        self.boolean_operations = value

    def get_input_options(self):
        return self.input_options

    def set_input_options(self, value):
        self.input_options = value
#        print(self.input_options)

    def grid(self, row: int, column: int):
        self.separator.grid(row=row, column = column, columnspan=100, sticky='ew')
        self.current_class_label.grid(column=column, row=row+1, sticky='nsew')
        self.btn_remove_self.grid(row=row+1,column=column+1,sticky='nsew')
        if self.mathematical_operations is not None:
            for idx, current_mathematical_operation in enumerate(self.mathematical_operations):
#                current_mathematical_operation.set_input("0.")
#                current_mathematical_operation.set_multiplier("0.")
                current_mathematical_operation.grid(row=(row+idx+2), column=column)
            self.btn_add_equation.grid(row=row+len(self.mathematical_operations)+2,column=column,sticky='nsew',padx=10,pady=10)
            return row, row + len(self.mathematical_operations)+2, column, column+7
        else:
            self.btn_add_equation.grid(row=row+len(self.mathematical_operations)+2,column=column,sticky='nsew',padx=10,pady=10)
            return row, row+2, column, column
        
    def on_add_equation(self):
        self.mathematical_operations.append(Equation(parent = self.parent, handler=self, is_negation = False, input = 0., multiplier = 1., addition = 0., equality_signs = '==', comparator = 0., input_options=self.input_options))
        self.handler.update_class()

    def on_remove_equation(self,equation_to_delete):
        self.mathematical_operations.remove(equation_to_delete)
        self.handler.update_class()

    def on_remove_self(self):
        if self.handler is not None:
            self.handler.remove_class(self)

    def calculate(self):
        current_constants = [None] * len(self.mathematical_operations)
        for idx,current_mathematical_operation in enumerate(self.mathematical_operations):
            current_constants[idx] = current_mathematical_operation.calculate()
#        for boolean_operation_dict in self.boolean_operations:
#            next_constants = [None] * len(boolean_operation_dict)
#            for key, value in boolean_operation_dict:
#                operand1, operation_sign, operand2 = value
#                if operand1 is None or operation_sign is None or operand2 is None:
#                    continue
#                next_constants[int(key)] = current_constants[int(operand1)] * ops[operation_sign] * current_constants[int(operand2)]
#            current_constants = next_constants
#
        if current_constants is not None:
            if len(current_constants) >= 1:
                return current_constants[0]
        return None