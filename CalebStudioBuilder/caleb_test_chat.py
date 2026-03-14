from image_maker import CalebImageMaker

print("--- BOOTING CALEB ---")
image_brain = CalebImageMaker()

print("\nCaleb is ready. Type 'draw [whatever]' to test it.")
print("Type 'quit' to leave.")

while True:
    # Grab what you type, make it lowercase, and clean up the edges
    user_input = input("\nYou: ").strip().lower()
    
    if user_input == 'quit':
        break
        
    # Bulletproof check: just look for the word "draw" anywhere
    if "draw" in user_input:
        # Cut the word "draw" out so it just leaves the rest of your idea
        prompt = user_input.replace("draw", "").strip()
        print(f"Caleb: You got it. Drawing '{prompt}'...")
        
        # Fire the simple drawing tool
        image_brain.draw_simple(prompt, "chat_art.png")
        
        print("Caleb: Done. Check your folder for 'chat_art.png'. What else you need?")
    else:
        print("Caleb: I just have my visual brain wired up right now. Tell me to 'draw' something!")
