from Libraries.imports import *

class MarriageHomeScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = MDApp.get_running_app()

    def on_enter(self):
        if not "user_id" in self.app.user_details:
            self.app.change_screen("home")
            return
        else:
            self.user_id = self.app.user_details["user_id"]
            self.current_screen = self.app.root.get_screen('marriage_home')
            self.grid_layout = self.current_screen.ids.grid_layout


    def show_marriage_options(self,mr_code):
        self.cards = ["video","gift","photos","feedback"]
        self.grid_layout.clear_widgets()
        self.mr_code = mr_code
        photo_screen = self.app.root.get_screen("photo_screen")
        if photo_screen.textures:
            photo_screen.textures = []

        self.marriage_details = self.app.api.get("/marriage_invites/by_field/marriage_code/"+self.mr_code.upper())

        if 'user_id' not in self.marriage_details:
            self.app.show_dialog("Invalid Code", "Not a valid MR Code ,If its valid please logout and login again")
            return

        payload = { "query" : {"user_id": self.user_id,"marriage_code":self.mr_code.upper()},"require": {}}
        self.response_dict = self.app.api.post("/find_one/marriage_responses",json=payload)


        if not self.response_dict and self.user_id != self.marriage_details["user_id"]:
            self.app.show_dialog("No Option", "Sorry, Either You have not responded to this MR or You are not Inviter")
            return

        for card in self.cards:

            add_card = MDCard(
                id=f"{card}",
                size_hint=(0.45,None),
                #size=("200dp", "200dp"),
                height="200dp",
                radius=[20],
                ripple_behavior=True,
                elevation=8,
                on_release=lambda x: self.card_clicked(x)
            )


            bg = MDRelativeLayout(FitImage(
                source=f"{card}.JPG",
                radius=[20]
            ))


            arrow_btn = MDIconButton(
                icon="chevron-right",
                id=f"{card}",
                pos_hint={"center_y": 0.01, "right": 1},
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),
                md_bg_color=(0, 0, 0, 0.5),
                on_release=lambda x: self.card_clicked(x)
            )
            print(f"Card in upper function is {card}")
            bg.add_widget(arrow_btn)
            add_card.add_widget(bg)
            self.grid_layout.add_widget(add_card)

    def card_clicked(self,instance):
        call_method = getattr(self,f"{instance.id}_clicked")
        call_method(instance)

    def video_clicked(self,instance):
        video_screen = self.app.root.get_screen("video_screen")
        video_screen.on_enter()
        self.app.change_screen("video_screen")
        video_screen.show_video(self.mr_code)



    def gift_clicked(self,instance):
        self.app.change_screen("gift_screen")

    def photos_clicked(self,instance):
        #If photos screen already loaded , then reset the photo memory textures
        self.app.change_screen("photo_screen")
        print(instance.id)

    def feedback_clicked(self,instance):
        self.app.change_screen("feedback_screen")