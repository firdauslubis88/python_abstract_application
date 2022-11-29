import tkinter as tki
from tkinter import HORIZONTAL, ttk
from PIL import Image
from PIL import ImageTk
import cv2
import numpy as np
import threading

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import os
import time
import datetime
import math
import json

#from helpers import find_methods, face_landmarks_name_to_idx_list, RETURN_TYPE
from .criteria import Criteria
from .classification import Classification
from .utils import textWithBackground
from .Person import Person

from typing import List, Mapping, Optional, Tuple, Union
from mediapipe.framework.formats import landmark_pb2
import dataclasses

from . import helpers

_PRESENCE_THRESHOLD = 0.5
_VISIBILITY_THRESHOLD = 0.5
_BGR_CHANNELS = 3

WHITE_COLOR = (224, 224, 224)
BLACK_COLOR = (0, 0, 0)
RED_COLOR = (0, 0, 255)
GREEN_COLOR = (0, 128, 0)
BLUE_COLOR = (255, 0, 0)

@dataclasses.dataclass
class DrawingSpec:
    # Color for drawing the annotation. Default to the white color.
    color: Tuple[int, int, int] = WHITE_COLOR
    # Thickness for drawing the annotation. Default to 2 pixels.
    thickness: int = 2
    # Circle radius. Default to 2 pixels.
    circle_radius: int = 2

def _normalized_to_pixel_coordinates(
    normalized_x: float, normalized_y: float, image_width: int,
    image_height: int) -> Union[None, Tuple[int, int]]:
    """Converts normalized value pair to pixel coordinates."""
    # Checks if the float value is between 0 and 1.
    def is_valid_normalized_value(value: float) -> bool:
        return (value > 0 or math.isclose(0, value)) and (value < 1 or
                                                        math.isclose(1, value))

    if not (is_valid_normalized_value(normalized_x) and
            is_valid_normalized_value(normalized_y)):
        # TODO: Draw coordinates even if it's outside of the image bounds.
        return None
    x_px = min(math.floor(normalized_x * image_width), image_width - 1)
    y_px = min(math.floor(normalized_y * image_height), image_height - 1)
    return x_px, y_px

def _normalize_color(color):
  return tuple(v / 255. for v in color)

class AbstractApplication:
    def __init__(self, video_folder_path: str = '.', video_file_name: str = '01.mp4', output_path: str = None, time_start: time.struct_time = 0, persons: dict = None, available_methods = None, to_estimates = None):

#        time.mktime()
#        videos_list = []
#        for file in os.listdir("."):
#            if file.endswith((".mp4",".avi")):
#                videos_list.append(os.path.join(".", file))

        self.video_folder_path = video_folder_path# '.'
        self.current_video_file_name = video_file_name# '01.mp4'
        current_video_file_name_no_extension = self.current_video_file_name.split('.')[-2]
#        if self.current_video_file_name_no_extension is not None:
#            if len(self.current_video_file_name_no_extension) > 1:
#                self.current_video_file_name_no_extension = self.current_video_file_name_no_extension[-2]
#            else:
#                self.current_video_file_name_no_extension = self.current_video_file_name_no_extension[0]
#        print('video_file_name: ', self.current_video_file_name)
        # store the video stream object and output path, then initialize
        # the most recently read frame, thread for reading frames, and
        # the thread stop event
        self.vs = cv2.VideoCapture(self.video_folder_path + '/' + self.current_video_file_name)
        self.frame_fps = self.vs.get(cv2.CAP_PROP_FPS)
        self.frame_start = 0
        if time_start is not None:
            self.frame_start = time_start# ((time_start.tm_hour*60+time_start.tm_min) * 60 + time_start.tm_sec)*self.frame_fps
        self.vs.set(cv2.CAP_PROP_POS_FRAMES, self.frame_start)

        self.output_path = output_path
        self.frame = None
        self.resume_event = None
        self.pause_event = None
        self.stop_event = None
        self.screen_capture_event = None
        # initialize the root window and image panel
        self.root = tki.Tk()
        self.panel = None
        self.panel_image_row_min = 0
        self.panel_image_row_max = 19
        self.panel_image_column_min = 0
        self.panel_image_column_max = 19

        self.debugger_panels_row_min = self.panel_image_row_max+1
        self.slider_playback_panels_row_min = self.panel_image_row_max+2
        self.playback_panels_row_min = self.panel_image_row_max+3
        self.separator_panels_row_min = self.panel_image_row_max+4
        self.criteria_panels_row_min = self.panel_image_row_max+5
        
        self.entry_playback_value = tki.StringVar()
        self.entry_playback = None
        self.slider_playback = None
        self.slider_playback_is_focus = False
        self.btn_pause = None
        self.btn_forward = None
        self.btn_backward = None
        self.btn_prev_section = None
        self.btn_next_section = None
        self.btn_resume = None
        self.btn_add_class = None
        self.btn_record_result = None
        self.btn_save_class = None
        self.btn_load_class = None
        self.criteria_list = []
        self.evaluation_list = []

        self.class_list = []
        self.class_row_min = None
        self.class_row_max = None
        self.class_column_min = None
        self.class_column_max = None

        self.input_options = None

        self.font = cv2.FONT_HERSHEY_COMPLEX

        self.is_changed = False
        self.prev_is_playing = None
        self.is_playing = True

        self.next_frame = None

        # start a thread that constantly pools the video sensor for
        # the most recently read frame
        self.person_changed_event = threading.Event()
        self.changed_event = threading.Event()
        self.resume_event = threading.Event()
        self.pause_event = threading.Event()
        self.stop_event = threading.Event()
        self.screen_capture_event = threading.Event()
        # set a callback to handle when the window is closed
        self.root.wm_title("MRLAB Attention Detection")
        self.root.wm_protocol("WM_DELETE_WINDOW", self.on_close)

