from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
from LightThread import LightThread
from LEDStrip import LEDStrip
import signal
import jsonschema
import route_schemas as rschema
import json
import requests

app = Flask(__name__)
CORS(app)

PORT_NUM = 5000

Strips = {}

"""
Helper functions:
"""

def setup_strip(STRIP_NAME, LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_BRIGHTNESS, LED_INVERT, LED_CHANNEL):
    global Strips
    if len(Strips) >= 3:
        raise ValueError
    if STRIP_NAME in Strips:
        raise KeyError
    for strip in Strips:
        if LED_PIN == Strips[strip].pin:
            raise IndexError
    print("\t" + STRIP_NAME + " added on pin " + str(LED_PIN))
    Strips[STRIP_NAME] = LEDStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_BRIGHTNESS, LED_INVERT, LED_CHANNEL)

def teardown_strip(target_strip_name):
    global Strips
    if target_strip_name not in Strips:
        raise KeyError
    target_strip = Strips.pop(target_strip_name)
    target_strip.clear()
    target_strip.stop_thread()
    print("\t " + target_strip_name + " removed")

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
    
    #Get data from the payload
    color = data['color']
    brightness = data['brightness']

    #Set the LEDStrip pixels to the given color
    target_strip.set_all_pixels(color)

    #Update LED strip brightness
    target_strip.set_brightness(brightness)

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

    #Set the LED strip to the given pattern
    target_strip.set_pattern(pattern)

    #Update LED strip brightness
    target_strip.set_brightness(brightness)

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
    brightness = data['brightness']

    # Start the rainbow cycle in a new thread
    target_strip.restart_thread(target_strip.cycle_rainbow, args=(color_interval,speed))

    #Update LED strip brightness
    target_strip.set_brightness(brightness)

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

    #Start the color wipe in a new thread
    target_strip.restart_thread(target_strip.color_wipe, args=(bg_color, wipe_color, pixels, speed, seamless))

    #Update LED strip brightness
    target_strip.set_brightness(brightness)

    #Send a response to the client
    return jsonify({'status': 'success'}), 201

@app.route('/clusterrun', methods=['POST'])
def cluster_run():
    print("payload:")
    print(request)
    try:
        #Validate the request payload
        data = request.json
        jsonschema.validate(data,rschema.base_schema)
        jsonschema.validate(data,rschema.cluster_run_schema)
        jsonschema.validate(data,rschema.brightness_schema)
        jsonschema.validate(data,rschema.speed_schema)
        target_strip = get_strip(data['target_strip'])
    #Return an error if validation fails
    except jsonschema.ValidationError as e:
        return jsonify({"error": e.message}), 400
    #Return an error if the strip doesn't exist
    except KeyError:
        return jsonify({'error': ('Strip ' + data['target_strip'] + " doesn't exist!")  }), 400

    print("Data load")

    #Read from request payload
    bg_color = data['bg_color']
    cluster_color = data['cluster_color']
    cluster_spacing = data['cluster_spacing']
    cluster_size = data['cluster_size']
    brightness = data['brightness']
    speed = data['speed']

    print("Pre-run")
    target_strip.restart_thread(target_strip.cluster_run, args=(bg_color,cluster_color,cluster_size,cluster_spacing,speed))
    print("Post-run")
    target_strip.set_brightness(brightness)

    return jsonify({'status' : 'success'}),201

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

#Blink the LED strip between a given array of colors
@app.route('/blink',methods=['POST'])
def blink():
    try:
        #Validate the request payload
        data = request.json
        jsonschema.validate(data,rschema.base_schema)
        jsonschema.validate(data,rschema.color_array_schema)
        jsonschema.validate(data,rschema.speed_schema)
        jsonschema.validate(data,rschema.brightness_schema)
        target_strip = get_strip(data['target_strip'])
    #Return an error if validation fails
    except jsonschema.ValidationError as e:
        return jsonify({"error": e.message}), 400
    #Return an error if the strip doesn't exist
    except KeyError:
        return jsonify({'error': ('Strip ' + data['target_strip'] + " doesn't exist!")  }), 400

    #Read the request payload
    colors = data['colors']
    speed = data['speed']
    brightness = data['brightness']

    #Start the blink animation
    target_strip.restart_thread(target_strip.blink,args=(colors, speed))

    #Set the brightness of the LED strip
    target_strip.set_brightness(brightness)

    #Send a response to the client
    return jsonify({'status': 'success'}), 201

