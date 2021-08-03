# Barry

# -----------------------------------
#              Modules

# Bot
import asyncpraw
import discord
from discord import Permissions, Embed, Colour
from discord.ext.commands import Bot, has_permissions, CheckFailure, cooldown, BucketType
from keep_alive import keep_alive
import os

# Time
from datetime import datetime
import time

# Misc
import emoji as e
import random
import re

# -----------------------------------
#               Globals
prefix = 'b!'  #Prefix
intents = discord.Intents.all() #Allows Barry to track all things 
client = Bot(command_prefix=prefix, intents=intents)  #The bot itself
token = os.environ['barry_token']  #Barry's token so that the client is the program
reddit = asyncpraw.Reddit(client_id = '5x8y8ZHQbkMW1w', client_secret = os.environ['barry_praw_secret'], 
user_agent = 'discord.com:Barry:1.0 by u/Saharth') #The reddit app Barry has so that he can get posts

# Gets the time and date
t = datetime.utcnow()
currentDate = t.strftime("%d/%m/%y")
currentTime = t.strftime('%H:%M')

pointsRecord = []
client.remove_command('help')


#-----------------------------------
#            Logs Events
# Well, mostly

#When the bot wakes up
@client.event
async def on_ready():

	print(f'We have logged on as {client.user}')
	activity = discord.Activity(type=discord.ActivityType.listening, name='b!help')
	client.heartbeat_timeout = 350.0
	await client.change_presence(status=discord.Status.online, activity=activity)
	print(f'Reddit Activity: {reddit.read_only}')


# Filter
@client.event
async def on_message(message):
	global pointsRecord


	if 'Barian' in message.guild.name:
		curses = [
        'fuck', 'shit', 'bitch', 'cunt', 'dick', 'shag', 'nigg', 'niga',
        'negr', 'ass', 'slag', 'wank', 'pussy', 'gay', 'fag', 'bastard',
        'cock', 'boob', 'penis', 'paki', 'feck', 'vagina', 'coon',
        'prick', 'clit', 'retard'
    ]
		# Iterates through the curses list
		for word in curses:
			# If a word there is in the message and the author isn't an admin
			if (word == ''.join(message.content.split()).lower() or word in message.content.split()) and message.author.guild_permissions.administrator == False:
				# Try to delete it, but be aware other bots might have gotten there first, and except the errors that come from it
				try:
					await message.delete()
				except discord.errors.NotFound:
					pass
				# Send a warning embed
				warning = Embed(colour = Colour.teal(), description = f'No profanities here {message.author.mention}', 
				title = 'Profanity Warning:')
				# Thumbnail is a raging Michael Scott
				warning.set_thumbnail(url = 'https://media.giphy.com/media/zCpYQh5YVhdI1rVYpE/giphy.gif')
				await message.channel.send(embed = warning)

# Points
	# This will effectively allow the 'Barian_Points' file to act as a server containing the messages
	def getPoints(filename):
		file = open(filename, 'r')
		pointsRecord = []

		for line in file:
			line = line.split(',')
			person = {}
			person['Name'] = line[0]
			try:
				person['Points'] = int(line[1])
			except ValueError:
				pass
			pointsRecord.append(person)
		file.close()

		return pointsRecord[1:]

	pointsRecord = getPoints('Barian_Points.csv')

	# Updates the points 
	def updatePoints(message, pointsRecord):
		# Iterates through pointsRecord
		for i in range(len(pointsRecord)):
			# Sets the person to the current iteration of the list
			person = pointsRecord[i]
			# If the person is the author
			if person['Name'] == message.author.name:
				# And the channel is lounge
				if message.channel.name == '››│lounge' or message.channel.name == '››│count-to-10000':
					# Add one to their points
					person['Points'] += 1
					break
				# If it's bump us, and they've tried bumping the server
				elif message.channel.name == '››│bump-us' and message.content.lower() == '!d bump':
					# Give them 10 points
					person['Points'] += 10
					break
			# Otherwise iterate over
			else:
				continue
		# Sorts the pointsRecord so that the leaders are in ascending order, on every iteration
		pointsRecord = sorted(pointsRecord, key = lambda x: x['Points'], reverse = True)	
		return pointsRecord

	# Writes the points to a file because the bot will inevitably go offline and if data is lost every time that'd be scuffed af.
	def writePoints(filename, pointsRecord):
		file = open(filename, 'w')

		file.write('Name, Points\n')
		for person in pointsRecord:
			name = person['Name']
			points = person['Points']
			file.write(f'{name},{points}\n')
		
		file.close()

	# If the server is Barian, and they wrote in lounge, bump us or count
	if 'Barian Esports' in message.guild.name and message.author.bot == False and 'lounge' in message.channel.name or 'bump' in message.channel.name or 'count' in message.channel.name:
		# Run the whole thing
		pointsRecord = updatePoints(message,pointsRecord)
		writePoints('Barian_Points.csv', pointsRecord)
	# Then run all the commands on the message because the possibility exists that it was a command
	await client.process_commands(message)	
	

@client.command(name = 'upgradePoints')
async def hotFix(ctx):
	admins = [member for member in ctx.guild.members if member.guild_permissions.administrator == True]
	audits = await ctx.guild.audit_logs(limit = 2200).flatten()
	file = open('Barian_Points.csv', 'w')
	file.write('Name,Points\n')

	for admin in admins:
		file.write(f'{admin.name},0\n')

	for entry in audits:
		if str(entry.action) == 'AuditLogAction.kick':
			if entry.target.bot != True:
				file.write(f'{entry.target.name},0\n')
	
	await ctx.send('You fixed the points system, sorta. Yay!')

