import os
from discord_poster import post_to_discord
from ip_getter import ip_getter

webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
stack_name= os.getenv("STACK_NAME")
region = os.getenv("AWS_REGION")
public_ip = ip_getter(stack_name, region)


def main():
    print(stack_name)
    post_to_discord(webhook_url, public_ip)


if __name__ == "__main__":
    main()