#Pause a running animation.
@app.route('/pause',methods=['POST'])
def pause():
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

    #Get the target strip's thread
    thread = target_strip.get_thread()

    #Check to see if the thread is actually running something
    if thread is not None:
        if not thread.paused():
            thread.pause()
            return jsonify({'status': 'success'}), 201
        else:
            return jsonify({'error': 'Animation is already paused'}), 400
    else:
        return jsonify({'error': 'No animation found'}), 400

#Resume a paused animation
@app.route('/resume',methods=['POST'])
def resume():
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

    #Get the target strip's thread
    thread = target_strip.get_thread()

    #Check to see if the thread is actually running something
    if thread is not None:
        if thread.paused():
            thread.resume()
            return jsonify({'status': 'success'}), 201
        else:
            return jsonify({'error': 'Animation is not paused'}), 400
    else:
        return jsonify({'error': 'No animation found'}), 400

#Set the brightness of the LED strip. Not really effective on fade animations
@app.route('/setbrightness', methods=['POST'])
def set_brightness():
    try:
        #Validate the request payload
        data = request.json
        jsonschema.validate(data,rschema.base_schema)
        jsonschema.validate(data,rschema.brightness_schema)
        target_strip = get_strip(data['target_strip'])
    #Return an error if validation fails
    except jsonschema.ValidationError as e:
        return jsonify({"error": e.message}), 400
    #Return an error if the strip doesn't exist
    except KeyError:
        return jsonify({'error': ('Strip ' + data['target_strip'] + " doesn't exist!")  }), 400
        
    #Get the target strip's thread
    thread = target_strip.get_thread()
    
    #Read the request payload
    brightness = data['brightness']

    #Set the strip brightness
    target_strip.set_brightness(brightness)

    #Send a response to the client
    return jsonify({'status': 'success'}), 201

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
    except ValueError:
        return jsonify({"error": "You cannot add more three LED strips!"}), 400
    except KeyError:
        return jsonify({"error": "An LED strip with that name already exists!"}), 400
    except IndexError:
        return jsonify({"error":"An LED strip is already using that pin!"}), 400
    return jsonify({'status': 'success'}), 201

@app.route('/removestrip',methods=['POST'])
def remove_strip():
    try:
        jsonschema.validate(request.json,rschema.base_schema)
        target_strip = request.json["target_strip"]
        teardown_strip(target_strip)
    except jsonschema.ValidationError as e:
        return jsonify({"error": e.message}), 400
    except KeyError:
        return jsonify({"error": "That strip doesn't exist!"}), 400
    return jsonify({'status': 'success'}), 201

"""
Clear the strip when the program ends from ctrl-c or on pi shutdown
"""
def end_signal_handler(signal, frame):
    global Strips
    try:
        # Clean up resources here
        for strip in list(Strips):
            print("\tRemoving " + strip)
            teardown_strip(strip)
    except Exception as e:
        # Log the error
        print(f'Error while cleaning up resources: {e}')
    finally:
        # Exit the app
        exit(0)

signal.signal(signal.SIGHUP,end_signal_handler)
signal.signal(signal.SIGINT, end_signal_handler)

"""
Load initial strip congfiguration from init.json
"""
def __load_strips():
    with open('init.json', 'r') as f:
        init_strips =  json.load(f)
    try:
        for strip in init_strips['strips']:
            strip_name = strip["STRIP_NAME"]
            led_count = strip["LED_COUNT"]
            led_pin = strip["LED_PIN"]
            led_freq_hz = strip["LED_FREQ_HZ"]
            led_dma = strip["LED_DMA"]
            led_invert = strip["LED_INVERT"]
            led_brightness = strip["LED_BRIGHTNESS"]
            led_channel = strip["LED_CHANNEL"]
            print("\tLoading " + strip_name + " on pin " + str(led_pin) + "...")
            setup_strip(strip_name, led_count, led_pin, led_freq_hz, led_dma, led_invert, led_brightness, led_channel)
    except jsonschema.ValidationError as e:
        print("\n" + e.message)
        print("Please update init.json to resolve this error.")
        return
    except ValueError:
        print("\nYou cannot add more three LED strips!")
        print("Please update init.json to resolve this error.")
        return
    except KeyError:
        print("\nAn LED strip with that name already exists!")
        print("Please update init.json to resolve this error.")
        return
    except IndexError:
        print("\nAn LED strip is already using that pin!")
        print("Please update init.json to resolve this error.")
        return

__load_strips()

