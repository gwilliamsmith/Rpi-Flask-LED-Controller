
add_strip_schema = {
        "type": "object",
        "properties": {
            "STRIP_NAME": {"type": "string"},
            "LED_COUNT": {"type": "integer"},
            "LED_PIN": {"type": "integer"},
            "LED_FREQ_HZ": {"type": "integer"},
            "LED_DMA": {"type": "integer"},
            "LED_INVERT": {"type": "boolean"},
            "LED_BRIGHTNESS": {"type": "integer"},
            "LED_CHANNEL": {"type": "integer"},
            "LED_STRIP": {
                "oneOf": [
                    {"type": "integer"},
                    {"type": "null"}
                ]
            }
        },
    "required": ["STRIP_NAME", "LED_COUNT", "LED_PIN", "LED_FREQ_HZ", "LED_DMA", "LED_INVERT", "LED_BRIGHTNESS", "LED_CHANNEL"]
    }