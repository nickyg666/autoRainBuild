# ==============================================
# 🌈 RAINBOW TURTLE 🌈
# ==============================================
# Make your turtle draw in ALL colors!

# Step 1: Import turtle (our drawing tool)
import turtle

# Step 2: Create our turtle artist
artist = turtle.Turtle()
artist.speed(15)  # Make it super fast!

# Step 3: List of colors to use
colors = ["red", "orange", "yellow", "green", "blue", "purple"]

# Step 4: Draw a colorful flower!
# We'll use a loop to repeat patterns
for i in range(36):
    # Pick a color from our list
    # % means "wrap around" - goes back to start after last color
    color = colors[i % len(colors)]
    
    # Set the pen color
    artist.color(color)
    
    # Draw one petal
    artist.forward(100)
    artist.right(45)
    artist.forward(50)
    artist.right(135)
    artist.forward(100)
    artist.right(45)
    artist.forward(50)
    
    # Turn to next petal
    artist.right(110)

# Move to center and make a center circle
artist.penup()
artist.goto(0, 0)
artist.pendown()
artist.color("gold")
artist.circle(20)

# Keep drawing on screen
turtle.done()

# ==============================================
# 🎨 CREATE YOUR OWN ART! 🎨
# ==============================================
# TRY THIS:
# - Add more colors to the colors list!
# - Change the numbers in the loops
# - Make different shapes!
# - Change artist.speed() to 1 (slow) and watch carefully!
# ==============================================
