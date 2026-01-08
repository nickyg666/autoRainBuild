# ==============================================
# 🐢 TURTLE DRAWING FUN! 🐢
# ==============================================
# Learn to draw cool pictures with Python!

# Step 1: Import the turtle module
# This gives us a magic turtle to draw with!
import turtle

# Step 2: Make our turtle
# Think of this like picking up a pen!
pen = turtle.Turtle()

# Step 3: Make turtle faster
pen.speed(10)

# Step 4: Draw a SQUARE
# A square has 4 sides, each line turns 90 degrees
for i in range(4):
    # Move forward (draw a line)
    pen.forward(100)
    
    # Turn right 90 degrees
    pen.right(90)

# Step 5: Move to new spot without drawing
pen.penup()      # Lift pen up
pen.goto(0, -50) # Move to new spot
pen.pendown()    # Put pen down

# Step 6: Draw a CIRCLE
pen.circle(50)

# Step 7: Move again
pen.penup()
pen.goto(0, 100)
pen.pendown()

# Step 8: Draw a TRIANGLE
# Triangle has 3 sides, each turn is 120 degrees
for i in range(3):
    pen.forward(100)
    pen.left(120)  # Left turn this time!

# Keep the drawing on screen
turtle.done()

# ==============================================
# 🎨 TRY CHANGING THIS! 🎨
# ==============================================
# IDEAS:
# - Change forward(100) to forward(200)
# - Change the colors: pen.color("red")
# - Draw more shapes!
# - Make the turtle move to new spots!
# ==============================================
