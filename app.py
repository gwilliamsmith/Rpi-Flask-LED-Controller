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

"""
Helper functions:
"""

def setup_strip(STRIP_NAME, LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_BRIGHTNESS, LED_INVERT, LED_CHANNEL):
    global Strips
    if len(Strips) >= 3:
        raise ValueError("Max number of strips reached")
    Strips[STRIP_NAME] = LEDStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_BRIGHTNESS, LED_INVERT, LED_CHANNEL)

def teardown_strip(strip_name):
    global Strips
    target_strip = Strips.pop(strip_name)
    target_strip.clear()
    target_strip.stop_thread()

def get_strip(strip_name):
    global Strips
    return Strips[strip_name]

"""
Routes:
"""
#Sets the entire LED strip to a given color
@app.route('/setcolor', methods=['POST'])
def set_color():
    try:
        #Validate the request payload
        data = request.json
        jsonschema.validate(data,rschema.base_schema)
        jsonschema.validate(data,rschema.color_schema)
        jsonschema.validate(data,rschema.brightness_schema)
        target_strip = get_strip(data['target_strip'])
    #Return an error if validation fails
    except jsonschema.ValidationError as e:
        return jsonify({"error": e.message}), 400
    #Return an error if the strip doesn't exist
    except KeyError:
        return jsonify({'error': ('Strip ' + data['target_strip'] + " doesn't exist!")  }), 400
    
    #Stop any animation that's running on the strip
    target_strip.stop_thread()
    
    #Get the color from the payload
    color = data['color']

    #Set the LEDStrip pixels to the given color
    target_strip.set_all_pixels(color)

    # Send a response to the client
    return jsonify({'status': 'success'}), 201

#Sets the LED strip to a given pattern
@app.route('/setpattern', methods=['POST'])
def set_pattern():
    try:
        #Validate the request payload
        data = request.json
        jsonschema.validate(data,rschema.base_schema)
        jsonschema.validate(data,rschema.pattern_schema)
        jsonschema.validate(data,rschema.brightness_schema)
        target_strip = get_strip(data['target_strip'])
    #Return an error if validation fails
    except jsonschema.ValidationError as e:
        return jsonify({"error": e.message}), 400
    #Return an error if the strip doesn't exist
    except KeyError:
        return jsonify({'error': ('Strip ' + data['target_strip'] + " doesn't exist!")  }), 400
    
    #Stop any animation that's running on the strip
    target_strip.stop_thread()

    # Read from the request payload
    pattern = data['pattern']
    brightness = data['brightness']

    #Update LED strip brightness
    target_strip.set_brightness(brightness)

    #Set the LED strip to the given pattern
    target_strip.set_pattern(pattern)

    # Send a response to the client
    return jsonify({'status': 'success'}), 201

#Sets the LED strip to wheel through the rainbow
@app.route('/startrainbow', methods=['POST'])
def start_rainbow():
    try:
        #Validate the request payload
        data = request.json
        jsonschema.validate(data,rschema.base_schema)
        jsonschema.validate(data,rschema.start_rainbow_schema)
        jsonschema.validate(data,rschema.speed_schema)
        jsonschema.validate(data,rschema.brightness_schema)
        target_strip = get_strip(data['target_strip'])
    #Return an error if validation fails
    except jsonschema.ValidationError as e:
        return jsonify({"error": e.message}), 400
    #Return an error if the strip doesn't exist
    except KeyError:
        return jsonify({'error': ('Strip ' + data['target_strip'] + " doesn't exist!")  }), 400
    
    #Read from the request payload
    color_interval = data['color_interval']
    speed = data['speed']

    # Start the rainbow cycle in a new thread
    target_strip.restart_thread(target_strip.cycle_rainbow, args=(color_interval,speed))

    # Send a response to the client
    return jsonify({'status': 'success'}), 201

#Clear the LED strip and turn all LEDs off
@app.route('/clear', methods=['POST'])
def clear():
    try:
        #Validate the request payload
        data = request.json
        jsonschema.validate(data,rschema.base_schema)
        target_strip = get_strip(data['target_strip'])
    #Return an error if validation fails
    except jsonschema.ValidationError as e:
        return jsonify({"error": e.message}), 400
    #Return an error if the strip doesn't exist
    except KeyError:
        return jsonify({'error': ('Strip ' + data['target_strip'] + " doesn't exist!")  }), 400

    #Stop any animations running on the strip
    target_strip.stop_thread()

    #Clear the LED strip
    target_strip.clear()

    # Send a response to the client
    return jsonify({'status': 'success'}), 201

