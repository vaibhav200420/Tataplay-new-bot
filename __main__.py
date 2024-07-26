import os
from pyrogram import filters, idle, Client
from bot.config import TG_CONFIG
from bot.config import token_file, client_secrets_json
from bot.helpers.utils import find_auth_code
from bot.config import gauth
from bot.config import START_MSG
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pydrive2 import auth
from bot.services.tplay.api import TPLAY_API
from bot.helpers.utils import post_to_telegraph
import datetime

app = Client(
    TG_CONFIG.session,
    bot_token=TG_CONFIG.bot_token,
    api_id=TG_CONFIG.api_id,
    api_hash=TG_CONFIG.api_hash,
    sleep_threshold=30
)

@app.on_message(filters.chat(TG_CONFIG.sudo_users) & filters.command('gdrive'))
async def gdrive_helper(_, message):
    if len(message.text.split()) == 1:

        if not os.path.exists(client_secrets_json):
            await message.reply(
            "<b>No Client Secrets JSON File Found!</b>",
        )
            return

        
        if not os.path.exists(token_file):
            try:
                authurl = gauth.GetAuthUrl().replace("online", "offline")
            except auth.AuthenticationError:
                await message.reply(
                    '<b>Wrong Credentials!</b>',
                )
                return
            
            text = (
                '<b>Login In To Google Drive</b>\n<b>Send</b>`/gdrive [verification_code]`'
            )
            await message.reply(text, reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("🔗 Log In URL", url=f"{authurl}")
                    ]
                ]
            ))
            return
        await message.reply(
            "<b>You're already logged in!\nTo logout type</b><code>/gdrive logout</code>",
        )
    #/gdrive logout
    elif len(message.text.split()) == 2 and message.text.split()[1] == 'logout':
        os.remove(token_file)
        await message.reply(
            '<b>You have logged out of your account!</b>',
        )
    #/gdrive [verification_code]
    elif len(message.text.split()) == 2:
        gauth.LoadCredentialsFile(token_file)
        try:
            if "localhost" in message.text.split()[1]:
                gauth.Auth(find_auth_code(message.text.split()[1]))
            else:
                gauth.Auth(message.text.split()[1])

        except auth.AuthenticationError:
            await message.reply('<b>Your Authentication code is Wrong!</b>')
            return
        gauth.SaveCredentialsFile(token_file)
        await message.reply(
            '<b>Authentication successful!</b>',
        )
    else:
        await message.reply('<b>Invaild args!</b>\nCheck <code>/gdrive</code> for usage guide')

@app.on_message(filters.chat(TG_CONFIG.sudo_users) & filters.incoming & filters.command(['webdl']) & filters.text)
def webdl_cmd_handler(app, message):
    if len(message.text.split(" ")) <= 2:
        message.reply_text(
            "<b>Syntax: </b>`/webdl -c [CHANNEL SLUG] [OTHER ARGUMENTS]`")
        return
    
    command = message.text.replace("/webdl", "").strip()
    if "-c" in command:
        from bot.services.tplay.main import TPLAY
        downloader = TPLAY(command, app, message)
        downloader.start_process()



@app.on_message(filters.incoming & filters.command(['start']) & filters.text)
def start_cmd_handler(app, message):
    code = "Access Denied" if message.from_user.id not in TG_CONFIG.sudo_users else "Welcome Admin"
    message.reply_text(START_MSG.format(message.from_user.username, code))


async def main():
    await app.start()
    await idle()
    await app.stop()

if __name__ == "__main__":
    app.loop.run_until_complete(main())
