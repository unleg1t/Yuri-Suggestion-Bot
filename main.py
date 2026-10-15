# -*- coding: utf-8 -*-
"""
Created on Wed Oct 14 09:21:00 2026

@author: ketch
"""

# Imports
import discord, os, asyncio, pyrebase
from flask import Flask
from threading import Thread


# Constants
# Note: For your discord bot token, just add an env var named "DISCORD_BOT_TOKEN" with the value.
# Also, for firebase, you need to add FIREBASE_API_KEY, FIREBASE_AUTH_DOMAIN, FIREBASE_DB_URL AND FIREBASE_STORAGE_BUCKET as env vars.
YURI_CLIENT_ACCENT = '#a152e6'

UNLEGIT_USER_ID = 966584910104129556
YURI_GUILD_ID = 1537350044309782631
SUGGESTIONS_CHANNEL_ID = 1544487981031620698

HELP_DICT = {
    'help': ['`y!help <optional:query>`', '[ADMIN ONLY] Provides a list of all commands available, if the optionary query is provided then it describes the command being queried.'],
    'done': ['`y!done <task-num>`', '[ADMIN ONLY] Marks the task number mentioned, as completed and removes it from the task list.'],
    'remove': ['`y!remove <task-num>`', '[ADMIN ONLY] Removes the task corresponding to the task number mentioned, from the task list.'],
    'list': ['`y!list`', 'Lists all the tasks in an embed list format.'],
    'tasks': ['`y!tasks`', 'Lists all the tasks in an embed list format.'],
    'todos': ['`y!todos`', 'Lists all the tasks in an embed list format.'],
    'suggestions': ['`y!suggestions`', 'Lists all the tasks in an embed list format.'],
    'clear': ['`y!clear`', '[ADMIN ONLY] Clears the entire suggestion list.'],
    'update remove': ['`y!update remove <task-num>`', '[ADMIN ONLY] Removes the task corresponding to the task number mentioned, from the finished/completed tasks list.'],
    'update list': ['`y!update list`', 'Lists all the finished/completed tasks in an embed list format.'],
    'update info': ['`y!update info`', 'Lists all the finished/completed tasks in an embed list format.'],
    'finished': ['`y!finished`', 'Lists all the finished/completed tasks in an embed list format.'],
    'completed': ['`y!completed`', 'Lists all the finished/completed tasks in an embed list format.'],
    'update clear': ['`y!update clear`', '[ADMIN ONLY] Clears the entire finished/completed tasks list.']
}



# Storage Setup
#---------FIREBASE SETUP----------
# Initializes the configurations for the firebase realtime database.
FIREBASE_API_KEY = os.getenv('FIREBASE_API_KEY')
AUTH_DOMAIN, DB_URL, STORAGE_BUCKET = os.getenv('FIREBASE_AUTH_DOMAIN'), os.getenv('FIREBASE_DB_URL'), os.getenv('FIREBASE_STORAGE_BUCKET')

database_config = {
    "apiKey": FIREBASE_API_KEY,
    "authDomain":  AUTH_DOMAIN,
    "databaseURL": DB_URL,
    "storageBucket": STORAGE_BUCKET
}

firebase_client = pyrebase.initialize_app(database_config)
firebase_db_obj = firebase_client.database()

FIREBASE_DB_READY = True

# STORAGE = {}
# storage_dirty = False

def strg_store(key, value) :
    firebase_db_obj.child('storage').child(key).set(value)
    return

def strg_fetch(key) :
    branch = firebase_db_obj.child('storage').child(key).get()
    return (branch.val() if branch != None else None)

def strg_get(key) :
    branch = firebase_db_obj.child('storage').child(key).get()
    return (branch.val() if branch != None else None)

def strg_contains(key) :
    return (key in firebase_db_obj.child('storage').shallow().get())

def strg_remove(key) :
    global storage_dirty
    
    try :
        return firebase_db_obj.child('storage').child(key).remove()
    except :
        return None

def strg_pop(key) :
    global storage_dirty
    
    try :
        return firebase_db_obj.child('storage').child(key).remove()
    except :
        return None

def strg_list_fetch(lname) :
    return (strg_fetch(lname) if strg_contains(lname) else [])

