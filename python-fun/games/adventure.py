# ==============================================
# 🏰 MAGICAL CASTLE ADVENTURE 🏰
# ==============================================
# An epic choose-your-own-adventure game!

# Step 1: Print welcome screen
print("""
╔══════════════════════════════════════╗
║     🏰 MAGICAL CASTLE ADVENTURE 🏰    ║
║                                       ║
║  You stand before a mysterious castle!  ║
║  What will you do?                     ║
╚══════════════════════════════════════╝
""")

# Step 2: First choice
print("Do you want to:")
print("1. 🚪 Go through the front door")
print("2. 🪟 Climb through a window")

# Step 3: Get player's choice
# input() waits for player to type something
choice = input("👉 Type 1 or 2 and press Enter: ")

# Step 4: Check what player chose
if choice == "1":
    # Going through the door!
    print("\n🚪 You walk through the front door...")
    print("Suddenly, a dragon appears! 🐉")
    print("Do you:")
    print("1. ⚔️ Fight the dragon")
    print("2. 🏃 Run away!")
    
    dragon_choice = input("👉 Type 1 or 2: ")
    
    if dragon_choice == "1":
        print("\n⚔️ You fight bravely!")
        print("🎉 The dragon becomes your friend!")
        print("🏆 YOU WIN - DRAGON MASTER!")
    else:
        print("\n🏃 You run away fast!")
        print("😢 But you find a treasure chest!")
        print("🏆 YOU WIN - TREASURE HUNTER!")

elif choice == "2":
    # Climbing through the window!
    print("\n🪟 You climb through the window...")
    print("You land in a room full of gold! 💰")
    print("But there's a guard! 👮")
    print("Do you:")
    print("1. 🤝 Be friendly to the guard")
    print("2. 🎭 Try to sneak past")
    
    guard_choice = input("👉 Type 1 or 2: ")
    
    if guard_choice == "1":
        print("\n🤝 The guard becomes your friend!")
        print("🎉 He shares the treasure!")
        print("🏆 YOU WIN - TRUSTED FRIEND!")
    else:
        print("\n🎭 You try to sneak...")
        print("😰 But the guard catches you!")
        print("😢 GAME OVER - Try being friendly!")

else:
    # Player typed something wrong
    print("\n❌ That's not a choice!")
    print("🤔 Think carefully and try again!")

# End of game
print("\n" + "=" * 40)
print("Thanks for playing! 🎮")
print("Play again by running: python3 adventure.py")
print("=" * 40)

# ==============================================
# 🎮 MAKE YOUR OWN ADVENTURE! 🎮
# ==============================================
# IDEAS:
# - Add more rooms to explore!
# - Add magical items to find!
# - Make different endings!
# - Add puzzles to solve!
# - Create new characters!
# ==============================================
