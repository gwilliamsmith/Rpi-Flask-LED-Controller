from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
from LightThread import LightThread
from LEDStrip import LEDStrip
import signal
import jsonschema
import route_schemas as rschema

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

# Dict of LEDStrips
Strips = {}

#Strips['desk_strip'] = LEDStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)

"""
Helper functions:
"""

def setup_strip(STRIP_NAME, LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_BRIGHTNESS, LED_INVERT, LED_CHANNEL):
    global Strips
    if len(Strips) >= 3:
        raise ValueError("Max number of strips reached")
    Strips[STRIP_NAME] = LEDStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_BRIGHTNESS, LED_INVERT, LED_CHANNEL)

def get_strip(strip_name):
    global Strips
    return Strips[strip_name]
"""
Routes:
"""

@app.route('/setcolor', methods=['POST'])
def set_color():
    try:
        target_strip = get_strip(request.json['strip_name'])
    except KeyError:
        return jsonify({'error': 'No strip specified'}), 400
    target_strip.stop_thread()
    # Read the color from the request body

    color = request.json['color']
    target_strip.set_all_pixels(color)

    # Send a response to the client
    return jsonify({'status': 'success'})

@app.route('/setpattern', methods=['POST'])
def set_pattern():
    try:
        target_strip = get_strip(request.json['strip_name'])
    except KeyError:
        return jsonify({'error': 'No strip specified'}), 400
    target_strip.stop_thread()

    # Read the color pattern from the request body
    data = request.json
    pattern = data['pattern']
    brightness = data.get('brightness', 50)

    target_strip.set_pattern(pattern)

    # Send a response to the client
    return jsonify({'status': 'success'})

@app.route('/startrainbow', methods=['POST'])
def start_rainbow():
    try:
        target_strip = get_strip(request.json['strip_name'])
    except KeyError:
        return jsonify({'error': 'No strip specified'}), 400
    # Start the rainbow cycle in a new thread
    if not request.data:
        target_strip.restart_thread(target_strip.cycle_rainbow)
    else:
        data = request.json
        interval = data.get('interval',10)
        speed = data.get('speed',20)
        target_strip.restart_thread(target_strip.cycle_rainbow, args=(interval,speed))
    # Send a response to the client
    return jsonify({'status': 'success'})

@app.route('/clear', methods=['POST'])
def clear():
    try:
        target_strip = get_strip(request.json['strip_name'])
    except KeyError:
        return jsonify({'error': 'No strip specified'}), 400
    target_strip.stop_thread()
    target_strip.clear()
    # Send a response to the client
    return jsonify({'status': 'success'})

@app.route('/colorwipe', methods=['POST'])
def color_wipe():
    try:
        target_strip = get_strip(request.json['strip_name'])
    except KeyError:
        return jsonify({'error': 'No strip specified'}), 400

    data = request.json
    bg_color = data['bg_color']
    wipe_color = data['wipe_color']
    pixels = data['pixels']
    interval = data['interval']
    seamless = data['seamless']
    brightness = data.get('brightness', 50)

    target_strip.restart_thread(target_strip.color_wipe, args=(bg_color, wipe_color, pixels, interval, seamless))

    return jsonify({'status': 'success'})

# Define the '/fadecolor' endpoint
@app.route('/fadecolor', methods=['POST'])
def fade_color():
    try:
        target_strip = get_strip(request.json['strip_name'])
    except KeyError:
        return jsonify({'error': 'No strip specified'}), 400
    # Read the color, minimum brightness, maximum brightness, and interval from the request body, if present
    data = request.json
    color = data.get('color', '#FFFFFF')
    min_brightness = data.get('min_brightness', 0)
    max_brightness = data.get('max_brightness', 255)
    interval = data.get('interval', 500)
    target_strip.restart_thread(target_strip.fade,args=(color,min_brightness,max_brightness,interval))
    return jsonify({'status': 'success'})

@app.route('/fadepattern',methods=['POST'])
def fade_pattern():
    try:
        target_strip = get_strip(request.json['strip_name'])
    except KeyError:
        return jsonify({'error': 'No strip specified'}), 400
    #Read the pattern, minimum brightness, maximum brightness, and interval from the request body, if present
    data = request.json
    pattern = data['pattern']
    min_brightness = data.get('min_brightness', 0)
    max_brightness = data.get('max_brightness', 255)
    interval = data.get('interval', 500)

    target_strip.restart_thread(target_strip.fadePattern, args=(pattern,min_brightness,max_brightness,interval))
    return jsonify({'status': 'success'})

@app.route('/blink',methods=['POST'])
def blink():
    try:
        target_strip = get_strip(request.json['strip_name'])
    except KeyError:
        return jsonify({'error': 'No strip specified'}), 400
    data = request.json
    color1 = data.get('color1', '#FFFFFF')
    color2 = data.get('color2', '#000000')
    interval = data.get('interval', 500)
    brightness = data.get('brightness', 50)

    target_strip.restart_thread(target_strip.blink,args=(color1,color2, interval))
    return jsonify({'status': 'success'})

@app.route('/pause',methods=['POST'])
def pause():
    try:
        target_strip = get_strip(request.json['strip_name'])
    except KeyError:
        return jsonify({'error': 'No strip specified'}), 400
    thread = target_strip.get_thread()
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
    try:
        target_strip = get_strip(request.json['strip_name'])
    except KeyError:
        return jsonify({'error': 'No strip specified'}), 400
    thread = target_strip.get_thread()
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
    try:
        target_strip = get_strip(request.json['strip_name'])
    except KeyError:
        return jsonify({'error': 'No strip specified'}), 400
    thread = target_strip.get_thread()
    if thread is not None: thread.pause()
    data = request.json
    brightness = data.get('brightness', 127)
    target_strip.set_brightness(brightness)
    if thread is not None: thread.resume()
    return jsonify({'status': 'success'})

@app.route('/addstrip', methods=['POST'])
def add_strip():
    try:
        jsonschema.validate(request.json,rschema.add_strip_schema)
        strip_name = request.json["STRIP_NAME"]
        led_count = request.json["LED_COUNT"]
        led_pin = request.json["LED_PIN"]
        led_freq_hz = request.json["LED_FREQ_HZ"]
        led_dma = request.json["LED_DMA"]
        led_invert = request.json["LED_INVERT"]
        led_brightness = request.json["LED_BRIGHTNESS"]
        led_channel = request.json["LED_CHANNEL"]
        setup_strip(strip_name, led_count, led_pin, led_freq_hz, led_dma, led_invert, led_brightness, led_channel)
    except jsonschema.ValidationError as e:
        return jsonify({"error": e.message}), 400
    except ValueError as e:
        return jsonify({"error": e}), 400
    return jsonify({'status': 'success'}), 201

"""
Clear the strip when the program ends from ctrl-c or on pi shutdown
"""
def end_signal_handler(signal, frame):
    global Strips
    """Clean up resources and exit the app when `SIGHUP` is received."""
    try:
        # Clean up resources here
            for strip in Strips:
                Strips[strip].clear()
    except Exception as e:
        # Log the error
        print(f'Error while cleaning up resources: {e}')
    finally:
        # Exit the app
        exit(0)

signal.signal(signal.SIGHUP,end_signal_handler)
signal.signal(signal.SIGINT, end_signal_handler)


