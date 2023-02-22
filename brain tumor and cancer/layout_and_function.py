from collections import deque
from typing import Dict
import threading
import os
import flet
from flet import *
from flet import (
    ElevatedButton,
    FilePicker,
    FilePickerResultEvent,
    FilePickerUploadEvent,
    FilePickerUploadFile,
    Page,
    ProgressRing,
    Ref,
    Row,
    Text,
    icons,
    Image,
    ResponsiveRow,
    VerticalDivider,
    Card,
    UserControl
)
from flet.column import Column

class MainApp(UserControl):
    def __init__(self, pg:Page):
        super().__init__()
        self.prog_bars: Dict[str, ProgressRing] = {}
        self.files = Ref[Column]()
        self.upload_button = Ref[ElevatedButton]()
        self.pg = pg
        self.ret = Row([Column([Row(
            [Row(vertical_alignment=CrossAxisAlignment.START,controls=[Column([ElevatedButton(
                "Select files...",
                icon=icons.FOLDER_OPEN,
                on_click=lambda _: self.file_picker.pick_files(allow_multiple=True),
            ),
            Column(ref=self.files),
            ElevatedButton(
                "Upload",
                ref=self.upload_button,
                icon=icons.UPLOAD,
                on_click=self.upload_files,
                disabled=True,
            ),])]),
                    Card(content=Container(height= 450, width= 850, padding=8, content=Column(controls=[])))]),
                    Column([Row(alignment= MainAxisAlignment.CENTER ,controls=[ElevatedButton(text='IMAGE', icon=icons.IMAGE, on_click=lambda e:self.show_image(e)),
                                                                                ElevatedButton(text='PREDICT', icon=icons.ARROW_BACK, on_click=lambda e:self.pred_image(e)),
                                                                                 ElevatedButton(text='CLEAR', icon=icons.DELETE_ROUNDED, on_click=lambda e:self.clear_pg(e))]),
                    Text('RESULTS'),
                    Card(content=Container(height= 70, width=1000, padding=8, content=Column(controls=[]))),])])
        ])
                    
    def build(self):
        self.file_picker = FilePicker(on_result=self.file_picker_result, on_upload=self.on_upload_progress)
        self.pg.overlay.append(self.file_picker)
        self.img = Row() 

        
        print(self.ret.controls[0].controls[1].controls[2].content.content.controls)
        return self.ret
        
    def file_picker_result(self,e: FilePickerResultEvent):
        self.upload_button.current.disabled = True if e.files is None else False
        self.prog_bars.clear()
        self.files.current.controls.clear()
        if e.files is not None:
            for f in e.files:
                prog = ProgressRing(value=0, bgcolor="#eeeeee", width=20, height=20)
                self.prog_bars[f.name] = prog
                self.files.current.controls.append(Row([prog, Text(f.name)]))
        self.update()

    def on_upload_progress(self,e: FilePickerUploadEvent):
        self.prog_bars[e.file_name].value = e.progress
        self.prog_bars[e.file_name].update()
        self.update()
             
    def upload_files(self,e):
        uf = []
        uf = deque(uf)
        if self.file_picker.result is not None and self.file_picker.result.files is not None:
            for f in self.file_picker.result.files:
                uf.appendleft(
                    FilePickerUploadFile(
                        f.name,
                        upload_url=self.pg.get_upload_url(f.name, 600),
                    )
                )
        uf = list(uf)
        self.file_picker.upload(uf)
        self.update()
        
    
    #A function that displays the selected image              
    def show_image(self, e):
        path_of_the_directory = f'assets/uploads'
        folder_walk = os.walk(path_of_the_directory)
        first_file = next(folder_walk)[2][0]
        f = os.path.join(path_of_the_directory, first_file)
        path = f
        img = Image(height=450, width=850,
        src=path,
        fit="contain",
        )
        self.ret.controls[0].controls[0].controls[1].content.content.controls.append(img)
        self.update()
    
    #A function to predict the selected image    
    def pred_image(self, e):
        import tensorflow as tf
        from keras.preprocessing import image
        from keras.models import  model_from_json
        from keras.utils import load_img, img_to_array
        path_of_the_directory = f'assets/uploads'
        folder_walk = os.walk(path_of_the_directory)
        first_file = next(folder_walk)[2][0]
        f = os.path.join(path_of_the_directory, first_file)
        path = f
        import numpy as np
        json_file = open('model.json', 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        loaded_model = model_from_json(loaded_model_json)
        loaded_model.load_weights("brainmodel.h5")
        test_image = load_img(path, target_size = (240, 240))
        test_image = img_to_array(test_image)
        test_image = np.expand_dims(test_image, axis = 0)
        test_image = test_image/255
        #Changes in code
        pred = loaded_model.predict(test_image)
        result = np.where(pred > 0.5, 1, 0) #<--to get the binary category
        if result ==1:
            self.ret.controls[0].controls[1].controls[2].content.content.controls.append(Text('The tumor is cancerous'))
        else:
            self.ret.controls[0].controls[1].controls[2].content.content.controls.append(Text('The tumer is not cancerous'))
        self.update()
    
    #A function to clear the page for a new working area    
    def clear_pg(self, e):
        path1 = f'assets/uploads'
        os.chdir(path1)
        all_files = os.listdir()
        for f in all_files:
            os.remove(f)
            
        lst = self.ret.controls[0].controls[0].controls[1].content.content.controls
        lst.remove(lst[0])
        lst1 = self.ret.controls[0].controls[1].controls[2].content.content.controls
        lst1.remove(lst1[0])
        self.update()
  
    
    
    
        

