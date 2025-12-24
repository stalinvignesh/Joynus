from kivy.core.text import LabelBase

from Libraries.imports import *
import requests_cache
#To avoid circular import , import app related classes locally
from AppClasses.Profile import ProfileScreen
from AppClasses.SentScreen import SentScreen
from AppClasses.VideoScreen import VideoScreen
from AppClasses.ReceivedScreen import ReceivedScreen
from AppClasses.APIClient import APIClient
from AppClasses.MapScreen import MapScreen
from AppClasses.MarriageHomeScreen import MarriageHomeScreen
from AppClasses.PhotoScreen import PhotoScreen
from AppClasses.PhotoScreen import PhotoViewerScreen
from AppClasses.GiftScreen import GiftScreen
from AppClasses import FeedBackScreen
#os.environ["KIVY_GL_BACKEND"] = "angle_sdl2"
#from kivy.config import Config
#Config.set('graphics', 'multisamples', '0')
#os.environ["KIVY_GL_BACKEND"] = "sdl2"
#os.environ["KIVY_GL_CONFIG"] = "depthsize=0, stencilsize=0"
#os.environ['PATH'] += r'C:\Users\admin\AppData\Local\Programs\Python\Python312\share\gstreamer\1.0\msvc_x86_64\bin'
#os.environ['PATH'] += r'C:\Users\admin\AppData\Local\Programs\Python\Python312\share\gstreamer\1.0\msvc_x86_64\lib'
#os.environ['PATH'] += r'C:\Users\admin\AppData\Local\Programs\Python\Python312\share\gstreamer\1.0\msvc_x86_64\include'


class LoginScreen(Screen):
    pass

class OTPScreen(Screen):
    pass


class HomeScreen(Screen):
    def on_enter(self):
        self.app = MDApp.get_running_app()
        if not hasattr(self.app,"user_details"):
            self.show_user_form()
        else:
            self.ids.phone_label.text = (f"Welcome {self.app.user_details["name"]} ,"
                                         f"to the world of celebration!!!")
            print("User "+self.app.user_details["name"])

    def show_user_form(self):
        self.form_content = Builder.load_string('''
MDBoxLayout:
    orientation: "vertical"
    spacing: "12dp"
    size_hint_y: None
    adaptive_height : True

    MDTextField:
        id: name_input
        hint_text: "Full Name"
        write_tab: False
    MDTextField:
        id: mobile_input
        hint_text: "Mobile Number"
        input_filter: "int"
        max_text_length: 10
        write_tab: False
    MDTextField:
        id: age_input
        hint_text: "Age"
        input_filter: "int"
        write_tab: False
    MDTextField:
        id: email_input
        hint_text: "Email ID"
        write_tab: False
        helper_text_mode: "on_error"
    MDTextField:
        id: pin_input
        hint_text: "Six Digit PIN To Login"
        input_filter: "int"
        password: True
        max_text_length: 6
        write_tab: False
''')

        self.form_dialog = MDDialog(
            title="Your Details Please",
            type="custom",
            content_cls=self.form_content,
            buttons=[
                MDRaisedButton(text="CANCEL", on_release=lambda x: self.form_dialog.dismiss()),
                MDRaisedButton(text="SUBMIT", on_release=lambda x: self.save_user_details())
            ],
        )
        self.form_dialog.open()

    def save_user_details(self):
        name = self.form_content.ids.name_input.text.strip()
        age = self.form_content.ids.age_input.text.strip()
        email = self.form_content.ids.email_input.text.strip()
        pin = self.form_content.ids.pin_input.text.strip()
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        pin_hash = pwd_context.hash(pin)

        if not name or not age or not email or not pin:
            self.show_dialog("Incomplete Form", "Please fill in all fields.")
            return

        today_date = str(datetime.now())
        pipeline = [
            {"$group": {"_id": None, "max_uid": {"$max": "$user_id"}}}
        ]
        response = self.app.api.post("/aggregate/user_data", json=pipeline)
        max_uid = response[0]["max_uid"] if response else 0
        max_uid += 1
        self.user_data = {
            "user_id": max_uid,
            "mobile": self.app.phone_number,
            "name": name,
            "age": age,
            "created_date": today_date,
            "last_login" : today_date,
            "email": email,
            "pin": pin_hash,
            "is_pin_permanent": True,
        }
        print(self.user_data)
        ins = self.app.api.post("/insert/user_data",json=self.user_data)
        #self.app.store.put(self.app.phone_number, **self.user_data)
        if "id" in ins:
            self.app.show_dialog("Welcome","Thank you for registering "+name)
            self.form_dialog.dismiss()
            with requests_cache.disabled():
                self.app.user_details = self.app.api.get(f"/user_data/by_field/mobile/{self.app.phone_number}")
            if "id" in self.app.user_details:
                payload = {"query": {"mobile": self.app.phone_number}, "data": {"last_login": str(datetime.now())}}
                print(f"user details {self.app.user_details}")
                update_last_login = self.app.api.put("/update/user_data", json=payload)
                self.app.store.put("user", phone=self.app.phone_number,token=self.app.api.access_token)
                self.ids.phone_label.text = (f"Welcome {self.app.user_details["name"]} ,"
                                             f"to the world of celebration!!!")
        else:
            self.app.show_dialog("Error","Error in Registering")

class AttendMarriageScreen(Screen):
    def on_enter(self):
        self.app = MDApp.get_running_app()
        if not "name" in self.app.user_details:
            self.app.change_screen("home")

class InvitesScreen(Screen):
    pass

