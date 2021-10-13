import re
import time
import asyncio

from pyrogram import Client, filters
from pyrogram.errors import FloodWait, UserNotParticipant
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from . import (
    FIND,
    admin_list,
    Database,
    ACTIVE_CHATS,
    CHAT_DETAILS,
    INVITE_LINK,
    remove_emoji,
    time_formatter,
    gen_invite_links,
)

db = Database()


@Client.on_callback_query(filters.regex(r"config\((.+)\)"), group=2)
async def cb_config(bot, update: CallbackQuery):
    """
    A Callback Funtion For Chaning The Number Of Total Pages / 
    Total Results / Results Per pages / Enable or Diable Invite Link /
    Enable or Disable PM File Chat
    """
    global CHAT_DETAILS
    query_data = update.data
    chat_id = update.message.chat.id
    chat_name = remove_emoji(update.message.chat.title)
    user_id = update.from_user.id
    
    chat_dict = CHAT_DETAILS.get(str(chat_id))
    chat_admins = chat_dict.get("admins") if chat_dict != None else None

    if ( chat_dict or chat_admins ) == None: # Make Admin's ID List
        chat_admins = await admin_list(chat_id, bot, update)

    if user_id not in chat_admins:
        return

    chat_id = re.findall(r"config\((.+)\)", query_data)[0]
    
    settings = await db.find_chat(int(chat_id))
    
    mp_count = settings["configs"]["max_pages"]
    mf_count = settings["configs"]["max_results"]
    mr_count = settings["configs"]["max_per_page"]
    show_invite = settings["configs"]["show_invite_link"]
    pm_file_chat  = settings["configs"].get("pm_fchat", False)
    accuracy_point = settings["configs"].get("accuracy", 0.80)
    
    text=f"<i><b>Configurez votre <u><code>{chat_name}</code></u> Paramètres de filtre du groupe...</b></i>\n"
    
    text+=f"\n<i>{chat_name}</i> Current Settings:\n"

    text+=f"\n - Filtre maximum: <code>{mf_count}</code>\n"
    
    text+=f"\n - Nombre maximal de pages: <code>{mp_count}</code>\n"
    
    text+=f"\n - Filtre maximum par page: <code>{mr_count}</code>\n"

    text+=f"\n - Pourcentage de précision: <code>{accuracy_point}</code>\n"
    
    text+=f"\n - Afficher le lien d'invitation: <code>{show_invite}</code>\n"
    
    text+=f"\n - Fournir un fichier dans katnice en Privée: <code>{pm_file_chat}</code>\n"
    
    text+="\nAjuster la valeur au-dessus à l'aide des boutons ci-dessous... "
    buttons=[
        [
            InlineKeyboardButton
                (
                    "Filtrer par page", callback_data=f"mr_count({mr_count}|{chat_id})"
                ), 
    
            InlineKeyboardButton
                (
                    "Nombre maximum de pages",       callback_data=f"mp_count({mp_count}|{chat_id})"
                )
        ]
    ]


    buttons.append(
        [
            InlineKeyboardButton
                (
                    "Nombre total de filtres", callback_data=f"mf_count({mf_count}|{chat_id})"
                )
        ]
    )


    buttons.append(
        [                
             InlineKeyboardButton
                (
                    "Afficher les liens d'invitation", callback_data=f"show_invites({show_invite}|{chat_id})"
                ),

            InlineKeyboardButton
                (
                    "Fichier de Chat du bot", callback_data=f"inPM({pm_file_chat}|{chat_id})"
                )
        ]
    )


    buttons.append(
        [
            InlineKeyboardButton
                (
                    "Précision du résultat", callback_data=f"accuracy({accuracy_point}|{chat_id})"
                )
        ]
    )


    buttons.append(
        [
            InlineKeyboardButton
                (
                    "🔙 Retour", callback_data=f"settings"
                )
        ]
    )
    
    
    reply_markup=InlineKeyboardMarkup(buttons)
    
    await update.message.edit_text(
        text, 
        reply_markup=reply_markup, 
        parse_mode="html"
    )


