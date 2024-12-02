import cv2
import zxing
import numpy as np
import tempfile
from kivy.app import App
from kivy.uix.camera import Camera
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.graphics.texture import Texture


class QRScannerApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical')
        self.camera = Camera(play=True)
        self.label = Label(text="Scan a QR code")
        self.layout.add_widget(self.camera)
        self.layout.add_widget(self.label)

        # Create a ZXing decoder instance
        self.decoder = zxing.BarCodeReader()

        # Set to store scanned QR codes to avoid duplicates
        self.scanned_codes = set()

        # Call on_frame every 1/30th of a second
        Clock.schedule_interval(self.on_frame, 1.0 / 30.0)

        return self.layout

    def on_frame(self, dt):
        frame = self.camera.texture
        if frame:
            # Convert Kivy texture buffer to NumPy array
            buf = frame.pixels
            width, height = frame.size
            img = np.frombuffer(buf, dtype=np.uint8).reshape((height, width, 4))  # RGBA format

            # Convert the image to RGB (OpenCV uses BGR by default)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)

            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
                temp_filename = tmpfile.name
                cv2.imwrite(temp_filename, img_rgb)

            # Decode the image using ZXing
            barcode = self.decoder.decode(temp_filename)

            if barcode:
                qr_data = barcode.parsed
                self.label.text = f"QR Code Found: {qr_data}"

                # Check if the QR code is already scanned
                if qr_data not in self.scanned_codes:
                    self.scanned_codes.add(qr_data)

                    # Write scanned QR codes to a text file
                    with open("scanned_qr_codes.txt", "a") as file:
                        file.write(qr_data + "\n")

            texture = Texture.create(size=(img_rgb.shape[1], img_rgb.shape[0]), colorfmt='rgb')
            texture.blit_buffer(img_rgb.tobytes(), colorfmt='rgb', bufferfmt='ubyte')
            self.camera.texture = texture


if __name__ == '__main__':
    QRScannerApp().run()

