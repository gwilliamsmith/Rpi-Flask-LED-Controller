from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
from LightThread import LightThread
from LEDStrip import LEDStrip
import signal

app = Flask(__name__)
CORS(app)

# Initialize the WS2812B LED strip
LED_COUNT = 30  # Change this to match the number of LEDs on your strip
LED_PIN = 12
LED_FREQ_HZ = 800000
LED_DMA = 10
LED_BRIGHTNESS = 50
LED_INVERT = False
LED_CHANNEL = 0

Strip1ThreadID = -1

# Strip of lights for under the desk
desk_strip = LEDStrip("desk_strip", LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)

"""
Helper functions:
"""

def getStrip1Thread():
    global desk_strip
    return desk_strip.thread
def killStrip1Thread():
    global desk_strip
    if desk_strip.thread is not None:
        print("Killing")
        desk_strip.thread.pause()
        desk_strip.thread.stop()
        desk_strip.thread.join()
        desk_strip.threadID=-1

def startStrip1Thread(function, *args, **kwargs):
    global desk_strip
    if desk_strip.thread is None:
        desk_strip.thread = LightThread(name = "Strip1Thread" ,target = function, *args, **kwargs)
        desk_strip.thread.start()
        desk_strip.threadID = desk_strip.thread.ident
        return desk_strip.thread
    else:
        print("Strip1 is already running something!")

def restartStrip1Thread(function, *args, **kwargs):
    killStrip1Thread()
    return startStrip1Thread(function, *args, **kwargs)

"""
Routes:
"""

@app.route('/setcolor', methods=['POST'])
def set_color():
    global desk_strip
    killStrip1Thread()
    # Read the color from the request body
    color = request.json['color']
    desk_strip.set_all_pixels(color)

    # Send a response to the client
    return jsonify({'status': 'success'})

@app.route('/setpattern', methods=['POST'])
def set_pattern():
    global desk_strip
    killStrip1Thread()

    # Read the color pattern from the request body
    pattern = request.json['pattern']

    desk_strip.set_pattern(pattern)

    # Send a response to the client
    return jsonify({'status': 'success'})

@app.route('/startrainbow', methods=['POST'])
def start_rainbow():
    global desk_strip
    # Start the rainbow cycle in a new thread
    if not request.data:
        restartStrip1Thread(desk_strip.cycle_rainbow)
    else:
        data = request.json
        interval = data.get('interval',10)
        speed = data.get('speed',20)
        restartStrip1Thread(desk_strip.cycle_rainbow, args=(interval,speed))
    # Send a response to the client
    return jsonify({'status': 'success'})

@app.route('/clear', methods=['POST'])
def clear():
    global desk_strip
    killStrip1Thread()
    desk_strip.clear()
    # Send a response to the client
    return jsonify({'status': 'success'})

@app.route('/colorwipe', methods=['POST'])
def color_wipe():
    global desk_strip

    data = request.json
    bg_color = data['bg_color']
    wipe_color = data['wipe_color']
    pixels = data['pixels']
    interval = data['interval']
    seamless = data['seamless']

    restartStrip1Thread(desk_strip.color_wipe, args=(bg_color, wipe_color, pixels, interval, seamless))

    return jsonify({'status': 'success'})

# Define the '/fadecolor' endpoint
@app.route('/fadecolor', methods=['POST'])
def fade_color():
    global desk_strip
    # Read the color, minimum brightness, maximum brightness, and interval from the request body, if present
    data = request.json
    color = data.get('color', '#FFFFFF')
    min_brightness = data.get('min_brightness', 0)
    max_brightness = data.get('max_brightness', 255)
    interval = data.get('interval', 500)
    restartStrip1Thread(desk_strip.fade,args=(color,min_brightness,max_brightness,interval))
    return jsonify({'status': 'success'})

@app.route('/fadepattern',methods=['POST'])
def fade_pattern():
    global desk_strip
    #Read the pattern, minimum brightness, maximum brightness, and interval from the request body, if present
    data = request.json
    pattern = data['pattern']
    min_brightness = data.get('min_brightness', 0)
    max_brightness = data.get('max_brightness', 255)
    interval = data.get('interval', 500)

    restartStrip1Thread(desk_strip.fadePattern, args=(pattern,min_brightness,max_brightness,interval))
    return jsonify({'status': 'success'})

@app.route('/blink',methods=['POST'])
def blink():
    global desk_strip
    data = request.json
    color1 = data.get('color1', '#FFFFFF')
    color2 = data.get('color2', '#000000')
    interval = data.get('interval', 500)

    restartStrip1Thread(desk_strip.blink,args=(color1,color2, interval))
    return jsonify({'status': 'success'})

@app.route('/pause',methods=['POST'])
def pause():
    thread = getStrip1Thread()
    if thread is not None:
        if not thread.paused():
            thread.pause()
            return jsonify({'status': 'success'})
        else:
            return jsonify({'error': 'Thread is already paused'})
    else:
        return jsonify({'error': 'No thread found'})

@app.route('/resume',methods=['POST'])
def resume():
    thread = getStrip1Thread()
    if thread is not None:
        if thread.paused():
            thread.resume()
            return jsonify({'status': 'success'})
        else:
            return jsonify({'error': 'Thread is not paused'})
    else:
        return jsonify({'error': 'No thread found'})

@app.route('/setbrightness', methods=['POST'])
def set_brightness():
    global desk_strip
    thread = getStrip1Thread()
    if thread is not None: thread.pause()
    data = request.json
    brightness = data.get('brightness', 127)
    desk_strip.set_brightness(brightness)
    if thread is not None: thread.resume()
    return jsonify({'status': 'success'})

"""
Clear the strip when the program ends from ctrl-c or on pi shutdown
"""
def end_signal_handler(signal, frame):
    global desk_strip
    """Clean up resources and exit the app when `SIGHUP` is received."""
    try:
        # Clean up resources here
        desk_strip.clear()
    except Exception as e:
        # Log the error
        print(f'Error while cleaning up resources: {e}')
    finally:
        # Exit the app
        exit(0)

signal.signal(signal.SIGHUP,end_signal_handler)
signal.signal(signal.SIGINT, end_signal_handler)