# Member Joins
@client.event
async def on_member_join(member):
	global currentDate
	global currentTime
	# If they're a Motion bastard, ban them
	if 'Motion' in member.name:
			await member.ban()
	# If it's you then give yourself executive immediately
	elif 'Dominus 11' in member.name and 'Barian' in member.guild.name :
		role = discord.utils.get(member.guild.roles, name = '◆Executive◆')
		await member.add_roles(role)
	
	# Finds the guild because apparently there's no natural way of finding the guild in a client event which is very annoying
	guild = member.guild
	# Checks to see if the person has already been added to the points system
	if not member.bot:
		file = open('Barian_Points.csv', 'r')
		inFile = False
		for line in file:
			line = line.split(',')
			if line[0] == member.name:
				inFile = True
				break
		file.close()
		# If they aren't in the file, then it appends them to the end of it
		if not inFile:
			file = open('Barian_Points.csv', 'a')
			file.write(f'{member.name},0\n')
	
	# Assuming it's Barian, it gets the necessary channels that are going to be needed
	if 'Barian Esports' in guild.name:
		community = discord.utils.get(guild.roles, name = '◆Barian Community◆')
		portal = discord.utils.get(guild.channels, name = '››│portal')
		rules = discord.utils.get(guild.channels, name = '››│rules')
		roles = discord.utils.get(guild.channels, name = '››│self-roles')
		logs = discord.utils.get(guild.channels, name = '››│barry-logs')

		#Gives them the Barian Community role
		await member.add_roles(community)
		# Announces in the portal
		announcementEmbed = Embed(colour =  Colour.teal(), 
		title = f'Welcome to Barian Esports {member.name}!', 
		description = f'Hi {member.mention}, welcome to our Discord Server!\nPlease be sure to go through {rules.mention} and {roles.mention} before doing anything. Enjoy your stay here! A member of staff should be in touch shortly to help you get settled in! If you want more info about my commands, do \'b!help\'!').set_footer(text = member, 
		icon_url = member.avatar_url).set_thumbnail(url = guild.icon_url)
		await portal.send(embed = announcementEmbed)

		# Makes a record of it in logs
		logging = Embed(colour  =Colour.teal(), 
		title = 'Member Joined:')
		logging.add_field(name = 'Member:', value = member.mention)
		logging.add_field(name = 'Account Created On:', 
		value = member.created_at.strftime('%d/%m/%y'))
		# Sets it to Sokka being totally high on cactus juice
		logging.set_thumbnail(url = 'https://media.giphy.com/media/kkSkgexb9xBoQ/giphy.gif')
		logging.set_footer(text = f'ID: {member.id} | Date: {currentDate} | Time: {currentTime}')
		logging.set_author(name = member.name, icon_url = member.avatar_url)
		await logs.send(embed = logging)

		# Checks to see if they're in the kicks file and removes them if so
		def updateKicks():
			file = open('Barian Kicks.txt', 'r')
			kicks = []
			# Adds each member name to a list of names
			for line in file:
				kicks.append(line)
			file.close()
		
			# If the name of the kicked person matches the name of the member that joined
			for kicked in kicks:
				if re.search(member.name, kicked):
					# Removes them from the list for rewriting
					kicks.remove(kicked)
					break
		
			# Writes the new list of kicked people back up
			file = open('Barian Kicks.txt', 'w')
			for kicked in kicks:
				file.write(f'{kicked}\n')
			file.close()
	
		updateKicks()


#Member leaves/is forcibly removed
@client.event
async def on_member_remove(member):
	global currentDate
	global currentTime

	def checkKicked():
		file = open('Barian Kicks.txt', 'r')
		for line in file:
			if member.name in line:
				file.close()
				return True
		return False

	guild = member.guild
	# If this occurred in Barian, then it fetches the channel, if not, nobody actually gives a damn so yeah
	if 'Barian' in guild.name:
		# Gets the portal and the logs, alongside to check if they were kicked or left of their own will
		portal = discord.utils.get(guild.channels, name = '››│portal')
		logs = discord.utils.get(guild.channels, name = '››│barry-logs')
		kicked = checkKicked()
	
		# If they've been kicked it, shamelessly and publicly disgraces them
		if kicked:
			announcementEmbed = Embed(colour = Colour.teal(), title = f'Goodbye {member.name}.', 
			description = f'Goodbye {member.mention}, you have been removed from Barian Esports team and community server.Please come back with a better demeanor next time!')
			announcementEmbed.set_footer(text = member, icon_url = member.avatar_url)
			announcementEmbed.set_thumbnail(url = 'https://media.giphy.com/media/OoaTf8fEuesP6/giphy.gif')
			await portal.send(embed = announcementEmbed)

		else:
			# Announces their departure in the portal
			announcementEmbed = Embed(colour = Colour.teal(), title = f'Goodbye {member.name}.', 
			description = f'Goodbye {member.mention}, you have departed from Barian Esports team and community server. We hoped you enjoyed your stay here. Good luck in all your future endeavours!')
			announcementEmbed.set_footer(text = member, icon_url = member.avatar_url)
			announcementEmbed.set_thumbnail(url = 'https://media.giphy.com/media/fWgQH01z4rjwrZckyM/giphy.gif')
			await portal.send(embed = announcementEmbed)

			# Makes a record of it in logs
			logging = Embed(colour  =Colour.teal(), title = 'Member Left:', 
			description = f'Member {member.mention} has left the server.')
			# Sets the thumbnail to their icon because there's not much better, I'll find something
			logging.set_thumbnail(url = member.avatar_url)
			logging.set_author(name = member, icon_url = member.avatar_url)
			logging.set_footer(text = f'ID: {member.id} | Date: {currentDate} | Time: {currentTime}')
			await logs.send(embed = logging)

