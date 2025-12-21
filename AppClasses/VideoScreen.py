import yt_dlp
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.metrics import dp
from kivy.uix.scrollview import ScrollView
from kivymd.uix.button import MDFlatButton
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.screen import MDScreen
from yt_dlp.utils import ExtractorError
from Libraries.imports import *
from kivy.uix.video import Video
from kivy.uix.videoplayer import VideoPlayer
from yt_dlp import YoutubeDL
import threading
import json
from websocket import WebSocketApp
from kivy.clock import Clock
from kivymd.uix.label import MDLabel
from kivy.effects.dampedscroll import DampedScrollEffect
from kivy.uix.behaviors import TouchRippleBehavior
from kivymd.uix.bottomsheet.bottomsheet import MDBottomSheet , MDCustomBottomSheet , MDBottomSheetContent



class VideoScreen(Screen):
    def __init__(self, **kwargs):
        super(VideoScreen, self).__init__(**kwargs)
        self.app = MDApp.get_running_app()

    def on_enter(self):
        self.video_screen = self.app.root.get_screen('video_screen')
        self.video_container = self.video_screen.ids.video_container
        if not "user_id" in self.app.user_details:
            self.app.change_screen("home")
        else:
            self.user_id = self.app.user_details["user_id"]


    def show_video(self,*args):
        if args:
            self.mr_code = args[0]
            #self.video_container = args[1]
        else:
            self.mr_code = self.video_screen.ids.mr_text.text
            #video_status = self.video_screen.ids.video_status

        self.user_id = self.app.user_details["user_id"]

        if not self.mr_code:
            self.app.show_dialog("MR Code Must","Please enter MR Code")
            return

        payload = { "query" : {"user_id": self.user_id,"marriage_code":self.mr_code.upper()},"require": {}}
        self.response_dict = self.app.api.post("/find_one/marriage_responses",json=payload)

        self.marriage_details = self.app.api.get("/marriage_invites/by_field/marriage_code/"+self.mr_code.upper())

        if not self.marriage_details:
            self.app.show_dialog("Invalid Code", "Looks like it is not a valid MR Code")
            return

        if 'public' in self.marriage_details["live_url"] and not self.marriage_details["live_url"]["public"]:
            if not self.response_dict and self.user_id != self.marriage_details["user_id"]:
                self.app.show_dialog("No Option", "Sorry, Either You have not responded to this MR or You are not Inviter")
                return

        if 'url' in self.marriage_details["live_url"]:
            self.live_url = self.marriage_details["live_url"]["url"]
        else:
            self.live_url = self.marriage_details["live_url"]

        if not self.live_url:
            self.app.show_dialog("No URL",
                                 "Inviter has not updated the Live URL yet.Please wait or check with him/her.")
            return
        print(self.live_url)
        if hasattr(self,'video'):
            self.video.state = 'stop'
            self.video_container.remove_widget(self.video)

        stream_url = self.get_stream_url(self.live_url)
        if stream_url:
            self.video = VideoPlayer(
                source=stream_url,
                options={'eos': 'loop', 'allow_stretch': True,'fit_mode': 'fill','keep_ratio': True},
                allow_fullscreen=True,
                fullscreen=True,
                size_hint=(1, 1)
            )
            self.video_container.add_widget(self.video)
            self.video.state = 'play'
            self.scroll_view_kv = '''
MDScrollView:
    id : scroll_chats
    scroll_y: 0
    do_scroll_x: False
    effect_cls : "ScrollEffect"
    scroll_type : ['bars','content']
    MDBoxLayout:
        id : comment_box
        orientation : "vertical"
        padding : 0
        spacing : 0
        size_hint_y : 0.2
        height : self.minimum_height       
            
'''
            self.scroll_view = Builder.load_string(self.scroll_view_kv)
            self.video_container.add_widget(self.scroll_view)
            effect = DampedScrollEffect
            effect.edge_damping=0.3
            effect.overscroll=3
            self.scroll_view.effect_cls = effect
            self.comment_box = self.scroll_view.ids.comment_box
            self.comment_section = MDBoxLayout(id="comment_section", orientation="horizontal",size_hint_y=0.2,padding=0,spacing=0)
            self.comment_text = MDTextField(id="comment_text", mode="fill",height="30dp",font_name="Segoe-UI-Emoji",multiline=False)
            self.comment_text.hint_text = "Type Your Message here..."
            self.video_container.add_widget(self.comment_section)
            self.comment_section.add_widget(self.comment_text)
            self.emot_icon = MDIconButton(icon="emoticon-outline")
            self.send_icon = MDIconButton(icon="arrow-up-circle-outline",theme_text_color="Primary")
            self.ws = LiveWebSocketClient(mr_code=self.mr_code,comments_container=self.comment_box,scroll_view=self.scroll_view)
            self.ws.start()
            self.emot_icon.bind(on_release=lambda x: self.show_emots())
            self.send_icon.bind(on_release=lambda x: self.ws.send_comment(self.comment_text.text.strip(),self.comment_text))
            self.comment_section.add_widget(self.emot_icon)
            self.comment_section.add_widget(self.send_icon)
        else:
            self.app.show_dialog("Link Error", f"Live Link Error, Try Clicking again or Possibly Recording expired!!!")
            return

    def get_stream_url(self,youtube_url):
        ydl_opts = {'format': 'best',
                    'quiet': True
                    }
        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=False)
                return info['url']  # direct stream URL
        except yt_dlp.utils.ExtractorError as e:
            print(f"[ERROR] Failed to extract stream URL: {e}")
        except Exception as e:
            print(f"[ERROR] Unexpected issue: {e}")
        return None

    def show_emots(self):
        self.emot_content = Factory.EmojiBottomSheetContent()
        if not hasattr(self,'bottom_sheet'):
            self.bottom_sheet = MDBottomSheet(auto_dismiss=True)
            self.bottom_sheet.add_widget(self.emot_content)
            self.bottom_sheet.bind(on_dismiss=self.on_dismiss_sheet)
            self.bottom_sheet.default_opening_height = Window.height * 0.4

        # This MUST be a child of a MDScreen
            if isinstance(self.parent, (Screen, MDScreen)):
                print(self.parent)
                self.parent.add_widget(self.bottom_sheet)
            else:
            # Fallback: Add to MDScreen manually if needed
                screen = self.get_screen_parent()
                if screen:
                    screen.add_widget(self.bottom_sheet)
        Clock.schedule_once(lambda dt: self.bottom_sheet.open(), 0.1)

    def on_dismiss_sheet(self):
        if hasattr(self,'bottom_sheet'):
            self.bottom_sheet.parent.remove_widget(self.bottom_sheet)
            print("Bottom sheet removed properly.")



    def get_screen_parent(self):
        parent = self.comment_section
        while parent:
            if isinstance(parent, (Screen, MDScreen)):
                return parent
            parent = parent.parent
        return None


    def on_leave(self, *args):
        if hasattr(self,'video'):
            self.video.state = 'stop'
            self.video_container.remove_widget(self.video)
        self.video_container.clear_widgets()


