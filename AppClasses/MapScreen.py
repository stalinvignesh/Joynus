from kivy_garden.mapview import MapView, MapMarker
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.toast import toast
from kivy.properties import ObjectProperty
import time

class MapScreen(MDScreen):
    target_input = ObjectProperty()
    last_tap_time = 0
    last_tap_pos = (0, 0)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = MDApp.get_running_app()

    def on_enter(self):
        #print(dir(self.ids.mapview))
        toast(text="Double click to set the location",duration=3)
        self.ids.mapview.bind(on_touch_down=self.on_map_double_tap)

    def on_map_double_tap(self, instance, touch):
        # Check if it's inside the mapview only
        if not self.ids.mapview.collide_point(*touch.pos):
            #print(*touch.pos)
            #print("was in collide point")
            return

        # Prevent false triggers (like scroll/drag)
        if abs(touch.dx) > 5 or abs(touch.dy) > 5:
            #print(f"{abs(touch.dx)} and {abs(touch.dy)} is touch dx and dy")
            return  # it's a swipe/drag not a tap

        now = time.time()
        if (now - self.last_tap_time) < 1 and self._is_same_position(touch.pos, self.last_tap_pos):
            try:
                lat, lon = self.ids.mapview.get_latlon_at(*touch.pos)
                self.target_input.text = f"{lat:.5f}, {lon:.5f}"
                marker = MapMarker(lat=lat, lon=lon)
                self.ids.mapview.add_marker(marker)
                #print("inside Try block")
                #print(f"{now} {self.last_tap_time} was times")
                #print(touch.pos)
                #print(self.last_tap_pos)
                self.app.change_screen("wedding_details")
            except Exception as e:
                print("Error converting touch to lat/lon:", e)
        else:
            self.last_tap_time = now
            self.last_tap_pos = touch.pos

    def _is_same_position(self, pos1, pos2, threshold=30):
        return abs(pos1[0] - pos2[0]) < threshold and abs(pos1[1] - pos2[1]) < threshold
