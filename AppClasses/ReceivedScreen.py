from Libraries.imports import *

class ReceivedScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = MDApp.get_running_app()
        self.selected_item = ""


    def on_enter(self):
        if not "user_id" in self.app.user_details:
            self.app.change_screen("home")
            return
        else:
            self.userid = self.app.user_details["user_id"]
            if self.userid:
                    self.selected_item = self.app.list_selected
            else:
                self.app.show_dialog("Become User", "Come on! Be an user, go back home and register please!")
                return

            payload = {"query": {"user_id": self.userid},
                       "require": {"marriage_code": 1, "groom": 1, "bride": 1, "marriage_date": 1}}
            self.list_of_mr_codes = self.app.api.post("/find/marriage_invites", json=payload)
            self.current_screen = self.app.root.get_screen('received_resp')
            self.render_list("")


    def open_drop_down(self,caller_widget):

        menu_items = [
            {
                "text": f"{mr_code["marriage_code"]} -- {mr_code["groom"]} Weds {mr_code["bride"]}",
                "on_release": lambda x=mr_code["marriage_code"]: self.show_details(x, caller_widget)
            }
            for mr_code in self.list_of_mr_codes
        ]
        self.menu = MDDropdownMenu(
            caller=caller_widget,
            items=menu_items,
            width_mult=4
        )
        self.menu.open()

    def show_details(self, mr_code, widget):
        widget.set_item(mr_code)
        self.menu.dismiss()

        if self.selected_item == "received_responses" :
            pipeline = [
                { "$lookup" :
                  {"from" : "user_data" , "localField" : "user_id" , "foreignField" : "user_id" , "as" : "user" }},
                {"$unwind": { "path" : "$user" , "preserveNullAndEmptyArrays": True } },
                {"$match" : {"marriage_code" : mr_code}},
                {"$project": { "response_type":1, "inviter_relation":1,"food_count":1 ,"engagement_availability":1,
                           "accommodation_needed":1 ,"response_message":1,"user_name":1,
                            "user": {"email": "$user.email", "mobile": "$user.mobile"}}}
                ]
            self.response = self.app.api.post("/aggregate/marriage_responses", json=pipeline)
            #print(response)
            if not self.response:
                self.app.show_dialog("No Data","No Response for this Marriage Code")


            self.current_screen.ids.data_list.clear_widgets()

            for resp in self.response:
                if not 'user_name' in resp: resp['user_name'] = 'Unknown Name'
                list_item = OneLineAvatarIconListItem(
                    text=f"{resp['user_name']} - {resp['user']['mobile']} - {resp['user']['email']} - {resp['response_type']}"
                )
                view_icon = IconRightWidget(icon="eye-arrow-left", on_release=lambda x, i=resp: self.show_response(i))
                show_icon = IconLeftWidgetWithoutTouch(icon="account-arrow-right-outline")
                list_item.add_widget(show_icon)
                list_item.add_widget(view_icon)
                self.current_screen.ids.data_list.add_widget(list_item)

        elif self.app.list_selected == "received_feedbacks":
            pipeline = [
                { "$lookup" :
                  {"from" : "user_data" , "localField" : "user_id" , "foreignField" : "user_id" , "as" : "user" }},
                {"$unwind": { "path" : "$user" , "preserveNullAndEmptyArrays": True } },
                {"$match" : {"marriage_code" : mr_code}},
                {"$project": { "feedback":1,"updated" : 1, "user" : { "name": 1 , "mobile" : 1 , "email" : 1 }}}
                ]
            self.feedback_response = self.app.api.post("/aggregate/marriage_feedbacks", json=pipeline)
            if not self.feedback_response:
                self.app.show_dialog("No Data","No Response for this Marriage Code")

            self.current_screen.ids.data_list.clear_widgets()

            for resp in self.feedback_response:
                if not 'user_name' in resp: resp['user_name'] = 'Unknown Name'
                list_item = OneLineAvatarIconListItem(
                    text=f"{resp['user']['name']} - {resp['user']['mobile']} - {resp['user']['email']} - {resp['feedback']} - {resp['updated']}"
                )
                show_icon = IconLeftWidgetWithoutTouch(icon="account-arrow-right-outline")
                list_item.add_widget(show_icon)
                self.current_screen.ids.data_list.add_widget(list_item)
        elif self.app.list_selected == "received_gifts":
            pipeline = [
                { "$lookup" :
                  {"from" : "user_data" , "localField" : "user_id" , "foreignField" : "user_id" , "as" : "user" }},
                {"$unwind": { "path" : "$user" , "preserveNullAndEmptyArrays": True } },
                {"$match" : {"marriage_code" : mr_code}},
                {"$project": { "voucher_code":1,"gift_message" : 1, "user" : { "name": 1 , "mobile" : 1 , "email" : 1 }}}
                ]
            self.gifts_response = self.app.api.post("/aggregate/gifts_payments", json=pipeline)
            if not self.gifts_response:
                self.app.show_dialog("No Data","No Response for this Marriage Code")

            self.current_screen.ids.data_list.clear_widgets()

            for resp in self.gifts_response:
                if not 'user_name' in resp: resp['user_name'] = 'Unknown Name'
                list_item = OneLineAvatarIconListItem(
                    text=f"{resp['user']['name']} - {resp['user']['mobile']} - {resp['user']['email']} - {resp['voucher_code']} - {resp['gift_message']}"
                )
                show_icon = IconLeftWidgetWithoutTouch(icon="account-arrow-right-outline")
                list_item.add_widget(show_icon)
                self.current_screen.ids.data_list.add_widget(list_item)

    def show_response(self,resp):
        content = MDBoxLayout(orientation="vertical", spacing=10, padding=10, adaptive_height=True,
                              adaptive_width=True, size_hint=(None, None))
        if not 'user_name' in resp: resp['user_name'] = 'Unknown Name'
        if not 'inviter_relation' in resp : resp['inviter_relation'] = 'Not Mentioned'
        content.add_widget(
            MDLabel(text=f"[b]Name : {resp["user_name"]}  [i]Mobile : {resp["user"]["mobile"]} "
                         f"Email : {resp["user"]["email"]}[/i][/b]"
                         f"[/b]", markup=True, adaptive_height=True, adaptive_width=True))
        content.add_widget(
            MDLabel(text=f"[b]Related As : {resp["inviter_relation"]}[/b]",
                         markup=True, adaptive_height=True, adaptive_width=True))
        if resp["response_type"] == "in-person":
            if resp["food_count"]:
                for meal, count in resp["food_count"].items():
                    content.add_widget(
                        MDLabel(text=f"[b][u]Food Count for {meal}[/u] - [i]{count}[/i]"
                                f"[/b]", markup=True, adaptive_height=True, adaptive_width=True))
            content.add_widget(
                MDLabel(text=f"[b]Available For Engagement : {resp["engagement_availability"]}",
                        markup=True, adaptive_height=True, adaptive_width=True))
            content.add_widget(
                MDLabel(text=f"[b]Accommodation Needed[Rooms]: {resp["accommodation_needed"]}",
                        markup=True, adaptive_height=True, adaptive_width=True))
            content.add_widget(
                MDLabel(text=f"[b]Response Message : [/b][i] {resp["response_message"]}[/i]",
                        markup=True, adaptive_height=True, adaptive_width=True))

        elif resp["response_type"] == "virtual":
            content.add_widget(MDLabel(text=f"[b]Response Message for Virtually Attending: [i]{resp["response_message"]}[/i]"
                                        f"[/b]", markup=True,adaptive_height=True,adaptive_width=True))

        card = MDCard(orientation="vertical", padding=20, size_hint=(None, None),
                      md_bg_color=self.app.theme_cls.primary_color,
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
        if hasattr(self,"response"):
            self.current_screen.ids.data_list.clear_widgets()
            for item in self.response:
                list_text = f"{item['user_name']} - {item['user']['mobile']} - {item['user']['email']} - {item['response_type']}"
                if search_text.lower() in list_text.lower():
                    list_item = OneLineAvatarIconListItem()
                    list_item.text = self._highlight_match(list_text, search_text)
                    list_item.markup = True  # Enable rich text
                    list_item.add_widget(IconLeftWidgetWithoutTouch(icon="account-arrow-right-outline"))
                    view_icon = IconRightWidget(icon="eye-arrow-left", on_release=lambda x, i=item: self.show_response(i))
                    list_item.add_widget(view_icon)
                    self.current_screen.ids.data_list.add_widget(list_item)
        if hasattr(self,"feedback_response"):
            self.current_screen.ids.data_list.clear_widgets()
            for resp in self.feedback_response:
                list_text = text=f"{resp['user']['name']} - {resp['feedback']} - {resp['user']['mobile']} - {resp['user']['email']} -  {resp['updated']}"
                if search_text.lower() in list_text.lower():
                    list_item = OneLineAvatarIconListItem()
                    list_item.text = self._highlight_match(list_text, search_text)
                    list_item.markup = True  # Enable rich text
                    list_item.add_widget(IconLeftWidgetWithoutTouch(icon="account-arrow-right-outline"))
                    self.current_screen.ids.data_list.add_widget(list_item)
        if hasattr(self,"gifts_response"):
            self.current_screen.ids.data_list.clear_widgets()
            for resp in self.gifts_response:
                list_text = text=f"{resp['user']['name']} - {resp['voucher_code']} - {resp['gift_message']} - {resp['user']['mobile']} - {resp['user']['email']}"
                if search_text.lower() in list_text.lower():
                    list_item = OneLineAvatarIconListItem()
                    list_item.text = self._highlight_match(list_text, search_text)
                    list_item.markup = True  # Enable rich text
                    list_item.add_widget(IconLeftWidgetWithoutTouch(icon="account-arrow-right-outline"))
                    self.current_screen.ids.data_list.add_widget(list_item)