#        self.persons = {}
#        self.persons["person_a"] = Person("person_a",0,192,720,480, self.current_video_file_name_no_extension)
#        self.persons["person_b"] = Person("person_b",0,1000,720,480, self.current_video_file_name_no_extension)


#        print('persons: ', persons)
        self.persons = persons
        self.persons_list = []
#        self.current_person = None
#        if self.persons is None:
#            if self.vs is not None:
#                self.persons = {"person_a":Person("person_a",0,0,int(self.vs.get(cv2.CAP_PROP_FRAME_WIDTH)),int(self.vs.get(cv2.CAP_PROP_FRAME_HEIGHT)), current_video_file_name_no_extension)}
#
        for key, value in self.persons.items():
            self.persons_list.append(key)
        self.current_person_sv = tki.StringVar()
        self.current_person_sv.set(list(self.persons.keys())[0])
        self.current_person = self.persons[self.current_person_sv.get()]

#            self.frame_start = (24 * 60 + 30)*self.frame_fps
        

#        result = self.vs.set(cv2.CAP_PROP_POS_FRAMES, self.frame_start)
        #########################USER INPUT VARIABLE END#########################
#        self.GE = gaze.Gazetimation(self)
#        methods_found = find_methods(gaze.Gazetimation,'function_to_call')
        self.available_methods = available_methods# []
#        for method_found in methods_found:
#            self.available_methods.append(method_found.__name__)
#
#        initial_method = 'mou'# self.available_methods[0] #find_methods(gaze.Gazetimation,'function_to_call')[0].__name__

#        estimations_idx_list = self.get_to_estimate_for_method(initial_method)# self.GE.get_to_estimate_for_method(initial_method)# ["left_eye_gaze","right_eye_gaze","body_direction"]
#        self.available_estimations_idx = estimations_idx_list

        self.to_estimates = to_estimates# {}# {initial_method:["left_eye_gaze","right_eye_gaze","body_direction"]}
#        self.to_estimates = {initial_method:estimations_idx_list}

        self.criteria_list.append(tki.Button(self.root, text="Add new criteria", command=self.add_new_criteria))
        for method_name, to_estimates in self.to_estimates.items():
            for to_estimate in to_estimates:
                self.add_new_criteria(method_name, to_estimate) #self.criteria_list.append(Criteria(self.root, self.available_methods, estimations_idx_list, method_name, to_estimate))

        self.figure = plt.figure(figsize=(2, 2))
        self.ax = plt.axes(projection='3d')
        self.ax.view_init(elev=10, azim=10)

        self.bar1 = FigureCanvasTkAgg(self.figure, self.root)

        self.debugger_panel = None

        self.mouse_x = None
        self.mouse_y = None
        self.root.bind('<Motion>', self.motion)

        self.start_time = time.time()
        self.current_fps_interval_count = 0
        self.fps_interval = 3

        self.default_class_expression = self.generate_default_class_expression()
        self.text_to_print = None

        self.thread = threading.Thread(target=self.video_loop, args=())
        self.thread.start()

    def screen_capture(self):
        # grab the current timestamp and use it to construct the
        # output path
        ts = datetime.datetime.now()
        filename = "{}.jpg".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))
        p = os.path.sep.join((self.output_path, filename))
        # save the file
        cv2.imwrite(p, self.frame.copy())
        print("[INFO] saved {}".format(filename))
        self.screen_capture_event.clear()

    def set_slider_playback_focus(self,value):
        self.slider_playback_is_focus = True

    def reset_slider_playback_focus(self,value):
        self.slider_playback_is_focus = False
        if self.prev_is_playing is not None:
            self.is_playing = self.prev_is_playing

    def motion(self, event):
        self.mouse_x = event.x
        self.mouse_y = event.y

    def get_current_time(self):
        current_fps = self.vs.get(cv2.CAP_PROP_POS_FRAMES)
        current_hour = math.floor(current_fps / (self.frame_fps * 3600))
        current_minute = math.floor((current_fps - current_hour * 60 * 60 * self.frame_fps)/(self.frame_fps * 60))
        current_second = math.floor((current_fps - current_hour * 60 * 60 * self.frame_fps - current_minute * self.frame_fps * 60)/(self.frame_fps))
        return str(current_hour) + ":" + str(current_minute) + ":" + str(current_second)