def strg_list_query(func) :
    def wrapper(lname, *args, **kwargs) :
        l = strg_list_fetch(lname)
        return func(l, *args, **kwargs)
    return wrapper

def strg_list_modification(func) :
    def wrapper(lname, *args, **kwargs) :
        l = strg_list_fetch(lname)
        result = func(l, *args, **kwargs)
        strg_store(lname, l.copy())
        return result
    return wrapper

@strg_list_query
def strg_list_get(l, index) :
    return l[index]

@strg_list_query
def strg_list_contains(l, item) :
    return (item in l)

@strg_list_modification
def strg_list_insert(l, index, item) :
    l.insert(index, item)
    return

strg_list_append = lambda lname, item: strg_list_insert(lname, -1, item)

@strg_list_modification
def strg_list_pop(l, index = -1) :
    _v = l.pop(index)
    return _v

@strg_list_modification
def strg_list_clear(l) :
    l.clear()
    return



# Flask Setup
app = Flask(__name__)

@app.route('/')
def home() :
    if strg_get('TODO_TASKS') != None :
        return (
            'whoopsie! you caught us naughty girls having yuri sex >w< oh nuu~' + 
            '<br><hr><br><br>' + 
            '<h3># Yuri-Client Accepted Suggestions</h3>' + 
            '<br>' + 
            ('<br>'.join([f'<br>♡ Task-{i + 1}:</b> {suggestion.title()}' for i, suggestion in enumerate(strg_get('TODO_TASKS'))]) if len(strg_get('TODO_TASKS') or []) > 0 else '<br>-# No new suggestions lodged at the moment.<br><br><br><br>') + 
            '• To remove a task, type y!done <task-num> or y!remove <task-num>' + 
            '<br>' + 
            '• To share a new suggestion, drop it in the suggestions channel, and daddy unlegit will have a look at it.'
        )
    else :
        return 'whoopsie! you caught us naughty girls having yuri sex >w< oh nuu~'

@app.route('/just_monika')
def just_monika() :
    if strg_get('COMPLETED_TASKS') != None :
        return (
            'just monika.' + 
            '<br><hr><br><br>' + 
            '<h3># Yuri-Client Finished/Completed Tasks</h3>' + 
            '<br>' + 
            ('<br>'.join([f'<br>♡ Task-{i + 1}:</b> {completed_task.title()}' for i, completed_task in enumerate(strg_get('COMPLETED_TASKS'))]) if len(strg_get('COMPLETED_TASKS') or []) > 0 else '<br>-# No new finished/completed tasks have been lodged at the moment.<br><br><br><br>') + 
            '• To remove a task, type y!update remove <task-num>'
        )
    else :
        return 'just monika.'

def run_flask() :
    app.run(host = '0.0.0.0', port = 10_000)

def keep_alive() :
    server = Thread(target = run_flask, daemon = True)
    server.start()



# Discord Setup
bot = discord.Client(intents = discord.Intents.all())
yuri_guild, suggestions_channel = None, None

async def send_discord_dm(user_id, user = None, content = None, **kwargs) :
    if user == None: user = bot.get_user(user_id) or (await bot.fetch_user(user_id))
    if user.dm_channel == None :
        await user.create_dm()
    await user.dm_channel.send(content, **kwargs)
    return

def create_todo_embed() :
    todo_embed = discord.Embed(
        title = '# Yuri-Client Accepted Suggestions',
        url = 'https://yuri-suggestion-bot.onrender.com/',
        description = ('\n'.join([f'♡ Task-{i + 1}: {suggestion.title()}' for i, suggestion in enumerate(strg_get('TODO_TASKS'))]) if len(strg_get('TODO_TASKS') or []) > 0 else '_ _\n-# No new suggestions lodged at the moment.\n_ _\n_ _\n_ _\n_ _'),
        color = discord.Colour.from_str(YURI_CLIENT_ACCENT)
    )
    
    todo_embed.set_thumbnail(url = 'https://cdn.discordapp.com/attachments/1537350046863851602/1544105762392117289/logo.png?ex=6acffc8d&is=6aceab0d&hm=46c6fd2a64ed15254c495b343463568ebfe1b45e1ca45e0c8e3c274b94c970fc&')
    todo_embed.set_footer(
        text = '• To remove a task, type y!done <task-num> or y!remove <task-num>\n• To share a new suggestion, drop it in the suggestions channel, and daddy unlegit will have a look at it.',
        icon_url = 'https://sun9-37.vkuserphoto.ru/Xrj_iEhllM2zCVTr-mJkzSTYAWvEsfL1ssZBxA/Tz26Yw2Ruhk.jpg'
    )
    return todo_embed

