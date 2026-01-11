#!/usr/bin/env python3
# LED CONTROL PROGRAM
# This program lets you control colorful LED lights!
# You can make them glow, blink, fade, and show rainbows!

# First, we need to import special tools to help us talk to the lights
import gpiod        # Tool to control the GPIO pins (the wires that connect to LEDs)
import time         # Tool to pause and wait (like counting seconds)
import threading    # Tool to do many things at once (like patting your head and rubbing your tummy)
import sys          # Tool to read commands you type in
import atexit       # Tool to remember to turn lights off when we're done
import math         # Tool for doing math calculations
import json         # Tool for saving and loading information from files
import os           # Tool for working with files and folders on the computer

# This is where we save the information about which LEDs are connected
CONFIG_FILE = "/etc/led_config.json"

# These numbers control how fast the lights blink
# FREQ means "frequency" - how many times we blink per second (500 times!)
# PERIOD is how long one blink takes (1 divided by 500 = very fast!)
FREQ = 500
PERIOD = 1.0 / FREQ

# This is our color dictionary!
# A dictionary is like a special book where we can look up colors
# Each color name has 3 numbers that tell the computer how to mix red, green, and blue
# The numbers go from 0 (none) to 255 (super bright)
COLORS = {
    "red": (255, 0, 0),        # All red, no green or blue
    "green": (0, 255, 0),      # All green
    "blue": (0, 0, 255),       # All blue
    "white": (255, 255, 255),  # Mix all colors together = white!
    "black": (0, 0, 0),        # All zeros = off! (like when you're sleeping)
    "yellow": (255, 255, 0),   # Mix red and green = yellow (like mixing paint!)
    "cyan": (0, 255, 255),     # Mix green and blue = cyan (like ocean water)
    "magenta": (255, 0, 255),  # Mix red and blue = magenta (like pink)
    "orange": (255, 165, 0),   # Mostly red, some green = orange (like a carrot!)
    "purple": (128, 0, 128),   # Half red, half blue = purple (like grapes)
    "pink": (255, 192, 203),   # Light red = pink (like cotton candy)
    "lime": (0, 255, 0),       # Bright green = lime (like the fruit)
    "maroon": (128, 0, 0),     # Dark red = maroon (like a dark cherry)
    "navy": (0, 0, 128),       # Dark blue = navy (like the ocean at night)
    "olive": (128, 128, 0),    # Mix red and green = olive (like an olive)
    "teal": (0, 128, 128),     # Mix green and blue = teal (like a duck!)
    "aqua": (0, 255, 255),     # Mix green and blue = aqua (like tropical water)
    "silver": (192, 192, 192), # Gray-white = silver (like a coin)
    "gray": (128, 128, 128),   # Equal mix of all colors = gray (like a cloudy day)
    "gold": (255, 215, 0),     # Yellow-orange = gold (like treasure!)
    "indigo": (75, 0, 130),    # Deep purple-blue = indigo (like a crayon)
    "violet": (238, 130, 238), # Purple-pink = violet (like a flower)
    "brown": (165, 42, 42),    # Dark red = brown (like chocolate!)
    "chartreuse": (127, 255, 0), # Mix yellow and green = chartreuse (like a lime)
    "crimson": (220, 20, 60),  # Bright red = crimson (like a rose)
    "darkblue": (0, 0, 139),   # Dark blue (like midnight)
    "darkgreen": (0, 100, 0),  # Dark green (like a forest)
    "darkred": (139, 0, 0),    # Dark red (like blood)
    "lavender": (230, 230, 250), # Light purple (like a flower)
    "turquoise": (64, 224, 208), # Blue-green (like a gemstone)
}

# This lock is like having only one bathroom - it prevents confusion
# When one part of the program is changing colors, the lock makes sure
# nobody else tries to change them at the same exact time!
lock = threading.Lock()

# This remembers what brightness each LED color should be right now
# We use 'r' for red, 'g' for green, and 'b' for blue
# The numbers are from 0 to 100 (like a percentage - 100% is super bright!)
current_duty = {}

# This stores information about each LED we have connected
# Like which pins on the computer each LED is plugged into
led_configs = []

# This is like a stop sign - when it's True, we keep running
# When it's False, we stop everything and turn off the lights
running = True

# =============================================
# FUNCTIONS (these are like recipes we can use)
# =============================================