#    def get_time_from_frame(self,current_fps):
#        if current_fps is None:
#            return None
##        current_fps = self.vs.get(cv2.CAP_PROP_POS_FRAMES)
#        current_hour = math.floor(current_fps / (self.frame_fps * 3600))
#        current_minute = math.floor((current_fps - current_hour * 60 * 60 * self.frame_fps)/(self.frame_fps * 60))
#        current_second = math.floor((current_fps - current_hour * 60 * 60 * self.frame_fps - current_minute * self.frame_fps * 60)/(self.frame_fps))
#        return str(current_hour) + ":" + str(current_minute) + ":" + str(current_second)
#
#    def get_frame_from_time(self,value: str):
#        if value is None:
#            return None
#        splitted_var = value.split(':')
#        if splitted_var is None:
#            return None
#        if len(splitted_var) != 3:
#            return None
#        hour, minute, second = splitted_var
#        return (60*60*int(hour) + 60*int(minute) + int(second)) * self.frame_fps
#
    def set_video_time(self):
        if self.next_frame is not None:
            self.prev_is_playing = self.is_playing
            self.vs.set(cv2.CAP_PROP_POS_FRAMES, self.next_frame)
            self.next_frame = None
            self.is_playing = True
        self.changed_event.clear()

    def on_set_video_time_slider(self,value):
        self.next_frame = float(value) / 10000. * self.vs.get(cv2.CAP_PROP_FRAME_COUNT)
        self.entry_playback_value.set(helpers.get_time_from_frame(self.next_frame,self.frame_fps))
        self.changed_event.set()

    def on_set_video_time_entry(self,value):
        next_frame = self.get_frame_from_time(self.entry_playback_value.get())
        if next_frame is not None:
            if self.slider_playback is not None:
#                self.slider_playback.set(int(float(next_frame / float(self.vs.get(cv2.CAP_PROP_FRAME_COUNT)) * 10000.))) -->> NOT NEEDED!!!!
                self.next_frame = next_frame
                self.changed_event.set()

    def resume_video(self):
        self.is_playing = True
        self.resume_event.clear()

    def pause_video(self):
        self.is_playing = False
        self.pause_event.clear()

    def on_resume(self):
        self.resume_event.set()

    def on_pause(self):
        self.pause_event.set()

    def on_backward_frame(self):
        self.next_frame = self.vs.get(cv2.CAP_PROP_POS_FRAMES) - 5*self.frame_fps
        if self.next_frame < 0:
            self.next_frame = 0
        self.entry_playback_value.set(helpers.get_time_from_frame(self.next_frame,self.frame_fps))
        self.changed_event.set()

    def on_forward_frame(self):
        self.next_frame = self.vs.get(cv2.CAP_PROP_POS_FRAMES) + 5*self.frame_fps#float(value) / 10000. * self.vs.get(cv2.CAP_PROP_FRAME_COUNT)
        if self.next_frame > self.vs.get(cv2.CAP_PROP_FRAME_COUNT):
            self.next_frame = self.vs.get(cv2.CAP_PROP_FRAME_COUNT)
        self.entry_playback_value.set(helpers.get_time_from_frame(self.next_frame,self.frame_fps))
        self.changed_event.set()

    def generate_default_class_expression(self):
        pass

    def on_prev_section_callback(self):
        pass

    def on_next_section_callback(self):
        pass

    def on_prev_section(self):
        next_frame_candidate = self.on_prev_section_callback()
        if next_frame_candidate is not None:
            self.next_frame = next_frame_candidate
            self.entry_playback_value.set(helpers.get_time_from_frame(self.next_frame,self.frame_fps))
            self.changed_event.set()

    def on_next_section(self):
        next_frame_candidate = self.on_next_section_callback()
        if next_frame_candidate is not None:
            self.next_frame = next_frame_candidate
            self.entry_playback_value.set(helpers.get_time_from_frame(self.next_frame,self.frame_fps))
            self.changed_event.set()

    def on_close(self):
        # set the stop event, cleanup the camera, and allow the rest of
        # the quit process to continue
        print("[INFO] closing...")
        del self.current_person
        self.stop_event.set()
        self.vs.release()
        self.root.quit()

    def person_changed(self):
        if self.persons is None:
            return
        self.current_person = self.persons[self.current_person_sv.get()]
        self.load_class()
        self.person_changed_event.clear()

    def on_person_changed(self,value):
        self.person_changed_event.set()

    def get_to_estimate_for_method(self, method_name):
        return self.GE.get_to_estimate_for_method(method_name)# ["left_eye_gaze","right_eye_gaze","body_direction"]

    def get_criteria_summary(self) -> dict:
        if len(self.criteria_list) > 1:
            return_criteria_summary = None
            for idx, current_criteria in enumerate(self.criteria_list):
                if idx < (len(self.criteria_list)-1):
                    if current_criteria.get_method_name() is not None:
                        if current_criteria.get_estimations_idx() is not None:
                            if return_criteria_summary is None:
                                return_criteria_summary = {current_criteria.get_method_name():[current_criteria.get_estimations_idx()]}
                            elif current_criteria.get_method_name() not in return_criteria_summary:
                                return_criteria_summary[current_criteria.get_method_name()] = [current_criteria.get_estimations_idx()]
                            else:
                                if current_criteria.get_estimations_idx() not in return_criteria_summary[current_criteria.get_method_name()]:
                                    return_criteria_summary[current_criteria.get_method_name()].append(current_criteria.get_estimations_idx())
            return return_criteria_summary
        return None

    def update_criteria(self):
        for widget in self.root.grid_slaves():
            if int(widget.grid_info()["row"]) >= (self.criteria_panels_row_min ):
                widget.grid_forget()

        for ndex, i in enumerate(self.criteria_list):
            if ndex == (len(self.criteria_list)-1):
                i.grid(row=self.criteria_panels_row_min+ndex,column=4,sticky='nse')
            else:
                i.grid(row=self.criteria_panels_row_min+ndex)

    def add_new_criteria(self,initial_method=None,initial_estimations_idx=None):
        self.criteria_list.insert(0, Criteria(self, self.root, self.available_methods,initial_method,initial_estimations_idx))
        self.update_criteria()

