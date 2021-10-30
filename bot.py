#!/usr/bin/env python3

# bot.py
import os
import csv
import socket
import ipaddress

import Azure_Updates as az

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
client = discord.Client()
TOKEN = os.getenv('DISCORD_TOKEN')
seceretChannel = os.getenv('SECERET_CHANNEL')

bot = commands.Bot(command_prefix='!', case_insensitive=True)
wish_file = os.path.join(os.environ['USERPROFILE'], "Documents", "wishes.csv")
ip_file = os.path.join(os.environ['USERPROFILE'], "Documents", "ipaddresses.csv")


@bot.event
async def on_ready():
    az.az_login()
    print("Everything's all ready to go~")


@bot.command(name='AddToWishList')
async def AddToWishList(ctx, *args):
    """
    :: Adds an string of text to the wish list.
    """
    wish = ' '.join(args)

    success = append_list_as_row(wish_file, ("Wish::"+wish))
    if success == 0:
        await ctx.channel.send(f"The following was added to wish list: {wish}")
    else:
        await ctx.channel.send(f"An Error occurred adding to wish list")


@bot.command(name='ShowWishList')
async def ShowWishList(ctx):
    """
    :: View items in the wish list
    """
    wish_list = return_csv_as_list(wish_file)
    for wishes in wish_list:
        await ctx.channel.send(wishes)

    await ctx.channel.send(f"End of list")


@bot.command(name='AddIPAddress')
async def AddIPAddress(ctx, *args):
    """
    :: Only allows valid IPv4 Addresses to join the Terraria Server
    """

    channel = ctx.channel.id
    ipAddress = ''.join(args)

    if channel == int(seceretChannel):
        try:
            # check if the IP address is valid
            ipaddress.ip_address(str(ipAddress))

            # check if IP is already in list
            ip_addresses = return_csv_as_list(ip_file)
            if ipAddress in ip_addresses:
                await ctx.channel.send(f"The following IP already exists in IP Address list: {ipAddress}")
                return

            success = append_list_as_row(ip_file, ipAddress)
            if success == 0:
                await ctx.channel.send(f"The following was added to IP Address list: {ipAddress}")
            else:
                await ctx.channel.send(f"An Error occurred adding to IP Address list")

            # add the new IP addresses to to the list of IPs pulled from the CSV file
            ip_addresses.append(ipAddress)

            try:
                print(az.az_set_nsg_rules(ip_addresses))
            except Exception as z:
                await ctx.channel.send(f'Exception trying to add ipAddress to Azure:{z}')

        except Exception as x:
            await ctx.channel.send(f'Exception:{x}')
            await ctx.channel.send(f'Invalid IP Address {ipAddress}. Look up IP here https://whatismyipaddress.com')
    else:
        await ctx.channel.send('Cannot use command here')


@bot.command(name='ShowIPAddresses')
async def ShowIPAddresses(ctx):
    """
    :: View list of added IP Addresses
    """
    channel = ctx.channel.id

    if channel == int(seceretChannel):
        ip_addresses = return_csv_as_list(ip_file)
        for items in ip_addresses:
            await ctx.channel.send(items)

        await ctx.channel.send(f"End of list")
    else:
        await ctx.channel.send('Cannot use command here')


@bot.command(name='ping')
async def ping(ctx):
    """
    :: checks the ping of the bot.
    """

    # Get the latency of the bot
    latency = bot.latency  # Included in the Discord.py library
    # Send it to the user
    await ctx.channel.send(latency)


@bot.command(name='echo')
async def echo(ctx, *args):
    """
    :: repeats any said after !echo.
    """
    response = ""
    for arg in args:
        response = response + " " + arg

    await ctx.channel.send(response)


def append_list_as_row(file_name, list_of_elem):
    try:
        # Open file in append mode
        with open(file_name, 'a+', newline='') as write_obj:
            # Create a writer object from csv module
            csv_writer = csv.writer(write_obj, delimiter=',')
            # Add contents of list as last row in the csv file
            csv_writer.writerow([list_of_elem])

        write_obj.close()
        return 0
    except:
        # unknown error handled
        return 1


def return_csv_as_list(file_name):
    # Open file in read
    output_list = []
    line_count = 0
    with open(file_name, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        # output_list.append(next(csv_reader))

        for row in csv_reader:
            output_list.append(''.join(row))
    csv_file.close()
    return output_list


@AddToWishList.error
async def AddToWishList_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send('A Bad Argument error has occurred')
    elif isinstance(error, commands.CommandInvokeError):
        await ctx.send('A Command Invoke Error occurred')
    else:
        await ctx.send('Something really wrong occurred')

bot.run(TOKEN)