# Load the LED information from our saved file
def load_config():
    global led_configs  # We can change the led_configs variable inside this function
    
    # Check if our configuration file exists
    if os.path.exists(CONFIG_FILE):
        try:
            # Open the file and read what's inside
            with open(CONFIG_FILE, 'r') as f:
                # Load the JSON data (JSON is a computer-friendly format)
                data = json.load(f)
                # Get the list of LEDs from the data
                led_configs = data.get('leds', [])
                # If we found some LEDs, return True (success!)
                if led_configs:
                    return True
        except:
            # If something goes wrong, just keep going
            pass
    # Return False (no configuration found)
    return False

# Save the LED information to our file so we remember it next time
def save_config():
    # Put our LED information in a dictionary
    data = {'leds': led_configs}
    # Open the file and write the data to it
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f, indent=2)  # indent=2 makes it pretty and readable!

# Ask the user which LEDs they have and save the information
def setup_leds():
    global led_configs, current_duty  # We can change these variables
    
    # Try to load the configuration from the file
    if not load_config():
        # If no configuration file exists, let's ask the user!
        print("LED configuration not found. Setting up...")
        
        # Ask how many LEDs they have (must be 1, 2, or 3)
        num_leds = int(input("How many LEDs (1-3)? "))
        # Make sure it's between 1 and 3
        num_leds = max(1, min(3, num_leds))
        
        # For each LED, ask for its information
        for i in range(num_leds):
            print(f"\nLED {i + 1} configuration:")
            
            # Ask which GPIO chip the LED is connected to
            # GPIO chip is like the place where all the wires plug in
            chip = input(f"  GPIO chip path [default: /dev/gpiochip1]: ").strip() or "/dev/gpiochip1"
            
            # Ask for the pin numbers for each color
            # Pins are like individual sockets on the chip
            red_pin = int(input(f"  Red pin number: "))
            green_pin = int(input(f"  Green pin number: "))
            blue_pin = int(input(f"  Blue pin number: "))
            
            # Save all this information for this LED
            led_configs.append({
                'id': i + 1,        # Give the LED an ID number (1, 2, or 3)
                'chip': chip,       # Which chip it's connected to
                'red': red_pin,     # Which pin is for red
                'green': green_pin, # Which pin is for green
                'blue': blue_pin    # Which pin is for blue
            })
        
        # Save all this information to the file
        save_config()
    
    # For each LED we have, set up its initial brightness (all off)
    for led in led_configs:
        current_duty[led['id']] = {'r': 0, 'g': 0, 'b': 0}
    
    # Tell the user what we configured
    print(f"\nConfigured {len(led_configs)} LED(s)")
    for led in led_configs:
        print(f"  LED {led['id']}: {led['chip']} (R:{led['red']} G:{led['green']} B:{led['blue']})")

# Convert a hue (color wheel position) to RGB colors
# Hue is a number from 0 to 360 that goes around the color wheel
# This is like turning a dial to pick a color!
def hue_to_rgb(hue):
    # Divide by 60 because there are 6 main colors in a rainbow
    h = hue / 60
    
    # This is a fancy math trick to figure out how much of each color to mix
    # The abs means "absolute value" which means always positive
    x = 255 * (1 - abs((h % 2) - 1))
    
    # Now we figure out which section of the color wheel we're on
    # and return the right mix of red, green, and blue
    if 0 <= h < 1:
        return (255, int(x), 0)      # Red to Yellow
    elif 1 <= h < 2:
        return (int(x), 255, 0)      # Yellow to Green
    elif 2 <= h < 3:
        return (0, 255, int(x))      # Green to Cyan
    elif 3 <= h < 4:
        return (0, int(x), 255)      # Cyan to Blue
    elif 4 <= h < 5:
        return (int(x), 0, 255)      # Blue to Magenta
    else:
        return (255, 0, int(x))      # Magenta to Red

