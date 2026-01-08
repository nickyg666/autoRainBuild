# ==============================================
# 🔢 GUESS THE NUMBER GAME 🔢
# ==============================================
# This is a game where you try to guess a number!

# Step 1: Import random - gives us a magic random number picker
import random

# Step 2: Pick a secret number between 1 and 100
secret_number = random.randint(1, 100)

# Step 3: Set guesses to 0 (we'll count how many tries)
guesses = 0

# Step 4: Welcome the player!
print("🎮 WELCOME TO GUESS THE NUMBER!")
print("I'm thinking of a number between 1 and 100")
print("Can you guess it?")

# Step 5: Start the game loop (keeps going until you win!)
while True:
    # Ask for a guess
    guess = input("🤔 What's your guess? ")
    
    # Step 6: Convert text to a number
    # (input() gives us text, we need a number)
    guess = int(guess)
    
    # Count this guess
    guesses = guesses + 1
    
    # Step 7: Check if the guess is right
    if guess == secret_number:
        print(f"🎉 YOU WIN! You got it in {guesses} tries!")
        break  # Stop the game - you won!
    
    # Step 8: Give hints
    if guess < secret_number:
        print("📈 Too LOW! Try a bigger number!")
    else:
        print("📉 Too HIGH! Try a smaller number!")
    
    print("---")  # Just a line to make it pretty

# ==============================================
# 🎮 TRY CHANGING THIS GAME! 🎮
# ==============================================
# IDEAS:
# - Change the range: random.randint(1, 50)
# - Add a limit on guesses
# - Add more hints!
# - Make it harder or easier
# ==============================================