# Whenever a member has been banned from the guild
@client.event
async def on_member_ban(guild,user):
	global currentDate
	global currentTime
	# Get the portal
	portal = discord.utils.get(guild.channels, name = '››│portal')
	# If the guild is one of the Barian twins
	if portal != None:
		# Write a semi- toxic announcement Embed to them
		announcementEmbed = Embed(colour =  Colour.teal(), title = f'Adios {user.name}!',
				description = f'Adios to you {user.mention}! You have transgressed against one of our server rules or done something seriously bad, because we felt the need to ban you! So goodbye and farewell! Hopefully we\'ll see you again on better terms!')
		# Set the thumbnail to Lily being a savage
		announcementEmbed.set_thumbnail(url = 'https://media.giphy.com/media/dEC8R8Ws5c6VG/giphy.gif')
		# Set the footer to their name and avatar url so we know
		announcementEmbed.set_footer(text = user, icon_url = user.avatar_url)
		# Send it onto the portal
		await portal.send(embed = announcementEmbed)

# Whenever a message is deleted 
# (NB: May not always run as it isn't always stored in internal cache)
@client.event
async def on_message_delete(message):
	global currentDate
	global currentTime
	# Create a record of it in logs, though the potential exists for it to not exist in the internal cache
	if 'Barian' in message.guild.name and not message.author.bot:
		logs = discord.utils.get(message.guild.channels, name = '››│barry-logs')
		logging = Embed(colour = Colour.teal(), title = f'Message by {message.author.name} Deleted in {message.channel.name}:', 
		description = message.content)
		logging.set_author(name = message.author, icon_url = message.author.avatar_url)
		logging.set_footer(text = f'ID: {message.author.id} | Date: {currentDate} | Time: {currentTime}' )
		await logs.send(embed = logging)

# Whenever a member changes something about them
@client.event
async def on_member_update(before, after):
	global currentDate
	global currentTime

	guild = after.guild
	if 'Barian' in guild.name:
		logs = discord.utils.get(guild.channels, name = '››│barry-logs')
		# If they changed their nickname
		if before.nick != after.nick:
			# Create a log embed containing their nickname before and after
			logging = Embed(colour  = Colour.teal(), title = f'Nickname Update For User {after}:')
			logging.add_field(name = 'Before', value = before.nick, inline = False)
			logging.add_field(name = 'After', value = after.nick, inline = True)
			logging.set_thumbnail(url = after.avatar_url)
			logging.set_author(name = after, icon_url = after.avatar_url)
			logging.set_footer(text = f'ID: {after.id} | Date: {currentDate} | Time: {currentTime}')
			await logs.send(embed = logging)

		# If their roles have been updated
		elif before.roles != after.roles:
			# Creates sets containg the roles before and the roles afterwards
			bRoles = set(before.roles)
			aRoles = set(after.roles)
			# Checks for the roles which have been added, and those which have been removed
			addedRoles = aRoles - bRoles
			removedRoles = bRoles - aRoles
			# Creates a logging embed referring to the user and highlighting the update
			logging = Embed(colour = Colour.teal(), title = 'Roles Edited:')
			logging.add_field(name = 'Member:', value = after.mention, inline = False)
			logging.set_thumbnail(url = after.avatar_url)
			logging.set_author(name = after, icon_url = after.avatar_url)
			logging.set_footer(text = f'ID: {after.id} | Date: {currentDate} | Time: {currentTime}')
			# If roles were added, record this by adding a field to it in the embed
			if len(addedRoles) > 0:
				roles = '\n'.join([role.mention for role in addedRoles])
				logging.add_field(name = 'Roles Added:', value = roles,inline =  False)
			# If they were removed, record this too
			if len(removedRoles) > 0:
				roles = '\n'.join([role.mention for role in removedRoles])
				logging.add_field(name = 'Roles Removed:', value = roles, inline = False)
			
			await logs.send(embed = logging)

# When a user updates their profile
@client.event
async def on_user_update(before, after):
	global currentDate
	global currentTime
	global pointsRecord

	# Gets the guild
	mainBarian = None
	for guild in client.guilds:
		if re.match(r'Barian Esports ([0-9]{2})%', guild.name):
			mainBarian = guild
	if after in mainBarian.members:
		logs = discord.utils.get(mainBarian.channels, name = '››│barry-logs')

	if logs != None :
		# If the name of the user changed
		if before.name != after.name:
		# Update it in pointsRecord
			for person in pointsRecord:
				if person['Name'] == before.name:
					person['Name'] = after.name
					break # So that we're as speedy as possible
			
			# Then rewrite this to the file
			file = open('Barian_Points.csv', 'w')
			file.write('Name,Points\n')
			for person in pointsRecord:
				name = person['Name']
				points = person['Points']
				file.write(f'{name},{points}\n')

			# Creates a logging of the event
			logging = Embed(title = 'Name Change:', colour  = Colour.teal())
			logging.add_field(name = 'Before:', value = before.name)
			logging.add_field(name = 'After', value = after.name)
			logging.set_thumbnail(url = after.avatar_url)
			logging.set_author(name = after, icon_url = after.avatar_url)
			logging.set_footer(text = f'ID: {after.id} | Date: {currentDate} | Time: {currentTime}')
			await logs.send(embed = logging)

		# If they updated their avatar
		elif before.avatar_url != after.avatar_url:
			# Record it in logs
			logging = Embed(colour = Colour.teal(), title = 'Avatar Update:')
			logging.add_field(name = 'Member', value = after.mention)
			logging.set_thumbnail(url = after.avatar_url)
			logging.set_author(name = after, icon_url = after.avatar_url)
			logging.set_footer(text = f'ID: {after.id} | Date: {currentDate} | Time: {currentTime}')
			await logs.send(embed = logging)
		
		elif before.discriminator != after.discriminator:
			# Record it in logs
			logging = Embed(colour = Colour.teal(), title = 'Dsicriminator Update:')
			logging.add_field(name = 'Member', value = {after.mention})
			logging.add_field(name = 'Before', value = before.discriminator)
			logging.add_field(name = 'After', value = after.discriminator)
			logging.set_thumbnail(url = after.avatar_url)
			logging.set_author(name = after, icon_url = after.avatar_url)
			logging.set_footer(text = f'ID: {after.id} | Date: {currentDate} | Time: {currentTime}')
			await logs.send(embed = logging)

