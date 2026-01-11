#!/usr/bin/python3
# LED GPIO controller - chase rainbow colors across LEDs
# Fixed to use correct gpiod API

import gpiod
import time

class Pin:
    """Named GPIO pins for LEDs"""
    # LED 1 - MIDDLE
    Led1Red = 230
    Led1Green = 71
    Led1Blue = 74
    
    # LED 2 - CLOSEST TO ETH
    Led2Red = 233
    Led2Green = 72
    Led2Blue = 75
    
    # LED 3 - FARTHEST FROM ETH
    Led3Red = 69
    Led3Green = 73
    Led3Blue = 233

    @classmethod
    def all_leds(cls):
        """Return all LED pins as a list"""
        return [
            cls.Led1Red, cls.Led1Green, cls.Led1Blue,
            cls.Led2Red, cls.Led2Green, cls.Led2Blue,
            cls.Led3Red, cls.Led3Green, cls.Led3Blue,
        ]

def chase_mode(speed=30):
    """Chase rainbow colors across all LEDs"""
    chip = gpiod.Chip("/dev/gpiochip1")
    
    # Request all GPIOs
    settings = {}
    for pin in Pin.all_leds():
        settings[pin] = gpiod.LineSettings(
            direction=gpiod.line.Direction.OUTPUT,
            output_value=gpiod.line.Value.INACTIVE
        )
    
    req = gpiod.request_lines("/dev/gpiochip1", consumer="led_chase", config=settings)
    
    try:
        colors = [
            (255, 0, 0),    # Red
            (0, 255, 0),    # Green
            (0, 0, 255),    # Blue
            (255, 255, 0),  # Yellow
            (0, 255, 255),    # Cyan
            (255, 0, 255),    # Magenta
            (255, 255, 255),    # White
            (0, 0, 0),      # Off
        ]
        
        color_names = ["Red", "Green", "Blue", "Yellow", "Cyan", "Magenta", "White", "Off"]
        delay = max(0.1, 2.0 - (speed / 50.0))
        
        while True:
            for i, color in enumerate(colors):
                r_val, g_val, b_val = color
                
                # Set each LED's pins based on this color
                if i == 0:
                    req.set_value(Pin.Led1Red, gpiod.line.Value.ACTIVE if r_val > 0 else gpiod.line.Value.INACTIVE)
                    req.set_value(Pin.Led1Green, gpiod.line.Value.ACTIVE if g_val > 0 else gpiod.line.Value.INACTIVE)
                    req.set_value(Pin.Led1Blue, gpiod.line.Value.ACTIVE if b_val > 0 else gpiod.line.Value.INACTIVE)
                elif i == 1:
                    req.set_value(Pin.Led2Red, gpiod.line.Value.ACTIVE if r_val > 0 else gpiod.line.Value.INACTIVE)
                    req.set_value(Pin.Led2Green, gpiod.line.Value.ACTIVE if g_val > 0 else gpiod.line.Value.INACTIVE)
                    req.set_value(Pin.Led2Blue, gpiod.line.Value.ACTIVE if b_val > 0 else gpiod.line.Value.INACTIVE)
                elif i == 2:
                    req.set_value(Pin.Led3Red, gpiod.line.Value.ACTIVE if r_val > 0 else gpiod.line.Value.INACTIVE)
                    req.set_value(Pin.Led3Green, gpiod.line.Value.ACTIVE if g_val > 0 else gpiod.line.Value.INACTIVE)
                    req.set_value(Pin.Led3Blue, gpiod.line.Value.ACTIVE if b_val > 0 else gpiod.line.Value.INACTIVE)
                
                time.sleep(delay)
            
            # Off between colors
            for pin in Pin.all_leds():
                req.set_value(pin, gpiod.line.Value.INACTIVE)
                req.set_value(pin, gpiod.line.Value.INACTIVE)
                req.set_value(pin, gpiod.line.Value.INACTIVE)
            time.sleep(delay)
            
            print(f"Cycle {i % 7}: {color_names[i % len(color_names)]}")
    
    except KeyboardInterrupt:
        print("\nStopping...")
    
    finally:
        req.release()
        print("LEDs released")

if __name__ == "__main__":
    import sys
    
    speed = 30
    if len(sys.argv) > 1:
        speed = int(sys.argv[1])
        speed = max(0, min(100, speed))
    
    print(f"Starting rainbow chase at speed {speed}")
    chase_mode(speed)
