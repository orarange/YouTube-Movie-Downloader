from yt_dlp import YoutubeDL
import os
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk
import threading
import time
from PIL import Image, ImageTk
import requests
from io import BytesIO

user = os.getlogin()
root = Tk()
file_type_menu = None
download_button = None
thumbnail_label = None
title_label = None
fetching_info = False

def show_downloading_window():
    download_window = Toplevel(root)
    download_window.title("Downloading")
    download_window.overrideredirect(True)
    
    root.update_idletasks()
    main_width = root.winfo_width()
    main_height = root.winfo_height()
    main_x = root.winfo_x()
    main_y = root.winfo_y()
    
    download_window.geometry(f"200x100+{main_x + main_width // 2 - 100}+{main_y + main_height // 2 - 50}")
    
    label = Label(download_window, text="Now downloading")
    label.pack(expand=True)
    
    def update_label():
        while True:
            for i in range(1, 5):
                if not label.winfo_exists():
                    return
                label.config(text=f"Now downloading{'.' * i}")
                time.sleep(0.5)
    
    threading.Thread(target=update_label, daemon=True).start()
    return download_window

def download_video():
    url = url_entry.get()
    save_dir = save_dir_entry.get()
    
    selected_type = file_type_menu.get()
    match selected_type:
        case 'MP4':
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'outtmpl': f'{save_dir}/%(title)s.%(ext)s',
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': ['ja'],
                'subtitlesformat': 'best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec':'mp4',
                    'preferredquality': '192',
                }]
            }
        case 'M4A':
            ydl_opts = {
                'format': 'bestaudio[ext=m4a]/best[ext=m4a]',
                'outtmpl': f'{save_dir}/%(title)s.%(ext)s',
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': ['ja'],
                'subtitlesformat': 'best',
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'm4a',
                }]
            }
        case 'vorbis':
            ydl_opts = {
                'format': 'bestaudio[ext=webm]/best[ext=webm]',
                'outtmpl': f'{save_dir}/%(title)s.%(ext)s',
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': ['ja'],
                'subtitlesformat': 'best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec':'vorbis',
                    'preferredquality': '192',
                }]
            }
        case 'opus':
            ydl_opts = {
                'format': 'bestaudio[ext=webm]/best[ext=webm]',
                'outtmpl': f'{save_dir}/%(title)s.%(ext)s',
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': ['ja'],
                'subtitlesformat': 'best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec':'opus',
                    'preferredquality': '192',
                }]
            }
        case _:
            messagebox.showerror('エラー', '拡張子を選択してください')
            return
    
    download_window = show_downloading_window()
    
    def download():
        with YoutubeDL(ydl_opts) as ydl:        
            try:
                ydl.download([url])
            except Exception as e:
                download_window.destroy()
                messagebox.showerror('エラー', f'ダウンロードに失敗しました: {str(e)}')
                return
            
            print('ダウンロード完了しました')
            download_window.destroy()
            messagebox.showinfo('ダウンロード完了', 'ダウンロードが完了しました')
    threading.Thread(target=download).start()

def select_save_dir():
    save_dir = filedialog.askdirectory()
    if save_dir == '':
        return
    save_dir_entry.delete(0, END)
    save_dir_entry.insert(0, save_dir)

def create_label(root, text):
    label = Label(root, text=text)
    label.pack()
    return label

def create_entry(root, width, initial_text=None):
    entry = Entry(root, width=width)
    if initial_text:
        entry.insert(0, initial_text)
    entry.pack()
    return entry

def create_button(root, text, command):
    button = Button(root, text=text, command=command)
    button.pack()
    return button

def create_combobox(root, width, values):
    combobox = ttk.Combobox(root, width=width, state="readonly")
    combobox['values'] = values
    combobox.pack()
    return combobox

def on_url_entry_change(*args):
    global fetching_info
    if url_entry.get() and not fetching_info:
        fetching_info = True
        if not file_type_menu:
            threading.Thread(target=create_file_type_menu).start()
        threading.Thread(target=fetch_video_info).start()

def fetch_video_info():
    global thumbnail_label, title_label, fetching_info
    url = url_entry.get()
    if not url:
        fetching_info = False
        return
    
    if file_type_menu:
        file_type_menu.config(state='disabled')
    
    ydl_opts = {'quiet': True, 'skip_download': True}
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        title = info.get('title', 'No title')
        thumbnail_url = info.get('thumbnail', None)
        
        if title_label:
            title_label.destroy()
        title_label = create_label(root, f"Title: {title}")
        title_label.pack(after=url_entry)
        
        if thumbnail_url:
            response = requests.get(thumbnail_url)
            img_data = response.content
            img = Image.open(BytesIO(img_data))
            img = img.resize((200, 150), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            if thumbnail_label:
                thumbnail_label.config(image=photo)
                thumbnail_label.image = photo
            else:
                thumbnail_label = Label(root, image=photo)
                thumbnail_label.image = photo
                thumbnail_label.pack(after=title_label)
    
    if file_type_menu:
        file_type_menu.config(state='readonly')
    
    fetching_info = False

def create_file_type_menu():
    global file_type_menu, download_button
    create_label(root, 'ファイルタイプ')
    file_type_menu = create_combobox(root, 50, ('MP4', 'M4A', 'vorbis', 'opus'))
    download_button = create_button(root, 'ダウンロード', download_video)

root.title('YouTubeダウンローダー')

create_label(root, 'URL')
url_entry = create_entry(root, 50)
url_entry.bind("<KeyRelease>", on_url_entry_change)

create_label(root, 'ダウンロード先ディレクトリ')
save_dir_entry = create_entry(root, 50, f'C:/Users/{user}/Videos')

create_button(root, 'ダウンロード先ディレクトリを選択', select_save_dir)

root.iconbitmap('youtube.ico')
root.geometry('500x375')

root.mainloop()