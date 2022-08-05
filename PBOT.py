####
#   Imports
####

import asyncio
from discord.ext import commands
from discord.utils import get
import discord
import time
import random
from discord.ext.commands import has_permissions, MissingPermissions
intents = discord.Intents.default()
intents.members = True
intents.presences = True
client = commands.Bot(command_prefix='?', intents=intents)


####
#   Client events
####

@client.event
async def on_ready():
    print ("The bot is ready")

####
#   Commands
####

####
#   Server managment commands
####

#Unban commmand
@client.command()
@has_permissions(ban_members=True)
async def unban(ctx, *, member):
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split('#')
    for ban_entry in banned_users:
        user = ban_entry.user
        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f'Unbanned {user.mention}')
            return

#Ban command
@client.command()
@has_permissions(kick_members=True)
async def ban(message, ban_member:discord.Member, *, reason=None):
    if ban_member == client.user: await message.channel.send("You can't ban me :angry:")
    elif ban_member == message.author: await message.send("You can't ban yourself :drool:") 
    elif ban_member.top_role >= message.author.top_role: await message.channel.send("This person's role is higher or equal to yours!")
    else:
        await ban_member.kick(reason=reason)

@ban.error
async def ban_error(message, error):
    if isinstance(error, MissingPermissions):
        await message.send("You don't have permissions to ban this member")

#Kick command
@client.command()
@has_permissions(kick_members=True)
async def kick(message, kick_member:discord.Member, *, reason=None):
    if kick_member == client.user: await message.channel.send("You can't kick me :angry:")
    elif kick_member == message.author: await message.send("You can't kick yourself :drool:") 
    elif kick_member.top_role >= message.author.top_role: await message.channel.send("This person's role is higher or equal to yours!")
    else:
        await kick_member.kick(reason=reason)

@kick.error
async def kick_error(message, error):
    if isinstance(error, MissingPermissions):
        await message.send("You don't have permissions to kick this member")

@client.command()
async def move(ctx, member : discord.Member, channel : discord.VoiceChannel):
    await member.move_to(channel)

#send a private message to the user
@client.command()
async def pv(ctx, member: discord.Member, *, message):
    await member.send(message)
    await member.send(f"Message sent by {ctx.author.name}")
    await ctx.channel.send(f'{member.mention} has received your message')

@client.command()
async def pin(ctx, *, message):
    await ctx.channel.send(message)
    await ctx.message.delete()

@client.command()
async def clear5 (ctx):
    await ctx.channel.purge(limit=5)
    await ctx.channel.send(f'{ctx.author.mention}, the last 5 mensages were clear, dont send messages until this message disapear.')
    time.sleep(3)
    await ctx.channel.purge(limit=1)

@client.command()
async def clear10 (ctx):
    await ctx.channel.purge(limit=10)
    await ctx.channel.send(f'{ctx.author.mention}, the last 10 mensages were clear, dont send messages until this message disapear.')
    time.sleep(3)
    await ctx.channel.purge(limit=1)

@client.command()
async def clearall (ctx):
    await ctx.channel.purge(limit=None)
    await ctx.channel.send(f'{ctx.author.mention}, this channel were cleared, dont send messages until this message disapear.')
    time.sleep(3)
    await ctx.channel.purge(limit=1)

####
#   Trivia game
####

#create a list with the questions and the answers for the trivia
questions = [
    {
        #first question is "What is the capital of Brazil?" and the answer is "Brasilia"
        #the other answers are "Sao Paulo", "Rio de Janeiro", "Brasilia"
        "question": "What is the capital of Brazil?",
        "answers": ["São Paulo", "Brasilia", "Rio de Janeiro", "Salvador"],
        "correct": "Brasilia"
    },
    {
        #second question is "What is the capital of France?" and the answer is "Paris"
        #the other answers are "Paris", "Lyon", "Marseille"
        "question": "What is the capital of France?",
        "answers": [ "Lyon", "Paris", "Marseille", "Nice"],
        "correct": "Paris"
    },
    {
        #third question is "What is the capital of Germany?" and the answer is "Berlin"
        #the other answers are "Berlin", "Munich", "Frankfurt"
        "question": "What is the capital of Germany?",
        "answers": ["Berlin", "Munich", "Frankfurt", "Hamburg"],
        "correct": "Berlin"
    },
    {
        #fourth question is "Which one of these options is not a programming language?" and the answer is "Kentmics"
        #the other answers are "Python", "Java", "Brainfuck"
        "question": "Which one of these options is not a programming language?",
        "answers": ["Python", "Java", "Brainfuck", "Kentmics"],
        "correct": "Kentmics"
    },
]