#    def add_new_criteria(self):
#        self.add_initialize_new_criteria(self,None,None)
#        self.criteria_list.insert(0, Criteria(self, self.root, self.available_methods))
#        self.update_criteria()

    def remove_criteria(self,current_criteria):
        self.criteria_list.pop(current_criteria)
        self.update_criteria()

    def check_remove_criteria(self):
        if self.criteria_list is not None:
            if len(self.criteria_list) > 1:
                for idx,current_criteria in enumerate(self.criteria_list):
                    if idx < (len(self.criteria_list) - 1):
                        if current_criteria.get_should_be_removed() is True:
                            self.remove_criteria(idx)
                
    def update_class(self):
        row_start = self.class_row_min
        row_end = self.class_row_max
        column_start = (self.panel_image_column_max+1)
        column_end = self.class_column_max

        if row_start is not None and row_end is not None and column_start is not None and column_end is not None:
            for widget in self.root.grid_slaves():
#                if int(widget.grid_info()["row"]) >= row_start and int(widget.grid_info()["row"]) <= row_end:
                if int(widget.grid_info()["column"]) >= column_start:
                    widget.grid_forget()

        if self.class_list is None:
            return None

        current_min_row = None
        current_max_row = -1
        current_min_column = self.panel_image_column_max+1
        current_max_column = None
        for ndex, widget in enumerate(self.class_list):
            min_row, max_row, min_column, max_column = widget.grid(row=current_max_row+1,column=current_min_column)
            if current_min_row is None:
                current_min_row = min_row
            else:
                if min_row < current_min_row:
                    current_min_row = min_row
            if current_max_row is None:
                current_max_row = max_row
            else:
                if max_row > current_min_row:
                    current_max_row = max_row
            if current_min_column is None:
                current_min_column = min_column
            else:
                if min_column < current_min_column:
                    current_min_column = min_column
            if current_max_column is None:
                current_max_column = max_column
            else:
                if max_column > current_min_column:
                    current_max_column = max_column

