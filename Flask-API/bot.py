import random
import requests
import discord
from discord import app_commands
from discord.ext import tasks
from datetime import time
import zoneinfo

# Your bot token
TOKEN = "BOT TOKEN HERE"

# Channel where daily posts will be sent
CHANNEL_ID = CHANNEL ID HERE
# Server ID for Slash commands
GUILD_ID = SERVER ID HERE
# Timezone for daily post
TZ = zoneinfo.ZoneInfo("Europe/Oslo")

# Base API URL
BASE_URL = "https://ffxivcollect.com/api"

# Available Types
CATEGORIES = {
    "mount": "mounts",
    "minion": "minions",
    "achievement": "achievements",
    "title": "titles",
    "orchestrion": "orchestrions",
    "frame": "frames",
    "spell": "spells",
    "emote": "emotes",
    "barding": "bardings",
    "hairstyle": "hairstyles",
    "armoire": "armoires",
    "outfit": "outfits",
    "fashion": "fashions",
    "facewear": "facewear",
    "triad": "triad",
    "record": "records",
    "survey_record": "survey-records",
    "leve": "leves",
    "relic": "relics",
    "tomestone": "tomestones",
}

# Discord client setup
intents = discord.Intents.default()
client = discord.Client(intents=intents)

# Slash command tree
tree = app_commands.CommandTree(client)


# Get random type from selected category
def get_random_item(category_key):
    endpoint = CATEGORIES[category_key]
    url = f"{BASE_URL}/{endpoint}?language=en"

    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    results = data["results"] if "results" in data else data

    if not results:
        raise Exception(f"No results found for {category_key}")

    return random.choice(results), category_key


# Create Discord embed
def create_embed(item, category_key):
    name = item.get("name", "Unknown")

    description = (
        item.get("description")
        or item.get("tooltip")
        or item.get("source")
        or "No description available."
    )

    embed = discord.Embed(
        title=f"{category_key.replace('_', ' ').title()}: {name}",
        description=description,
        color=discord.Color.gold()
    )

    if item.get("patch"):
        embed.add_field(name="Patch", value=str(item["patch"]), inline=True)

    if item.get("owned"):
        embed.add_field(name="Owned by", value=str(item["owned"]), inline=True)

    if item.get("source"):
        embed.add_field(name="Source", value=str(item["source"]), inline=False)

    image = item.get("image") or item.get("icon")
    if image:
        embed.set_image(url=image)

    return embed


# Shared for category commands
async def send_random_category(interaction, category_key):
    await interaction.response.defer()

    try:
        item, category_key = get_random_item(category_key)
        embed = create_embed(item, category_key)
        await interaction.followup.send(embed=embed)

    except Exception as e:
        await interaction.followup.send(f"Error: `{e}`")


# Runs when bot starts to show it connects in consol log
@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

    guild = discord.Object(id=GUILD_ID)

    # global commands working in log
    tree.copy_global_to(guild=guild)
    await tree.sync(guild=guild)

    print("Slash commands synced to server")

    if not daily_random.is_running():
        daily_random.start()
        print("Daily task started")

    print(f"Next daily post: {daily_random.next_iteration}")
#Daily post command for testing
@tree.command(name="postdaily", description="Test the daily random post now")
async def postdaily(interaction: discord.Interaction):
    await interaction.response.defer()

    category_key = random.choice(list(CATEGORIES.keys()))
    item, category_key = get_random_item(category_key)

    embed = create_embed(item, category_key)

    await interaction.followup.send(
        content="Test daily random FFXIVCollect item:",
        embed=embed
    )
# Random item from any type
@tree.command(name="random", description="Random FFXIVCollect item from any category")
async def random_command(interaction: discord.Interaction):
    await interaction.response.defer()

    try:
        category_key = random.choice(list(CATEGORIES.keys()))
        item, category_key = get_random_item(category_key)

        embed = create_embed(item, category_key)
        await interaction.followup.send(embed=embed)

    except Exception as e:
        await interaction.followup.send(f"Error: `{e}`")


# Specific slash commands
@tree.command(name="mount", description="Random FFXIV mount")
async def mount(interaction: discord.Interaction):
    await send_random_category(interaction, "mount")


@tree.command(name="minion", description="Random FFXIV minion")
async def minion(interaction: discord.Interaction):
    await send_random_category(interaction, "minion")


@tree.command(name="achievement", description="Random FFXIV achievement")
async def achievement(interaction: discord.Interaction):
    await send_random_category(interaction, "achievement")


@tree.command(name="title", description="Random FFXIV title")
async def title(interaction: discord.Interaction):
    await send_random_category(interaction, "title")


@tree.command(name="orchestrion", description="Random FFXIV orchestrion roll")
async def orchestrion(interaction: discord.Interaction):
    await send_random_category(interaction, "orchestrion")


@tree.command(name="emote", description="Random FFXIV emote")
async def emote(interaction: discord.Interaction):
    await send_random_category(interaction, "emote")


@tree.command(name="spell", description="Random FFXIV spell")
async def spell(interaction: discord.Interaction):
    await send_random_category(interaction, "spell")


@tree.command(name="hairstyle", description="Random FFXIV hairstyle")
async def hairstyle(interaction: discord.Interaction):
    await send_random_category(interaction, "hairstyle")


@tree.command(name="outfit", description="Random FFXIV outfit")
async def outfit(interaction: discord.Interaction):
    await send_random_category(interaction, "outfit")


@tree.command(name="fashion", description="Random FFXIV fashion accessory")
async def fashion(interaction: discord.Interaction):
    await send_random_category(interaction, "fashion")


# Daily post at exactly 08:00 Europe/Oslo time (untested)
@tasks.loop(time=time(hour=8, minute=0, tzinfo=TZ))
async def daily_random():
    channel = client.get_channel(CHANNEL_ID)

    if channel:
        try:
            category_key = random.choice(list(CATEGORIES.keys()))
            item, category_key = get_random_item(category_key)

            embed = create_embed(item, category_key)

            await channel.send(
                content="Daily random FFXIVCollect item:",
                embed=embed
            )

        except Exception as e:
            await channel.send(f"Daily post failed: `{e}`")


# bot starts running
client.run(TOKEN)
