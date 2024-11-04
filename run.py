import os
from dotenv import load_dotenv
from discord_bot import bot

def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Get the Discord token
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        raise ValueError("DISCORD_TOKEN not found in environment variables")
    
    # Run the bot
    bot.run(token)

if __name__ == "__main__":
    main()