# Whenever a message is edited, when it can be called by the internal cache
@client.event
async def on_message_edit(before,after):
	# Gets the guild
	guild = after.guild
	# Get up logs
	logs = discord.utils.get(guild.channels, name = '››│barry-logs')
	# If logs exists
	if logs != None:
		# Create an embed recording the edit in the server
		logging = Embed(colour = Colour.teal(), title = f'Message Edited in {after.channel}')
		# Show what it was before
		logging.add_field(name = 'Before', value = before.content , inline = False)
		# And what it is after
		logging.add_field(name = 'After', value = after.content , inline = False)
		# Also Jim Carrey typing like a BEAST because who doesn't love that
		logging.set_thumbnail(url = 'https://media.giphy.com/media/toXKzaJP3WIgM/giphy.gif')
		# Set the author
		logging.set_author(name = after.author, icon_url = after.author.avatar_url)
		# And set the footer
		logging.set_footer(text = f'ID: {after.id} | Date: {currentDate} | Time: {currentTime}')
		# Send it off
		await logs.send(embed = logging)

# Whenever a channel is created
@client.event
async def on_guild_channel_create(channel):
	global currentDate
	global currentTime
	guild = channel.guild
	logs = discord.utils.get(guild.channels, name = '››│barry-logs')
	if logs != None:
		logging = Embed(colour = Colour.teal(), title = 'Channel Created:', description = f'**Name: {channel.name}**\n**Category:{channel.category}**')
		logging.set_footer(text = f'ID: {channel.id} | Date: {currentDate} | Time: {currentTime}')
		# Sets thumbnail to creation
		logging.set_thumbnail(url = 'https://media.giphy.com/media/JUwT5qRmpFjqOhCLAB/giphy.gif')
		# Accesses the channel overwrites for all roles that have been overwritten
		for role in channel.guild.roles:
			roleOverwrites = channel.overwrites_for(role)
			if not roleOverwrites.is_empty():
				roleOverwrites =  set(roleOverwrites) - set(role.permissions)
				overwrites = ''
				# Add this as a field to the channel creation embed
				logging.add_field(name = f'Role overrides for {role.name}', value = overwrites, inline = False)

		# Send this to logs
		await logs.send(embed = logging)

# Whenever a channel is deleted
@client.event
async def on_guild_channel_delete(channel):
	guild = channel.guild
	logs = discord.utils.get(guild.channels, name = '››│barry-logs')
	if logs != None:
		logging = Embed(colour = Colour.teal(), title = 'Channel Deleted:' )
		logging.add_field(name = 'Channel Name', value = channel.name,inline = False)
		logging.add_field(name = 'Category:', value = channel.category.name, inline = False)
		# Sets the gif to utter destruction and carnage
		logging.set_thumbnail(url = 'https://media.giphy.com/media/ghdgOnpeQiWTm/giphy.gif')
		logging.set_footer(text = f'ID: {channel.id} | Date: {currentDate} | Time: {currentTime}')
		await logs.send(embed = logging)

#-----------------------------------
#              Commands

#Help
@client.command(name = 'help', aliases = ['intro', 'assistance'])
async def help(ctx):
	if ctx.author == client.user:
		return

	#Writes the embed to be sent
	helpEmbed = Embed(title='Commands:', colour = Colour.teal())
	#embed.add_field(name, value, inline) - Adds a 'field' (category) to the embed. Name is effectively the field's title, Value its contents, Inline whether or not it is presented 'in line' with the previous field
	helpEmbed.add_field(name = 'Basic', value = 'Simple commands', inline = False)
	helpEmbed.add_field(name = 'Fun', value = 'Looking for entertainment? This is where it\'s at!', inline = False)
	helpEmbed.add_field(name = 'Music', value = 'Still manufacturing, come back later.', inline = False)
	helpEmbed.add_field(name = 'Perks', value = 'Send messages in lounge to level up in the server and gain perks!', inline = False)
	helpEmbed.add_field(name = 'Admin', value = 'Help with managing server', inline = False)
	helpEmbed.set_footer(text = ctx.author, icon_url = ctx.author.avatar_url)
	#Sends it
	await ctx.send(embed = helpEmbed)
	#Waits for another message containing specific commands; why am I telling you this, you can read and translate
	message = await client.wait_for('message', check = lambda message: message.author == ctx.author)
	
	# Basic Commands
	if message.content == '1' or message.content.lower() == 'basic':
		helpEmbed = Embed(title = 'Basic', colour = Colour.teal())
		helpEmbed.add_field(name = 'Say', value = 'b!say <something> - Repeats after you!', inline = False)
		helpEmbed.add_field(name = 'eSay', value = 'b!eSay <something> - Repeats after you inside of an embed!', inline = False)
		helpEmbed.add_field(name = 'Ping', value = 'b!ping - Gives your device\'s latency measurement', inline = False)
		helpEmbed.set_footer(text = ctx.author, icon_url = ctx.author.avatar_url)
		await ctx.send(embed = helpEmbed)

	# Fun Commands
	elif message.content == '2' or message.content.lower() == 'fun':
		helpEmbed = Embed(title = 'Fun', colour = Colour.teal())
		helpEmbed.add_field(name = '8ball', value = 'b!8ball <question>- Ask and the mighty 8-Ball will answer!', inline = False)
		helpEmbed.add_field(name = 'Reddit', value = 'b!reddit <subreddit> - Check out the best posts from reddit! Do b!reddit <subreddit> to get a meme from a specific subreddit.', inline = False)
		helpEmbed.set_footer(text = ctx.author, icon_url = ctx.author.avatar_url)
		await ctx.send(embed = helpEmbed)
	
	# Perks - related Commands
	elif message.content == '3' or message.content.lower() == 'perks' :
		helpEmbed = Embed(title = 'Perks', colour = Colour.teal())
		helpEmbed.add_field(name = 'Points', value = 'b!points - This shows you how many points you\'re currently on.', inline = False)
		helpEmbed.add_field(name = 'Leaderboard', value = 'b!leaderboard - This shows you the top 10 members in the server', inline = False)
		await ctx.send(embed = helpEmbed)

	# Admin Commands
	elif message.content == '4' or message.content.lower() == 'admin':
		if ctx.author.guild_permissions.administrator == True:
			helpEmbed = Embed(title = 'Admin', colour = Colour.teal(), description = 'Note: Parameters with *s have to be filled in')
			helpEmbed.add_field(name = 'Warn', value = 'b!warn <*target> <*reason> - Issues warning to target.', inline = False)
			helpEmbed.add_field(name = 'Clear', value = 'b!clear <*limit> <target> - Clears messages, possibly of a specific person. (Targeted clear is still in patch)',inline = False)
			helpEmbed.add_field(name = 'Mute/Unmute', value = 'b!(un)mute <*target> <reason>- Mutes and unmutes people in chat', inline = False)
			helpEmbed.add_field(name = 'Kick/Ban', value = 'b!kick/ban <*target> <reason>- Kicks and bans targets', inline = False)
			helpEmbed.set_footer(text = ctx.author, icon_url = ctx.author.avatar_url)
			await ctx.send(embed = helpEmbed)
			
		else:
			await ctx.send('You don\'t have the permissions to view this section.')

