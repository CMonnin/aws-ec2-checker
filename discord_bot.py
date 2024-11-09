import discord
from discord.ext import commands
import subprocess
import os
import boto3
from botocore.exceptions import ClientError
from datetime import datetime

# Initialize bot with necessary intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Configuration - Should be moved to a config file in production
ALLOWED_SCRIPTS = {
    'ip': 'ip_getter.py',
}

# AWS configuration
AWS_REGION = os.getenv('AWS_REGION')
STACK_NAME = os.getenv('STACK_NAME')
ASG_NAME = f"{STACK_NAME}-asg"  # Assuming ASG name follows stack name pattern

class ServerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ec2_client = boto3.client('ec2', region_name=AWS_REGION)
        self.asg_client = boto3.client('autoscaling', region_name=AWS_REGION)
    
    def get_asg_instance(self):
        """Get the current running instance in the ASG"""
        try:
            response = self.asg_client.describe_auto_scaling_groups(
                AutoScalingGroupNames=[ASG_NAME]
            )
            
            if not response['AutoScalingGroups']:
                return None
                
            instances = response['AutoScalingGroups'][0]['Instances']
            running_instances = [i for i in instances if i['LifecycleState'] == 'InService']
            
            if not running_instances:
                return None
                
            return running_instances[0]['InstanceId']
            
        except ClientError:
            return None

    def set_asg_capacity(self, desired_capacity):
        """Set the ASG desired capacity"""
        try:
            self.asg_client.update_auto_scaling_group(
                AutoScalingGroupName=ASG_NAME,
                DesiredCapacity=desired_capacity,
                MinSize=desired_capacity,
                MaxSize=max(desired_capacity, 1)
            )
            return True
        except ClientError as e:
            print(f"Error updating ASG capacity: {e}")
            return False

    @commands.command(name='start')
    @commands.has_role('Server Admin')
    async def start_server(self, ctx):
        """Start the game server by setting ASG capacity to 1"""
        try:
            await ctx.send("🔄 Starting server... Please wait...")
            
            # Check if server is already running
            instance_id = self.get_asg_instance()
            if instance_id:
                await ctx.send("ℹ️ Server is already running! Use !ip to get the connection details.")
                return
            
            # Set ASG capacity to 1 to start a new instance
            if self.set_asg_capacity(1):
                await ctx.send("✅ Server is starting up! Hold on to your butts!")
            else:
                await ctx.send("❌ Failed to start the server. Please check AWS console for details.")
                
        except Exception as e:
            await ctx.send(f"❌ Error starting server: {str(e)}")

    @commands.command(name='stop')
    @commands.has_role('Server Admin')
    async def stop_server(self, ctx):
        """Stop the game server by setting ASG capacity to 0"""
        try:
            await ctx.send("🔄 Stopping server...")
            
            # Check if server is already stopped
            instance_id = self.get_asg_instance()
            if not instance_id:
                await ctx.send("ℹ️ Server is already stopped!")
                return
            
            # Set ASG capacity to 0 to terminate the instance
            if self.set_asg_capacity(0):
                await ctx.send("✅ Server is shutting down.")
            else:
                await ctx.send("❌ Failed to stop the server. Please check AWS console for details.")
                
        except Exception as e:
            await ctx.send(f"❌ Error stopping server: {str(e)}")

    @commands.command(name='ip')
    async def get_ip(self, ctx):
        """Get the current server IP and status"""
        try:
            instance_id = self.get_asg_instance()
            
            embed = discord.Embed(
                title="🎮 Server Status",
                timestamp=datetime.utcnow(),
                color=discord.Color.green() if instance_id else discord.Color.red()
            )
            
            if instance_id:
                response = self.ec2_client.describe_instances(InstanceIds=[instance_id])
                instance = response['Reservations'][0]['Instances'][0]
                public_ip = instance.get('PublicIpAddress', 'No IP assigned')
                
                embed.add_field(name="IP Address", value=f"`{public_ip}:34197`", inline=False)
            else:
                embed.add_field(name="Status", value="⭕ Server is stopped", inline=False)
                embed.add_field(name="Note", value="Use !start to start the server", inline=False)
            
            embed.set_footer(text="The factory must grow")
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Error getting server status: {str(e)}")

    @commands.command(name='status')
    async def server_status(self, ctx):
        """Get detailed server status"""
        try:
            instance_id = self.get_asg_instance()
            
            embed = discord.Embed(
                title="📊 Detailed Server Status",
                timestamp=datetime.utcnow(),
                color=discord.Color.blue()
            )
            
            # Get ASG information
            asg_response = self.asg_client.describe_auto_scaling_groups(
                AutoScalingGroupNames=[ASG_NAME]
            )
            asg = asg_response['AutoScalingGroups'][0]
            
            embed.add_field(
                name="ASG Status",
                value=f"Desired: {asg['DesiredCapacity']}\n"
                      f"Min: {asg['MinSize']}\n"
                      f"Max: {asg['MaxSize']}",
                inline=False
            )
            
            if instance_id:
                response = self.ec2_client.describe_instances(InstanceIds=[instance_id])
                instance = response['Reservations'][0]['Instances'][0]
                
                state = instance['State']['Name']
                instance_type = instance['InstanceType']
                launch_time = instance['LaunchTime'].strftime("%Y-%m-%d %H:%M:%S UTC")
                public_ip = instance.get('PublicIpAddress', 'No IP assigned')
                
                embed.add_field(name="Instance ID", value=instance_id, inline=True)
                embed.add_field(name="State", value=state, inline=True)
                embed.add_field(name="Instance Type", value=instance_type, inline=True)
                embed.add_field(name="Launch Time", value=launch_time, inline=True)
                embed.add_field(name="Public IP", value=public_ip, inline=True)
            else:
                embed.add_field(name="Server Status", value="No instances running", inline=False)
            
            embed.set_footer(text="The factory must grow")
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Error getting detailed status: {str(e)}")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            await ctx.send("❌ You don't have permission to use this command.")
        elif isinstance(error, commands.CommandNotFound):
            await ctx.send("❌ Unknown command. Use !help to see available commands.")
        else:
            await ctx.send(f"❌ An error occurred: {str(error)}")

@bot.event
async def on_ready():
    print(f'Bot is ready and logged in as {bot.user}')
    await bot.add_cog(ServerCommands(bot))

