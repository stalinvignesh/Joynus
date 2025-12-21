import requests_cache

from Libraries.imports import *

class ProfileScreen(Screen):

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.app = MDApp.get_running_app()

    def on_enter(self):
        self.initial_values = {}
        #print(sys.path)
        if not "name" in self.app.user_details:
            self.app.change_screen("home")

        if self.app.user_details:
            for field_id, value in self.app.user_details.items():
                text_field = self.app.root.get_screen("profile_screen").ids.get(f"{field_id}_field")
                if text_field:
                    text_field.text = str(value)
                    if field_id == "mobile":
                        text_field.readonly = True
                    self.initial_values[field_id] = str(value)
                    # Bind to change handler
                    text_field.bind(text=self.check_if_modified)

    def check_if_modified(self, instance, value):
        modified = False
        for field_id, original in self.initial_values.items():
            current_value = self.app.root.get_screen("profile_screen").ids[f"{field_id}_field"].text
            if current_value != original:
                modified = True
                break
        self.app.root.get_screen("profile_screen").ids.update_btn.disabled = not modified

    def show_loading(self):
        """Create and show a loading dialog."""
        if not hasattr(self, 'loading_dialog'):
            box = MDBoxLayout(orientation='vertical', padding=20, spacing=20)
            spinner = MDSpinner(size_hint=(None, None), size=(46, 46), pos_hint={"center_x": 0.5})
            box.add_widget(spinner)
            self.loading_dialog = MDDialog(
                title="Updating...",
                type="custom",
                content_cls=box,
                auto_dismiss=False
            )
        self.loading_dialog.open()

    def hide_loading(self):
        """Dismiss the loading dialog if it exists."""
        if hasattr(self, 'loading_dialog'):
            self.loading_dialog.dismiss()

    def show_snackbar(self, message, success=True):
        MDSnackbar(MDLabel(text=message),
            bg_color=(0, 0.6, 0, 1) if success else (1, 0, 0, 1),
            duration=3
        ).open()

    def update_profile(self,name,email,mobile,age):
        self.show_loading()

        def _do_update(*args):
            new_data = {
                "name": name,
                "email": email,
                "age": age
            }
            payload = { "query" : {"mobile": mobile} , "data" : new_data }
            result = self.app.api.put("/update/user_data",json=payload)
            with requests_cache.disabled():
                self.app.user_details = self.app.api.get(f"/user_data/by_field/mobile/{self.app.phone_number}")

            self.hide_loading()

            if result.get("modified_count"):
                self.show_snackbar("User Data updated successfully.")
            else:
                self.show_snackbar("No changes made or user not found.", success=False)

        # Simulate slight delay (if needed) to make loading visible
        Clock.schedule_once(_do_update, 0.5)


