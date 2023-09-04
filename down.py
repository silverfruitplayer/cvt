import os
from pyrogram import Client, filters, idle
import ffmpeg
import logging
from time import  time
import datetime
from psutil import boot_time
import asyncio
import yt_dlp
import re
import subprocess
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO)

app = Client("down",
            api_id=6,
            api_hash="eb06d4abfb49dc3eeb1aeb98ae0f581e",
            bot_token="6365720098:AAF3oFnfznps-ZrMTjvReLTFKQr5zBO49xE")

# Set the path to the ffmpeg executable
ffmpeg_path = '/path/to/ffmpeg'

ydl_opts_vid = {
    'ffmpeg_location': ffmpeg_path,
    'format': 'best[ext=mp4]/best',
}

ydl_opts_aud = {
    'format': 'm4a/bestaudio/best',
    # ℹ️ See help(yt_dlp.postprocessor) for a list of available Postprocessors and their arguments
    'postprocessors': [{  # Extract audio using ffmpeg
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
    }]
}

active_downloads = {}


@app.on_message(filters.command("start"))
async def start(_, message):
    start = time()
    s_up = datetime.datetime.fromtimestamp(boot_time()).strftime("%Y-%m-%d %H:%M:%S")
    replymsg = await message.reply_text("...")
    end = round(time() - start, 2)
    await replymsg.edit_text(f"Bot is alive!\nPingTime Taken: {end} seconds\nServer up since: {s_up}")
    return   


@app.on_message(filters.command("ban"))
async def start(_, message):
    await message.reply_to_message.chat.ban_member(message.reply_to_message.from_user.id)
    await message.reply("banned")
    return 

@app.on_message(filters.command("unban"))
async def start(_, message):
    await message.reply_to_message.chat.unban_member(message.reply_to_message.from_user.id)
    await message.reply("unbanned")
    return 

@app.on_message(filters.command("purge"))
async def purge(client, message):
    app.set_parse_mode("markdown")
    if message.chat.type not in (("supergroup", "channel")):
        return

    message_ids = []
    count_del_etion_s = 0

    if message.reply_to_message:
        for a_s_message_id in range(
            message.reply_to_message.message_id,
            message.message_id
        ):
            message_ids.append(a_s_message_id)
        if len(message_ids) > 0:
            await client.delete_messages(
                chat_id=message.chat.id,
                message_ids=message_ids,
                revoke=True
            )
            count_del_etion_s += len(message_ids)

    status_message = await message.reply_text(
        f"```Purged!```"
    )
    await asyncio.sleep(5)
    await status_message.delete()
    await message.reply_to_message.delete()

@app.on_message(filters.command("convert") & ~filters.edited)
async def convert_and_send(client, message):
    if message.reply_to_message:
        if message.reply_to_message.text or message.reply_to_message.sticker or message.reply_to_message.animation:
            return await message.reply("**Wtf is this shit.**")
        """
        if message.reply_to_message.video.file_name.endswith('.mp4'):
            await message.reply("**Bitch! Video already in mp4.**")
            return
        """

        if message.reply_to_message.document.file_name.endswith('.mkv'):
            x = await message.reply("**Downloading... Please note that larger file will require longer time to download.**")   
            mkv_path = await message.reply_to_message.download()
            #progress_bar = tqdm(total=os.path.getsize(mkv_path), unit="B", unit_scale=True)
            
            #print(progress_bar)      
            name, _ = os.path.splitext(mkv_path)
            mp4_path = name + ".mp4"
            ffmpeg.input(mkv_path).output(mp4_path, c="copy").run(overwrite_output=True)
            await x.edit("**Waiting for 10s to send video to avoid FloodWait**")
            await asyncio.sleep(10)
            await message.reply_video(mp4_path)  
            await x.delete()          
            os.remove(mkv_path)
            os.remove(mp4_path)
            print("storage cleared")
            return
        else:
            await message.reply("**Wtf is this shit.**")    
    else:
        await message.reply("**Reply to some video Dumbass !!.**")

        
@app.on_message(filters.command("vid"))
async def process_vid_command(client, message):
    if len(message.command) == 2:
        youtube_link = message.command[1]

        try:
            with yt_dlp.YoutubeDL(ydl_opts_vid) as ydl:
                info = ydl.extract_info(youtube_link, download=False)
                video_file = ydl.prepare_filename(info)
                await message.reply_text(f"**Downloading: {info['title']}**")

                ydl.download([youtube_link])  # Download the video

                await client.send_video(message.chat.id, video_file, caption=info['title'])
                os.remove(video_file)
                print("Storage cleared.")
        except Exception as e:
            await message.reply_text(f"Something happened and could not Download that.\n!!Error start!!\n\n{e}\n\n!!Error end!!")
    else:
        await message.reply_text("**Usage: /vid <link>.**")

@app.on_message(filters.command("aud"))
async def process_vid_command(client, message):
    if len(message.command) == 2:
        youtube_link = message.command[1]

        try:
            with yt_dlp.YoutubeDL(ydl_opts_aud) as ydl:
                info = ydl.extract_info(youtube_link, download=False)
                audio_file = ydl.prepare_filename(info)
                ydl.download([youtube_link])
                await message.reply_text(f"**Downloading audio of: {info['title']}**")

            await app.send_audio(message.chat.id, audio_file, caption=info['title'])
            os.remove(audio_file)
            print("storage cleared.")
        except Exception as e:
            await message.reply_text("**Something Happened and was Unable to Download**")
            await message.reply_text(f"!!ERROR START!!\n\n`{e}`\n\n!!ERROR END!!**")
        finally:
            if message.chat.id in active_downloads:
                del active_downloads[message.chat.id]
    else:
        await message.reply_text("**Usage /aud <link>.**")  

@app.on_message(filters.text)
async def handle_message(client, message):
    query = message.text
    try:
        x = await message.reply_text("Downloading...")

        subprocess.run(['yt-dlp', '--extract-audio', '--audio-format', 'mp3', '-o', 'song.%(ext)s', f'ytsearch:{query}'], check=True)

        await x.edit("Uploading...")

        await client.send_audio(message.chat.id, audio="song.mp3", caption=query)
        os.remove("song.mp3")
        print("storage cleared")
        await x.delete()

    except subprocess.CalledProcessError:
        await message.reply_text("Not looking good fam.")


app.start()
idle()