# This function controls one color of one LED
# It runs in its own "thread" which means it runs independently
# while the rest of the program does other things
def pwm_thread(led_config, color_key):
    # Get the LED ID and chip information
    led_id = led_config['id']
    chip = led_config['chip']
    
    # Figure out which pin this thread is controlling
    if color_key == 'r':
        line = led_config['red']     # Red pin
    elif color_key == 'g':
        line = led_config['green']   # Green pin
    else:
        line = led_config['blue']    # Blue pin
    
    # This loop runs forever (until we tell it to stop)
    while running:
        # Get the current brightness for this color
        # We use the lock to make sure nobody else changes it while we're reading it
        with lock:
            duty = current_duty[led_id][color_key]
        
        # If brightness is 0 or less, turn the light off completely
        if duty <= 0:
            # Set up the pin as an output (we control it)
            config = {
                line: gpiod.LineSettings(
                    direction=gpiod.line.Direction.OUTPUT
                )
            }
            # Turn the pin off
            with gpiod.request_lines(chip, consumer="rgb", config=config) as req:
                req.set_value(line, gpiod.line.Value.INACTIVE)
                # Wait a tiny bit (one PERIOD of time)
                time.sleep(PERIOD)
            continue  # Go back to the start of the loop
        
        # If brightness is 100 or more, turn the light on completely
        if duty >= 100:
            # Set up the pin as an output
            config = {
                line: gpiod.LineSettings(
                    direction=gpiod.line.Direction.OUTPUT
                )
            }
            # Turn the pin on
            with gpiod.request_lines(chip, consumer="rgb", config=config) as req:
                req.set_value(line, gpiod.line.Value.ACTIVE)
                # Wait a tiny bit
                time.sleep(PERIOD)
            continue  # Go back to the start of the loop
        
        # If brightness is between 0 and 100, we need to blink it really fast!
        # This is called "PWM" (Pulse Width Modulation)
        # It's like blinking so fast your eye can't see it blinking - 
        # it just looks dimmer because it's off part of the time
        ton = PERIOD * (duty / 100.0)   # How long to keep it ON
        toff = PERIOD - ton              # How long to keep it OFF
        
        # Set up the pin as an output
        config = {
            line: gpiod.LineSettings(
                direction=gpiod.line.Direction.OUTPUT
            )
        }
        # Turn it on for the "on" time
        with gpiod.request_lines(chip, consumer="rgb", config=config) as req:
            req.set_value(line, gpiod.line.Value.ACTIVE)
            time.sleep(ton)
            # Turn it off for the "off" time
            req.set_value(line, gpiod.line.Value.INACTIVE)
            time.sleep(toff)

# Set all LEDs to the same color
def set_rgb(r, g, b, brightness=100):
    # Use the lock so nobody changes colors while we're setting them
    with lock:
        # For each LED we have, set its colors
        for led_id in current_duty:
            # Convert the 0-255 color values to 0-100 brightness percentages
            # The division and multiplication makes the numbers the right size
            current_duty[led_id]['r'] = (r / 255) * brightness
            current_duty[led_id]['g'] = (g / 255) * brightness
            current_duty[led_id]['b'] = (b / 255) * brightness

# Turn all the LEDs off
def turn_off():
    global running  # We can change the running variable
    running = False  # Tell all the threads to stop
    
    # Use the lock to set all brightnesses to 0 (off)
    with lock:
        for led_id in current_duty:
            current_duty[led_id]['r'] = 0
            current_duty[led_id]['g'] = 0
            current_duty[led_id]['b'] = 0

# Rainbow cycle: slowly go through all the colors of the rainbow
def rainbow_cycle(speed, duration=None):
    hue = 0  # Start at the beginning of the color wheel
    
    # Calculate how fast to go (speed 0-100, higher is faster)
    # max means "at least this value"
    step_delay = max(0.01, 1.0 - (speed / 100.0))
    start_time = time.time()  # Remember when we started
    
    # Loop forever (or until we're told to stop)
    while running:
        # Get the color for this position on the wheel
        r, g, b = hue_to_rgb(hue)
        # Set the LEDs to this color
        set_rgb(r, g, b)
        # Move to the next color on the wheel
        hue = (hue + 1) % 360  # % 360 means wrap around to 0 when we reach 360
        # Wait a tiny bit
        time.sleep(step_delay)
        
        # If we have a duration, check if we've run long enough
        if duration and (time.time() - start_time) >= duration:
            break  # Stop the loop

