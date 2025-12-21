from kivy.uix.modalview import ModalView
from kivy_garden.mapview import MapView, MapMarker


class MapPopup(ModalView):
    def __init__(self, text_input, **kwargs):
        super().__init__(**kwargs)
        self.text_input = text_input
        self.size_hint = (0.9, 0.9)
        self.auto_dismiss = False
        self.mapview = MapView(zoom=10, lat=12.9716, lon=77.5946)  # Bangalore as default
        self.mapview.bind(on_touch_up=self.on_map_touch)
        self.add_widget(self.mapview)

    def on_map_touch(self, instance, touch):
        if self.mapview.collide_point(*touch.pos):
            lat, lon = self.mapview.get_latlon_at(*touch.pos)
            self.text_input.text = f"{lat:.5f}, {lon:.5f}"
            marker = MapMarker(lat=lat, lon=lon)
            self.mapview.add_marker(marker)
            self.dismiss()
            return True
        return False