class RequestToAttendScreen(Screen):

    def __init__(self,**kwargs):
        super(RequestToAttendScreen,self).__init__(**kwargs)
        self.app = MDApp.get_running_app()

    def on_enter(self, *args):
        if not "name" in self.app.user_details:
            self.app.change_screen("home")
        else:
            if hasattr(self.app,'update_resp'):
                self.is_update=True
                self.marriage_code = self.app.update_resp['marriage_code']
            else:
                self.is_update=False
                self.marriage_code = self.app.root.get_screen("attend_marriage").ids.marriage_code.text
            self.marriage_code = self.marriage_code.upper()
            self.user_name = self.app.user_details["name"]
            self.selected_relation = ""
            self.engagement_state = False
            self.dynamic_input = ObjectProperty()
            self.inserted = False
            self.container = self.ids.response_box
            self.container.add_widget(MDLabel(text="Marriage Code "+self.marriage_code))
            self.container.add_widget(MDLabel(text="Your Name "+self.user_name+" and please select anyone below"
                                                                                " on how the inviter is related to you"))

            #segment_control = MDSegmentedControl(on_active=lambda x: self.on_selection())
            #segment = MDSegmentedButton()
            #container.add_widget(segment)
            segment_kivy = '''
MDBoxLayout:
    orientation: 'vertical'
    id : segment_box
    size_hint_y : None
    padding : 20
    spacing: 20
    #adaptive_height: True
    MDSegmentedButton:
        size_hint_x: 1
        on_marked : app.root.ids.request_to_attend.on_selection(*args)
      
        MDSegmentedButtonItem:
            id : friend
            text: "Friend"
    
        MDSegmentedButtonItem:
            id : family
            text: "Family"
            
        MDSegmentedButtonItem:
            id : colleague
            text: "Colleague"
            
        MDSegmentedButtonItem:
            id: business_associate
            text: "Business Associate"
    
        MDSegmentedButtonItem:
            id : other
            text: "Other"

'''
            self.segment_obj = Builder.load_string(segment_kivy)
            self.container.add_widget(self.segment_obj)
            self.user_id = self.app.user_details["user_id"]
            #self.seg_container = self.app.root.get_screen("request_to_attend").ids.segment_box
            if not self.is_update:

                payload = { "query" : {"marriage_code" : self.marriage_code , "user_id" : self.user_id } ,
                            "require" : { "_id" : 0} }
                self.response_check = self.app.api.post("/find/marriage_responses",json=payload)
                cursor_to_list = list(self.response_check)
                if len(cursor_to_list) != 0:
                    self.app.show_dialog("Already Joined", "Hope you have already joined with us with your inputs! Meet you soon!")
                    self.app.change_screen('attend_marriage')

            payload = {"query" : {"marriage_code" : self.marriage_code} , "require" :  {"food_preference" : 1,
                                                                                        "food_options": 1,
                                                                                        "engagement_date":1,
                                                                                        "accommodation_provided":1} }
            self.invite_cur = self.app.api.post("/find/marriage_invites",json=payload)
            for self.invite_data in self.invite_cur:
                self.container.add_widget(MDLabel(text="Food Provided :"+self.invite_data["food_preference"]))
                served_list = self.invite_data["food_options"].split("|")
                self.people_count = {}
                for served in served_list:
                    self.container.add_widget(MDLabel(text=served))
                    served_text = MDTextField(id=served+"_food",
                                                          hint_text="Please enter no of people available for "+served,
                                                          write_tab=False,input_filter="int",max_text_length=3)
                    self.container.add_widget(served_text)
                    self.people_count[served] = served_text
            if self.is_update and 'food_count' in self.app.update_resp:
                for served, count in self.app.update_resp['food_count'].items():
                    self.people_count[served].text = count

            inner_layout = MDBoxLayout(orientation="horizontal",spacing="20",padding=10,adaptive_size=True,size_hint_y=None)
            self.container.add_widget(inner_layout)
            if self.invite_data["engagement_date"]:
                inner_layout.add_widget(
                    MDLabel(text="Available for Engagement on " + self.invite_data["engagement_date"] + " ?",
                            adaptive_size=True,size_hint_y=None,pos_hint={"center_y": 0.5}))
                engagement_check = MDSwitch(icon_active="check",size_hint_y=None,pos_hint={"center_y": 0.5})
                engagement_check.bind(active=self.check_active)
                inner_layout.add_widget(engagement_check)

            if self.invite_data["accommodation_provided"]:
                self.switch_layout = MDBoxLayout(orientation="horizontal",spacing="35",padding=10,adaptive_height=True,
                                                 size_hint_y=None)
                self.container.add_widget(self.switch_layout)
                self.switch_layout.add_widget(MDLabel(text="Need Accommodation?",adaptive_size=True,size_hint_y=None,
                                                      pos_hint={"center_y": 0.5}))
                switch = MDSwitch(icon_active="check",size_hint_y=None,pos_hint={"center_y": 0.5})
                switch.bind(active=self.get_active)
                #switch.bind(on_thumb_down=self.clear_input)
                self.switch_layout.add_widget(switch)
            self.dynamic_input = None
            self.response_input = MDTextField(
                hint_text="Any short message response that you want to send inviter ", max_text_length=200,
                mode="fill", write_tab=False,size_hint_y=None,
                pos_hint={"center_x": 0.5})
            button_text = "Ok! Let's Go to Wedding"
            if self.is_update:
                button_text = "Update it!"
                self.response_input.text = self.app.update_resp['response_message']
            self.go_button = MDRaisedButton(text=button_text,pos_hint={"center_x": 0.5},size_hint_y=None)
            self.container.add_widget(self.response_input)
            self.container.add_widget(self.go_button)
            self.go_button.bind(on_release=self.save_response)


    def save_response(self,instance):
        if self.is_update:
            response_id = self.app.update_resp['response_id']
        else:
            response_id = self.app.get_increament("marriage_responses","response_id")
        food_count = {}
        for served,count_text_obj in self.people_count.items():
            food_count[served] = count_text_obj.text
        accommodation_text = self.dynamic_input.text if self.dynamic_input else ""
        self.selected_relation = self.text_field.text if hasattr(self,"text_field") else self.selected_relation
        if not self.selected_relation:
            self.app.show_dialog("Check Relation","Please provide your relation with your inviter")
            return
        marriage_response = {
            "user_id" : self.user_id,
            "response_id" : response_id,
            "response_type" : "in-person",
            "marriage_code" : self.marriage_code,
            "user_name" : self.user_name,
            "inviter_relation" : self.selected_relation,
            "food_count" : food_count,
            "engagement_availability" : self.engagement_state,
            "accommodation_needed" : accommodation_text,
            "response_message" : self.response_input.text

        }
        marriage_response_upd = {
            "user_id" : self.user_id,
            "response_type" : "in-person",
            "marriage_code" : self.marriage_code,
            "user_name" : self.user_name,
            "inviter_relation" : self.selected_relation,
            "food_count" : food_count,
            "engagement_availability" : self.engagement_state,
            "accommodation_needed" : accommodation_text,
            "response_message" : self.response_input.text

        }
        if self.inserted:
            self.app.show_dialog("Already Inserted", "Hope you have already joined with us with your inputs")
            self.app.change_screen('attend_marriage')
        else:
            if not self.is_update:
                self.response_insert = self.app.api.post("/insert/marriage_responses", json=marriage_response)
                self.inserted = True
                print("inside else " + str(self.inserted))
                #print(marriage_response)
                MDSnackbar(MDIcon(icon='hands-pray',adaptive_height=True,adaptive_width=True,
                                           size_hint_y=None),
                       MDLabel(text="Hey " + self.user_name + ".Thank you for joining us."
                                                                 "We'll make the Celebration more joyous with you!!!"),
                       snackbar_x="30dp",
                       snackbar_y="30dp",
                       md_bg_color=(0, 128, 0, 1),orientation="horizontal",
                       duration=3
                       ).open()
            elif self.is_update :
                payload = { "query" : {"user_id" :self.user_id ,"marriage_code": self.marriage_code ,
                                       "response_id" : response_id} ,
                            "data" : marriage_response_upd }
                self.response_update = self.app.api.put("/update/marriage_responses",json=payload)
                self.inserted = True
                MDSnackbar(MDIcon(icon='hands-pray',adaptive_height=True,adaptive_width=True,
                                           size_hint_y=None),
                       MDLabel(text="Hey " + self.user_name + ".Thank you for update decision."
                                                                 "We'll make the Celebration more joyous with you!!!"),
                       snackbar_x="30dp",
                       snackbar_y="30dp",
                       md_bg_color=(0, 128, 0, 1),orientation="horizontal",
                       duration=3
                       ).open()




    def get_active(self,switch,is_active):
        print("Inside"+str(is_active))
        if is_active:
            if not self.dynamic_input:
                self.dynamic_input = MDTextField(
                    hint_text="Rooms:",max_text_length=2,mode="rectangle",write_tab=False,
                    pos_hint={"x": .9},size_hint_x=None,width="80dp",input_filter="int"
                )
                self.switch_layout.add_widget(self.dynamic_input)
        else:
            if self.dynamic_input and self.dynamic_input.parent:
                self.switch_layout.remove_widget(self.dynamic_input)
                self.dynamic_input = None

    def check_active(self,engagement_check,is_active):
        if is_active:
            print("check active")
            self.engagement_state = True
        else:
            print("check inactive")
            self.engagement_state = False

    def on_selection(self,segment_button, segment_item,bool_obj):
        selected = segment_item.text

        if selected != "Other":
            self.selected_relation = selected
            self.remove_text_field()
            print(self.selected_relation)
        elif selected == "Other":
            self.remove_text_field()
            self.text_field = MDTextField(hint_text="Your Relation Please",write_tab=False)
            self.text_field.my_tag = "remove"
            self.segment_obj.add_widget(self.text_field)
            print(self.selected_relation)

    def remove_text_field(self):
        for child in self.segment_obj.children[:]:  # copy the list to avoid mutation issues
            if hasattr(child, "my_tag") and child.my_tag == "remove":
                self.segment_obj.remove_widget(child)

    #def on_pre_enter(self, *args):
    #    self.ids.response_box.clear_widgets()

    def on_leave(self, *args):
        self.container.clear_widgets()
        if hasattr(self.app,'update_resp'):
            delattr(self.app,'update_resp')