#        self.btn_add_class = tki.Button(self.root, text='Add Class', command=self.add_new_class)
#        print('current_max_row: ', current_max_row)
        self.btn_add_class.grid(row=current_max_row+1,column=self.panel_image_column_max+1,sticky='nsew',padx=10,pady=10)
        self.btn_record_result.grid(row=current_max_row+1,column=self.panel_image_column_max+2,sticky='nsew',padx=10,pady=10)
        self.btn_save_class.grid(row=current_max_row+1,column=self.panel_image_column_max+3,sticky='nsew',padx=10,pady=10)
        self.btn_load_class.grid(row=current_max_row+1,column=self.panel_image_column_max+4,sticky='nsew',padx=10,pady=10)

        row_start = current_min_row
        row_end = current_max_row
        column_start = current_min_column
        column_end = current_max_column
        return row_start, row_end, column_start, column_end

    def add_new_class(self):
        if self.class_list is None:
            class_name = "0"
        else:
            class_name = (str(len(self.class_list)+1))
        self.class_list.insert(0, Classification(self.root, self, class_name, input_options=self.input_options))
        self.class_row_min, self.class_row_max, self.class_column_min, self.class_column_max = self.update_class()

    def remove_class(self, current_class):
        self.class_list.remove(current_class)
        self.class_row_min, self.class_row_max, self.class_column_min, self.class_column_max = self.update_class()

    def record_result(self):
        if self.btn_record_result['text'] == 'Start Recording':
            self.btn_record_result['text'] ="Stop Recording"
        else:
            self.btn_record_result['text'] ="Start Recording"

    def save_class(self):
        class_dict = {}
        for current_class in self.class_list:
            classification_name = current_class.get_class_name()
            mathematical_expressions = current_class.get_mathematical_operations()
            mathematical_expression_list = []
            for current_mathematical_expression in mathematical_expressions:
                current_expression = current_mathematical_expression.get_input()
                mathematical_expression_list.append(current_expression)
            if mathematical_expression_list is not None:
                class_dict[classification_name] = mathematical_expression_list

        if class_dict is not None:
            prefix = self.current_video_file_name.split(".")[0]
            save_file_name = prefix + '_' + self.current_person.get_name() + '_saved_class.json'
            with open(save_file_name, 'w+') as fp:
                json.dump(class_dict, fp)

    def load_class(self):
        prefix = self.current_video_file_name.split(".")[0]
        save_file_name = prefix + '_' + self.current_person.get_name() + '_saved_class.json'
        self.class_list.clear()
        try:
            fp = open(save_file_name, 'r')
        except:
            print("Could not open/read file:", save_file_name)
            self.class_row_min, self.class_row_max, self.class_column_min, self.class_column_max = self.update_class()
            return

#        with open(save_file_name, 'r') as fp:
        class_dict = json.load(fp)
        if class_dict is None:
            return None
        for key, value in class_dict.items():
            self.class_list.insert(0, Classification(self.root, self, key, mathematical_operations=value, input_options=self.input_options))
        self.class_row_min, self.class_row_max, self.class_column_min, self.class_column_max = self.update_class()

    def video_loop(self):
        try:
            # keep looping over frames until we are instructed to stop
            while not self.stop_event.is_set():
                if self.is_playing:
                    ret, full_frame = self.vs.read() # getting frame from camera 
                    if not ret: 
                        break # no more frames break

                    #  resizing frame
#                    self.frame_counter +=1 # frame counter
                    self.current_fps_interval_count += 1
                    current_fps = self.vs.get(cv2.CAP_PROP_POS_FRAMES)
                    frame_idx_is_allowed = ((current_fps % self.fps_interval) == 0)
                    if frame_idx_is_allowed is False:
#                    if self.current_fps_interval_count < self.fps_interval:
                        continue
                    else:
                        self.current_fps_interval_count = 0

                    self.frame = full_frame[self.current_person.row_init:self.current_person.row_init+self.current_person.height,self.current_person.col_init:self.current_person.col_init+self.current_person.width]

                    end_time = time.time()-self.start_time
                    fps = self.fps_interval/end_time# (frame_counter-last_frame)/end_time
                    self.start_time = time.time()

                    self.frame =textWithBackground(self.frame,f'FPS: {round(fps,1)}',self.font, 1.0, (30, 50), bgOpacity=0.9, textThickness=2)
                    self.frame =textWithBackground(self.frame,f'Mouse: {self.mouse_x},{self.mouse_y}',self.font, 0.5, (30, 200), bgOpacity=0.9, textThickness=1)

                    current_hour = math.floor(current_fps / (self.frame_fps * 3600))
                    current_minute = math.floor((current_fps - current_hour * 60 * 60 * self.frame_fps)/(self.frame_fps * 60))
                    current_second = math.floor((current_fps - current_hour * 60 * 60 * self.frame_fps - current_minute * self.frame_fps * 60)/(self.frame_fps))
                    current_time = str(current_hour) + ":" + str(current_minute) + ":" + str(current_second)
                    self.frame =textWithBackground(self.frame,f'Time: {current_time}',self.font, 1.0, (30, 100), bgOpacity=0.9, textThickness=2)
                    self.frame =textWithBackground(self.frame,f'Frame: {self.vs.get(cv2.CAP_PROP_POS_FRAMES)}',self.font, 1.0, (30, 150), bgOpacity=0.9, textThickness=2)

                    if self.slider_playback is not None:
                        if not self.slider_playback_is_focus:
                            self.slider_playback.set(int(float(self.vs.get(cv2.CAP_PROP_POS_FRAMES)) / float(self.vs.get(cv2.CAP_PROP_FRAME_COUNT)) * 10000.))

                    if self.btn_record_result is not None:
                        if self.btn_record_result['text'] == 'Stop Recording':
                            if not self.is_frame_in_section():
                                print('Not in section?')
                                if self.panel is not None:
                                    image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                                    image = Image.fromarray(image)
                                    image = ImageTk.PhotoImage(image)
                                    self.panel.configure(image=image)
                                    self.panel.image = image
                                continue

                    current_input_options = self.execute_algorithm()