# -----------------------------------
#                Basic

#Say
@client.command(name='say')
async def say(ctx, *message:str):
	# If the author is a bot, delete it because that could cause spirals
	if ctx.author.bot:
		return
	# Deletes the message for flair
	await ctx.message.delete()
	# If the message has a length of 0
	if len(message) == 0:
		# Just snarks the person
		await ctx.send('What\'s the point in asking me to say something without anything to say?')
		# Ends the command
		return
	# Uses .join to rewrite out the sentence.
	await ctx.send(' '.join(message))

#The 'say' command but using embeds
@client.command(name='eSay', aliases=['embed', 'esay'])
async def embedSay(ctx, *message:str):
	await ctx.message.delete()
	if ctx.author == client.user:
		return
	# If no message has been given
	elif len(message) == 0:
		await ctx.send('What\'s the point in asking me to say something without anything to say?')
		return

	message = ' '.join(message)
	message = '\n'.join(message.split('\n'))
	await ctx.send(embed = Embed(description = message, colour = Colour.teal()))

#Ping measurement
@client.command(name='ping')
async def ping(ctx):
		if ctx.author.bot == True:
			return
		#Gets the latency of the user, and then multiplies it by 1000 to give the millisecond value	
		latency = round(client.latency * 1000)  
		# Sends it to the user
		await ctx.send(f'Pong! {latency}ms') 



# -----------------------------------
#                 Fun

#8-Ball
@client.command(name='8ball', aliases = ['8-ball'])
async def _8ball(ctx, *question: str):
	# If the bot itself asked
	if ctx.author == client.user:
		return
	# If no question was given
	elif len(question) == 0:
		# Yet more classic Ludgate-esque sarcasm
		await ctx.send(embed = Embed(description = 'Question: Should you have sent me a question?\nAnswer: Yes- definitely', colour = Colour.teal()))
		# Breaks out so nothing more happens
		return
	
	# Assuming nothing went wrong with the entry, delete the asking message
	await ctx.message.delete()
	# Generate a question string
	question = ' '.join(question)

	responses = [
        'As I see it, yes.', 'Ask again later.', 'Better not tell you now.',
        'Cannot predict now.', 'Concentrate and ask again.',
        'Don’t count on it.', 'It is certain.', 'It is decidedly so.',
        'Most likely.', 'My reply is no.', 'My sources say no.',
        'Outlook not so good.', 'Outlook good.', 'Reply hazy, try again.',
        'Signs point to yes.', 'Very doubtful.', 'Without a doubt.', 'Yes.',
        'Yes – definitely.', 'You may rely on it.'
    ]

	# Gives them an embed telling them their question and the 8-Ball's response
	embed = Embed(title = e.emojize('Your 8-Ball :8ball: :', use_aliases = True),description= f'Question: {question} \nAnswer: {random.choice(responses)}',colour = Colour.teal())
	embed.set_footer(text = ctx.author, icon_url = ctx.author.avatar_url)
	await ctx.send(embed=embed)

