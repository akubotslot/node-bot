import telebot
import yt_dlp
import time
import os
from googleapiclient.discovery import build
from telebot import types

BOT_TOKEN = '7738342100:AAEQNlXm5W4dYTnVISmSbP25QhkK1I14D7E'  # Replace with your bot token
YOUTUBE_API_KEY = 'AIzaSyCCuICozmuvB8gLtBDmpGtdX7cLJ1V2SE4'
bot = telebot.TeleBot(BOT_TOKEN)
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

# Menyimpan hasil pencarian dalam konteks
search_results = {}

@bot.message_handler(commands=['sendfile'])
def send_file_to_user(message):
    chat_id = message.chat.id
    file_path = '1.jpg'  # Path to the file you want to send

    if os.path.exists(file_path):  # Check if the file exists
        try:
            with open(file_path, 'rb') as file:
                bot.send_document(chat_id, file, caption="Here is the file you requested!")
            bot.reply_to(message, "File sent successfully!")
        except Exception as e:
            bot.reply_to(message, f"Error sending file: {e}")
    else:
        bot.reply_to(message, "The requested file does not exist.")


@bot.message_handler(commands=['downloadmp3'])
def download_audio(message):
    # Pastikan ada argumen setelah perintah
    if len(message.text.split()) < 2:
        bot.reply_to(message, "Silakan sertakan tautan video YouTube setelah perintah /downloadmp3.")
        return

    try:
        # Ambil tautan video dari pesan
        video_url = message.text.split(' ', 1)[1]  # Ambil semua teks setelah perintah
        # Opsi untuk yt-dlp
        ydl_opts = {'format': 'bestaudio/best', 'outtmpl': '%(id)s.%(ext)s'}

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)
            audio_file = ydl.prepare_filename(info_dict)
            bot.reply_to(message, "Downloading your music...")
            ydl.download([video_url])

        # Dapatkan judul video
        title = info_dict.get('title', 'Unknown')
        # Ganti spasi dengan garis bawah di judul
        title = title.replace(' ', '_')
        # Buat nama file baru
        new_filename = f"{title}.mp3"
        # Ganti nama file yang diunduh
        os.rename(audio_file, new_filename)

        # Kirim file audio sebagai dokumen ke pengguna dengan fitur reply
        with open(new_filename, 'rb') as audio:
            bot.send_document(message.chat.id, audio, reply_to_message_id=message.message_id, caption="Download Successful!")

        # Hapus file setelah delay
        time.sleep(3)  # Tunggu 3 detik
        os.remove(new_filename)  # Hapus file yang diunduh

    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

@bot.message_handler(commands=['downloadmp4'])
def download_video(message):
    if len(message.text.split()) < 2:
        bot.reply_to(message, "Silakan sertakan tautan video YouTube setelah perintah /downloadmp4.")
        return

    try:
        video_url = message.text.split(' ', 1)[1]
        ydl_opts = {'format': 'bestvideo+bestaudio/best', 'outtmpl': '%(id)s.%(ext)s'}

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)
            video_file = ydl.prepare_filename(info_dict)
            bot.reply_to(message, "Downloading your video...")
            ydl.download([video_url])

        title = info_dict.get('title', 'Unknown').replace(' ', '_')
        new_filename = f"{title}.mp4"
        os.rename(video_file, new_filename)

        with open(new_filename, 'rb') as video:
            bot.send_video(message.chat.id, video, reply_to_message_id=message.message_id, caption="Download Successful!")

        time.sleep(3)
        os.remove(new_filename)

    except Exception as e:
        bot.reply_to(message, f"Error: {e}")


@bot.message_handler(commands=['search'])
def search_youtube(message):
    query = message.text.split(' ', 1)
    if len(query) < 2:
        bot.reply_to(message, "Silakan masukkan judul lagu setelah perintah /search.")
        return

    search_query = query[1]
    request = youtube.search().list(q=search_query, part='id,snippet', type='video', maxResults=10)
    response = request.execute()

    # Simpan hasil pencarian
    search_results[message.chat.id] = {}

    keyboard = types.InlineKeyboardMarkup()
    for i, item in enumerate(response['items']):
        video_id = item['id']['videoId']
        title = item['snippet']['title']
        search_results[message.chat.id][i] = video_id  # Simpan ID video
        keyboard.add(types.InlineKeyboardButton(text=title, callback_data=f"select_video_{i}"))

    bot.send_message(message.chat.id, "Hasil pencarian:", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith('select_video_'))
def select_video(call):
    index = int(call.data.split('_')[2])
    video_id = search_results[call.message.chat.id][index]
    video_url = f"https://www.youtube.com/watch?v={video_id}"

    # Kirim InlineKeyboardMarkup untuk opsi download
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(text="Download MP3", callback_data=f"download_mp3_{video_id}"),
        types.InlineKeyboardButton(text="Download MP4", callback_data=f"download_mp4_{video_id}")
    )
    bot.send_message(call.message.chat.id, f"Video yang Anda pilih: {video_url}", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith('download_mp3_') or call.data.startswith('download_mp4_'))
def download_format(call):
    # Pisahkan format dan video ID dari callback_data
    data = call.data.split('_')
    format_type = data[1]  # 'mp3' atau 'mp4'
    video_id = data[2]
    video_url = f"https://www.youtube.com/watch?v={video_id}"

    if format_type == "mp3":
        # Unduh MP3
        try:
            ydl_opts = {'format': 'bestaudio/best', 'outtmpl': '%(id)s.%(ext)s'}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(video_url, download=False)
                audio_file = ydl.prepare_filename(info_dict)
                bot.send_message(call.message.chat.id, "Downloading MP3...")
                ydl.download([video_url])

            title = info_dict.get('title', 'Unknown').replace(' ', '_')
            new_filename = f"{title}.mp3"
            os.rename(audio_file, new_filename)

            with open(new_filename, 'rb') as audio:
                bot.send_document(call.message.chat.id, audio, caption="Download MP3 Successful!")
            os.remove(new_filename)

        except Exception as e:
            bot.send_message(call.message.chat.id, f"Error downloading MP3: {e}")

    elif format_type == "mp4":
        # Unduh MP4
        try:
            ydl_opts = {
                'format': 'bestvideo[height<=720]+bestaudio/best',  # Resolusi maksimum 720p
                'outtmpl': '%(id)s.%(ext)s',
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',  # Konversi ke MP4
                }],
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(video_url, download=False)
                video_file = ydl.prepare_filename(info_dict)
                bot.send_message(call.message.chat.id, "Downloading MP4...")
                ydl.download([video_url])

            title = info_dict.get('title', 'Unknown').replace(' ', '_')
            new_filename = f"{title}.mp4"
            os.rename(video_file, new_filename)

            with open(new_filename, 'rb') as video:
                bot.send_video(call.message.chat.id, video, caption="Download MP4 Successful!")
            os.remove(new_filename)

        except Exception as e:
            bot.send_message(call.message.chat.id, f"Error downloading MP4: {e}")

bot.polling()