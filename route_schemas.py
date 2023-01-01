
baseSchema = {
    'type': 'object',
    'properties':{
        'target_strip' : {'type':'string'}
    },
    'required': ['target_strip']
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
            'type': 'number',
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