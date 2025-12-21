from Libraries.imports import *


class FeedBackScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = MDApp.get_running_app()

    def on_enter(self, *args):
        self.user_id = self.app.user_details["user_id"]
        self.mr_code = self.app.root.get_screen('marriage_home').ids.mar_code.text.upper()
        self.layout = self.ids.feedback_layout
        self.top_label = MDLabel(text=f"Marriage Code : {self.mr_code}", halign="center", font_style="H4",
                            adaptive_height=True)
        self.layout.add_widget(self.top_label)
        self.feedback_label = MDLabel(text=f"Please Enter your Valuable Feedback for this Marriage.It could be anything like"
                                     f" Food,Greeting,Hall,Sounds etc,.", halign="left",
                                font_style="H6", adaptive_height=True)
        self.feedback_text = MDTextField(hint_text=f"Your Feedback...")
        self.layout.add_widget(self.feedback_label)
        self.layout.add_widget(self.feedback_text)
        self.feedback_button = MDRaisedButton(text="SEND 💌", pos_hint={"center_x": 0.5}, font_name="Segoe-UI-Emoji",
                                         on_release=lambda x: self.save_feedback())
        self.layout.add_widget(self.feedback_button)

    def save_feedback(self,*args):
        payload = {"query": {"marriage_code": self.mr_code, "user_id": self.user_id }, "require": {}}
        self.feedback_check = self.app.api.post("/find/marriage_feedbacks", json=payload)
        cursor_to_list = list(self.feedback_check)
        if len(cursor_to_list) != 0:
            self.app.show_dialog("Already Done",
                                   "Hope you have already provided your feedbacks!")
        else:
            self.feedback_data = { "user_id" : self.user_id,
                                  "marriage_code" : self.mr_code,
                                   "feedback":self.feedback_text.text
                                 }
            if self.inserted:
                self.app.show_dialog("Already Inserted",
                                         "Hope you have already joined with us with your inputs!")
            else:
                feedback_insert = self.app.api.post("/insert/marriage_feedbacks",json=self.feedback_data)
                self.inserted = True
                MDSnackbar(MDIcon(icon='hands-pray',adaptive_height=True,adaptive_width=True,
                                           size_hint_y=None),
                MDLabel(text="Thanks for your Feedback.We will work on it!!!"),
                        snackbar_x="30dp",
                        snackbar_y="30dp",
                        md_bg_color=(0, 128, 0, 1),
                        orientation="horizontal",
                        duration=3
                ).open()

