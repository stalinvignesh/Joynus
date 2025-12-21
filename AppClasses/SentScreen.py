import webbrowser

from Libraries.imports import *

class SentScreen(Screen):

    def __init__(self, **kwargs):
        super(SentScreen, self).__init__(**kwargs)
        self.app = MDApp.get_running_app()


    def on_enter(self):
        if not "user_id" in self.app.user_details:
            self.app.change_screen("home")
            return
        else:
            self.userid = self.app.user_details["user_id"]

        if self.userid:
            if self.app.list_selected == "sent_invites":
                self.show_sent_invites(self.userid)
            elif self.app.list_selected == "sent_responses":
                self.show_responses(self.userid)
        else:
            self.app.show_dialog("Become User","Come on! Be an user, go back home and register please!")
            return

    def show_sent_invites(self, userid):
        print(userid)
        payload = { "query" : {"user_id": self.userid} , "require" : {"_id" : 0 } }
        self.sent_cur = self.app.api.post("/find/marriage_invites",json=payload)
        current_screen = self.app.root.get_screen('sent')
        layout = current_screen.ids.sent_box
        current_screen.ids.data_list.clear_widgets()
        current_screen.ids.sent_label.text = "Your Sent Invites"
        if self.sent_cur:
            for sent in self.sent_cur:
                if not 'marriage_code' in sent : sent['marriage_code'] = ''
                list_item = OneLineAvatarIconListItem(
                    text=f"{sent['groom']} Weds {sent['bride']} at {sent['venue']} , MR Code : {sent['marriage_code']}"
                )
                edit_icon = IconRightWidget(icon="pencil", on_release=lambda x, i=sent: self.go_wedding_screen(i))
                view_icon = IconRightWidget(icon="eye-arrow-left", on_release=lambda x, i=sent: self.show_details(i))
                show_icon = IconLeftWidgetWithoutTouch(icon="human-male-female")
                list_item.add_widget(show_icon)
                list_item.add_widget(edit_icon)
                list_item.add_widget(view_icon)
                current_screen.ids.data_list.add_widget(list_item)

    def go_wedding_screen(self,mr_details):
        #from main import WeddingDetailScreen
        #wed_screen = WeddingDetailScreen()
        dialog = MDDialog(
            title="Update! New QR",
            text="If you update details , A New Updated QR Code will be generated",
            buttons=[
                MDRaisedButton(text="That's OK", on_release=lambda x: dialog.dismiss()),
                MDRaisedButton(text="Oh No! Go Back!", on_release=lambda x: (dialog.dismiss(),self.app.go_back()))
            ]
        )
        dialog.open()
        wed_scr = self.app.root.get_screen("wedding_details")
        wed_scr.ids.groom_name.text = mr_details['groom']
        wed_scr.ids.bride_name.text = mr_details['bride']
        wed_scr.ids.wedding_datetime.readonly = False
        wed_scr.ids.wedding_datetime.text = str(mr_details['marriage_date'])
        wed_scr.ids.engagement_datetime.readonly = False
        if 'engagement_date' in mr_details :
            wed_scr.ids.engagement_datetime.text = str(mr_details['engagement_date'])
        wed_scr.ids.wedding_venue.text = mr_details['venue']
        wed_scr.ids.welcome_msg.text = mr_details['welcome_message']
        wed_scr.ids.qr_button.text = "Get Updated QR"
        if 'marriage_code' in mr_details:
            self.app.update_mr = mr_details['marriage_code']
        self.app.change_screen("wedding_details")


    def show_responses(self,userid):

        payload = { "query" : {"user_id": userid} , "require" : {"_id" : 0 } }
        self.resp_cur = self.app.api.post("/find/marriage_responses",json=payload)
        current_screen = self.app.root.get_screen('sent')
        layout = current_screen.ids.sent_box
        current_screen.ids.data_list.clear_widgets()
        current_screen.ids.sent_label.text = "Your Responses To Marriages"
        self.responded_marriage = []
        if self.resp_cur:
            for resp in self.resp_cur:
                payload = { "query" : {"marriage_code":resp['marriage_code']}, "require" : {"_id" : 0}}
                resp_marriage = self.app.api.post("find_one/marriage_invites/",json=payload)
                self.responded_marriage.append(resp_marriage)
                if not 'groom' in resp_marriage : resp_marriage['groom'] = "No Data"
                if not 'bride' in resp_marriage: resp_marriage['bride'] = "No Data"
                list_item = OneLineAvatarIconListItem(
                    text=f"Code : {resp['marriage_code']} - {resp['response_type']} - "
                         f"{resp_marriage['groom']} Weds {resp_marriage['bride']} "
                )
                edit_icon = IconRightWidget(icon="pencil", on_release=lambda x, i=resp: self.go_received_screen(i))
                view_icon = IconRightWidget(icon="eye-arrow-left", on_release=lambda x, i=resp: self.show_details(i))
                show_icon = IconLeftWidgetWithoutTouch(icon="hand-wave")
                list_item.add_widget(show_icon)
                list_item.add_widget(edit_icon)
                list_item.add_widget(view_icon)
                current_screen.ids.data_list.add_widget(list_item)

    def go_received_screen(self,resp_details):
        dialog = MDDialog(
            title="Update! virtual to in-person",
            text="If you already responded as Virtual , now it will change to In-Person",
            buttons=[
                MDRaisedButton(text="Yes! That's OK", on_release=lambda x: dialog.dismiss()),
                MDRaisedButton(text="Oh No! Go Back!", on_release=lambda x: (dialog.dismiss(),self.app.go_back()))
            ]
        )
        dialog.open()
        rec_scr = self.app.root.get_screen("request_to_attend")
        self.app.update_resp = resp_details
        print(resp_details)
        self.app.change_screen("request_to_attend")

    def show_details(self,sent):
        content = MDBoxLayout(orientation="vertical", spacing=25, padding=25, adaptive_height=True,
                              adaptive_width=True, size_hint=(None, None))
        if self.app.list_selected == "sent_invites":
            content.add_widget(
                MDLabel(text=f"[b]{sent["groom"]}  Weds {sent["bride"]} "
                             f"On [i]{sent["marriage_date"]}[/i][/b]"
                             , markup=True, adaptive_height=True, adaptive_width=True))
            if 'food_preference' not in sent : sent['food_preference'] = ''
            venue_lbl = MDLabel(markup=True, size_hint_y=None)
            venue_lbl.text_size=[venue_lbl.width,None]
            venue_lbl.height = venue_lbl.texture_size[1]

            if re.match("https:", sent['venue']):
                venue_text = (f"[ref={sent["venue"]}][color=#2980b9][u]"
                              f"Google Maps Location[/u][/color][/ref]")
                venue_lbl.bind(on_ref_press=lambda inst,ref: webbrowser.open(ref))
            else:
                venue_text = sent['venue']

            venue_lbl.text=f"[b]At [i]{venue_text}[/i] with Foods you prefer[i] \"{sent["food_preference"]}\" [/i][/b]"
            content.add_widget(venue_lbl)

            if 'food_options' not in sent : sent['food_options'] = "No Foods(That's OK)"
            content.add_widget(
                MDLabel(text=f"[b]You are Providing [i]{sent["food_options"]}[/i] for this occasion!!![/b]"
                             , markup=True, adaptive_height=True, adaptive_width=True))
            if 'engagement_date' in sent:
                content.add_widget(
                    MDLabel(text=f"[b]You have an Engagement set on [i]{sent["engagement_date"]}[/i] for this Wedding"
                                 f"[/b]", markup=True, adaptive_height=True, adaptive_width=True))
            if 'accommodation_provided' in sent and sent["accommodation_provided"]:
                content.add_widget(
                    MDLabel(
                        text=f"[b]Great,You are also providing Accommodation for your Visitors"
                             f"[/b]", markup=True, adaptive_height=True, adaptive_width=True))
            if 'live_url' in sent and isinstance(sent["live_url"], dict):
                if sent["live_url"]["public"]:
                    content.add_widget(
                        MDLabel(
                            text=f"[b]Woohoo! You Updated Ceremony's LIVE URL [i]{sent["live_url"]["url"]}[/i]"
                             f" and Anybody can watch with Marriage Code[/b]", markup=True, adaptive_height=True, adaptive_width=True))
                else:
                    content.add_widget(
                        MDLabel(
                            text=f"[b]Woohoo! You Updated Ceremony's LIVE URL [i]{sent["live_url"]["url"]}[/i]"
                                 f" and Only people Responded can watch[/b]", markup=True, adaptive_height=True,
                            adaptive_width=True))
            if 'events' in sent and sent['events']:
                for event in sent['events']:
                    content.add_widget(
                        MDLabel(
                            text=f"[b]Wow You also have an event arranged - [i]{event["event_name"]}[/i]"
                                f" for {event["event_description"]}[/b]", markup=True, adaptive_height=True,
                            adaptive_width=True))
                    if 'event_foods' in event:
                        content.add_widget(
                            MDLabel(
                                text=f"[b]Serving [i]{event["event_foods"]}[/i] also in the event"
                                    f"[/b]", markup=True, adaptive_height=True,
                                    adaptive_width=True))
                    if 'event_date' in event:
                        content.add_widget(
                            MDLabel(
                                text=f"[b]Event is going to be on [i]{event["event_date"]}[/i]"
                                     f" at {event["event_venue"]}[/b]", markup=True, adaptive_height=True,
                                adaptive_width=True))
        elif self.app.list_selected == "sent_responses":
            content.add_widget(
                MDLabel(text=f"You have Responded for [b]{sent["marriage_code"]} and your decision to attending it as"
                             f" [i]{sent["response_type"]}[/i][/b]"
                             , markup=True, adaptive_height=True, adaptive_width=True))
            if 'inviter_relation' not in sent : sent['inviter_relation'] = "-Not Mentioned-"
            content.add_widget(
                MDLabel(text=f"You are Related to this Wedding as a [b]{sent["inviter_relation"]} with a message"
                             f" [i]{sent["response_message"]}[/i][/b]"
                             , markup=True, adaptive_height=True, adaptive_width=True))

        card = MDCard(orientation="vertical", padding=20, size_hint=(None, None),
                      md_bg_color=self.app.theme_cls.primary_color,
                      adaptive_size=True)
        card.add_widget(content)
        card.opacity = 0
        card.scale = 0.9

        anim = Animation(opacity=1, d=3, t='out_quad')
        self.dialog = MDDialog(
        title="Sent Data",
        type="custom",
        content_cls=card,
        radius=[20, 20, 20, 20]
        )
        self.dialog.open()
        anim.start(card)

    def on_search_text(self, text):
        self.render_list(text)

    def _highlight_match(self, full_text, search_text):
        if not search_text:
            return full_text
        lower_full = full_text.lower()
        lower_search = search_text.lower()

        start = lower_full.find(lower_search)
        if start == -1:
            return full_text

        end = start + len(search_text)
        highlighted = (
            f"{full_text[:start]}"
            f"[color=#FF5722][b]{full_text[start:end]}[/b][/color]"
            f"{full_text[end:]}"
        )
        return highlighted

    def render_list(self, search_text):
        #container = self.root.ids.list_container
        current_screen = self.app.root.get_screen('sent')
        if self.app.list_selected == "sent_invites":
            if hasattr(self,"sent_cur") : self.response = self.sent_cur
        elif self.app.list_selected == "sent_responses":
            if hasattr(self,"resp_cur") : self.response = self.resp_cur

        if hasattr(self,"response"):
            current_screen.ids.data_list.clear_widgets()
            for item in self.response:
                #print(f"yes coming inside  {item} and selected {self.app.list_selected}")
                if self.app.list_selected == "sent_invites":
                    list_text = f"{item['groom']} Weds {item['bride']} at {item['venue']} , MR Code : {item['marriage_code']}"
                    show_icon = IconLeftWidgetWithoutTouch(icon="human-male-female")
                    edit_icon = IconRightWidget(icon="pencil", on_release=lambda x, i=item: self.go_wedding_screen(i))
                elif self.app.list_selected == "sent_responses":
                    if not 'response_type' in item : item['response_type']  = 'Unknown'
                    for m_data in self.responded_marriage:
                        if m_data['marriage_code'] == item['marriage_code']:
                            marriage_data = m_data
                    list_text = f"Code : {item['marriage_code']} - {item['response_type']} - {marriage_data['groom']} Weds {marriage_data['bride']}"
                    show_icon = IconLeftWidgetWithoutTouch(icon="hand-wave")
                    edit_icon = IconRightWidget(icon="pencil", on_release=lambda x, i=item: self.go_received_screen(i))

                if search_text.lower() in list_text.lower():
                    list_item = OneLineAvatarIconListItem()
                    list_item.text = self._highlight_match(list_text, search_text)
                    list_item.markup = True  # Enable rich text
                    view_icon = IconRightWidget(icon="eye-arrow-left", on_release=lambda x, i=item: self.show_details(i))
                    list_item.add_widget(show_icon)
                    list_item.add_widget(edit_icon)
                    list_item.add_widget(view_icon)
                    current_screen.ids.data_list.add_widget(list_item)