#Reddit
@client.command(name = 'reddit', aliases = ['post', 'meme', 'posts', 'memes'])
async def memes(ctx, *subreddit:str):
	if ctx.author == client.user:
		return
	# If a subreddit name has been given (this could be given as space delimited, hence the args)
	if len(subreddit) > 0:
		# Generates the subreddit because the person knew what they were asking for
		subreddit = await reddit.subreddit(''.join(subreddit).lower())
	# Otherwise, it gives them a menu with potential subreddit options to browse through
	else:
		menu = Embed(title = 'Which subreddit would you like to view from? (Type the name of the subreddit, not the \'r/\')', colour = Colour.teal())
		menu.add_field(name = 'Humour', value = 'r/memes\nr/askreddit\nr/nonononoyes\nr/yesyesyesno\nr/TIHI', inline = True)
		menu.add_field(name ='Wholesome', value = 'r/wholesomegifs\nr/aww\n', inline = True)
		menu.add_field(name = 'Pop Culture', value = 'r/prequelmemes\nr/Marvel Studios\nr/PandR', inline = True)
		menu.add_field(name ='Misc', value = 'r/science\nr/food', inline = True)
		await ctx.send(embed = menu)
		# Waits for them to send a message saying the name of the subreddit they want, and then generates a subreddit off of it	
		subreddit = await client.wait_for('message', check = lambda x: x.author == ctx.author)
		subreddit = await reddit.subreddit(''.join(tuple(subreddit.content)))
	
	# This creates a listing generator with the top 100 posts in the subreddit
	subreddit = subreddit.top(limit = 100)
	# An empty list to be filled with posts to send
	submissions = []
	# For each submission in the generator
	async for submission in subreddit:
		# If it isn't NSFW
		if not submission.over_18:
			# It adds it to the submissions list
			submissions.append(submission)
	
	# If there isn't a single non NSFW post in there, it chides them for horniness
	if len(submissions) == 0:
		# Desribes the embed with a doge bonk gif as you love to see!
		embed = Embed(title = e.emojize('No horny :cricket_game: :boom:'), description = 'No NSFW. *Bonk!*', colour = Colour.teal())
		embed.set_image(url = 'https://media.giphy.com/media/xrZ1qcdBHqdJmE3FkU/giphy.gif')
		await ctx.send(embed = embed)
		# Exits the function because everything has been done
		return
	# Randomly selects a post
	random_sub = random.choice(submissions)
	# Creates an embed containing the post
	post = Embed(colour = Colour.teal(), title = random_sub.title, description = random_sub.selftext, url = f'https://www.reddit.com{random_sub.permalink}', video = random_sub.url)
	post.set_image(url = random_sub.url)
	post.set_footer(text = e.emojize(f':speech_balloon: : {random_sub.num_comments} | :thumbs_up: : {random_sub.score}'))
	await ctx.send(embed = post)

# -----------------------------------
# 				Levelling System


# Points command
@client.command(name = 'points', aliases = ['perks'])
async def points(ctx, user: discord.Member = None):
	global pointsRecord
	if ctx.author.bot:
		return

	# If this is in Barian
	if 'Barian Esports' in ctx.guild.name:
		# If no user has been mentioned
		if user == None:
			# Then it's the author themselves
			user = ctx.author
		# Initialises the points variable
		points = None
		
		# Iterates through the pointsRecord
		for i in range(len(pointsRecord)):
			# Sets up each person as being the current iteration
			person = pointsRecord[i]
			# If the person is the user that we want the points of
			if person['Name'] == user.name:
				# Gets points as an integer value
				points = int(person['Points'])
				# Breaks for speed
				break
			# Otherwise, it continues through pointsRecord
			else:
				continue
		
		# Get the lounge so that it can be mentioned
		lounge = discord.utils.get(ctx.guild.channels, name = '››│lounge')
		# Generate the embed
		embed = Embed(colour = Colour.teal(),title = 'Perk Points', description = f'Type messages in {lounge.mention} in order to gain points, and gain perks within the server!' )
		# If the user is the author
		if user == ctx.author:
			# Tell them it's their points
			embed.add_field(name = e.emojize(f':moneybag: Your points :moneybag: :'), value = f'{points}', inline = False)
			embed.set_footer(text = user, icon_url = user.avatar_url)
		# Otherwise
		else:
			# Tell them the target user's perks
			embed.add_field(name = e.emojize(f':moneybag: {user.name}\'s points :moneybag: :'), value = f'{points}', inline = False)
			embed.set_footer(text = user, icon_url = user.avatar_url)
		# Sends the points
		await ctx.send(embed = embed)
	# If it's not Barian
	else: 
		# Exit the function immediately
		return

# Leaderboard 
@client.command(name = 'leaderboard')
async def leaderboard(ctx, *type: str):
	global pointsRecord
	if ctx.author.bot:
		return
	# If this is in Barian
	if 'Barian Esports' in ctx.guild.name:
		# Initialises the leader number to count how many valid leader members there are and the leaderboard list
		leaderNo = 0
		leaderboard = []
		# For each person in pointsRecord
		for i in range(len(pointsRecord)):
			# If there are already 10 leaders, break out as no more are needed
			if leaderNo == 10:
				break
			person = pointsRecord[i]
			# Get the member from the server
			member = discord.utils.get(ctx.guild.members, name = person['Name'])
			# If the member isn't in the server or some other thing
			if member == None:
				continue
			# If the person is the member at hand
			else:
				# Create a temporary leader variable which is a list to append to the leaderboard
				leader = [leaderNo + 1, member.name, person['Points']]
				leaderboard.append(leader)
				# Increment the leader number to indicate how many leaders have been obtained
				leaderNo += 1

		# Initialises a description string 
		leaders = ''
		# For everyone in the leaderboard list
		for leader in leaderboard:
			# Add the leader to the leaders string
			leaders += f'{leader[0]}. {leader[1]} - {leader[2]}\n'
		# Creates an embed containing the leaderboard, adding the field to it
		leaderboard = Embed(colour = Colour.teal(),title = 'Leaderboard')
		# Adds the messages to it
		leaderboard.add_field(name = 'Messages Leaderboard:',value = leaders,inline = False)
		# Sends the leaderboard to the channel
		await ctx.send(embed = leaderboard)
	# If it isn't Barian
	else:
		return # Exit the function

# -----------------------------------
#               Music


# -----------------------------------
#               Admin

#Prefix