def create_finished_list_embed() :
    finished_list_embed = discord.Embed(
        title = '# Yuri-Client Finished/Completed Tasks',
        url = 'https://yuri-suggestion-bot.onrender.com/just_monika',
        description = '-# This is a list of tasks that have been marked as finished/completed by daddy unlegit[p.s. he finished inside me~].\n\n' + ('\n'.join([f'♡ Task-{i + 1}: {completed_task.title()}' for i, completed_task in enumerate(strg_get('COMPLETED_TASKS'))]) if len(strg_get('COMPLETED_TASKS') or []) > 0 else '_ _\n-# No new finished/completed tasks have been lodged at the moment.\n_ _\n_ _\n_ _\n_ _'),
        color = discord.Colour.from_str(YURI_CLIENT_ACCENT)
    )
    
    finished_list_embed.set_thumbnail(url = 'https://cdn.discordapp.com/attachments/1537350046863851602/1544105762392117289/logo.png?ex=6acffc8d&is=6aceab0d&hm=46c6fd2a64ed15254c495b343463568ebfe1b45e1ca45e0c8e3c274b94c970fc&')
    finished_list_embed.set_footer(
        text = 'To remove a task, type y!update remove <task-num>',
        icon_url = 'https://sun9-37.vkuserphoto.ru/Xrj_iEhllM2zCVTr-mJkzSTYAWvEsfL1ssZBxA/Tz26Yw2Ruhk.jpg'
    )
    return finished_list_embed

async def update_todo_embed() :
    todo_embed = create_todo_embed()
    
    if strg_contains('TODO_EMBED_MSG_ID') :
        _TODO_EMBED_MSG_ID = strg_get('TODO_EMBED_MSG_ID')
        try :
            todo_embed_msg = await suggestions_channel.fetch_message(_TODO_EMBED_MSG_ID)
            await todo_embed_msg.edit(embed = todo_embed)
            return
        except :
            print('[LOG]: Failed to fetch the pre-existing todo embed message, so creating a new one.')
    else :
        print('[LOG]: Could not find any pre-existing todo embed message, so a new one will be created instead.', flush = True)
    todo_embed_msg = await suggestions_channel.send(content = '', embed = todo_embed)
    strg_store('TODO_EMBED_MSG_ID', todo_embed_msg.id)
    return todo_embed_msg, todo_embed

@bot.event
async def on_ready() :
    global yuri_guild, suggestions_channel
    
    print('[LOG] Getting the girls in bed...', flush = True)
    
    yuri_guild = bot.get_guild(YURI_GUILD_ID) or (await bot.fetch_guild(YURI_GUILD_ID))
    suggestions_channel = bot.get_channel(SUGGESTIONS_CHANNEL_ID) or (await bot.fetch_channel(SUGGESTIONS_CHANNEL_ID))
    
    print('[LOG] Rubbing up their pussies.. massaging the melons~', flush = True)
    
    await update_todo_embed()
    
    print('[LOG] Started having yuri sex~ >w<', flush = True)
    return

@bot.event
async def on_reaction_add(reaction, user) :
    if reaction.emoji == '✅' and user.id == UNLEGIT_USER_ID and reaction.message.channel.id == SUGGESTIONS_CHANNEL_ID :
        strg_list_append('TODO_TASKS', reaction.message.content)
        await update_todo_embed()
        send_discord_dm(reaction.message.author.id, content = f'✅ | Your suggestion for yuri-client(quoted below) has been accepted! You can now see it in the list of other accepted suggestions.\n> {reaction.message.content}')
        await reaction.message.delete()
    if reaction.emoji == '❌' and user.id == UNLEGIT_USER_ID and reaction.message.channel.id == SUGGESTIONS_CHANNEL_ID :
        send_discord_dm(reaction.message.author.id, content = f'❌ | Your suggestion for yuri-client(quoted below) has been rejected!\n> {reaction.message.content}')
        await reaction.message.delete()
    return

