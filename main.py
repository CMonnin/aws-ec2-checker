import os
from discord_poster import post_to_discord
from ip_getter import ip_getter

webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
tag_name = os.getenv("TAG_NAME")
region = os.getenv("AWS_REGION")
public_ip = ip_getter(tag_name, region)


def main():
    post_to_discord(webhook_url, public_ip)


if __name__ == "__main__":
    main()