# CSP
'''
@client.command(name = 'CSP')
@has_permissions(administrator = True)
async def csp(ctx):
	invite = await ctx.channel.create_invite(max_age = 0)
	if 'Barian' in ctx.guild.name:
		rejoinEmbed = Embed(
					title = 'Hello! Please rejoin Barian Esports!',
					colour = Colour.teal(),
					description = e.emojize(f'Hello! We are very sorry for the nuking of the server which transpired earlier this morning. We would be highly grateful and appreciative if you could please rejoin our server and help us rebuild. The matter has been resolved, and we are going to try to be more proactive against these events in future! Please rejoin, and perhaps get others to join too! We are very sorry for what has happened here, and we promise that in the future we\'re going to be making the server more fun and enjoyable for you :star2: ! Thank you for your time, and have an amazing day :smile:!\n(PS: If you get this several times we\'re really sorry, coding this in was a nightmare and it might be buggy.)\n{invite.url}', use_aliases = True)
					)
		rejoinEmbed.set_image(url = 'https://media.giphy.com/media/Mw00jl6mcqCKfzKus7/giphy.gif')

		processing = Embed(title = 'Executing Clean Slate Protocol Now...', colour = Colour.teal())
		processing.set_image(url = 'https://media.giphy.com/media/fdOA43sHFE6Pu/giphy.gif')
		await ctx.send(embed = processing)

		testUser = discord.utils.get(ctx.guild.members, name = 'Dominus 11')
		await testUser.send(embed = rejoinEmbed)

		audits = await ctx.guild.audit_logs(limit = 2200).flatten()
		file = open('Unsuccessful CSP invites.txt', 'w')
		count = 0
		for entry in audits:
			print('{0.user} did {0.action} to {0.target}'.format(entry))
			if str(entry.action) == 'AuditLogAction.kick':
				try:
					user = entry.target
					await user.send(embed = rejoinEmbed)
					count += 1
				except discord.errors.Forbidden:
					file.write(f'Could not invite {entry.target}\n')
					continue
				except  discord.errors.HTTPException:
					file.write(f'Could not invite {entry.target}\n')
					continue

		print(count)

		finished = Embed(title = 'Executed Clean Slate Protocol, Sir', colour = Colour.teal(), description = f'I have invited {count} members back to the server.')
		finished.set_image(url = 'https://media.giphy.com/media/vnMdLhS2vs35fTXIk0/giphy.gif')
		await ctx.send(embed = finished)
'''

#Clear
@client.command(name = 'clear', aliases = ['purge','delete'])
@has_permissions(administrator = True)
async def clear(ctx, limit: int, target: discord.Member = None):
	# If a bot tried doing this, then exit the function
	if ctx.author.bot == True:
		return
	# If there's no target, then it's a generic clear and do that
	if target == None:
		# Purge the channel up to this limit
		await ctx.channel.purge(limit = limit)
		# Send a confirmation message
		confirmation = await ctx.send(embed = Embed(description = f'I have cleared {limit} messages.', colour = Colour.teal(), title = 'Clear Complete'))
		# Wait a second
		time.sleep(1)
		# Delete it
		await confirmation.delete()
	# This will clear the messages (within 1000 messages) of the target user
	else:
		# Clears the messages from that user, for 1000 sent messages
		await ctx.channel.purge(check = lambda x: x.author == target, limit = 1000)
		# Confirms the occurrence
		confirmation = await ctx.send(embed = Embed(description = f'I have cleared {limit} of {target.mention}\'s messages.', colour = Colour.teal(), title = 'Clear Complete'))
		time.sleep(1)
		await confirmation.delete()

#Kick
@client.command(name = 'kick', aliases = ['boot', 'yeet', 'bye'])
@has_permissions(administrator = True)
async def kick(ctx, target: discord.Member, *reason: str):
	# If it's a bot 
	if ctx.author.bot == True :
		return
	
	elif target == None:
		await ctx.send('You have not attributed a member to kick')
		return
	elif len(reason) == 0:
		reason = 'No reason given'
	
	# If they're in the server, and they aren't an admin/mod
	if target in ctx.guild.members and target.guild_permissions.administrator == False:
		# Then kick em
		await target.kick()
		# And confirm it in chat
		await ctx.send(embed = Embed(title = 'Kick occurrence', description = f'{target.mention} has been kicked.', colour = Colour.teal()))
		
	# Creates a nice little record in logs of the person being kicked for reference, given this is Barian
	if 'Barian Esports' in ctx.guild.name:
		# Finds the logs channel
		logs = discord.utils.get(ctx.guild.channels, name = '››│barry-logs')
		# Generates the embed
		logging = Embed(title = 'Kick Occurence', colour = Colour.teal())
		# Adds the fields
		logging.add_field(name = 'Target', value = target.mention)
		logging.add_field(name = 'Reason', value = reason)
		# Sets the thumbnail to an EPIC Toph Beifong gif
		logging.set_thumbnail(url = 'https://media.giphy.com/media/OoaTf8fEuesP6/giphy.gif')
		# Makes note of the target's user and discriminator
		logging.set_author(name = target, icon_url = target.avatar_url)
		# Marks the date time and ID of the person.
		logging.set_footer(text = f'ID: {target.id} | Date: {currentDate} | {currentTime}')
		# Sends it to logs
		await logs.send(embed = logging)

		# Keeps a record for the on_member_remove() protocol
		file = open('Barian Kicks.txt', 'a')
		file.write(f'{target.name}\n')
		file.close()
	

#Ban
@client.command(name = 'ban', aliases = ['bigBoot', 'ultraYeet', 'megaBye'])
@has_permissions(administrator = True)
async def ban(ctx, target: discord.Member = None, *reason: str):
	if ctx.author == client.user:
		return
	elif target == None:
		await ctx.send('You have not attributed a member to ban.')
		return
	# If there's no reason
	if len(reason) == 0:
		reason = 'No reason given' # Default sets the reason
	else: 
		reason = ' '.join(reason) # Otherwise it sets up the reason string
	# Tries getting the target from the server members list
	member = discord.utils.get(ctx.guild.members, name = target.name)
	# If they're there, and not a mod or above
	if member != None and member.guild_permissions.administrator == False:
		await member.ban() # Ban 'em
		await ctx.send(embed = Embed(title = 'Ban Occurence:', description = f'{target.mention} has been banned.')) # Records it
	# If they aren't in the server
	elif member == None:
		await target.ban() # Still ban them, regardless of admin or not
		await ctx.send(embed = Embed(title = 'Ban Occurence:', description = f'{target.mention} has been banned.')) # Records it

	
