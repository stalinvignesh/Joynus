from Libraries.imports import *

class RegisterScreen(Screen):

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.app = MDApp.get_running_app()


    def save_user_details(self,name,email,mobile,age,pin):
        self.current_screen = self.app.root.get_screen("register_screen")
        name = self.current_screen.ids.name_field.text.strip()
        age = self.current_screen.ids.age_field.text.strip()
        mobile = self.current_screen.ids.mobile_field.text.strip()
        email = self.current_screen.ids.email_field.text.strip()
        pin =self.current_screen.ids.pin_field.text.strip()

        if not name or not age or not email or not pin or not mobile:
            self.app.show_dialog("Incomplete Form", "Please fill in all fields.")
            return

        try:
            if self.app.api.register(mobile, pin):
                payload = {
                    "mobile": mobile,
                    "name": name,
                    "age": age,
                    "email": email,
                    "pin": pin,
                }
                self.register_response = self.app.api.post("/register_new",json=payload)
                email_got = self.register_response.get("email")
                mobile_got = self.register_response.get("mobile")
                message = self.register_response.get("message")

                if mobile_got == "Error":
                    self.app.show_dialog("Register Error", f"Error inserting in DB {message}")
                    return
                self.app.show_dialog("Registration Success",f"Thank You.New User {mobile_got} with {email_got} id Registered")
            else:
                self.app.show_dialog("Register Error", "Register Failed.Check If mobile already exists with Login")
        except Exception as e:
            self.app.show_dialog("Register Error", f"Check If mobile already exists with Login.Error : \n{str(e)}")
            return
        self.app.change_screen("login")