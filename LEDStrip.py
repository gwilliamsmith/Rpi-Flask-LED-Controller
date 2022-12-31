import rpi_ws281x
import threading
import time
from LightThread import LightThread

class LEDStrip():
    def __init__(self, LED_COUNT=60, LED_PIN=18, LED_FREQ_HZ=800000, LED_DMA=10, LED_INVERT=False, LED_BRIGHTNESS=255, LED_CHANNEL=0):
        self.num_leds = LED_COUNT
        self.brightness = LED_BRIGHTNESS
        self.channel = LED_CHANNEL

        # Initialize the LED strip
        self.strip = rpi_ws281x.PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
        self.strip.begin()

    """
    Set a given pixel to a given color
    """
    def set_pixel_color(self, pixel, color):
        self.strip.setPixelColor(pixel, self.__translateColor(color))
        #self.strip.show()

    """
    Set all pixels to a given color
    """
    def set_all_pixels(self, color):
        for i in range(self.num_leds):
            self.strip.setPixelColor(i, self.__translateColor(color))
        self.strip.show()

    """
    Turn off all LEDs in the strip
    """
    def clear(self):
        self.set_all_pixels("#000000")

    """
    Set the strip to a color, and fade it from a min_brightness to a max brightness over an interval, and then do the reverse.
    """
    def fade(self, color, min_brightness, max_brightness, interval):
        self.set_all_pixels(color)
        self.__fadeBrightness(min_brightness,max_brightness,interval)
    """
    Cycle through a rainbow of colors, stepping over given interval (default 10) with a given speed out of 1 second (default 20)
    """
    def cycle_rainbow(self, interval = 10, speed = 20):
        current_thread = threading.current_thread()
        while not current_thread.stopped():
            while not current_thread.paused():
                for j in range(256 * interval):
                    for i in range(self.strip.numPixels()):
                        if(current_thread.stopped()):
                            return
                        self.strip.setPixelColor(i, self.__wheel((int(i * 256 / self.strip.numPixels()) + j) & 255))
                    self.strip.show()
                    if(current_thread.stopped()):
                        return
                    time.sleep(speed / 1000.0)

    """
    Set a strip to a given pattern.
    """
    def set_pattern(self, pattern):
        # Set the color of each LED to the corresponding color in the pattern
        for color_position in pattern:
            color = color_position['color']
            if 'start' in color_position and 'end' in color_position:
                # Set the color of a range of LEDs
                start, end = color_position['start'], color_position['end']
                for i in range(start, end + 1):
                    self.set_pixel_color(i,color)
            else:
                # Set the color of a single LED
                position = color_position['position']
                self.set_pixel_color(position,color)
        self.strip.show()

    def color_wipe(self, bg_color, wipe_color, pixels, interval, seamless):
        current_thread = threading.current_thread()

        pixels = min(pixels, self.strip.numPixels())

        counter = 0
        print(seamless)
        
        # Loop indefinitely

        while not current_thread.stopped():
            while not current_thread.paused():
                # Set the background color for all LEDs
                for i in range(self.strip.numPixels()):
                    self.set_pixel_color(i, bg_color)
                # Set the wipe color for the specified number of pixels
                for i in range(pixels):
                    if seamless:
                        self.set_pixel_color((i+counter)%self.strip.numPixels(), wipe_color)
                    else:
                        self.set_pixel_color((i+counter), wipe_color)
                    if current_thread.stopped(): 
                        return
                    # Increment the counter variable
                counter = (counter + 1) % self.strip.numPixels()

                self.strip.show()

                if current_thread.stopped(): 
                    return

                # Wait for the specified interval
                time.sleep(interval / 1000.0)

    """
    Set a pattern for the LED strip, then fade from a min brighness to a max and back on an interval
    """
    def fadePattern(self, pattern, min_brightness, max_brightness, interval):
        # First, set the pattern of the LED Strip
        self.set_pattern(pattern)
        
        #Then, fade using the given parameters
        self.__fadeBrightness(min_brightness,max_brightness,interval)

    """
    Blink the entire strip between two colors on an interval
    """
    def blink(self, color1, color2, interval):
        current_thread = threading.current_thread()

        colorFlip = False

        while not current_thread.stopped():
            if colorFlip:
                self.set_all_pixels(color2)
                colorFlip = False
            else:
                self.set_all_pixels(color1)
                colorFlip = True
            time.sleep(interval/1000.0) 


    """
    Translates a color from a given hexcode color (#FFFFFF) to a rpi_ws281x color that can be used to set a pixel
    """
    def __translateColor(self, color):
        r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
        return rpi_ws281x.Color(r,g,b)

    """
    Generate rainbow colors across 0-255 positions. Private method
    """
    def __wheel(self, pos):
        if pos < 85:
            return rpi_ws281x.Color(pos * 3, 255 - pos * 3, 0)
        elif pos < 170:
            pos -= 85
            return rpi_ws281x.Color(255 - pos * 3, 0, pos * 3)
        else:
            pos -= 170
            return rpi_ws281x.Color(0, pos * 3, 255 - pos * 3)

    def __fadeBrightness(self, min_brightness, max_brightness, interval):
        strip = self.strip
        current_thread = threading.current_thread()

        # Loop indefinitely
        while not current_thread.stopped():
            # Fade in the LEDs
            for i in range(min_brightness, max_brightness + 1):
                if(current_thread.stopped()):
                        return
                strip.setBrightness(i)
                strip.show()
                time.sleep(interval / 1000.0)

            # Fade out the LEDs
            for i in range(max_brightness, min_brightness - 1, -1):
                if(current_thread.stopped()):
                        return
                strip.setBrightness(i)
                strip.show()
                time.sleep(interval / 1000.0)