@client.command()
async def game (ctx):
    #generate a random number between 0 and 3
    random_number = random.randint(0, 3)
    emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣"]
    #create an embed messages with the question and the answers
    embed = discord.Embed(title="Trivia", description=f"{questions[random_number]['question']} \n\r {questions[random_number]['answers'][0]} \n\r {questions[random_number]['answers'][1]} \n\r {questions[random_number]['answers'][2]} \n\r {questions[random_number]['answers'][3]}", color=0x00ff00).set_footer(text="React with the emojis to answer")
    msg = await ctx.channel.send(embed=embed)
    await asyncio.gather(
        *[msg.add_reaction(emoji) for emoji in emojis]
    )
    #wait for the user to react with the emojis
    def check(reaction, user):
        return user == ctx.author and reaction.message.id == msg.id and str(reaction.emoji) in ["1️⃣", "2️⃣", "3️⃣", "4️⃣"]
    try:
        reaction, user = await client.wait_for('reaction_add', timeout=30.0, check=check)
    except asyncio.TimeoutError:
        await msg.delete()
        await ctx.send("Time out")
    #check wath is the emoji the user reacted with
    if str(reaction.emoji) == "1️⃣":
        reacted = questions[random_number]['answers'][0]
    elif str(reaction.emoji) == "2️⃣":
        reacted = questions[random_number]['answers'][1]
    elif str(reaction.emoji) == "3️⃣":
        reacted = questions[random_number]['answers'][2]
    elif str(reaction.emoji) == "4️⃣":
        reacted = questions[random_number]['answers'][3]
    #check if the answer is correct
    if reacted == questions[random_number]['correct']:
        await msg.delete()
        await ctx.send("Correct!")
        await ctx.channel.purge(limit=1)
    else:
        await msg.delete()
        await ctx.send("Wrong!")
        await ctx.channel.purge(limit=1)

####
#   Mini-game
####

@client.command()
async def minigame(ctx):
    bombas = [{1, 3, 5, 7, 9}]
    emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
    msg1 = await ctx.send("The minigame is starting, please wait...")
    await msg1.delete()
    msg2 = await ctx.channel.send(f"Choose a number between 1 and 9, and try to avoid the bombs")
    msg = await ctx.channel.send(":blue_square::blue_square::blue_square::blue_square::blue_square:\n:blue_square:                                        :blue_square:\n:blue_square:                                        :blue_square:\n:blue_square:                                        :blue_square:\n:blue_square::blue_square::blue_square::blue_square::blue_square:")
    await asyncio.gather(
        *[msg.add_reaction(emoji) for emoji in emojis]
    )
    def check(reaction, user):
        return user == ctx.author and reaction.message.id == msg.id and str(reaction.emoji) in ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
    try:
        reaction, user = await client.wait_for('reaction_add', timeout=30.0, check=check)
    except asyncio.TimeoutError:
        await msg.delete()
        await msg1.delete()
        await msg2.delete()
        await ctx.send("Time out")
    #check wath is the emoji the user reacted with
    match (str(reaction)):
        case "1️⃣":
            reaction = 1
        case  "2️⃣":
            reaction = 2
        case  "3️⃣":
            reaction = 3
        case  "4️⃣":
            reaction = 4
        case  "5️⃣":
            reaction = 5
        case  "6️⃣":
            reaction = 6
        case  "7️⃣":
            reaction = 7
        case "8️⃣":
            reaction = 8
        case "9️⃣":
            reaction = 9
    #check if the answer is on the "bombas" array
    for i in range(len(bombas)):
        if reaction in bombas[i]:
            await msg.delete()
            await msg2.delete()
            await ctx.send("You lost!")
            time.sleep(1)
            await ctx.channel.purge(limit=1)
            return
        else:
            await msg.delete()
            await msg2.delete()
            await ctx.send("You won!")
            time.sleep(1)
            await ctx.channel.purge(limit=1)
            return



####
#   Token
####
token = input("Token: ")
client.run(token)