class ReceivedInvitesScreen(Screen):

    def __init__(self,**kwargs):
        super(ReceivedInvitesScreen,self).__init__(**kwargs)
        self.app = MDApp.get_running_app()
        self.inserted = False


    def on_enter(self, *args):
        self.container = self.ids.received_box

        #self.spinner = MDSpinner(size_hint=(None, None),color=[1, 0.4, 0, 1], size=("50dp", "50dp"), pos_hint={"center_x": 0.5, 'center_y': .5})
        #self.container.add_widget(self.spinner)
        #print(str(self.spinner))
        if not "name" in self.app.user_details:
            self.app.change_screen('home')
        else:
            self.user_name = self.app.user_details["name"]
            self.marriage_code = self.app.root.get_screen("attend_marriage").ids.marriage_code.text
            self.marriage_code = self.marriage_code.upper()
            self.invites_dict = self.app.api.get("/marriage_invites/by_field/marriage_code/"+self.marriage_code)
            if not self.invites_dict:
                self.app.show_dialog("Not Exist","There is no such Marriage Code")
                self.app.change_screen('attend_marriage')
            else:
                container = self.ids.received_box

                #container.clear_widgets()
                #local_dict = self.invites_dict
                start = 0
                for key , d_value in self.invites_dict.items():
                    #print(key)
                    card = MDCard(
                        orientation="horizontal",
                        padding=20,
                        size_hint=[None,None],
                        #size=["700dp", "60dp"],
                        #adaptive_size=True,
                        #pos_hint={"center_x": 0.5, "center_y": .4},
                        adaptive_size=True,
                        ripple_behavior=True,
                        elevation=8,
                        size_hint_y=None,
                        style="elevated",
                        md_bg_color="darkgrey",
                        radius=[20, 20, 20, 20],
                    )
                    #content = MDRelativeLayout(orientation="horizontal", spacing=25)
                    if key == "groom" and start == 0:
                        start+=1
                        self.ids.spin.active = False
                        #self.container.remove_widget(self.spinner)
                        #content.add_widget(MDRelativeLayout(orientation="horizontal", spacing=15))
                        card.add_widget(MDIcon(icon='hand-heart',adaptive_height=True,adaptive_width=True,
                                               theme_text_color="Custom",text_color=( 1, 0.4, 0, 1 ),size_hint_y=None))
                        card.add_widget(MDLabel(text=f"[b][color=#008000]{self.invites_dict['groom']}[/b] [i]Weds[/i] "
                                                    f"[b]{self.invites_dict['bride']}[/b]",adaptive_height=True,
                                            adaptive_width=True,size_hint_y=None,halign='center',
                                               theme_text_color="Primary",pos_hint={"center_x": 0.6,"center_y": 0.3},markup=True,
                                                text_color=( 0, 128, 0, 1 )))
                        self.add_content(card,container)
                        Clock.schedule_once(lambda dt, c=card, i=start: self.animate_card(c, delay=0.1 * start), 0.1 * start)

                    elif key == "marriage_date" and start == 1:
                        start+=1
                        #content.add_widget(MDRelativeLayout(orientation="horizontal", spacing=15))
                        card.add_widget(MDIcon(icon='calendar-heart',adaptive_height=True,adaptive_width=True,
                                               theme_text_color="Custom",text_color=( 1, 0.4, 0, 1 ),size_hint_y=None))
                        card.add_widget(MDLabel(text=f"[color=#008000]On the wonderful day [b][i]{self.invites_dict['marriage_date']}",adaptive_height=True,
                                            adaptive_width=True,size_hint_y=None,halign='center',text_color=( 0, 128, 0, 1 ),
                                               theme_text_color="Primary",pos_hint={"center_x": 0.6,"center_y": 0.3},markup=True))
                        self.add_content(card, container)
                        Clock.schedule_once(lambda dt, c=card, i=start: self.animate_card(c, delay=0.1 * start),
                                            0.1 * start)
                    elif key == "engagement_date" and start == 2 and d_value:
                        start+=1
                        #content.add_widget(MDRelativeLayout(orientation="horizontal", spacing=15))
                        card.add_widget(MDIcon(icon='calendar-clock',adaptive_height=True,adaptive_width=True,
                                               theme_text_color="Custom",text_color=( 1, 0.4, 0, 1 ),size_hint_y=None))
                        card.add_widget(MDLabel(text=f"[color=#008000]We Will get [i]engaged[/i] on [b][i]{self.invites_dict['engagement_date']}",adaptive_height=True,
                                            adaptive_width=True,size_hint_y=None,halign='center',text_color=( 0, 128, 0, 1 ),
                                               theme_text_color="Primary",pos_hint={"center_x": 0.6,"center_y": 0.3},markup=True))
                        self.add_content(card, container)
                        Clock.schedule_once(lambda dt, c=card, i=start: self.animate_card(c, delay=0.1 * start),
                                            0.1 * start)
                    elif key == "engagement_date" and not d_value:
                        start+=1
                    elif key == "venue" and start == 3:
                        start+=1
                        #content.add_widget(MDRelativeLayout(orientation="horizontal", spacing=15))
                        card.add_widget(MDIcon(icon='map-marker-radius',adaptive_height=True,adaptive_width=True,
                                               theme_text_color="Custom",text_color=( 1, 0.4, 0, 1 ),size_hint_y=None))
                        card.add_widget(MDLabel(text=f"[color=#008000]It is happening at "
                                                        f"[b]{self.invites_dict['venue']}[/b] "
                                                        f"with lot of love and "
                                                        f"[i]{self.invites_dict['food_preference']} "
                                                        f"{self.invites_dict['food_options']}[/i] foods to enjoy!",adaptive_height=True,
                                            adaptive_width=True,size_hint_y=None,halign='center',text_color=( 0, 128, 0, 1 ),
                                                   theme_text_color="Primary",pos_hint={"center_x": 0.6,"center_y": 0.3},markup=True))
                        self.add_content(card,container)
                        Clock.schedule_once(lambda dt, c=card, i=start: self.animate_card(c, delay=0.1 * start),
                                            0.1 * start)
                    elif key == "welcome_message" and start == 4 and d_value:
                        start+=1
                        #content.add_widget(MDRelativeLayout(orientation="horizontal", spacing=15))
                        card.add_widget(MDIcon(icon='human-greeting',adaptive_height=True,adaptive_width=True,
                                               theme_text_color="Custom",text_color=( 1, 0.4, 0, 1 ),size_hint_y=None))
                        card.add_widget(MDLabel(text=f"[color=#008000][i]{self.invites_dict['welcome_message']}[/i]",adaptive_height=True,
                                            adaptive_width=True,size_hint_y=None,halign='center',text_color=( 0, 128, 0, 1 ),
                                                   theme_text_color="Primary",pos_hint={"center_x": 0.6,"center_y": 0.3},markup=True))
                        self.add_content(card, container)
                        Clock.schedule_once(lambda dt, c=card, i=start: self.animate_card(c, delay=0.1 * start),
                                            0.1 * start)
                        print("start is "+str(start))
                    elif key == "welcome_message" and not d_value:
                        start+=1
                    '''elif key == "events" and start == 5 and d_value:
                        start+=1
                        print("inloop")
                        for event in self.invites_dict['events']:
                            print(event)
                            self.content.add_widget(MDLabel(text=f"We have some events to joy "
                                                            f"{self.invites_dict['events'][0]}",
                                                   theme_text_color="Primary"))
                            self.add_content(self.card, self.content, self.container)'''

            if self.invites_dict and len(self.invites_dict['events']):
                for event in self.invites_dict['events']:
                    container = self.ids.received_box
                    card = MDCard(
                            orientation="horizontal",
                            padding=20,
                            #size_hint=[None, None],
                            #size=["750dp", "60dp"],
                            #adaptive_height=True,
                            adaptive_size=True,
                            ripple_behavior=True,
                            elevation=8,
                            size_hint_y=None,
                            #size='self.texture_size[1] + 2*self.padding[1]',
                            # pos_hint={"center_x": 0.5, "center_y": .4},
                            style="elevated",
                            md_bg_color="darkgrey",
                            radius=[20, 20, 20, 20],
                    )
                    #content = MDRelativeLayout(orientation="horizontal",spacing=15,adaptive_height=True,adaptive_width=True,pos_hint={"center_x": 0.6},size_hint_y=None)
                    # content.add_widget(MDRelativeLayout(orientation="horizontal", spacing=15))

                    card.add_widget(MDIcon(icon='balloon',adaptive_height=True,adaptive_width=True,
                                           theme_text_color="Custom",text_color=( 1, 0.4, 0, 1 ),size_hint_y=None))
                    card.add_widget(MDLabel(text=f"[color=#008000]We have an event "
                                                    f"[b]{event['event_name']}[/b] to attend on "
                                                    f"[b]{event['event_date']}[b] with "
                                                    f"[i]{event['event_foods']}[/i] at "
                                                    f"[i][u]{event['event_venue']}[/u][/i]",
                                               theme_text_color="Primary",adaptive_height=True,text_color=( 0, 128, 0, 1 ),
                                            adaptive_width=True,size_hint_y=None,halign='center',
                                            markup=True,pos_hint={"center_x": 0.6,"center_y": 0.3}))

                    Clock.schedule_once(lambda dt, c=card, i=start: self.animate_card(c, delay=0.1 * start),
                                        0.1 * start)
                    self.add_content(card,container)

        screen = self.ids.received_box
        layout = MDRelativeLayout(orientation="horizontal", spacing=10,size_hint_y=None)
        screen.add_widget(layout)
        layout.add_widget(MDFillRoundFlatButton(text="Yes! I am attending",pos_hint={"center_x": 0.3},
                                                on_release=lambda x: self.next_screen()))
        layout.add_widget(MDFillRoundFlatButton(text="Yes, But I will attend it Virtually!", pos_hint={"center_x": 0.6},
                                                on_release=lambda x: self.show_virtual_form()))
        #layout.add_widget(MDFillRoundFlatButton(text="I am unable to!", pos_hint={"center_x": 0.9}))


    def animate_card(self, card, delay=0):
        anim = Animation(opacity=1, y=card.y + 50, d=3, t="out_bounce")
        anim.start(card)

    def next_screen(self):
        self.app.change_screen('request_to_attend')

    def add_content(self,card,container):
        #card.add_widget(content)
        container.add_widget(card)

    def show_virtual_form(self):
        self.form_content = Builder.load_string('''
MDBoxLayout:
    orientation: "vertical"
    spacing: "10dp"
    padding: "15dp"
    size_hint_y: None
    adaptive_height: True

    MDTextField:
        id: virtual_name
        hint_text: "Your Name"
        write_tab: False
        text : "{}"
    MDTextField:
        id: virtual_relation
        hint_text: "Your Relation with Inviter.Ex:Friend/Colleague/Cousin"
        write_tab: False
    MDTextField:
        id: virtual_reason
        hint_text: "You can mention reason if you want(Optional)"
        write_tab: False

'''.format(self.user_name))

        self.form_dialog = MDDialog(
            title="Your Details Please",
            type="custom",
            content_cls=self.form_content,
            buttons=[
                MDRaisedButton(text="CANCEL", on_release=lambda x: self.form_dialog.dismiss()),
                MDRaisedButton(text="SUBMIT", on_release=lambda x: self.save_virtual_details())
            ],
        )
        self.form_dialog.open()

    def save_virtual_details(self):
        user_id = self.app.user_details["user_id"]
        response_id = self.app.get_increament("marriage_responses", "response_id")
        payload = {"query": {"marriage_code": self.marriage_code, "user_id": user_id }, "require": {}}
        self.virt_response_check = self.app.api.post("/find/marriage_responses", json=payload)
        cursor_to_list = list(self.virt_response_check)
        if len(cursor_to_list) != 0:
            self.app.show_dialog("Already Joined",
                                   "Hope you have already joined with us with your inputs!")
            self.form_dialog.dismiss()
            self.app.change_screen('attend_marriage')
        else:
            self.virtual_name = self.form_content.ids.virtual_name.text.strip()
            self.virtual_relation = self.form_content.ids.virtual_relation.text.strip()
            self.virtual_reason = self.form_content.ids.virtual_reason.text.strip()
            if not self.virtual_relation:
                self.app.show_dialog("Incomplete Form", "Enter your relation pls")
                return
            self.virtual_data = { "user_id" : user_id,
                                  "response_id" : response_id,
                                  "marriage_code" : self.marriage_code,
                                    "user_name" : self.user_name,
                                    "inviter_relation" : self.virtual_relation,
                                     "response_type" : "virtual",
                                    "response_message":self.virtual_reason
                                 }
            #self.app.marriage_data["events"].append(self.events)
            print(str(self.inserted))
            if self.inserted:
                self.app.show_dialog("Already Inserted",
                                         "Hope you have already joined with us with your inputs!")
                self.form_dialog.dismiss()
                self.app.change_screen('attend_marriage')
            else:
                virtual_insert = self.app.api.post("/insert/marriage_responses",json=self.virtual_data)
                self.inserted = True
                MDSnackbar(MDIcon(icon='hands-pray',adaptive_height=True,adaptive_width=True,
                                           size_hint_y=None),
                MDLabel(text="Hey "+self.virtual_name+".Thanks for your response."
                                                                "We will notify you soon with link to watch it!!!"),
                        snackbar_x="30dp",
                        snackbar_y="30dp",
                        md_bg_color=(0, 128, 0, 1),
                        orientation="horizontal",
                        duration=3
                ).open()
                self.form_dialog.dismiss()

    def on_pre_enter(self, *args):
        self.ids.received_box.clear_widgets()  # Make sure to clear if not properly left the screen
        for child in self.ids.received_box.children[:]:  # copy the list to avoid mutation issues
            self.ids.received_box.remove_widget(child)
            self.ids.spin.active = True


    def on_leave(self, *args):
        self.container.clear_widgets()
        for child in self.container.children[:]:  # copy the list to avoid mutation issues
            self.container.remove_widget(child)