class EmojiBottomSheetContent(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", spacing=0, padding=0,**kwargs)
        self.size_hint_x = 1
        #self.height = dp(min(Window.height * 0.5, 400))
        self.height = dp(400)
        self.add_widget(MDLabel(text="Choose Emoji", halign="center",adaptive_height=True))
        self.scroll = ScrollView()
        self.scroll.height = dp(300)
        self.grid = MDGridLayout(id="emoji_grid",cols=6, adaptive_height=True, spacing="3dp",
                            adaptive_width=True,padding="3dp",size_hint_y=None)
        self.grid.bind(height=lambda *_: setattr(self.grid,'height',self.grid.minimum_height))
        self.scroll.add_widget(self.grid)
        emojis = [
            # Smileys & Emotions
            "😀", "😂", "🤣", "😊", "😍",
            "🤔", "😎", "🥺", "😡", "🤯",
            "🥰", "😴", "🤩", "😭", "🤢",'🥳',

            #Family and weds
            "💑", "👩‍❤️‍👨", "👨‍❤️‍👨", "👩‍❤️‍👩", "💏", "👩‍❤️‍💋‍👨",
            "👨‍❤️‍💋‍👨", "👩‍❤️‍💋‍👩", "❤️", "💘", "💍", "💒",
            "👰", "🤵","👰‍♂️", "🤵‍♀️", "🎂", "🍾",
            "🥂", "👪", "👨‍👩‍👦", "👨‍👩‍👧", "👨‍👩‍👧‍👦", "👨‍👨‍👦","💸",
            "👩‍👩‍👧", "👨‍👦", "👨‍👦‍👦", "👩‍👧","👩‍👧‍👧", "🌹", "💐",
            "🥀", "💌", "💝", "💞", "💕", "💖", "💗", "💓",

            # Gestures & People
            "👍", "👎", "🙏", "👋", "🤝",'💯',
            "💪", "👀", "👶", "👩‍💻", "🧑‍🎤","👏",

            # Animals & Nature
            "🐶", "🐱", "🦁", "🐯", "🦊",
            "🐝", "🦋", "🌹", "🌳", "🌈",

            # Food & Drink
            "🍎", "🍕", "🍔", "🍦", "🍩",
            "☕", "🍵", "🍺", "🍷", "🍫",

            # Objects & Symbols
            "❤️", "🔥", "⭐", "🎉", "💡",
            "📱", "💻", "🎮", "📚", "✈️"
        ]
        #print(LabelBase._fonts)
        for emoji in emojis:
            btn = MDFlatButton(text=emoji,font_name="Segoe-UI-Emoji",on_release=self.insert_emoji)
            self.grid.add_widget(btn)
        self.add_widget(self.scroll)
        self.add_widget(MDLabel(text="That's all we have", halign="center",adaptive_height=True))

    def insert_emoji(self, btn):
        video_screen = self.parent.parent
        bottom_sheet = self.parent
        video_screen.comment_text.text += btn.text
        bottom_sheet.dismiss()


class LiveWebSocketClient(Screen):

    def __init__(self, **kwargs):
        super().__init__()
        self.app = MDApp.get_running_app()
        self.mr_code = kwargs.get("mr_code").upper()
        self.comments_container = kwargs.get("comments_container")
        self.scroll_view = kwargs.get("scroll_view")


    def start(self):
        self.user_id = self.app.user_details["user_id"]
        self.user_name = self.app.user_details["name"]
        self.first_name = self.user_name.split()[0]
        self.base_ws_url = self.app.api.base_url.split("//")[1]
        self.color = f"#{random.randint(0, 255):02x}{random.randint(0, 255):02x}{random.randint(0, 255):02x}"
        self.ws = WebSocketApp(
            f"ws://{self.base_ws_url}/ws/live/{self.mr_code}?token={self.app.api.access_token}&user={self.user_id}"
            f"&nick_name={self.first_name}",
            on_message=self.on_message
        )
        threading.Thread(target=self.ws.run_forever, daemon=True).start()
        self.load_history_comments()

    def on_message(self, ws, message):
        Clock.schedule_once(lambda dt: self.add_message(message))

    def add_message(self, message):
        pattern = r"^(.*?):\s*(.*?)\s(\d{4}-\d{1,2}-\d{1,2}\s*\d{1,2}:\d{2}:\d{2}).*$"
        match = re.match(pattern, message)
        name, comment, timestamp = ['','','']
        if match:
            name, comment, timestamp = match.groups()
        formatted_message = f"[font=Segoe-UI-Emoji][b][color={self.color}][size=16]{name} :[/color][/b] {comment}[/size] [size=10]{timestamp}[/size][/font]"
        label = CommentLabel(id=str(self.user_id),text=formatted_message,font_name="Segoe-UI-Emoji",halign="right", size_hint_y=None, height=30,markup=True,
                             container=self.comments_container,mr_code=self.mr_code,actual_comment_data=match)
        label.text_size = (label.width, None)
        label.bind(width=lambda *_: setattr(label, 'text_size', (label.width, None)))
        label.bind(height=lambda *_: setattr(label,'height',label.texture_size[1]))
        self.comments_container.add_widget(label)
        Clock.schedule_once(lambda dt: setattr(self.scroll_view, 'scroll_y', 0))


    def send_comment(self, text,comment_text_box):
        if comment_text_box.text == '':
            self.app.show_dialog("Comment","Type something to post")
            return
        self.ws.send(text)
        comment_text_box.text = ''

    def send_reaction(self, emoji):
        self.ws.send(emoji)

    def load_history_comments(self):
        self.history_comments = self.app.api.get(f"/comments/{self.mr_code}")
        for comment in self.history_comments:
            self.add_message(comment)


class CommentLabel(TouchRippleBehavior, MDLabel):
    def __init__(self, text,container,mr_code,actual_comment_data,**kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.container = container
        self.mr_code = mr_code
        self.long_press_time = 2  # seconds to trigger long press
        self._touch_time = None
        self.actual_comment_data = actual_comment_data
        self.app = MDApp.get_running_app()

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self._touch_time = Clock.schedule_once(self.show_options, self.long_press_time)
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if self._touch_time and self._touch_time.is_triggered is False:
            self._touch_time.cancel()
        return super().on_touch_up(touch)

    def show_options(self, *args):
        menu_items = [
            {
                "text": "Delete",
                "leading_icon": "delete",
                "on_release": lambda x="Delete": self.delete_comment()
            }
        ]
        self.menu = MDDropdownMenu(
            caller=self,
            items=menu_items,
            width_mult=3,
        )
        self.menu.open()

    def delete_comment(self):
        self.menu.dismiss()
        user_id = self.app.user_details["user_id"]
        if not str(self.id) == str(user_id):
            self.app.show_dialog("Others","You cannot delete other user comments")
            return
        parent = self.container
        if parent:
            parent.remove_widget(self)
        name, comment, timestamp = self.actual_comment_data.groups()
        data = {"user_id":user_id,"comment":comment,"marriage_code":self.mr_code,"timestamp":timestamp}
        self.delete_status = self.app.api.delete("/delete_comment",json=data)
        print(f"Deleted comment with id {self.delete_status}")
