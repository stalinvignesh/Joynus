from Libraries.imports import *

class GiftScreen(Screen):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.app = MDApp.get_running_app()
        self.inserted = False


    def on_enter(self, *args):
        self.user_id = self.app.user_details["user_id"]
        self.mr_code = self.app.root.get_screen('marriage_home').ids.mar_code.text.upper()
        self.layout = self.ids.gift_layout
        top_label = MDLabel(text=f"Marriage Code : {self.mr_code}",halign="center",font_style="H4",adaptive_height=True)
        self.layout.add_widget(top_label)
        voucher_label = MDLabel(text=f"If you have any Gift Voucher to present, Enter Below",halign="left",
                                font_style="H6",adaptive_height=True)
        self.voucher_text = MDTextField(hint_text=f"Voucher code")
        self.layout.add_widget(voucher_label)
        self.layout.add_widget(self.voucher_text)
        voucher_words_label = MDLabel(text=f"Enter message to the recipient",halign="left",
                                      font_style="H6",adaptive_height=True)
        self.voucher_words_text = MDTextField(hint_text="Type anything on your mind to wish or congratulate")
        self.layout.add_widget(voucher_words_label)
        self.layout.add_widget(self.voucher_words_text)
        voucher_button = MDRaisedButton(text="SEND 💌",pos_hint={"center_x":0.5},font_name="Segoe-UI-Emoji",
                                        on_release=lambda x: self.send_gifts())
        self.layout.add_widget(voucher_button)
        or_label = MDLabel(text=f"OR",halign="center",font_style="H3",adaptive_height=True)
        self.layout.add_widget(or_label)
        pay_label = MDLabel(text=f"You can pour your blessings as CASH (Caring Act to Share Hearts)"
                            ,halign="center",font_style="H6",adaptive_height=True)
        self.payment_text = MDTextField(hint_text="Enter INR Amount to Pay Using UPI...")
        self.layout.add_widget(self.payment_text)
        pay_button = MDRaisedButton(text="PAY ❤️💸",pos_hint={"center_x":0.5},font_name="Segoe-UI-Emoji",
                                    on_release=lambda x: self.send_payments())
        self.layout.add_widget(pay_label)
        self.layout.add_widget(pay_button)

    def send_gifts(self,*args):
        payload = {"query": {"marriage_code": self.mr_code, "user_id": self.user_id }, "require": {}}
        self.gift_data = { "user_id" : self.user_id,
                              "marriage_code" : self.mr_code,
                              "voucher_code" : self.voucher_text.text,
                               "gift_message": self.voucher_words_text.text
                             }
        if self.inserted:
            self.app.show_dialog("Already Clicked",
                                     "Hope you have already gifted with us with your inputs!")
        else:
            gift_insert = self.app.api.post("/insert/gifts_payments",json=self.gift_data)
            self.inserted = True
            MDSnackbar(MDIcon(icon='hands-pray',adaptive_height=True,adaptive_width=True,
                                       size_hint_y=None),
            MDLabel(text="Thanks for your Valuable Gift !!!"),
                    snackbar_x="30dp",
                    snackbar_y="30dp",
                    md_bg_color=(0, 128, 0, 1),
                    orientation="horizontal",
                    duration=3
            ).open()

    def send_payments(self):
        upi_payload = {"query": {"marriage_code": self.mr_code.upper() } , "require": { "upi_id" : 1 , "_id" : 0 }}
        self.upi_response = self.app.api.post("/find_one/marriage_invites",json=upi_payload)
        #print(f"upi we got for mr code {self.mr_code} is {self.upi_response}")
        #from jnius import autoclass
        from urllib.parse import quote
        #Intent = autoclass('android.content.Intent')
        #Uri = autoclass('android.net.Uri')
        #PythonActivity = autoclass('org.kivy.android.PythonActivity')

        upi_id = self.upi_response["upi_id"]
        self.user_name = self.app.user_details["name"]
        note = f"Payment for Marriage Code  {self.mr_code.upper()}"

        uri = (
            "upi://pay"
            f"?pa={upi_id}"
            f"&pn={quote(self.user_name)}"
            f"&am={self.payment_text.text}"
            f"&cu=INR"
            f"&tn={quote(note)}"
        )

        #intent = Intent(Intent.ACTION_VIEW)
        #intent.setData(Uri.parse(uri))
        print(f"upi is {uri}")
        # Android will show chooser automatically
        #PythonActivity.mActivity.startActivity(intent)