class WeddingDetailScreen(Screen):

    def __init__(self, **kwargs):
        super(WeddingDetailScreen, self).__init__(**kwargs)
        self.selected_option = ""
        self.selected_main_foods = []
        self.selected_foods = []
        self.events = []
        self.app = MDApp.get_running_app()
        self.map_popup_open = False

    def on_enter(self, *args):

        if not "name" in self.app.user_details:
            self.app.change_screen('home')
        else:
            self.user_name = self.app.user_details["name"]


    def on_option_selected(self, selected_text):
        self.selected_option = selected_text.text
        self.app.marriage_data["food_preference"] = self.selected_option

    def update_selection(self):
        main_selected = []
        if self.ids.breakfast.active:
            main_selected.append("BreakFast")
        if self.ids.lunch.active:
            main_selected.append("Lunch")
        if  self.ids.dinner.active:
            main_selected.append("Dinner")

        if main_selected:
            self.selected_main_foods = "|".join(main_selected)
        else:
            self.selected_main_foods = "Additional: None"
        #print(self.selected_main_foods)
        self.app.marriage_data["food_options"] = self.selected_main_foods

    def on_accommodation_active(self,switch,is_active):
        if is_active:
            self.app.marriage_data["accommodation_provided"] = True
        else:
            self.app.marriage_data["accommodation_provided"] = False



    def show_events_form(self):
        self.form_content = Builder.load_string('''
MDBoxLayout:
    orientation: "vertical"
    spacing: "25dp"
    padding: "25dp"
    size_hint_y: None
    adaptive_height: True

    MDTextField:
        id: event_name
        hint_text: "Event Name"
        write_tab: False
    MDTextField:
        id: event_description
        hint_text: "Short Description about Event"
        write_tab: False
    MDTextField:
        id: event_date
        hint_text: "Event Date & Time"
        write_tab: False
        on_focus: if self.focus: app.root.ids.wedding_details.open_datetime_picker()

    MDLabel:
        text: "Foods"
        font_style: "Body1"
        halign: "left"

    BoxLayout:
        orientation: "horizontal"
        spacing: dp(5)
        size_hint_y: None
        #height: dp(50)
        adaptive_height: True
        #pos_hint: {"center_x": 0.5}

        MDCheckbox:
            id: veg
            on_active: app.root.ids.wedding_details.update_event_selection()
        MDLabel:
            text: "Only Veg"
            font_style: "Caption"
            valign: "middle"

        MDCheckbox:
            id: non_veg
            on_active: app.root.ids.wedding_details.update_event_selection()
        MDLabel:
            text: "Non Veg"
            font_style: "Caption"
            valign: "middle"

        MDCheckbox:
            id: hot_drinks
            on_active: app.root.ids.wedding_details.update_event_selection()
        MDLabel:
            text: "Coffee/Tea"
            font_style: "Caption"
            valign: "middle"
        MDCheckbox:
            id: soft_drinks
            on_active: app.root.ids.wedding_details.update_event_selection()
        MDLabel:
            text: "Cool Drinks/Juices"
            font_style: "Caption"
            valign: "middle"
        MDCheckbox:
            id: desserts
            on_active: app.root.ids.wedding_details.update_event_selection()
        MDLabel:
            text: "Desserts"
            font_style: "Caption"
            valign: "middle"

    MDTextField:
        id: event_venue
        hint_text: "Event Venue(Opt)"
        write_tab: False
''')

        self.form_dialog = MDDialog(
            title="Event Details Please",
            type="custom",
            content_cls=self.form_content,
            buttons=[
                MDRaisedButton(text="CANCEL", on_release=lambda x: self.form_dialog.dismiss()),
                MDRaisedButton(text="SUBMIT", on_release=lambda x: self.save_event_details())
            ],
        )
        self.form_dialog.open()

    def save_event_details(self):
            self.event_name = self.form_content.ids.event_name.text.strip()
            self.event_description = self.form_content.ids.event_description.text.strip()
            self.event_venue = self.form_content.ids.event_venue.text.strip()
            self.event_date = self.form_content.ids.event_date.text.strip()

            if not self.event_name:
                self.app.show_dialog("Incomplete Form", "Please fill in Event Name")
                return
            self.events = { "event_name" : self.event_name,
                            "event_description" : self.event_description,
                            "event_date":self.event_date,
                            "event_foods": self.selected_foods,
                            "event_venue":self.event_venue}
            self.app.marriage_data["events"].append(self.events)
            MDSnackbar(MDIcon(icon='hands-pray',adaptive_height=True,adaptive_width=True,
                                           size_hint_y=None),
                       MDLabel(text="Event "+self.event_name+" has been added!!!"),
                snackbar_x="30dp",
                snackbar_y="30dp",
                md_bg_color=(0, 128, 0, 1),orientation="horizontal",
                duration=3
            ).open()
            self.form_dialog.dismiss()

    def update_event_selection(self):
        selected = []
        if self.form_content.ids.veg.active:
            selected.append("Veg")
        if self.form_content.ids.non_veg.active:
            selected.append("Non-Veg")
        if self.form_content.ids.hot_drinks.active:
            selected.append("Hot Drinks")
        if self.form_content.ids.soft_drinks.active:
            selected.append("Cool Drinks")
        if  self.form_content.ids.desserts.active:
            selected.append("Snacks|Desserts")


        if selected:
            self.selected_foods = "|".join(selected)
        else:
            self.selected_foods = "Selected: None"
        print(self.selected_foods)

    def open_datetime_picker(self):
        date_dialog = MDDatePicker(min_date=datetime.now().date())
        date_dialog.bind(on_save=self.on_date_selected)
        date_dialog.open()

    def on_date_selected(self,date_obj,value,date_range):
        self.selected_date = value
        time_dialog = MDTimePicker()
        time_dialog.bind(on_save=self.on_time_selected)
        time_dialog.open()

    def on_time_selected(self, time_obj,value):
        dt = datetime.combine(self.selected_date, value)
        formatted = dt.strftime("%d-%m-%Y %I:%M %p")
        self.form_content.ids.event_date.text = formatted


    def on_leave(self):
        main_box_layout = self.app.root.get_screen("wedding_details").ids.fields_box_layout
        self.app.root.get_screen("wedding_details").ids.qr_button.text = "Generate QR Code"
        if not self.app.root.get_screen("wedding_details").ids.map_btn.preserve:
            self.app.reset_form_widgets(main_box_layout)