#                    self.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS, landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
                    

                    image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                    image = Image.fromarray(image)
                    image = ImageTk.PhotoImage(image)
            
                    # if the panel is None, we need to initialize it
                    if self.panel is None:
                        self.panel = tki.Label(image=image)
                        self.panel.image = image
                        self.panel.grid(row=self.panel_image_row_min,column=self.panel_image_column_min,rowspan=self.panel_image_row_max-self.panel_image_row_min+1,columnspan=self.panel_image_column_max-self.panel_image_column_min+1)

                        self.bar1.get_tk_widget().grid(row=self.debugger_panels_row_min,column=0)

                        self.entry_playback_value.set(current_time)
                        self.entry_playback = tki.Entry(self.root,textvariable=self.entry_playback_value)
                        self.entry_playback.bind('<Return>',self.on_set_video_time_entry)
                        self.entry_playback.grid(row=self.slider_playback_panels_row_min, column=0, columnspan=1,sticky='nsew')

                        self.slider_playback = tki.Scale(self.root, from_=0, to=10000, orient=HORIZONTAL,command=self.on_set_video_time_slider)
                        self.slider_playback.bind('<Button-1>',self.set_slider_playback_focus)
                        self.slider_playback.bind('<ButtonRelease-1>',self.reset_slider_playback_focus)
                        self.slider_playback.grid(row=self.slider_playback_panels_row_min, column=1, columnspan=self.panel_image_column_max-1+1,sticky='nsew')
                        self.slider_playback.set(int(float(self.vs.get(cv2.CAP_PROP_POS_FRAMES)) / float(self.vs.get(cv2.CAP_PROP_FRAME_COUNT)) * 10000.))

                        # create a buttons
                        self.btn_pause = tki.Button(self.root, text="Pause",
                            command=self.on_pause)
                        self.btn_pause.grid(row=self.playback_panels_row_min ,column=1,sticky='nsew',padx=10,pady=10)

                        self.btn_resume = tki.Button(self.root, text="Resume",
                            command=self.on_resume)
                        self.btn_resume.grid(row=self.playback_panels_row_min ,column=0,sticky='nsew',padx=10,pady=10)

                        self.btn_backward = tki.Button(self.root, text="Backward",
                            command=self.on_backward_frame)
                        self.btn_backward.grid(row=self.playback_panels_row_min ,column=2,sticky='nsew',padx=10,pady=10)

                        self.btn_forward = tki.Button(self.root, text="Forward",
                            command=self.on_forward_frame)
                        self.btn_forward.grid(row=self.playback_panels_row_min ,column=3,sticky='nsew',padx=10,pady=10)

                        self.btn_prev_section = tki.Button(self.root, text="Prev",
                            command=self.on_prev_section)
                        self.btn_prev_section.grid(row=self.playback_panels_row_min ,column=4,sticky='nsew',padx=10,pady=10)

                        self.btn_next_section = tki.Button(self.root, text="Next",
                            command=self.on_next_section)
                        self.btn_next_section.grid(row=self.playback_panels_row_min ,column=5,sticky='nsew',padx=10,pady=10)

                        self.option_person = tki.OptionMenu(self.root, self.current_person_sv, *self.persons_list, command=self.on_person_changed)
                        self.option_person.grid(row=self.playback_panels_row_min ,column=self.panel_image_column_max,sticky='nsew')

                        ttk.Separator(self.root,orient=tki.HORIZONTAL).grid(row=self.separator_panels_row_min, columnspan=self.panel_image_row_max-self.panel_image_row_min+1, sticky='ew')

                        self.update_criteria()

                        self.btn_add_class = tki.Button(self.root, text='Add Class', command=self.add_new_class)
                        self.btn_add_class.grid(row=0,column=self.panel_image_column_max+1,sticky='nsew',padx=10,pady=10,rowspan=1)

                        self.btn_record_result = tki.Button(self.root, text='Start Recording', command=self.record_result)
                        self.btn_record_result.grid(row=0,column=self.panel_image_column_max+2,sticky='nsew',padx=10,pady=10,rowspan=1)
                                
                        self.btn_save_class = tki.Button(self.root, text='Save Class', command=self.save_class)
                        self.btn_save_class.grid(row=0,column=self.panel_image_column_max+3,sticky='nsew',padx=10,pady=10,rowspan=1)

                        self.btn_load_class = tki.Button(self.root, text='Load Class', command=self.load_class)
                        self.btn_load_class.grid(row=0,column=self.panel_image_column_max+3,sticky='nsew',padx=10,pady=10,rowspan=1)

                        self.load_class()
                    else:
                        self.panel.configure(image=image)
                        self.panel.image = image
                        self.check_remove_criteria()
                        self.to_estimates = self.get_criteria_summary()