# Rainbow fade: slowly get brighter and dimmer while changing colors
def rainbow_fade(speed, duration=None):
    hue = 0
    # Calculate how fast to go
    step_delay = max(0.02, 2.0 - (speed / 50.0))
    start_time = time.time()
    
    # Loop forever
    while running:
        # First, slowly get brighter from 0% to 100%
        for brightness in range(0, 101, 5):  # Go up by 5% each time
            if not running:
                return  # Stop if we're told to
            r, g, b = hue_to_rgb(hue)
            set_rgb(r, g, b, brightness)  # Set color at this brightness
            time.sleep(step_delay / 10)    # Wait a tiny bit
        
        # Change to the next color
        hue = (hue + 30) % 360
        
        # Now, slowly get dimmer from 100% back to 0%
        for brightness in range(100, -1, -5):  # Go down by 5% each time
            if not running:
                return  # Stop if we're told to
            r, g, b = hue_to_rgb(hue)
            set_rgb(r, g, b, brightness)  # Set color at this brightness
            time.sleep(step_delay / 10)    # Wait a tiny bit
        
        # Check if we've run long enough
        if duration and (time.time() - start_time) >= duration:
            break  # Stop the loop

# Rainbow pulse: blink between bright and dim
def rainbow_pulse(speed, duration=None):
    hue = 0
    # Calculate how fast to go
    step_delay = max(0.05, 3.0 - (speed / 33.0))
    start_time = time.time()
    
    # Loop forever
    while running:
        # Get the color and show it at full brightness (100%)
        r, g, b = hue_to_rgb(hue)
        set_rgb(r, g, b, 100)
        time.sleep(step_delay)
        
        # Now show it at dim brightness (20%)
        set_rgb(r, g, b, 20)
        time.sleep(step_delay / 2)
        
        # Change to the next color
        hue = (hue + 15) % 360
        
        # Check if we've run long enough
        if duration and (time.time() - start_time) >= duration:
            break  # Stop the loop

# Rainbow blink: flash the light on and off
def rainbow_blink(speed, duration=None):
    hue = 0
    # Calculate how fast to go
    step_delay = max(0.1, 2.0 - (speed / 50.0))
    start_time = time.time()
    
    # Loop forever
    while running:
        # Show the color
        r, g, b = hue_to_rgb(hue)
        set_rgb(r, g, b)
        time.sleep(step_delay)
        
        # Turn it off completely (black)
        set_rgb(0, 0, 0)
        time.sleep(step_delay)
        
        # Change to the next color
        hue = (hue + 20) % 360
        
        # Check if we've run long enough
        if duration and (time.time() - start_time) >= duration:
            break  # Stop the loop

# Rainbow strobe: flash really fast (like a disco light!)
def rainbow_strobe(speed, duration=None):
    hue = 0
    # Calculate how fast to go (strobe is super fast!)
    step_delay = max(0.01, 0.2 - (speed / 500.0))
    start_time = time.time()
    
    # Loop forever
    while running:
        # Show the color
        r, g, b = hue_to_rgb(hue)
        set_rgb(r, g, b)
        time.sleep(step_delay)
        
        # Turn it off
        set_rgb(0, 0, 0)
        time.sleep(step_delay)
        
        # Change to the next color
        hue = (hue + 10) % 360
        
        # Check if we've run long enough
        if duration and (time.time() - start_time) >= duration:
            break  # Stop the loop

# Pulse mode: make a single color slowly get brighter and dimmer
def pulse_mode(color, speed, duration=None):
    # Get the RGB values for this color
    if color in COLORS:
        base_r, base_g, base_b = COLORS[color]
    else:
        base_r, base_g, base_b = color
    
    # Calculate how fast to go
    step_delay = max(0.05, 2.0 - (speed / 50.0))
    start_time = time.time()
    
    # Loop forever
    while running:
        # Slowly get brighter
        for brightness in range(0, 101, 5):
            if not running:
                return  # Stop if we're told to
            set_rgb(base_r, base_g, base_b, brightness)
            time.sleep(step_delay / 10)
        
        # Slowly get dimmer
        for brightness in range(100, -1, -5):
            if not running:
                return  # Stop if we're told to
            set_rgb(base_r, base_g, base_b, brightness)
            time.sleep(step_delay / 10)
        
        # Check if we've run long enough
        if duration and (time.time() - start_time) >= duration:
            break  # Stop the loop