'''
    def open_map(self, text_input):
        if not self.map_popup_open:
            self.map_popup_open = True
            popup = MapPopup(text_input)
            popup.bind(on_dismiss=self.reset_popup_flag)
            popup.open()

    def reset_popup_flag(self, *args):
        self.map_popup_open = False '''






class QRScanScreen(Screen):


    def on_enter(self):
        """Start the camera when screen is entered"""
        self.app = MDApp.get_running_app()
        if not "name" in self.app.user_details or not hasattr(self.app,"user_name"):
            self.app.change_screen("home")
        self.img = Image()
        self.add_widget(self.img)
        self.capture = cv2.VideoCapture(0)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.scanning = True
        #self.update(self)
        self._event = Clock.schedule_interval(self.update, 1.0 / 30)

    def on_leave(self):
        """Stop the camera when leaving the screen"""
        self.scanning = False
        if self.capture:
            self.capture.release()
        if hasattr(self, "_event"):
            self._event.cancel()
        Clock.unschedule(self.update)
        #self.clear_widgets()


    def update(self, dt):
        if not self.capture.isOpened():
            return
        ret, frame = self.capture.read()
        print(str(ret))
        #print(str(frame))
        if not ret:
            return

        # Detect QR code
        #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        try:
            self.decoded=decode(frame)
        except Exception as e:
            print("Error in decoding "+str(e))

        if self.decoded:
            data = self.decoded[0].data.decode("utf-8")
            print("QR Detected:", data)
            #self.manager.current = "your_target_screen"  # Navigate if needed
            #self.manager.get_screen("your_target_screen").handle_qr_data(data)
            self.on_leave()  # Stop scanning immediately
            return

        # Display video feed
        flipped = cv2.flip(frame, 0)
        buf = flipped.tobytes()
        texture = Texture.create(size=(flipped.shape[1], flipped.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        self.img.texture = texture

class CustomOneLineIconListItem(OneLineIconListItem):
    icon = StringProperty()

class WeddingApp(MDApp):

    otp_code = ""
    phone_number = ""
    LabelBase.register(
        name="Segoe-UI-Emoji",
        fn_regular="Segoe-UI-Emoji.ttf"  # Download from Google Fonts
    )
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_cls.primary_palette = "Green"       # Green tones
        self.theme_cls.primary_hue = "900"              # A deeper shade of green , 900 was set
        self.theme_cls.accent_palette = "LightGreen"    # Accent highlights
        self.theme_cls.accent_hue = "300"
        self.theme_cls.theme_style = "Dark"
        self.store = JsonStore("user.json")
        self.api = APIClient()
        self.marriage_data = {"events": []}
        self.screen_stack = []

    def build(self):
        folder = "AppClasses"
        for filename in os.listdir(folder):
            if filename.endswith('.kv'):
                Builder.load_file(os.path.join(folder, filename))
        root = Builder.load_file('app.kv')
        root.transition = FadeTransition(duration=0.3)
        if self.store.exists("user"):
            self.phone_number = self.store.get("user")["phone"]
            self.api.access_token = self.store.get("user")["token"]
            self.user_details = self.api.get(f"/user_data/by_field/mobile/{self.phone_number}")
            if 'error' in self.user_details: # When refresh failed after long time app closed
                print(f"{self.phone_number}")
                delete_refresh = self.api.delete(f"/delete_refresh/{self.phone_number}")
                self.api.logout()
                if self.store.exists("user"):
                    self.store.delete("user")
                root.current = "login"
            elif 'name' in self.user_details:
                root.current = "home"
                payload= {"query" :{"mobile":self.phone_number},"data" :{"last_login":str(datetime.now())}}
                update_last_login = self.api.put("/update/user_data",json=payload)
                print(f"[From API] {update_last_login} is returned")
        else:
            root.current = 'login'
            #request_permissions([Permission.CAMERA])
        return root

    def send_otp(self, phone_number):
        if len(phone_number) < 10 or len(phone_number) > 10:
            self.show_dialog("Invalid Number", "Please enter a valid phone number.")
            return
        self.phone_number = phone_number
        payload = { "phone_number" : self.phone_number }
        self.otp_code = self.api.post("/send_otp",json=payload)
        print(f"[From API] {self.otp_code} is returned")
        self.otp_code = str(random.randint(1000, 9999))
        print(f"[DEBUG] OTP Sent to {phone_number}: {self.otp_code}")
        self.root.current = "otp"
        self.root.get_screen('otp').ids.otp1.focus = True
        #self.otp_code = "1234"

    def verify_otp(self, input_otp):
        if self.api.login(self.phone_number,input_otp):
            self.user_details = self.api.get(f"/user_data/by_field/mobile/{self.phone_number}")
            if "id" in self.user_details:
                payload = {"query": {"mobile": self.phone_number}, "data": {"last_login": str(datetime.now())}}
                print(f"user details {self.user_details}")
                update_last_login = self.api.put("/update/user_data", json=payload)
                self.store.put("user", phone=self.phone_number,token=self.api.access_token)
                self.change_screen("home")
            else:
                self.change_screen("home")
        else:
            self.show_dialog("Invalid OTP","OTP Not Valid or Unable to login")
            return

    def verify_pin(self, input_pin):
        if self.api.login(self.phone_number,input_pin):
            self.user_details = self.api.get(f"/user_data/by_field/mobile/{self.phone_number}")
            if self.user_details["is_pin_permanent"]:
                payload = {"query": {"mobile": self.phone_number}, "data": {"last_login": str(datetime.now())}}
                print(f"user details {self.user_details}")
                update_last_login = self.api.put("/update/user_data", json=payload)
                self.store.put("user", phone=self.phone_number,token=self.api.access_token)
                self.change_screen("home")
            else:
                self._reset()
        else:
            self.show_dialog("Invalid PIN","PIN Not Valid or Unable to login")
            return

    def reset_pin(self):
        print(f"reset PIN for {self.phone_number}")
        self.temp_pin = str(random.randint(100000, 999999))
        print(self.temp_pin)
        try:
            if self.api.reset(self.phone_number, self.temp_pin):
                payload = { "phone_number" : self.phone_number, "otp" : self.temp_pin }
                self.reset_response = self.api.post("/reset_pin",json=payload)
                receiver_email = self.reset_response.get("email")
                if receiver_email == "Error":
                    self.show_dialog("Email Not Found", "No email associated with this user.")
                    return
                yag = yagmail.SMTP(user="joynus.india@gmail.com", password="qehu gngt koxg sttk")
                yag.send(
                to=receiver_email,
                subject="Your Temporary PIN for Joynus",
                contents=f"Please note down your temporary PIN : {self.temp_pin}",
                )
                self.show_dialog("Email Sent",f"Temporary PIN Sent to your Email {receiver_email} .Use that one time")
            else:
                self.show_dialog("Reset Error", "Reset Failed")
        except Exception as e:
            self.show_dialog("Email Error", f"Could not send email.\n{str(e)}")
            return



    def _reset(self):
        self.reset_form = Builder.load_string('''
MDBoxLayout:
    orientation: "vertical"
    spacing: "10dp"
    padding: "15dp"
    size_hint_y: None
    adaptive_height: True

    MDTextField:
        id: reset_phone_number
        hint_text: "Your Number"
        write_tab: False
        text : "{}"
    MDTextField:
        id: first_pin
        hint_text: "Enter New PIN"
        write_tab: False
    MDTextField:
        id: second_pin
        hint_text: "Enter New PIN again"
        write_tab: False
'''.format(self.phone_number))
        self.reset_dialog = MDDialog(title="Reset PIN",
            type="custom",
            content_cls=self.reset_form,
            buttons=[
                MDRaisedButton(text="CANCEL", on_release=lambda x: self.reset_dialog.dismiss()),
                MDRaisedButton(text="RESET",
                               on_release=lambda x: _reset_it())
            ],
        )
        self.reset_dialog.open()

        def _reset_it():
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            if self.reset_form.ids.first_pin.text == self.reset_form.ids.second_pin.text :
                pin_hash = pwd_context.hash(self.reset_form.ids.second_pin.text)
                payload = { "query" : {"mobile" : self.phone_number} ,"data" : { "pin" : pin_hash ,"is_pin_permanent" : True } }
                user_upd = self.api.put("/update/user_data",json=payload)
                self.show_dialog("Success","PIN Reset Successfully Done")
                self.reset_dialog.dismiss()
            else:
                self.show_dialog("Error in Reset" ,"New PINs does not match")
                return

    def show_dialog(self, title, text):
        dialog = MDDialog(title=title, text=text, size_hint=(0.8, 0.3),
                          buttons=[MDRaisedButton(text="OK", on_release=lambda x: dialog.dismiss())])
        dialog.open()


    def get_increament(self,collection_name,column_name):
        pipeline = [
            {"$group": {"_id": None, "max": {"$max": "$"+column_name}}}
        ]
        response = self.api.post("/aggregate/"+collection_name, json=pipeline)
        max_val = response[0]["max"] if response else 0

        if max_val:
           return max_val+1
        else:
            return 1

    def confirm_wedding_qr(self,*args):
        self.userid = self.user_details["user_id"]
        if not self.userid:
            self.show_dialog("Become User","Come on! Be an user, go back home and register please!")
            return
        dialog = MDDialog(
            title="Confirmation",
            text="QR Code once generated, it cannot be changed. Even if you edit the details later, "
                 "only NEW one will be generated. So please make sure all details are correct!",
            buttons=[
                MDRaisedButton(text="OK! I Confirm", on_release=lambda x: (dialog.dismiss(),self.generate_wedding_qr(*args))),
                MDRaisedButton(text="Check again! Wait!", on_release=lambda x: (dialog.dismiss()))
            ]
        )
        dialog.open()




    def generate_wedding_qr(self, groom, bride, date, venue,engagement_date,marriage_upi_id,welcome_msg):

        if not all([groom, bride, date, venue,marriage_upi_id]):
            self.show_dialog("Missing Info", "Please fill in required fields.")
            return


        max_of_wed = self.get_increament("marriage_invites","marriage_id")
        if hasattr(self,"update_mr"):
            new_marriage_code = self.update_mr
            is_update = True
        else:
            new_marriage_code = "MR-"+str(max_of_wed)
            is_update = False
        print(new_marriage_code)

        is_accommodation =  self.marriage_data["accommodation_provided"]

        details = (f"Groom: {groom}\nBride: {bride}\nDate: {date}\nEngagement(If): "
                   f"{engagement_date}\nVenue: {venue}\n{welcome_msg} Marriage Code : {new_marriage_code}")
        #details = "https://www.google.com"
        qr_img = qrcode.make(details)

        if self.is_lat_lon(venue):
            google_url = f"https://www.google.com/maps/search/?api=1&query={venue}"
            venue = google_url


        self.marriage_data |= {
            "marriage_id": max_of_wed,
            "marriage_code" : new_marriage_code,
            "user_id": self.userid,
            "groom": groom,
            "bride": bride,
            "marriage_date": date,
            "engagement_date": engagement_date,
            "accommodation_provided" : is_accommodation,
            "venue": venue,
            "welcome_message":welcome_msg,
            "upi_id" : marriage_upi_id,
            "created_date": str(datetime.now())
        }

        #print("given date "+date)
        #print("User id is "+str(self.userid))
        # print(self.marriage_data)
        #return
        if not is_update:
            payload = {"query": {"user_id": self.userid}, "require": {"marriage_date" : 1}}
            self.invites_cursor = self.api.post("/find/marriage_invites", json=payload)
            if self.invites_cursor:
                for invite_date in self.invites_cursor:
                    self.marriage_get_date = invite_date.get('marriage_date')
                    #print("Got Date is "+str(self.marriage_get_date))

                    if date == self.marriage_get_date:
                        self.show_dialog("Existing","You already have invited for the date "+self.marriage_get_date+"!!!")
                        return

            marriage_ins = self.api.post("/insert/marriage_invites", json=self.marriage_data)
            #print("Inserted New Invite")
        elif is_update:
            payload = { "query" : {"marriage_code" : new_marriage_code} ,
                            "data" : self.marriage_data }
            marriage_upd = self.api.put("/update/marriage_invites",json=payload)



        # Save locally
        qr_path = "wedding_qr.png"
        '''from kivy.utils import platform
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.WRITE_EXTERNAL_STORAGE])

            from android.storage import primary_external_storage_path
            storage_path = primary_external_storage_path()
            file_path = f"{storage_path}/Download/{pid}.jpg"
        else:
            file_path = f"C:\\Users\\admin\\Downloads\\{pid}.jpg"'''
        qr_img.save(qr_path)
        image_content = Builder.load_string('''
FitImage:
    source: "wedding_qr.png"
    size_hint_y: None
    size_hint_x: None
''')
        # Show popup
        buffer = BytesIO()
        qr_img.save(buffer,format='PNG')
        buffer.seek(0)
        image = CoreImage(buffer, ext="png")
        #image_widget = FitImage()
        #image_widget.texture = image.texture
        #image_widget.size_hint = (None, None)

        dialog = MDDialog(
            title="Your Wedding QR Code for Marriage Code "+new_marriage_code,
            type="custom",
            content_cls=Image(texture=image.texture,size_hint=(None,None)),
            buttons=[
                MDRaisedButton(text="Download", on_release=lambda x: self.download_qr(qr_path)),
                MDRaisedButton(text="Send Email", on_release=lambda x: self.email_qr(qr_path)),
                MDRaisedButton(text="Close", on_release=lambda x: dialog.dismiss())
            ]
        )
        dialog.open()

    def is_lat_lon(self,input_str):
        # Remove spaces and split by comma
        parts = [p.strip() for p in input_str.split(",")]

        if len(parts) != 2:
            return False  # Not a pair

        try:
            lat = float(parts[0])
            lon = float(parts[1])
            # Validate latitude and longitude ranges
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                return True
        except ValueError:
            pass

        return False

    def download_qr(self, filepath):
            self.show_dialog("Saved", f"QR Code saved as {filepath}")

    def email_qr(self, filepath):
            try:
                receiver_email = self.user_details.get("email", "")
                if not receiver_email:
                    self.show_dialog("Email Not Found", "No email associated with this user.")
                    return

                yag = yagmail.SMTP(user="joynus.india@gmail.com", password="MyJoynus@3")
                yag.send(
                    to=receiver_email,
                    subject="Your Wedding QR Invitation",
                    contents="Attached is your wedding QR code. Share it with your guests!",
                    attachments=filepath
                )
                self.show_dialog("Email Sent", f"QR Code sent to {receiver_email}")
            except Exception as e:
                self.show_dialog("Email Error", f"Could not send email.\n{str(e)}")

    def open_datetime_picker(self,caller_field):
        Clock.schedule_once(lambda dt: self._show_picker(caller_field), 0.1)

    def _show_picker(self, caller_field):
        date_dialog = MDDatePicker(min_date=datetime.now().date())
        date_dialog.caller = caller_field
        date_dialog.bind(on_save=self.on_date_selected)
        date_dialog.open()

    def on_date_selected(self,date_obj,value,date_range):
        self.selected_date = value
        time_dialog = MDTimePicker()
        time_dialog.caller = date_obj.caller
        time_dialog.bind(on_save=self.on_time_selected)
        time_dialog.open()

    def on_time_selected(self, time_obj,value):
        dt = datetime.combine(self.selected_date, value)
        formatted = dt.strftime("%d-%m-%Y %I:%M %p")
        text_field_to_set = time_obj.caller
        text_field_to_set.text = formatted

    def clear_qr_dates(self):
        self.root.get_screen("wedding_details").ids.wedding_datetime.text = ''
        self.root.get_screen("wedding_details").ids.engagement_datetime.text = ''


    def change_screen(self, new_screen_name):
        current = self.root.current
        if current != new_screen_name:
            if not self.screen_stack or self.screen_stack[-1] != current:
                self.screen_stack.append(current)
            self.root.current = new_screen_name

    def reset_form_widgets(self,layout):
        for child in layout.children:
            # Check if it's a TextField
            if isinstance(child, MDTextField):
                child.text = ""
            # Check if it's a Checkbox
            elif isinstance(child, MDCheckbox):
                child.active = False
            # Check if it's a Switch
            elif isinstance(child, MDSwitch):
                child.active = False
            # If it's a layout, go deeper recursively
            elif hasattr(child, 'children'):
                self.reset_form_widgets(child)

    def go_back(self):
        if self.screen_stack:
            last_screen = self.screen_stack.pop()
            self.root.current = last_screen
        else:
            self.show_dialog("That's it!","No Screen to go back to")

    def on_menu_press(self, button_instance):
        menu_items = [
            { "viewclass": "CustomOneLineIconListItem","text": "Total Food Count","icon" : "account-multiple-plus-outline",
             "on_release": lambda x="food_count": self.menu_callback(x)},
            {"viewclass": "CustomOneLineIconListItem", "text": "Update LIVE Link", "icon": "video-wireless-outline",
             "on_release": lambda x="update_live": self.menu_callback(x)},
            {"viewclass": "CustomOneLineIconListItem","text": "Sent Invites", "icon": "card-text-outline",
             "on_release": lambda x="sent_invites": self.menu_callback(x)},
            {"viewclass": "CustomOneLineIconListItem", "text": "Sent Responses", "icon": "card-text-outline",
             "on_release": lambda x="sent_responses": self.menu_callback(x)},
            {"viewclass": "CustomOneLineIconListItem", "text": "Received Response", "icon": "account-box-multiple-outline",
             "on_release": lambda x="received_responses": self.menu_callback(x)},
            {"viewclass": "CustomOneLineIconListItem", "text": "Received Feedbacks","icon": "comment-quote-outline",
             "on_release": lambda x="received_feedbacks": self.menu_callback(x)},
            {"viewclass": "CustomOneLineIconListItem", "text": "Received Gifts","icon": "gift-outline",
             "on_release": lambda x="received_gifts": self.menu_callback(x)},
            {"viewclass": "CustomOneLineIconListItem","text": "Logout","icon": "network-off-outline",
             "on_release": lambda x="logout": self.menu_callback(x)},
        ]

        self.menu = MDDropdownMenu(
            caller=button_instance,
            items=menu_items,
            width_mult=4,
        )
        self.menu.open()

    def menu_callback(self, action):
        print(f"Selected: {action}  {self.menu.items}")
        self.menu.dismiss()
        self.list_selected = action
        if action == "food_count" :
            self.show_food_count()
        elif action == "update_live":
            self.show_update_url()
        elif action == "sent_invites":
            self.change_screen("sent")
            ss_obj = self.root.get_screen('sent')
            ss_obj.on_enter()
        elif action == "sent_responses":
            self.change_screen("sent")
            ss_obj = self.root.get_screen('sent')
            ss_obj.on_enter()
        elif action == "received_responses":
            self.change_screen("received_resp")
            rs_obj = self.root.get_screen('received_resp')
            rs_obj.on_enter()
        elif action == "received_feedbacks":
            self.change_screen("received_resp")
            rs_obj = self.root.get_screen('received_resp')
            rs_obj.on_enter()
            rs_obj.ids.data_list.clear_widgets()
        elif action == "received_gifts":
            self.change_screen("received_resp")
            rs_obj = self.root.get_screen('received_resp')
            rs_obj.on_enter()
            rs_obj.ids.data_list.clear_widgets()
        elif action == "logout":
            self.logout()

    def show_food_count(self):

        self.user_name = self.user_details["name"]
        self.userid = self.user_details["user_id"]
        self.search_content = Builder.load_string('''
MDBoxLayout:
    orientation: "vertical"
    spacing: "10dp"
    padding: "15dp"
    size_hint_y: None
    adaptive_height: True

    MDLabel:
        id: virtual_name
        text : "{} , Enter Your Marriage Code"
        
    MDTextField:
        id: mr_code
        hint_text: "Your Marriage Code to get total food count"
        write_tab: False

'''.format(self.user_name))

        self.search_dialog = MDDialog(title="Total Food Count For Marriage",
            type="custom",
            content_cls=self.search_content,
            buttons=[
                MDRaisedButton(text="CANCEL", on_release=lambda x: self.search_dialog.dismiss()),
                MDRaisedButton(text="SEARCH",
                               on_release=lambda x: self.get_food_details(self.search_content.ids.mr_code.text.strip()))
            ],
        )
        self.search_dialog.open()

    def get_food_details(self,mr_code):
        print("Got mr code "+mr_code)
        #mr_code = mr_code.upper()

        payload = {"query" : {"marriage_code":mr_code.upper()} , "require" : { "_id":0,"food_count" : 1,
                                                                        "engagement_availability":1,
                                                                        "accommodation_needed":1,
                                                                            "response_type" : 1} }

        response_cur = self.api.post("/find/marriage_responses",json=payload)
        print(f"{response_cur} is the return value")

        invites_cur = self.api.get("/marriage_invites/by_field/marriage_code/"+mr_code.upper())
        userid = invites_cur["user_id"]
        print(f"Logged in {self.userid} and invited user {userid}")
        total_virtual = 0
        total_accommodation = 0
        total_engagement = 0
        total_count = {}
        if self.userid != userid:
            self.show_dialog("Not Inviter","Sorry,You are not the inviter of this marriage")
            return
        #if response_cur.alive:
        if response_cur:
            for data in response_cur:
                print(data)
                if data["response_type"] == "in-person":
                    #print(f"{data["food_count"] , data["accommodation_needed"] , data["engagement_availability"]}")
                    if data["accommodation_needed"] : total_accommodation += int(data["accommodation_needed"])
                    if data["engagement_availability"] : total_engagement += int(data["engagement_availability"])
                    if data["food_count"] :
                        for meal , count in data["food_count"].items():
                            if meal in total_count:
                                total_count[meal] += int(data["food_count"][meal])
                            else:
                                total_count[meal] = int(data["food_count"][meal])
                elif data["response_type"] == "virtual":
                    total_virtual += 1
            content = MDBoxLayout(orientation="vertical", spacing=10,padding=10, adaptive_height=True,
                                  adaptive_width=True,size_hint=(None, None))
            content.add_widget(MDLabel(text=f"[b][u]Food Count for Marriage {mr_code.upper()}[/u] - [i]{invites_cur["groom"]} "
                                        f" Weds {invites_cur["bride"]}[/i] On {invites_cur["marriage_date"]}"
                                        f"[/b]", markup=True,adaptive_height=True,adaptive_width=True))
            for meal , count in total_count.items():
                content.add_widget(MDLabel(text=f"[b][i]{meal.capitalize()}:[/b][/i] {count}",
                                           markup=True,adaptive_height=True,adaptive_width=True))

            if total_engagement:
                content.add_widget(MDLabel(text=f"[b][i]Available for Engagement:[/b][/i] "
                                        f"{total_engagement} Groups/Families", markup=True,adaptive_height=True,adaptive_width=True))

            content.add_widget(MDLabel(text=f"[b][i]Total Accommodation (Rooms) Needed:[/b][/i] "
                                            f"{total_accommodation}", markup=True, adaptive_height=True,
                                       adaptive_width=True))
            content.add_widget(MDLabel(text=f"[b][i]People Virtually Available :[/b][/i] "
                                        f"{total_virtual}", markup=True,adaptive_height=True,
                                       adaptive_width=True))


            #print(f"total accommodation {total_accommodation}")
            #print(f"total engagement {total_engagement}")
            #print(f"total foods {total_count}")
            #print(f"total virtual {total_virtual}")
            card = MDCard(orientation="vertical", padding=20, size_hint=(None, None),
                          md_bg_color=self.theme_cls.primary_color,
                          adaptive_size=True)
            card.add_widget(content)
            card.opacity = 0
            card.scale = 0.9

            anim = Animation(opacity=1, d=3, t='out_quad')
            self.dialog = MDDialog(
            title="Marriage Response",
            type="custom",
            content_cls=card,
            radius=[20, 20, 20, 20]
            )
            self.dialog.open()
            anim.start(card)
        else:
            # Show not found dialog
            self.dialog = MDDialog(
            title="No Results",
            text="No Response yet !!! :(",
            radius=[20, 20, 20, 20]
            )
            self.dialog.open()

    def show_update_url(self):
            self.user_name = self.user_details["name"]
            self.userid = self.user_details["user_id"]
            self.url_content = Builder.load_string('''
MDBoxLayout:
    orientation: "vertical"
    spacing: "25dp"
    padding: "25dp"
    size_hint_y: None
    adaptive_height: True

    MDLabel:
        id: virtual_name
        text : "{} , Enter Your Marriage Code"

    MDTextField:
        id: mr_code
        hint_text: "Your Marriage Code to update LIVE link/url"
        write_tab: False
        
    MDTextField:
        id: url
        hint_text: "Your LIVE Link/URL Please"
        write_tab: False
        public : False
    
    MDLabel :
        text : "[i]Activate below switch if [b]Anyone[/b] with your MR code can watch.If not, only those who [b]responded[/b] to your marriage can watch"
        size_hint_y: None
        height: self.texture_size[1]
        text_size: self.width, None
        markup : True
        theme_text_color: "Primary"
        spacing : 10
        
    MDSwitch :
        icon_active : "check"
        on_active : url.public = True if self.active else False
        

'''.format(self.user_name))

            self.url_dialog = MDDialog(title="LIVE Link For Marriage",
                                          type="custom",
                                          content_cls=self.url_content,
                                          buttons=[
                                              MDRaisedButton(text="CANCEL",
                                                             on_release=lambda x: self.url_dialog.dismiss()),
                                              MDRaisedButton(text="UPDATE",
                                                             on_release=lambda x: self.update_live_url(
                                                                 self.url_content.ids.mr_code.text.strip(),
                                                             self.url_content.ids.url.text.strip(),
                                                             self.url_content.ids.url.public))
                                          ],
                                          )
            self.url_dialog.open()

    def update_live_url(self,mr_code,url,is_public):

        invites_cur = self.api.get("/marriage_invites/by_field/marriage_code/"+mr_code.upper())

        if not invites_cur:
            self.show_dialog("Not Valid MR","Marriage Code entered is not valid")
            return

        userid = invites_cur["user_id"]
        print(f"Logged in {self.userid} and invited user {userid}")
        if self.userid != userid:
            self.show_dialog("Not Inviter","Sorry,You are not the inviter of this marriage")
            return

        payload= { "query" :{"marriage_code":mr_code.upper()} , "data" : {"live_url":{"url":url,"public":is_public}} }
        invites_upd = self.api.put("/update/marriage_invites",json=payload)
        if invites_upd.get("modified_count") > 0:
            self.show_dialog("Updated!","Whooo!!! Your LIVE Link is updated for "+mr_code+" !")
        else :
            self.show_dialog("Not Updated!","Something is not right, LIVE Link not updated!")

        self.url_dialog.dismiss()



    def logout(self):
        self.api.logout()
        if self.store.exists("user"):
            self.store.delete("user")
        print("logout")
        self.phone_number = ""
        self.user_name = ""
        self.user_details = None
        if self.root:
            self.root.get_screen("home").ids.phone_label.text = "Welcome"
            self.change_screen("login")





class GlobalExceptionHandler(ExceptionHandler):
    def handle_exception(self, inst):
        # Log the error or show a popup
        Logger.error(f"Unhandled Exception: {inst}")
        # Optional: show a dialog or fallback screen

        Clock.schedule_once(lambda dt: self.error_dialog(inst))
        return ExceptionManager.PASS  # or ExceptionManager.RAISE to crash

    def error_dialog(self,inst):
        dialog = MDDialog(
            title="Unexpected Error",
            text="An unexpected error!(May be input is wrong or insert twice) Try Restart App:\n" + str(inst),
            buttons=[MDRaisedButton(text="OK", on_release=lambda x: dialog.dismiss())],
        )
        dialog.open()

#This is Global method after App Class

def global_exception_handler(exc_type, exc_value, exc_traceback):
    from kivy.logger import Logger

    Logger.error("Unhandled Exception: {}".format("".join(traceback.format_exception(exc_type, exc_value, exc_traceback))))

    def show_dialog(*args):
        dialog = MDDialog(
            title="Unexpected Error",
            text="An unexpected error!(May be input is wrong or insert twice!):\n" + str(exc_value),
            buttons=[MDRaisedButton(text="OK", on_release=lambda x: dialog.dismiss())],
        )
        dialog.open()

    Clock.schedule_once(show_dialog, 0)

#sys.excepthook = global_exception_handler


if __name__ == '__main__':
    #ExceptionManager.add_handler(GlobalExceptionHandler())
    #sys.excepthook = global_exception_handler
    WeddingApp().run()