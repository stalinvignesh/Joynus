import io
from PIL import Image as PILImage
import requests
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.carousel import Carousel
from kivy.uix.scatter import Scatter
from plyer import filechooser
from Libraries.imports import *
from kivymd.uix.filemanager import MDFileManager
from kivy.uix.filechooser import FileChooserListView , FileChooserIconView


class PhotoScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = MDApp.get_running_app()
        self.textures = []

    def on_enter(self):
        if not "user_id" in self.app.user_details:
            self.app.change_screen("home")
            return
        else:
            self.user_id = self.app.user_details["user_id"]
            self.current_screen = self.app.root.get_screen('photo_screen')
            self.photo_layout = self.current_screen.ids.photo_layout
            self.mr_code = self.app.root.get_screen('marriage_home').ids.mar_code.text.upper()
            self.selected_path = []
            self.file_manager = MDFileManager(
                exit_manager=self.exit_manager,
                select_path=self.upload_photos,
                selector="multi",
                preview=True,  # Show image previews
                ext=[".png", ".jpg", ".jpeg", ".JPG"]  # Filter for images only
            )
            self.load_photos(self.mr_code)

    def upload_photos(self ,selected_path):
        self.exit_manager()
        files = []
        #files = [('files', open(fp, 'rb')) for fp in selected_path]
        for fp in selected_path:
            img = PILImage.open(fp)
            max_size = (1200, 1200)
            img.thumbnail(max_size)
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG', quality=80)
            img_byte_arr.seek(0)
            file_name = f"{os.path.basename(fp).split(".")[0]}.jpg"
            files.append(('files',(file_name,img_byte_arr,'image/jpeg')))
        data = {'user_id': self.user_id , 'marriage_code' : self.mr_code}
        toast(text="Uploading photo...", duration=3)
        uploaded = self.app.api.post("/upload_photos", files=files, data=data)
        print(f"{uploaded}")
        if self.textures:
            self.textures = []
        self.load_photos(self.mr_code)

    def open_file_manager(self, *args):
        # Open file manager at a default path (e.g., home directory)
        self.file_manager.show_disks()


    def exit_manager(self, *args):
        self.file_manager.close()

    def load_photos(self, user_id):
        self.photo_layout.clear_widgets()
        self.photo_ids = self.app.api.get(f"/get_photos/marriage/{self.mr_code}")
        print(self.photo_ids)
        if self.textures:
            idx = 0
            for texture_dict in self.textures:
                pid = texture_dict["pid"]
                texture = texture_dict["texture"]
                print(pid)
                img = Image(texture=texture)
                img.id = pid
                #self.textures.append({"pid": pid, "index": idx, "texture": texture})
                img.size_hint_x = 1  # Fill width
                img.size_hint_y = None
                img.height = dp(200)
                img.bind(on_touch_down=lambda inst, touch,i=idx: self.open_viewer(inst, i) if inst.collide_point(
                    *touch.pos) else None)
                self.photo_layout.add_widget(img)
                idx+=1
        else:
            idx = 0
            for photo_data in self.photo_ids:
                for pid in photo_data["photo_ids"]:
                    headers = self.app.api._headers()
                    img_d = requests.get(f"{self.app.api.base_url}/get_photo/{pid}", headers=headers)
                    img_data = img_d.content
                    data = io.BytesIO(img_data)
                    texture = CoreImage(data, ext="jpg").texture
                    img = Image(texture=texture)
                    img.id = pid
                    self.textures.append({"pid": pid, "index": idx, "texture": texture})
                    img.size_hint_x = 1  # Fill width
                    img.size_hint_y = None
                    img.height = dp(200)
                    img.bind(on_touch_down=lambda inst, touch,i=idx: self.open_viewer(inst, i) if inst.collide_point(
                        *touch.pos) else None)
                    self.photo_layout.add_widget(img)
                    idx += 1

    def open_viewer(self, img_obj, index):
        viewer = self.app.root.get_screen('photo_viewer')
        viewer.open_photos(img_obj,index)
        self.app.change_screen("photo_viewer")

class PhotoViewerScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = MDApp.get_running_app()


    def open_photos(self, img_obj, index):
        self.carousel = self.ids.carousel
        self.carousel.clear_widgets()
        self.textures = self.app.root.get_screen('photo_screen').textures
        self.user_id = self.app.user_details["user_id"]
        self.mr_code = self.app.root.get_screen('marriage_home').ids.mar_code.text.upper()

        for texture_dict in self.textures:
            texture = texture_dict.get("texture")
            pid = texture_dict.get("pid")
            img = Image(size_hint=(None,None))
            img.id = pid
            img.texture = texture
            img.allow_stretch = True
            img.keep_ratio = True
            Window.bind(size=self._update_size)
            self._update_size(img)
            scatter = Scatter(do_rotation=False, do_translation=True, do_scale=True, size_hint=(1, 1), pos=(0, 0))
            scatter.id = pid
            more_btn = MDIconButton(
                id=pid,
                icon="dots-vertical",
                pos_hint={"right": 0.98, "top": 0.98},
                on_release=lambda x: self.open_options(x)
            )
            self.add_widget(more_btn)
            scatter.add_widget(img)
            self.carousel.add_widget(scatter)
        self.carousel.index = index


    def _update_size(self,img):
        #scatter.size = Window.size
        img.size = Window.size

    def open_options(self, button_instance):
        menu_items = [
            { "viewclass": "CustomOneLineIconListItem","text": "Download","icon" : "download-outline",
             "on_release": lambda x="download": self.menu_callback(x)},
            {"viewclass": "CustomOneLineIconListItem", "text": "Delete", "icon": "delete-outline",
             "on_release": lambda x="delete": self.menu_callback(x)},
            {"viewclass": "CustomOneLineIconListItem","text": "Share", "icon": "share-outline",
             "on_release": lambda x="share": self.menu_callback(x)},
        ]

        self.menu = MDDropdownMenu(
            caller=button_instance,
            items=menu_items,
            width_mult=4,
        )
        self.menu.open()

    def menu_callback(self, action):
        print(f"Selected: {action}  {self.menu.items}")
        current_scatter = self.carousel.current_slide
        pid = current_scatter.id
        current_image = next((c for c in current_scatter.children if isinstance(c, Image)), None)
        self.menu.dismiss()
        self.list_selected = action
        if action == "download" :
            self.save_photo(current_image)
        elif action == "delete":
            dialog = MDDialog(
                title="Delete Confirm",
                text="Are you Sure to delete this photo?",
                buttons=[
                    MDRaisedButton(text="Yes! Sure",
                                   on_release=lambda x: (dialog.dismiss(),self.delete_photo(current_image,current_scatter))),
                    MDRaisedButton(text="Ah Ok! Let's Keep it", on_release=lambda x: dialog.dismiss())
                ]
            )
            dialog.open()

        elif action == "share":
            self.share_photo(current_image)


    def delete_photo(self,current_image,current_scatter):
        pid = current_image.id
        data = {'user_id': self.user_id , 'marriage_code' : self.mr_code}
        print(f"deleting pid {pid}")
        toast(text="Deleting photo...", duration=1)
        deleted = self.app.api.post(f"/delete_photo/{pid}", data=data)
        #delete_texture = [ self.textures.remove(t.get(pid)) for t in self.textures]
        self.app.root.get_screen('photo_screen').textures = list(filter(lambda d: d.get('pid') != pid, self.textures))
        self.carousel.remove_widget(current_scatter)
        current_index = self.carousel.index
        if len(self.carousel.slides) > 0:
            self.carousel.index = min(current_index, len(self.carousel.slides) - 1)
        else:
            # No slides left? Maybe go back to previous screen
            self.app.change_screen("photo_screen")
        print(f"Delete {deleted} ")


    def share_photo(self,current_image):
        pid = current_image.id
        data = BytesIO()
        core_image = CoreImage(current_image.texture)
        core_image.save(data, fmt='jpg')
        bytes_data = data.getvalue()
        from kivy.utils import platform
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.WRITE_EXTERNAL_STORAGE])

            from android.storage import primary_external_storage_path
            storage_path = primary_external_storage_path()
            file_path = f"{storage_path}/Download/{pid}.jpg"
        else:
            file_path = f"C:\\Users\\admin\\Downloads\\{pid}.jpg"
        with open(file_path, "wb") as f:
            f.write(bytes_data)
        #from plyer import share
        #share.share(filepath=file_path, title="Check out this photo!")
        print(f"Share  {pid}  ")
        # For Android, use plyer.share or Android intent

    def save_photo(self,current_image):
        pid = current_image.id
        data = BytesIO()
        core_image = CoreImage(current_image.texture)
        core_image.save(data, fmt='jpg')
        bytes_data = data.getvalue()
        from kivy.utils import platform
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.WRITE_EXTERNAL_STORAGE])

            from android.storage import primary_external_storage_path
            storage_path = primary_external_storage_path()
            file_path = f"{storage_path}/Download/{pid}.jpg"
        else:
            file_path = f"C:\\Users\\admin\\Downloads\\{pid}.jpg"
        with open(file_path, "wb") as f:
            f.write(bytes_data)
        self.app.show_dialog("Saved","Photo Saved in Downloads")
        print(f"Saved in Downloads {pid} ")
        # Save a copy locally if needed
