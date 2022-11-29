import tkinter as tki
from tkinter import ttk
import threading


class Criteria:
    def __init__(self, 
                handler,
                parent, 
                available_methods, 
#                available_estimation_idxs,
                initial_method = None, 
                initial_estimations_idx = None):

        self.handler = handler
        value_inside_method_name = tki.StringVar(parent)
        value_inside_method_name_initial = tki.StringVar(parent)
        self.value_inside_estimations_idx = tki.StringVar(parent)
#        value_inside_estimations_idx_initial = tki.StringVar(parent)

        value_inside_method_name.set("Select a Method")
        methods_list = []
        for available_method in available_methods:
            methods_list.append(available_method)

        if initial_method is None:
            self.methods_list_menu = tki.OptionMenu(parent, value_inside_method_name, *methods_list, command=self.set_method_name)
        else:
            value_inside_method_name_initial.set(initial_method)
            self.methods_list_menu = tki.OptionMenu(parent, value_inside_method_name_initial, *methods_list, command=self.set_method_name)

        self.value_inside_estimations_idx.set("Select Estimation Idxs")
#        self.value_inside_estimations_idx.trace('w', new_list)            
        estimations_list = ["Select Method First"]
        if initial_estimations_idx is None:
#            if estimations_list is None:
#                estimations_list = ["Select Method First"]
            self.estimations_list_menu = tki.OptionMenu(parent, self.value_inside_estimations_idx, *estimations_list, command=self.set_estimations_idx)
        else:
            self.value_inside_estimations_idx.set(initial_estimations_idx)
            self.estimations_list_menu = tki.OptionMenu(parent, self.value_inside_estimations_idx, *estimations_list, command=self.set_estimations_idx)

        if initial_method is None:
            estimations_list = self.set_method_name("Select a Method")
        else:
            estimations_list = self.set_method_name(initial_method)

        self.remove_button = tki.Button(parent, text="Remove", command=self.remove_criteria)        

        self.method_name = initial_method
#        self.estimations_idx = initial_estimations_idx
        self.should_be_removed = False

    def grid(self, row, rowspan = 1, columnspan = 1):
        self.methods_list_menu.grid(column=2, row=row, rowspan=rowspan, columnspan= columnspan, sticky='nsew')
        self.estimations_list_menu.grid(column=3, row=row, rowspan=rowspan, columnspan= columnspan, sticky='nsew')
        self.remove_button.grid(row=row, column = 4, sticky='nsew')

    def get_method_name(self):
        return self.method_name

    def set_method_name(self, method_name):
        self.method_name = method_name
        new_list = self.update_estimations_list()
#        self.estimations_list_menu.config(list=new_list)
        self.update_option_menu(new_list)
        
    def get_estimations_idx(self):
        return self.value_inside_estimations_idx.get()
#        return self.estimations_idx

    def set_estimations_idx(self, estimations_idx):
#        print(estimations_idx)
        self.value_inside_estimations_idx.set(estimations_idx)
#        self.estimations_idx = estimations_idx

    def get_should_be_removed(self):
        return self.should_be_removed

    def remove_criteria(self):
        self.should_be_removed = True

    def update_option_menu(self, new_list):
        menu = self.estimations_list_menu["menu"]
        menu.delete(0, "end")
        if new_list is None:
            new_list = ["Select Method First"]
        for string in new_list:
#            print(string)
            menu.add_command(label=string, command=lambda value=string: self.set_estimations_idx(value))

    def update_estimations_list(self):
        available_estimation_idxs = self.handler.get_to_estimate_for_method(self.method_name)
        estimations_list = []
        if available_estimation_idxs is not None:
            for available_estimation_idx in available_estimation_idxs:
                estimations_list.append(available_estimation_idx)
            return estimations_list
        else:
            return None
