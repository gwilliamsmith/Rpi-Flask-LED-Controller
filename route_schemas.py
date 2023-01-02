
base_schema = {
    'type': 'object',
    'properties':{
        'target_strip' : {'type':'string'}
    },
    'required': ['target_strip']
}

brightness_schema = {
    'type': 'object',
    'properties' : {
        'brightness':{
            'type': 'number',
            'minimum': 0,
            'maximum': 255
        }
    },
    'required':['brightness']
}

fade_brightness_schema = {
    'type': 'object',
    'properties' : {
        'min_brightness':{
            'type': 'integer',
            'minimum':0,
            'maximum':255
        },
        'max_brightness':{
            'type': 'integer',
            'minimum':0,
            'maximum':255
        }
    },
    'required':['min_brightness', 'max_brightness']
}

speed_schema = {
    'type': 'object',
    'properties' : {
        'speed':{
            'type': 'number',
            'minimum':0
        }
    },
    'required':['speed']
}

color_schema = {
    "type": "object",
    "properties": {
        "color": {
            "type": "string",
            "pattern": "^#[0-9a-fA-F]{6}$"
        },
    },
    'required':['color']
}

color_array_schema = {
    'type': 'object',
    'properties':{
        'colors': {
            'type': 'array',
            'items': {
                "type": "string",
                "pattern": "^#[0-9a-fA-F]{6}$"
            },
            'minItems':2
        }
    },
    'required':['colors']
}

pattern_schema = {
    'type': 'object',
    'properties' : {
        "pattern": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "color": {
                        "type": "string",
                        "pattern": "^#[0-9a-fA-F]{6}$"
                    },
                    "start": {
                        "type": "integer",
                        "minimum": 0
                    },
                    "end": {
                        "type": "integer",
                        "minimum": 0
                    },
                    "position": {
                        "type": "integer",
                        "minimum": 0
                    }
                },
                "required": ["color"],
                "oneOf": [
                    {
                        "required": ["start", "end"]
                    },
                    {
                        "required": ["position"]
                    }
                ]
            }
        }
    },
    'required':['pattern']
}

add_strip_schema = {
    "type": "object",
    "properties": {
        "STRIP_NAME": {"type": "string"},
        "LED_COUNT": {"type": "integer"},
        'LED_PIN': {
            'type': 'integer',
            'enum': [12, 18, 40, 52, 13, 19, 41, 45, 53]},
        },
        "LED_FREQ_HZ": {"type": "integer"},
        "LED_DMA": {"type": "integer"},
        "LED_INVERT": {"type": "boolean"},
        'LED_BRIGHTNESS': {
            'type': 'integer',
            'minimum': 0,
            'maximum': 255
        },
        "if":{
            "properties":{
                "LED_PIN": {"enum":[12, 18, 40, 52]}
            }
        },
        "then":{
            "properties":{
                "LED_CHANNEL": {"enum":[0]}
            },
            "required":["LED_CHANNEL"]
        },
        "else":{
            "properties":{
                "LED_CHANNEL": {"enum":[1]}
            },
            "required":["LED_CHANNEL"]
        },
        "required": ["STRIP_NAME", "LED_COUNT", "LED_PIN", "LED_FREQ_HZ", "LED_DMA", "LED_INVERT", "LED_BRIGHTNESS", "LED_CHANNEL"]
}

color_wipe_schema = {
    'type': 'object',
    'properties' : {
        'bg_color':{
            'type': 'string',
            'pattern': '^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$'
        },
        'wipe_color':{
            'type': 'string',
            'pattern': '^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$'
        },
        'pixels':{
            'type': 'integer',
            'minimum': 1
        },
        'seamless' : {'type':'boolean'}
    },
    'required':['bg_color', 'wipe_color', 'pixels']
}

start_rainbow_schema = {
    'type': 'object',
    'properties' : {
        'color_interval':{'type': 'number'}
    },
    'required':['color_interval']
}