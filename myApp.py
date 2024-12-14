import cv2   #For processing images
import zxing #For decoding barcode or QR code
import numpy as np #Handling arrays/ numerical operations
import tempfile #Allows creation of temporary files
#Importing kivy module
from kivy.app import App #Base class for Kivy application
from kivy.uix.camera import Camera #Accessing the device camera
from kivy.uix.label import Label #Displaying the text
from kivy.uix.boxlayout import BoxLayout #Organizing vertical/horizontal arrangement
from kivy.clock import Clock #schedule the periodic tasks
from kivy.graphics.texture import Texture 

class QRScannerApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical')
        self.camera = Camera(play=True)
        self.label = Label(text="Scan a QR code")
        self.layout.add_widget(self.camera)
        self.layout.add_widget(self.label)

        #Creating a ZXing decoder instance
        self.decoder = zxing.BarCodeReader()

        #Storing scanned QR codes to avoid duplicates using set function
        self.scanned_codes = set()

        #Call on_frame every 1/30th of a second
        Clock.schedule_interval(self.on_frame, 1.0 / 30.0)

        return self.layout

    def on_frame(self, dt):
        frame = self.camera.texture
        if frame:
            # Convert Kivy texture buffer to NumPy array
            buf = frame.pixels
            width, height = frame.size
            img = np.frombuffer(buf, dtype=np.uint8).reshape((height, width, 4)) 

            #Converting the image to RGB (OpenCV uses BGR by default)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)

            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
                temp_filename = tmpfile.name
                cv2.imwrite(temp_filename, img_rgb)

            #Decoding the image using ZXing
            barcode = self.decoder.decode(temp_filename)

            if barcode:
                qr_data = barcode.parsed
                self.label.text = f"QR Code Found: {qr_data}"

                #Checking if the QR code is already scanned
                if qr_data not in self.scanned_codes:
                    self.scanned_codes.add(qr_data)

                    #Writing scanned QR codes to a text file
                    with open("scanned_qr_codes.txt", "a") as file:
                        file.write(qr_data + "\n")

            texture = Texture.create(size=(img_rgb.shape[1], img_rgb.shape[0]), colorfmt='rgb')
            texture.blit_buffer(img_rgb.tobytes(), colorfmt='rgb', bufferfmt='ubyte')
            self.camera.texture = texture

if __name__ == '__main__':
    QRScannerApp().run()