#Sends a color across the LED strip
@app.route('/colorwipe', methods=['POST'])
def color_wipe():
    try:
        #Validate the request payload
        data = request.json
        jsonschema.validate(data,rschema.base_schema)
        jsonschema.validate(data,rschema.color_wipe_schema)
        jsonschema.validate(data,rschema.speed_schema)
        jsonschema.validate(data,rschema.brightness_schema)
        target_strip = get_strip(data['target_strip'])
    #Return an error if validation fails
    except jsonschema.ValidationError as e:
        return jsonify({"error": e.message}), 400
    #Return an error if the strip doesn't exist
    except KeyError:
        return jsonify({'error': ('Strip ' + data['target_strip'] + " doesn't exist!")  }), 400

    #Read from request payload
    bg_color = data['bg_color']
    wipe_color = data['wipe_color']
    pixels = data['pixels']
    speed = data['speed']
    seamless = data['seamless']
    brightness = data['brightness']

    #Update LED strip brightness
    target_strip.set_brightness(brightness)

    #Start the color wipe in a new thread
    target_strip.restart_thread(target_strip.color_wipe, args=(bg_color, wipe_color, pixels, speed, seamless))

    #Send a response to the client
    return jsonify({'status': 'success'}), 201

#Fades a color in and out on the whole strip
@app.route('/fadecolor', methods=['POST'])
def fade_color():
    try:
        #Validate the request payload
        data = request.json
        jsonschema.validate(data,rschema.base_schema)
        jsonschema.validate(data,rschema.color_schema)
        jsonschema.validate(data,rschema.fade_brightness_schema)
        jsonschema.validate(data,rschema.speed_schema)
        target_strip = get_strip(data['target_strip'])
    #Return an error if validation fails
    except jsonschema.ValidationError as e:
        return jsonify({"error": e.message}), 400
    #Return an error if the strip doesn't exist
    except KeyError:
        return jsonify({'error': ('Strip ' + data['target_strip'] + " doesn't exist!")  }), 400

    #Read the request payload
    color = data['color']
    min_brightness = data['min_brightness']
    max_brightness = data['max_brightness']
    speed = data['speed']

    #Start the fade animation in a new thread
    target_strip.restart_thread(target_strip.fade,args=(color,min_brightness,max_brightness,speed))

    #Send a response to the client
    return jsonify({'status': 'success'}), 201

#Fades a pattern of colors in and out
@app.route('/fadepattern',methods=['POST'])
def fade_pattern():
    try:
        #Validate the request payload
        data = request.json
        jsonschema.validate(data,rschema.base_schema)
        jsonschema.validate(data,rschema.pattern_schema)
        jsonschema.validate(data,rschema.fade_brightness_schema)
        jsonschema.validate(data,rschema.speed_schema)
        target_strip = get_strip(data['target_strip'])
    #Return an error if validation fails
    except jsonschema.ValidationError as e:
        return jsonify({"error": e.message}), 400
    #Return an error if the strip doesn't exist
    except KeyError:
        return jsonify({'error': ('Strip ' + data['target_strip'] + " doesn't exist!")  }), 400

    #Read the request payload
    pattern = data['pattern']
    min_brightness = data['min_brightness']
    max_brightness = data['max_brightness']
    speed = data['speed']

    #Start the fade animation in a new thread
    target_strip.restart_thread(target_strip.fadePattern, args=(pattern,min_brightness,max_brightness,speed))
    
    #Send a response to the client
    return jsonify({'status': 'success'}), 201

@app.route('/blink',methods=['POST'])
def blink():
    try:
        target_strip = get_strip(request.json['target_strip'])
    except KeyError:
        return jsonify({'error': 'No strip specified'}), 400
    data = request.json
    color1 = data.get('color1', '#FFFFFF')
    color2 = data.get('color2', '#000000')
    speed = data.get('speed', 500)
    brightness = data.get('brightness', 50)

    target_strip.restart_thread(target_strip.blink,args=(color1,color2, speed))
    return jsonify({'status': 'success'})

@app.route('/pause',methods=['POST'])
def pause():
    try:
        target_strip = get_strip(request.json['target_strip'])
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
        target_strip = get_strip(request.json['target_strip'])
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
        target_strip = get_strip(request.json['target_strip'])
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

@app.route('/removestrip',methods=['POST'])
def remove_strip():
    try:
        jsonschema.validate(request.json,rschema.base_schema)
        strip_name = request.json["target_strip"]
        teardown_strip(strip_name)
    except jsonschema.ValidationError as e:
        return jsonify({"error": e.message}), 400
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


