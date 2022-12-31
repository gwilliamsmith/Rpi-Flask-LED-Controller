from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
from LightThread import LightThread
from LEDStrip import LEDStrip

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

strip1 = LEDStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)

"""
Helper functions:
"""

def getStrip1Thread():
    global Strip1ThreadID
    for thread in threading.enumerate():
        if(thread.ident == Strip1ThreadID):
            return thread
    return None
def killStrip1Thread():
    global Strip1ThreadID
    for thread in threading.enumerate():
        if(thread.ident == Strip1ThreadID):
            thread.pause()
            thread.stop()
            thread.join()
            Strip1ThreadID = -1

def startStrip1Thread(function, *args, **kwargs):
    global Strip1ThreadID
    if(Strip1ThreadID == -1):
        Strip1Thread = LightThread(name = "Strip1Thread" ,target = function, *args, **kwargs)
        Strip1Thread.start()
        Strip1ThreadID = Strip1Thread.ident
        return Strip1Thread
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
    killStrip1Thread()
    # Read the color from the request body
    color = request.json['color']
    LEDStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL).set_all_pixels(color)

    # Send a response to the client
    return jsonify({'status': 'success'})

@app.route('/setpattern', methods=['POST'])
def set_pattern():
    killStrip1Thread()

    # Read the color pattern from the request body
    pattern = request.json['pattern']

    LEDStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL).set_pattern(pattern)

    # Send a response to the client
    return jsonify({'status': 'success'})

@app.route('/startrainbow', methods=['POST'])
def start_rainbow():
    strip = LEDStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    # Start the rainbow cycle in a new thread
    if not request.data:
        restartStrip1Thread(strip.cycle_rainbow)
    else:
        data = request.json
        interval = data.get('interval',10)
        speed = data.get('speed',20)
        restartStrip1Thread(strip.cycle_rainbow, args=(interval,speed))
    # Send a response to the client
    return jsonify({'status': 'success'})

@app.route('/clear', methods=['POST'])
def clear():
    killStrip1Thread()
    LEDStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL).clear()
    # Send a response to the client
    return jsonify({'status': 'success'})

@app.route('/colorwipe', methods=['POST'])
def color_wipe():
    data = request.json
    bg_color = data['bg_color']
    wipe_color = data['wipe_color']
    pixels = data['pixels']
    interval = data['interval']
    seamless = data['seamless']

    strip = LEDStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    restartStrip1Thread(strip.color_wipe, args=(bg_color, wipe_color, pixels, interval, seamless))

    return jsonify({'status': 'success'})

# Define the '/fadecolor' endpoint
@app.route('/fadecolor', methods=['POST'])
def fade_color():
    # Read the color, minimum brightness, maximum brightness, and interval from the request body, if present
    data = request.json
    color = data.get('color', '#FFFFFF')
    min_brightness = data.get('min_brightness', 0)
    max_brightness = data.get('max_brightness', 255)
    interval = data.get('interval', 500)
    strip = LEDStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    restartStrip1Thread(strip.fade,args=(color,min_brightness,max_brightness,interval))
    return jsonify({'status': 'success'})

@app.route('/fadepattern',methods=['POST'])
def fade_pattern():
    #Read the pattern, minimum brightness, maximum brightness, and interval from the request body, if present
    data = request.json
    pattern = data['pattern']
    min_brightness = data.get('min_brightness', 0)
    max_brightness = data.get('max_brightness', 255)
    interval = data.get('interval', 500)

    strip = LEDStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    restartStrip1Thread(strip.fadePattern, args=(pattern,min_brightness,max_brightness,interval))
    return jsonify({'status': 'success'})

@app.route('/blink',methods=['POST'])
def blink():
    global strip1
    data = request.json
    color1 = data.get('color1', '#FFFFFF')
    color2 = data.get('color2', '#000000')
    interval = data.get('interval', 500)

    restartStrip1Thread(strip1.blink,args=(color1,color2, interval))
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
    global strip1
    thread = getStrip1Thread()
    if thread is not None: thread.pause()
    data = request.json
    brightness = data.get('brightness', 127)
    strip1.set_brightness(brightness)
    if thread is not None: thread.resume()
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