@bot.event
async def on_message(message) :
    if message.content in ['y!tasks', 'y!suggestions', 'y!todos', 'y!list'] :
        if (todo_embed_msg_id := strg_get('TODO_EMBED_MSG_ID')) == None :
            todo_embed_msg, todo_embed = update_todo_embed()
            todo_embed_msg_id = todo_embed_msg.id
        else :
            todo_embed = create_todo_embed()
        
        await message.reply(
            content = f'-# **Note:** This is not the primary/main embed, and won\'t update each time that the main task list is updated. For the updated list, check: https://discord.com/channels/{YURI_GUILD_ID}/{SUGGESTIONS_CHANNEL_ID}/{todo_embed_msg_id}', 
            embed = todo_embed
        )
        return
    if message.content in ['y!update list', 'y!update info', 'y!finished', 'y!completed'] :
        await message.reply(
            embed = create_finished_list_embed()
        )
        return
    
    if message.author.id != UNLEGIT_USER_ID: return
    if not message.content.startswith('y!'): return
    
    if message.content.startswith('y!help') :
        query = message.content.lower()[len('y!help') : ].strip()
        if query != '' :
            if query not in HELP_DICT :
                await message.channel.send('The query provided is invalid, there is no such command available!')
            else :
                help_data = HELP_DICT[query]
                embed = discord.Embed(color = discord.Colour.from_str(YURI_CLIENT_ACCENT), title = help_data[0], description = help_data[1])
                await message.channel.send(embed = embed)
        else :
            pagination_emojis: list[str] = ['◀️', '▶️']
            per_page = 6
            queries = list(HELP_DICT.items())
            pages = [queries[i : i + per_page] for i in range(0, len(queries), per_page)]

            embeds = []
            for i, page in enumerate(pages) :
                embed = discord.Embed(color = discord.Colour.from_str(YURI_CLIENT_ACCENT), title = 'Yuri-Help', description = 'Daddy~ I am right here :3 Heres a list of ways in which you can fuck me:')
                for query, query_data in page :
                    name, desc = query_data
                    desc = desc if len(desc) <= 1024 else desc[ : 1024]
                    embed.add_field(name = name, value = desc, inline = False)
                    continue
                embed.set_footer(text = f'Page {i + 1} of {len(pages)}')
                embeds.append(embed)
                continue
            
            curr_page = 0
            msg = await message.channel.send(embed = embeds[curr_page])

            await msg.add_reaction(pagination_emojis[0])
            await msg.add_reaction(pagination_emojis[1])

            def check(reaction, user) :
                return ((user == message.author) and (str(reaction.emoji) in pagination_emojis) and (reaction.message.id == msg.id))

            while True :
                try :
                    reaction_add_task = asyncio.create_task(bot.wait_for('reaction_add', timeout = 60.0, check = check))
                    reaction_remove_task = asyncio.create_task(bot.wait_for('reaction_remove', timeout = 60.0, check = check))
                    
                    done, pending = await asyncio.wait(
                        [
                            reaction_add_task,
                            reaction_remove_task
                        ],
                        return_when = asyncio.FIRST_COMPLETED
                    )
                    
                    for task in pending :
                        task.cancel()
                    
                    reaction, user = done.pop().result()

                    if str(reaction.emoji) == pagination_emojis[1] :
                        curr_page = (curr_page + 1) % len(pages)
                    elif str(reaction.emoji) == pagination_emojis[0] :
                        curr_page = (curr_page - 1) % len(pages)
                    await msg.edit(embed = embeds[curr_page])
                    continue
                except asyncio.TimeoutError :
                    break
            
            await msg.edit(content = '-# This message is now inactive, interacting with it will no longer work. Invoke the command again to interact with it.')
        return
    elif message.content.startswith('y!done ') :
        task_num = message.content[len('y!done ') : ]
        task_list_len = len(strg_get('TODO_TASKS') or [])
        if task_list_len == 0 :
            await message.channel.send('The task list is currently empty.')
            return
        
        if task_num.isdigit() :
            task_num = int(task_num)
            if task_list_len >= task_num > 0 :
                confirmation_view = discord.ui.View(timeout = 5 * 60.0)
                yes_btn = discord.ui.Button(label = 'Yes', style = discord.ButtonStyle.success)
                no_btn = discord.ui.Button(label = 'No', style = discord.ButtonStyle.danger)
                
                async def yes_callback(interaction) :
                    try :
                        strg_list_append('COMPLETED_TASKS', strg_list_pop('TODO_TASKS', task_num - 1))
                        await update_todo_embed()
                        await interaction.message.edit(content = f'Task-{task_num} has been successfully marked as done and removed from the list of suggestions. You can now view it in the list of finished tasks by typing `y!update list`.', view = None)
                        await asyncio.sleep(4)
                        await interaction.message.delete()
                        
                        await message.delete()
                    except Exception :
                        await interaction.message.edit(content = 'Failed to remove the task.', view = None)
                    return
                
                async def no_callback(interaction) :
                    await interaction.message.edit(content = f'Task removal for Task-{task_num} has been cancelled.', view = None)
                    await asyncio.sleep(4)
                    await interaction.message.delete()
                    await message.delete()
                    return
                
                yes_btn.callback = yes_callback
                no_btn.callback = no_callback
                
                confirmation_view.add_item(yes_btn)
                confirmation_view.add_item(no_btn)
                
                await message.channel.send(f'Are you sure you want to remove Task-{task_num} from the pending tasks list and put it into the completed tasks list? Provided below is a transcript of the task:\n> {strg_list_get("TODO_TASKS", task_num - 1)}\n-# Click yes to continue, no to cancel.', view = confirmation_view)
            else :
                await message.channel.send(f'Invalid task number argument has been provided: {task_num}.')
            return
    elif message.content.startswith('y!remove ') :
        task_num = message.content[len('y!remove ') : ]
        task_list_len = len(strg_get('TODO_TASKS') or [])
        if task_list_len == 0 :
            await message.channel.send('The task list is currently empty.')
            return
        
        if task_num.isdigit() :
            task_num = int(task_num)
            if task_list_len >= task_num > 0 :
                confirmation_view = discord.ui.View(timeout = 5 * 60.0)
                yes_btn = discord.ui.Button(label = 'Yes', style = discord.ButtonStyle.success)
                no_btn = discord.ui.Button(label = 'No', style = discord.ButtonStyle.danger)
                
                async def yes_callback(interaction) :
                    try :
                        strg_list_pop('TODO_TASKS', task_num - 1)
                        await update_todo_embed()
                        await interaction.message.edit(content = f'Task-{task_num} has been successfully removed from the list of suggestions.', view = None)
                        await asyncio.sleep(4)
                        await interaction.message.delete()
                        await message.delete()
                    except Exception :
                        await interaction.message.edit(content = 'Failed to remove the task.', view = None)
                    return
                
                async def no_callback(interaction) :
                    await interaction.message.edit(content = f'Task removal for Task-{task_num} has been cancelled.', view = None)
                    await asyncio.sleep(4)
                    await interaction.message.delete()
                    await message.delete()
                    return
                
                yes_btn.callback = yes_callback
                no_btn.callback = no_callback
                
                confirmation_view.add_item(yes_btn)
                confirmation_view.add_item(no_btn)
                
                await message.channel.send(f'Are you sure you want to remove Task-{task_num}? Provided below is a transcript of the task:\n> {strg_list_get("TODO_TASKS", task_num - 1)}\n-# Click yes to continue, no to cancel.', view = confirmation_view)
            else :
                await message.channel.send(f'Invalid task number argument has been provided: {task_num}.')
            return
    elif message.content == 'y!clear' :
        confirmation_view = discord.ui.View(timeout = 5 * 60.0)
        yes_btn = discord.ui.Button(label = 'Yes', style = discord.ButtonStyle.success)
        no_btn = discord.ui.Button(label = 'No', style = discord.ButtonStyle.danger)
        
        async def yes_callback(interaction) :
            try :
                strg_list_clear('TODO_TASKS')
                await update_todo_embed()
                await interaction.message.edit(content = 'Task list has been cleared successfully.', view = None)
                await asyncio.sleep(4)
                await interaction.message.delete()
                await message.delete()
            except Exception :
                await interaction.message.edit(content = 'Failed to clear the task list.', view = None)
            return
        
        async def no_callback(interaction) :
            await interaction.message.edit(content = 'Task list clearance has been cancelled.', view = None)
            await asyncio.sleep(4)
            await interaction.message.delete()
            await message.delete()
            return
        
        yes_btn.callback = yes_callback
        no_btn.callback = no_callback
        
        confirmation_view.add_item(yes_btn)
        confirmation_view.add_item(no_btn)
        
        await message.channel.send('Are you sure you want to clear the task list?\n-# Click yes to continue, no to cancel.', view = confirmation_view)
    elif message.content.startswith('y!update remove ') :
        task_num = message.content[len('y!update remove ') : ]
        task_list_len = len(strg_get('COMPLETED_TASKS') or [])
        if task_list_len == 0 :
            await message.channel.send('The completed tasks list is currently empty.')
            return
        
        if task_num.isdigit() :
            task_num = int(task_num)
            if task_list_len >= task_num > 0 :
                confirmation_view = discord.ui.View(timeout = 5 * 60.0)
                yes_btn = discord.ui.Button(label = 'Yes', style = discord.ButtonStyle.success)
                no_btn = discord.ui.Button(label = 'No', style = discord.ButtonStyle.danger)
                
                async def yes_callback(interaction) :
                    try :
                        strg_list_pop('COMPLETED_TASKS', task_num - 1)
                        await interaction.message.edit(content = f'Task-{task_num} has been successfully removed from the list of finished/completed tasks.', view = None)
                        await asyncio.sleep(4)
                        await interaction.message.delete()
                        await message.delete()
                    except Exception :
                        await interaction.message.edit(content = 'Failed to remove the task.', view = None)
                    return
                
                async def no_callback(interaction) :
                    await interaction.message.edit(content = f'Task removal for Task-{task_num} has been cancelled.', view = None)
                    await asyncio.sleep(4)
                    await interaction.message.delete()
                    await message.delete()
                    return
                
                yes_btn.callback = yes_callback
                no_btn.callback = no_callback
                
                confirmation_view.add_item(yes_btn)
                confirmation_view.add_item(no_btn)
                
                await message.channel.send(f'Are you sure you want to remove Task-{task_num} from the finished/completed tasks list? Provided below is a transcript of the task:\n> {strg_list_get("COMPLETED_TASKS", task_num - 1)}\n-# Click yes to continue, no to cancel.', view = confirmation_view)
            else :
                await message.channel.send(f'Invalid task number argument has been provided: {task_num}.')
            return
    elif message.content == 'y!update clear' :
        confirmation_view = discord.ui.View(timeout = 5 * 60.0)
        yes_btn = discord.ui.Button(label = 'Yes', style = discord.ButtonStyle.success)
        no_btn = discord.ui.Button(label = 'No', style = discord.ButtonStyle.danger)
        
        async def yes_callback(interaction) :
            try :
                strg_list_clear('COMPLETED_TASKS')
                await update_todo_embed()
                await interaction.message.edit(content = 'The Finished/Completed Tasks list has been cleared successfully.', view = None)
                await asyncio.sleep(4)
                await interaction.message.delete()
                await message.delete()
            except Exception :
                await interaction.message.edit(content = 'Failed to clear the finished/completed tasks list.', view = None)
            return
        
        async def no_callback(interaction) :
            await interaction.message.edit(content = 'Task list clearance has been cancelled.', view = None)
            await asyncio.sleep(4)
            await interaction.message.delete()
            await message.delete()
            return
        
        yes_btn.callback = yes_callback
        no_btn.callback = no_callback
        
        confirmation_view.add_item(yes_btn)
        confirmation_view.add_item(no_btn)
        
        await message.channel.send('Are you sure you want to clear the finished/completed tasks list?\n-# Click yes to continue, no to cancel.', view = confirmation_view)
    return


# Execution of yuri sex~
if __name__ == '__main__' :
    BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    
    keep_alive()
    bot.run(BOT_TOKEN)
