import os
from pyrogram import Client, filters, idle
import ffmpeg
import logging
from time import  time
import datetime
from psutil import boot_time
import asyncio

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO)

app = Client("mf",
            api_id=6,
            api_hash="eb06d4abfb49dc3eeb1aeb98ae0f581e",
            bot_token="6560962385:AAGiDroDw4UZzgXac9wQK4hE2Sc5XchOrEY")

@app.on_message(filters.command("start"))
async def start(_, message):
    start = time()
    s_up = datetime.datetime.fromtimestamp(boot_time()).strftime("%Y-%m-%d %H:%M:%S")
    replymsg = await message.reply_text("...")
    end = round(time() - start, 2)
    await replymsg.edit_text(f"Bot is alive!\nPingTime Taken: {end} seconds\nServer up since: {s_up}")
    return   


@app.on_message(filters.private & filters.document)
async def convert_and_send(client, message):
    if message.document.file_name.endswith('.mkv'):
        mkv_path = await message.download()
        x = await message.reply("Download Started...")
        
        name, _ = os.path.splitext(mkv_path)
        mp4_path = name + ".mp4"
        
        in_stream = ffmpeg.input(mkv_path)
        out_stream = ffmpeg.output(in_stream, mp4_path)
        await out_stream.run(overwrite_output=True)

        await x.edit("Waiting for 10s to send video to avoid FloodWait")
        await asyncio.sleep(5)
        await message.reply_video(mp4_path)
        
        os.remove(mkv_path)
        os.remove(mp4_path)

app.start()
idle()
