import discord
from discord.ext import commands
import subprocess
import os

bot = commands.Bot(command_prefix='!', intents=discord.Intents.default())

ALLOWED_SCRIPTS = {
    'ip': 'ip_getter.py',
}

@bot.command()
async def run(ctx, script_name: str):
    """
    Runs a predefined script when called with !run script_name
    Only runs scripts from the ALLOWED_SCRIPTS dictionary
    """
    if not script_name in ALLOWED_SCRIPTS:
        await ctx.send(f"Error: Script '{script_name}' not found in allowed scripts.")
        return
        
    try:
        script_path = os.path.join('scripts', ALLOWED_SCRIPTS[script_name])
        
        if not os.path.exists(script_path):
            await ctx.send(f"Error: Script file not found.")
            return
            
        result = subprocess.run(['python', script_path], 
                              capture_output=True,
                              text=True,
                              timeout=30)  # 30 second timeout
        
        output = result.stdout if result.stdout else "Script completed with no output."
        await ctx.send(f"```\n{output}\n```")
        
    except subprocess.TimeoutExpired:
        await ctx.send("Error: Script execution timed out.")
    except Exception as e:
        await ctx.send(f"Error running script: {str(e)}")