# Blink mode: flash a single color on and off
def blink_mode(color, speed, duration=None):
    # Get the RGB values for this color
    if color in COLORS:
        r, g, b = COLORS[color]
    else:
        r, g, b = color
    
    # Calculate how fast to go
    step_delay = max(0.1, 2.0 - (speed / 50.0))
    start_time = time.time()
    
    # Loop forever
    while running:
        # Show the color
        set_rgb(r, g, b)
        time.sleep(step_delay)
        
        # Turn it off
        set_rgb(0, 0, 0)
        time.sleep(step_delay)
        
        # Check if we've run long enough
        if duration and (time.time() - start_time) >= duration:
            break  # Stop the loop

# Strobe mode: flash a single color really fast
def strobe_mode(color, speed, duration=None):
    # Get the RGB values for this color
    if color in COLORS:
        r, g, b = COLORS[color]
    else:
        r, g, b = color
    
    # Calculate how fast to go (strobe is super fast!)
    step_delay = max(0.01, 0.2 - (speed / 500.0))
    start_time = time.time()
    
    # Loop forever
    while running:
        # Show the color
        set_rgb(r, g, b)
        time.sleep(step_delay)
        
        # Turn it off
        set_rgb(0, 0, 0)
        time.sleep(step_delay)
        
        # Check if we've run long enough
        if duration and (time.time() - start_time) >= duration:
            break  # Stop the loop

# Parse the command line arguments (what the user typed)
# This looks for special flags like "-t" which means "time"
def parse_args():
    args = []  # This will hold the regular arguments
    duration = None  # This will hold the duration if we find "-t"
    
    # Go through each argument the user typed
    i = 1  # Start at 1 because 0 is the program name
    while i < len(sys.argv):
        # If we see "-t", the next thing is the duration
        if sys.argv[i] == '-t' and i + 1 < len(sys.argv):
            duration = float(sys.argv[i + 1])
            i += 2  # Skip both "-t" and the number
        else:
            # Otherwise, it's a regular argument
            args.append(sys.argv[i])
            i += 1  # Move to the next argument
    
    # Return both the regular arguments and the duration
    return args, duration

# =============================================
# MAIN PROGRAM (this is where everything starts)
# =============================================

