import tkinter as tki
from tkinter import ttk
import threading


class Evaluation:
    def __init__(self, 
                parent,
                evaluation_idx,
                current_results = None,
                current_results_type = None,
                ):

        if evaluation_idx is None:
            return None

        self.evaluation_idx = evaluation_idx
        self.current_results = current_results
        self.current_results_type = current_results_type

#        evaluation_idx_string = tki.StringVar(parent)
#        evaluation_idx_string.set("Estimation id: ")
        self.evaluation_idx_label = tki.Label(parent, text="Estimation id: ")

#        current_result_string = tki.StringVar(parent)
#        current_result_string.set("Result: ")
        self.current_result_label = tki.Label(parent, text="Result: ")

        if evaluation_idx is None:
            self.evaluation_idx_var_label = tki.Label(parent, text="NONE")
        else:
            self.evaluation_idx_var_label = tki.Label(parent, text=self.evaluation_idx)

        if current_results is None:
            self.current_result_var_label = tki.Label(parent, text="NONE")
        else:
            self.current_result_var_label = tki.Label(parent, text=self.current_results)

    def get_evaluation_idx(self):
        return self.evaluation_idx

    def set_evaluation_idx(self, value):
        self.evaluation_idx = value
        self.evaluation_idx_var_label.config(text = self.evaluation_idx)

    def get_current_result(self):
        return self.current_results

    def set_current_result(self, value):
        self.current_results = value
        self.current_result_var_label.config(text = self.current_results)

    def grid(self, row, column_start, rowspan = 1, columnspan = 1):
        self.evaluation_idx_label.grid(column=column_start, row=row, rowspan=rowspan, columnspan= columnspan, sticky='nsew')
        self.evaluation_idx_var_label.grid(column=column_start+1, row=row, rowspan=rowspan, columnspan= columnspan, sticky='nsew')
        self.current_result_label.grid(column=column_start+2, row=row, rowspan=rowspan, columnspan= columnspan, sticky='nsew')
        self.current_result_var_label.grid(column=column_start+3, row=row, rowspan=rowspan, columnspan= columnspan, sticky='nsew')