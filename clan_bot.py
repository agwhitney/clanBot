# Hydration timer
# Self-tag clan functionality
# Emoji tracker I guess

import asyncio
import configparser
import discord
from discord.ext import commands
import json


config = configparser.ConfigParser()
config.read('config.ini')
# Configuration variables
token = config.get('token', 'token')
rosters_file = config.get('roster', 'roster')
description = config.get('description', 'description')
prefix = config.get('prefix', 'prefix')

bot = commands.Bot(command_prefix=prefix, description=description)

# Program helper functions
def read_json(filename):
	""" A simple json.load utility.
	Returns json'ified data (a dict)
	"""
	with open(filename, 'r') as f:
		data = json.load(f)
	return data


def write_json(data, filename):
	""" A simple json.dump utility.
	Writes json data.
	"""
	with open(filename, 'w') as f:
		json.dump(data, f, indent=4)


# Bot Login/Logout
@bot.event
async def on_ready():
	print("Logged in as:")
	print('\t', bot.user.name)
	print('\t', bot.user.id)
	print("----------------------------")


@bot.command(pass_context=True)
async def logout(ctx):
	""" Mercilessly kills the bot and program."""
	await bot.say("Goodbye! uwu")
	bot.logout()
	raise SystemExit


@bot.command(pass_context=True)
async def create(ctx, clan_name: str):
	""" Creates a new clan (no spaces).

	:param ctx: <discord.ext.commands.Context>
		Context of the command invocation.

	:param clan_name: <str>
		Name of the clan to be made.
	"""
	clan_name = clan_name.lower()
	clans = read_json(rosters_file)

	if clans.get(clan_name) is None:
		clans[clan_name] = [ctx.message.author.id]
		write_json(clans, rosters_file)
		await bot.say(f"{clan_name} has been created!")

	else:
		await bot.say("A clan with that name already exists.")


@bot.command(pass_context=True)
async def join(ctx, clan_name: str):
	""" Join an existing clan.

	:param ctx: <discord.ext.commands.Context>
		Context of the command invocation.

	:param clan_name: <str>
		Name of the clan to join.
	"""
	clan_name = clan_name.lower()
	clans = read_json(rosters_file)
	user = ctx.message.author
	roster = clans.get(clan_name)

	if roster is None:
		await bot.say("That clan doesn't exist")
		return

	if user.id in roster:
		await bot.say("You're already in that clan.")
		return

	# Append user to roster and update the file
	roster.append(user.id)
	clans[clan_name] = roster
	write_json(clans, rosters_file)

	await bot.say(f"Welcome to {clan_name}, {user.display_name}!")


@bot.command(pass_context=True)
async def leave(ctx, clan_name: str):
	""" Removes the caller from the named clan.

	:param ctx: <discord.ext.commands.Context>
		Context of the command invocation.

	:param clan_name: <str>
		Name of the clan to be removed from.
	"""
	clan_name = clan_name.lower()
	clans = read_json(rosters_file)
	user = ctx.message.author
	roster = clans.get(clan_name)

	if roster is None:
		await bot.say("That clan doesn't exist!")
		return

	if not user.id in roster:
		await bot.say("You aren't in that clan!")
		return

	# Remove the user, then update clans and json file
	roster.remove(user.id)
	if roster == []:
		# If the roster is empty, remove the clan from the list
		clans.pop(clan_name)
	else:
		clans[clan_name] = roster

	write_json(clans, rosters_file)

	await bot.say(f"You've been removed from {clan_name}, {user.display_name}")


@bot.command(pass_context=True)
async def members(ctx, clan_name=None):
	""" List all the clans, or the members of a given clan. """
	clans = read_json(rosters_file)
	msg = ""

	if clan_name is None:
		await bot.say("Existing clans:")
		for name in clans.keys():
			msg += f"{name} \n"
	else:
		clan_name = clan_name.lower()
		roster = clans.get(clan_name)
		await bot.say(f"Members of {clan_name}:")
		for userID in roster:
			user = await bot.get_user_info(userID)
			msg += f"{user.display_name} \n"

	await bot.say(f"```{msg}```")


@bot.command(pass_context=True)
async def call(ctx, clan_name: str, *, content=None):
	""" Tags the members of a clan. """
	clan_name = clan_name.lower()
	clans = read_json(rosters_file)
	roster = clans.get(clan_name)

	if roster is None:
		await bot.say("That clan doesn't exist")
		return
	else:
		tags = ''
		for userID in roster:
			user = await bot.get_user_info(userID)
			tags += user.mention

	await bot.say(clan_name + ' - ' + tags)
	if content:
		await bot.say(content)


@bot.command(pass_context=True)
async def reminder(ctx, time: int, unit: str, *, content=None):
	""" Set a reminder for n minutes, hours, or days """
	user = ctx.message.author

	if unit.lower() in ('m', 'min', 'mins', 'minute', 'minutes'):
		factor = 60
	elif unit.lower() in ('h', 'hr', 'hrs', 'hour', 'hours'):
		factor = 60 * 60
	elif unit.lower() in ('d', 'day', 'days'):
		factor = 60 * 60 * 24
	else:
		await bot.say("Provide a valid unit of time")
		return

	await bot.say(f"You're reminder is queued, {user.display_name}!")
	await asyncio.sleep(time * factor)
	await bot.say(f"Here's your reminder, {user.mention}")
	if content:
		await bot.say(content)



bot.run(token)