#                    self.check_add_remove_update_evaluation(current_evaluations,row=0,column=6)

                    self.input_options = current_input_options
                    if self.input_options is None:
                        self.input_options = {"curr_frame": self.vs.get(cv2.CAP_PROP_POS_FRAMES)}
                    else:
                        self.input_options["curr_frame"] = self.vs.get(cv2.CAP_PROP_POS_FRAMES)

                if self.screen_capture_event.is_set():
                    self.screen_capture()

                if self.changed_event.is_set():
                    self.set_video_time()

                if self.resume_event.is_set():
                    self.resume_video()

                if self.pause_event.is_set():
                    self.pause_video()

                if self.person_changed_event.is_set():
                    self.person_changed()

        except RuntimeError as e:
            print("[INFO] caught a RuntimeError")        


    def execute_algorithm(self):
        pass

    def draw_landmarks(
        self,
        image: np.ndarray,
        landmark_list: landmark_pb2.NormalizedLandmarkList,
        connections: Optional[List[Tuple[int, int]]] = None,
        landmark_drawing_spec: Union[DrawingSpec,
                                    Mapping[int, DrawingSpec]] = DrawingSpec(
                                        color=RED_COLOR),
        connection_drawing_spec: Union[DrawingSpec,
                                    Mapping[Tuple[int, int],
                                            DrawingSpec]] = DrawingSpec()):
        """Draws the landmarks and the connections on the image.
        Args:
            image: A three channel BGR image represented as numpy ndarray.
            landmark_list: A normalized landmark list proto message to be annotated on
            the image.
            connections: A list of landmark index tuples that specifies how landmarks to
            be connected in the drawing.
            landmark_drawing_spec: Either a DrawingSpec object or a mapping from
            hand landmarks to the DrawingSpecs that specifies the landmarks' drawing
            settings such as color, line thickness, and circle radius.
            If this argument is explicitly set to None, no landmarks will be drawn.
            connection_drawing_spec: Either a DrawingSpec object or a mapping from
            hand connections to the DrawingSpecs that specifies the
            connections' drawing settings such as color and line thickness.
            If this argument is explicitly set to None, no landmark connections will
            be drawn.
        Raises:
            ValueError: If one of the followings:
            a) If the input image is not three channel BGR.
            b) If any connetions contain invalid landmark index.
        """
        if not landmark_list:
            return
        if image.shape[2] != _BGR_CHANNELS:
            raise ValueError('Input image must contain three channel bgr data.')
        image_rows, image_cols, _ = image.shape
        idx_to_coordinates = {}
        for idx, landmark in enumerate(landmark_list.landmark):
            if ((landmark.HasField('visibility') and
                landmark.visibility < _VISIBILITY_THRESHOLD) or
                (landmark.HasField('presence') and
                landmark.presence < _PRESENCE_THRESHOLD)):
                continue
            landmark_px = _normalized_to_pixel_coordinates(landmark.x, landmark.y,
                                                        image_cols, image_rows)
#            print('here?')
            if landmark_px:
#                print('here??')
                idx_to_coordinates[idx] = landmark_px
        if connections:
#            print('hei')
            num_landmarks = len(landmark_list.landmark)
            # Draws the connections if the start and end landmarks are both visible.
            for connection in connections:
#                print('hoi')
                start_idx = connection[0]
                end_idx = connection[1]
#                print('eiei')
                if not (0 <= start_idx < num_landmarks and 0 <= end_idx < num_landmarks):
                    raise ValueError(f'Landmark index is out of range. Invalid connection '
                                    f'from landmark #{start_idx} to landmark #{end_idx}.')
                if start_idx in idx_to_coordinates and end_idx in idx_to_coordinates:
#                    print('hui')
                    drawing_spec = connection_drawing_spec[connection] if isinstance(
                        connection_drawing_spec, Mapping) else connection_drawing_spec
#                    print('342')
                    cv2.line(image, idx_to_coordinates[start_idx],
                            idx_to_coordinates[end_idx], drawing_spec.color,
                            drawing_spec.thickness)
#                else:
#                    print('eh??')