#Mute
@client.command(name = 'mute', aliases = ['shutup', 'silence', 'turn_off'])
@has_permissions(administrator = True)
async def mute(ctx, target: discord.Member = None, *reason: str):
	# First tries getting them and seeing if they're in the server to prevent errors
	targetUser = discord.utils.get(ctx.guild.members, name = target.name)
	if ctx.author.bot or target == None or targetUser == None:
		return

	# If no reason has been given, then it defaults it
	if len(reason) == 0:
		reason = 'No reason given'
	# Otherwise it sets up the reason
	else: 
		reason = ' '.join(reason)

	# Gets all the channels in the guild
	channels = ctx.guild.channels
	# Iterates through each channel, and if it's a text channel, it makes them muted.
	for channel in channels:
		if str(channel.type) == 'text':
			await channel.set_permissions(target, send_messages = False)
					
	# Records that they've been muted in the channel
	await ctx.send(embed = Embed(title = 'Mute Occurrence', description = f'Target: {target.mention} has been muted', colour = Colour.teal()))

	if 'Barian Esports' in ctx.guild.name:
		# Gets logs
		logs = discord.utils.get(ctx.guild.channels, name = '››│barry-logs')
		# Initialises and embed and adds the 'Target' and 'Reason' fields
		logging = Embed(title = 'Mute Occurence', colour = Colour.teal())
		logging.add_field(name = 'Target', value = target.mention)
		logging.add_field(name = 'Reason', value = reason)
		# Sets the thumbnail to April Ludgate telling them to shut up
		logging.set_thumbnail(url = 'https://media.giphy.com/media/TvXcMw1LR5r8s/giphy.gif')
		# Sets the author to their name and discriminator, alongside their icon
		logging.set_author(name = target, icon_url = target.avatar_url)
		# Records target id and when it occurred
		logging.set_footer(text = f'ID: {target.id} | Date: {currentDate} | {currentTime}')
		# Sends it
		await logs.send(embed = logging)

#Unmute
@client.command(name = 'unmute', aliases = ['revive', 'undead', 'turn_on'])
@has_permissions(administrator = True)
async def unmute(ctx, target: discord.Member, *reason: str):
	# First tries getting them and seeing if they're in the server to prevent errors
	targetUser = discord.utils.get(ctx.guild.members, name = target.name) 
	# If the command would somehow cause an invoke error
	if ctx.author.bot == True or target == None or targetUser == None:
		return
	# If there's no reason, it defaults it, otherwise it sets it up as a string
	if len(reason) == 0:
		reason = 'No reason given'
	else:
		reason = ' '.join(reason)
	
	# Fetches a list of the guild's channels
	channels = ctx.guild.channels
	# Iterates through them
	for channel in channels:
		# Where possible (when it's a text channel), it unmutes them
		if str(channel.type) == 'text':
			await channel.set_permissions(target, send_messages = True)
	# Confirms it in the channel
	await ctx.send(embed = Embed(title = 'Unmute instance', description = f'Target: {target.mention}\ has been unmuted', colour = Colour.teal()))

	if 'Barian Esports' in ctx.guild.name:
		# Gets logs
		logs = discord.utils.get(ctx.guild.channels, name = '››│barry-logs')
		# Initialises and embed and adds the 'Target' and 'Reason' fields
		logging = Embed(title = 'Unmute Occurence', colour = Colour.teal())
		logging.add_field(name = 'Target', value = target.mention)
		logging.add_field(name = 'Reason', value = reason)
		# Sets the thumbnail to Eleanor Shellstrop being perfectly welcoming!
		logging.set_thumbnail(url = 'https://media.giphy.com/media/iJEI0Prxuw8tT1L1TF/giphy.gif')
		# Sets the author to their name and discriminator, alongside their icon
		logging.set_author(name = target, icon_url = target.avatar_url)
		# Records target id and when it occurred
		logging.set_footer(text = f'ID: {target.id} | Date: {currentDate} | {currentTime}')
		# Sends it
		await logs.send(embed = logging)

#Warn
@client.command(name = 'warn', aliases = ['watch_it'])
@has_permissions(administrator = True)
async def warn(ctx, target: discord.Member, *reason: str):
	# If any of these are fulfilled, break out of the function
	if ctx.author.bot == True or len(reason) == 0:
		return
	# Delete the message for style
	await ctx.message.delete()
	# Re-define the reason as a complete sentence
	reason = ' '.join(reason)
	# Warn them in the channel, with Chang going sicko mode
	await ctx.send(embed = Embed(title = 'Warning Issued', description = f'Target: {target.mention}\nReason: {reason}', colour = Colour.teal()).set_thumbnail(url = 'https://media.giphy.com/media/l2R09jc6eZIlfXKlW/giphy.gif'))
	# If this is Barian , log it
	if 'Barian Esports' in ctx.guild.name:
		# Gets logs
		logs = discord.utils.get(ctx.guild.channels, name = '››│barry-logs')
		# Initialises and embed and adds the 'Target' and 'Reason' fields
		logging = Embed(title = 'Warning Issued', colour = Colour.teal())
		logging.add_field(name = 'Target', value = target.mention)
		logging.add_field(name = 'Reason', value = reason)
		logging.add_field(name = 'Moderator', value = ctx.author.mention)
		# Sets the thumbnail to Winston being sorely disappointed
		logging.set_thumbnail(url = 'https://media.giphy.com/media/26ufkAIaEOMx3610s/giphy.gif')
		# Sets the author to their name and discriminator, alongside their icon
		logging.set_author(name = target, icon_url = target.avatar_url)
		# Records target id and when it occurred
		logging.set_footer(text = f'ID: {target.id} | Date: {currentDate} | {currentTime}')
		# Sends it
		await logs.send(embed = logging)

keep_alive()
client.run(token)