def main():
    # Make sure to turn off the lights when the program ends
    # This is like setting an alarm clock to remind us to clean up!
    atexit.register(turn_off)
    
    global running  # We can change the running variable
    
    # Set up the LEDs (ask the user if needed, or load from file)
    setup_leds()
    
    # Create threads for each color of each LED
    # A thread is like having a little helper that does its own job
    threads = []
    for led in led_configs:
        for color in ['r', 'g', 'b']:
            # Each thread will run the pwm_thread function
            threads.append(threading.Thread(target=pwm_thread, args=(led, color), daemon=True))
    
    # Start all the threads running
    for t in threads:
        t.start()
    
    # Parse the command line arguments to see what the user wants
    args, duration = parse_args()
    
    try:
        # If the user didn't give any arguments, show them how to use the program
        if len(args) < 1:
            print("Usage:")
            print("  Static color:")
            print("    led.py <color_name> [brightness] [-t duration_seconds]")
            print("    led.py <R> <G> <B> [brightness] [-t duration_seconds]")
            print()
            print("  Rainbow effects:")
            print("    led.py rainbow <mode> <speed> [-t duration_seconds]")
            print("    Modes: cycle, fade, pulse, blink, strobe")
            print("    Speed: 0-100 (higher is faster)")
            print()
            print("  Single color effects:")
            print("    led.py <color_name> <mode> <speed> [-t duration_seconds]")
            print("    Modes: pulse, blink, strobe")
            print()
            print("  Configuration:")
            print("    led.py --configure      Reconfigure LEDs")
            print()
            print("Examples:")
            print("  led.py red")
            print("  led.py red 50")
            print("  led.py red 50 -t 5")
            print("  led.py 255 248 3 35")
            print("  led.py rainbow cycle 100")
            print("  led.py rainbow fade 75")
            print("  led.py rainbow fade 25 -t 25")
            print("  led.py rainbow pulse 50 -t 10")
            print("  led.py red blink 80")
            print("  led.py red pulse 60 -t 30")
            sys.exit(1)  # Exit the program

        # If the user wants to reconfigure the LEDs
        if args[0] == "--configure":
            # Delete the old config file if it exists
            os.remove(CONFIG_FILE) if os.path.exists(CONFIG_FILE) else None
            # Clear our memory of the old config
            led_configs.clear()
            current_duty.clear()
            # Ask the user for the new config
            setup_leds()
            return  # We're done!

        # If the user wants a rainbow effect
        if args[0].lower() == "rainbow":
            # Make sure they gave us enough information
            if len(args) < 3:
                print("Rainbow usage: led.py rainbow <mode> <speed> [-t duration]")
                print("Modes: cycle, fade, pulse, blink, strobe")
                sys.exit(1)
            
            # Get the mode and speed
            mode = args[1].lower()
            speed = int(args[2])
            # Make sure speed is between 0 and 100
            speed = max(0, min(100, speed))
            
            # Tell the user what we're doing
            print(f"Rainbow {mode} mode at speed {speed}")
            if duration:
                print(f"Running for {duration} seconds...")
            
            # Run the right rainbow mode
            if mode == "cycle":
                rainbow_cycle(speed, duration)
            elif mode == "fade":
                rainbow_fade(speed, duration)
            elif mode == "pulse":
                rainbow_pulse(speed, duration)
            elif mode == "blink":
                rainbow_blink(speed, duration)
            elif mode == "strobe":
                rainbow_strobe(speed, duration)
            else:
                print(f"Unknown mode: {mode}")
                print("Available modes: cycle, fade, pulse, blink, strobe")
                sys.exit(1)
        
        # If the user wants a specific color (by name)
        elif args[0].lower() in COLORS:
            color_name = args[0].lower()
            
            # Check if they want an effect with that color
            if len(args) >= 2 and args[1].lower() in ["pulse", "blink", "strobe"]:
                color = COLORS[color_name]
                mode = args[1].lower()
                speed = int(args[2]) if len(args) > 2 else 50
                speed = max(0, min(100, speed))
                
                # Tell the user what we're doing
                print(f"{color_name} {mode} mode at speed {speed}")
                if duration:
                    print(f"Running for {duration} seconds...")
                
                # Run the right mode
                if mode == "pulse":
                    pulse_mode(color, speed, duration)
                elif mode == "blink":
                    blink_mode(color, speed, duration)
                elif mode == "strobe":
                    strobe_mode(color, speed, duration)
            else:
                # Just show the color at a specific brightness
                r, g, b = COLORS[color_name]
                brightness = int(args[1]) if len(args) > 1 else 100
                brightness = max(0, min(100, brightness))
                
                # Tell the user what we're doing
                print(f"Setting color: {color_name} (RGB: {r}, {g}, {b}) at {brightness}% brightness")
                if duration:
                    print(f"Running for {duration} seconds...")
                
                # Set the color
                set_rgb(r, g, b, brightness)
                
                # If there's a duration, wait that long
                # Otherwise, keep running forever
                if duration:
                    time.sleep(duration)
                else:
                    while True:
                        time.sleep(1)
        
        # If the user gave us RGB numbers directly
        else:
            try:
                # Read the RGB values
                r = int(args[0])
                g = int(args[1])
                b = int(args[2])
                brightness = int(args[3]) if len(args) > 3 else 100
                brightness = max(0, min(100, brightness))
                
                # Make sure the RGB values are valid (0 to 255)
                for val in (r, g, b):
                    if not (0 <= val <= 255):
                        print("RGB values must be between 0 and 255")
                        sys.exit(1)
                
                # Tell the user what we're doing
                print(f"Setting RGB to {r}, {g}, {b} at {brightness}% brightness")
                if duration:
                    print(f"Running for {duration} seconds...")
                
                # Set the color
                set_rgb(r, g, b, brightness)
                
                # If there's a duration, wait that long
                # Otherwise, keep running forever
                if duration:
                    time.sleep(duration)
                else:
                    while True:
                        time.sleep(1)
            
            except ValueError:
                # If they typed something that's not a number
                print("Invalid arguments. Use color name or integer RGB values.")
                sys.exit(1)
        
        # When we're done, turn off the lights
        turn_off()
    
    # If the user presses Ctrl+C, turn off the lights and exit
    except KeyboardInterrupt:
        turn_off()
        print("\nExiting...")
    
    # If something goes wrong with the arguments
    except ValueError:
        print("Invalid arguments.")
        sys.exit(1)

# This is the magic line that starts the program!
# It says "only run main() if this file is run directly"
# (so we can import this file from other programs without running it)
if __name__ == "__main__":
    main()