#        cv2.imshow('image',image)
#        cv2.waitKey(10)

        # Draws landmark points after finishing the connection lines, which is
        # aesthetically better.
        if landmark_drawing_spec:
            for idx, landmark_px in idx_to_coordinates.items():
                drawing_spec = landmark_drawing_spec[idx] if isinstance(
                    landmark_drawing_spec, Mapping) else landmark_drawing_spec
                # White circle border
                circle_border_radius = max(drawing_spec.circle_radius + 1,
                                            int(drawing_spec.circle_radius * 1.2))
                cv2.circle(image, landmark_px, circle_border_radius, WHITE_COLOR,
                            drawing_spec.thickness)
                # Fill color into the circle
                cv2.circle(image, landmark_px, drawing_spec.circle_radius,
                            drawing_spec.color, drawing_spec.thickness)

        scale_percent = 60 # percent of original size
        width = int(image.shape[1] * scale_percent / 100)
        height = int(image.shape[0] * scale_percent / 100)
        dim = (width, height)
        
        # resize image
        local_image = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)        
        local_image = Image.fromarray(local_image)
        local_image = ImageTk.PhotoImage(local_image)
        if self.debugger_panel is None:
            self.debugger_panel = tki.Label(image=local_image)
            self.debugger_panel.image = local_image
            self.debugger_panel.grid(row=self.debugger_panels_row_min,column=1)
        else:
            self.debugger_panel.configure(image=local_image)
            self.debugger_panel.image = local_image

    def plot_landmarks(self, landmark_list: landmark_pb2.NormalizedLandmarkList,
                    connections: Optional[List[Tuple[int, int]]] = None,
                    landmark_drawing_spec: DrawingSpec = DrawingSpec(
                        color=RED_COLOR, thickness=5),
                    connection_drawing_spec: DrawingSpec = DrawingSpec(
                        color=BLACK_COLOR, thickness=5),
                    elevation: int = 10,
                    azimuth: int = 10):
        """Plot the landmarks and the connections in matplotlib 3d.
        Args:
            landmark_list: A normalized landmark list proto message to be plotted.
            connections: A list of landmark index tuples that specifies how landmarks to
            be connected.
            landmark_drawing_spec: A DrawingSpec object that specifies the landmarks'
            drawing settings such as color and line thickness.
            connection_drawing_spec: A DrawingSpec object that specifies the
            connections' drawing settings such as color and line thickness.
            elevation: The elevation from which to view the plot.
            azimuth: the azimuth angle to rotate the plot.
        Raises:
            ValueError: If any connetions contain invalid landmark index.
        """
        if not landmark_list:
            return
#        plt.figure(figsize=(10, 10))
#        ax = plt.axes(projection='3d')
#        self.ax.view_init(elev=elevation, azim=azimuth)
        self.ax.cla()
        plotted_landmarks = {}
        x_data = []
        y_data = []
        z_data = []
        for idx, landmark in enumerate(landmark_list.landmark):
            if ((landmark.HasField('visibility') and
                landmark.visibility < _VISIBILITY_THRESHOLD) or
                (landmark.HasField('presence') and
                landmark.presence < _PRESENCE_THRESHOLD)):
                continue
            x_data.append(-landmark.z)
            y_data.append(landmark.x)
            z_data.append(-landmark.y)
            plotted_landmarks[idx] = (-landmark.z, landmark.x, -landmark.y / 720 * 1280)
        self.ax.scatter3D(x_data,y_data,z_data)

#            self.ax.scatter3D(
#                xs=[-landmark.z],
#                ys=[landmark.x],
#                zs=[-landmark.y],
#                color=_normalize_color(landmark_drawing_spec.color[::-1]),
#                linewidth=landmark_drawing_spec.thickness)
#            plotted_landmarks[idx] = (-landmark.z, landmark.x, -landmark.y)

        if connections:
#            print('connections')
            num_landmarks = len(landmark_list.landmark)
            # Draws the connections if the start and end landmarks are both visible.
            for connection in connections:
                start_idx = connection[0]
                end_idx = connection[1]
#                print(start_idx, end_idx)
                if not (0 <= start_idx < num_landmarks and 0 <= end_idx < num_landmarks):
                    raise ValueError(f'Landmark index is out of range. Invalid connection '
                                    f'from landmark #{start_idx} to landmark #{end_idx}.')
                if start_idx in plotted_landmarks and end_idx in plotted_landmarks:
                    landmark_pair = [
                        plotted_landmarks[start_idx], plotted_landmarks[end_idx]
                    ]
                    self.ax.plot3D(
                        xs=[landmark_pair[0][0], landmark_pair[1][0]],
                        ys=[landmark_pair[0][1], landmark_pair[1][1]],
                        zs=[landmark_pair[0][2], landmark_pair[1][2]],
                        color=_normalize_color(connection_drawing_spec.color[::-1]),
                        linewidth=connection_drawing_spec.thickness)
##        plt.pause(.001)
##        plt.show()

        self.figure.canvas.draw()
        self.figure.canvas.flush_events()
