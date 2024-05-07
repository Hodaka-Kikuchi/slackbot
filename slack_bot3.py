import os
import tkinter as tk
from tkinter import ttk, filedialog
import requests
import json
import time

# 送信中フラグ
sending_flag = False
last_modification_time = None

def send_slack_message(webhook_url, message):
    headers = {'Content-Type': 'application/json'}
    payload = {'text': message}
    response = requests.post(webhook_url, headers=headers, data=json.dumps(payload))
    if response.status_code != 200:
        sending_status_label.config(text="Failed to send message.")
    else:
        sending_status_label.config(text="Message sent successfully.")
        pass

def select_file():
    file_path = filedialog.askopenfilename()
    file_path_entry.delete(0, tk.END)
    file_path_entry.insert(0, file_path)

def start_sending():
    global sending_flag
    sending_status_label.config(text="Sending messages started.")
    webhook_url = webhook_url_entry.get()
    file_path = file_path_entry.get()
    
    # 送信フラグをTrueに設定
    sending_flag = True
    
    # 新しいスレッドでメッセージ送信を開始
    import threading
    threading.Thread(target=send_message, args=(webhook_url, file_path)).start()
    
    # startボタンを無効にする
    start_button.config(state='disabled')
    progress_bar.start()

def send_message(webhook_url, file_path):
    global sending_flag, last_modification_time
    while sending_flag:
        try:
            modification_time = os.path.getmtime(file_path)
            if modification_time != last_modification_time:
                with open(file_path, 'r') as file:
                    last_line = file.readlines()[-1]
                    send_slack_message(webhook_url, last_line)
                    last_modification_time = modification_time
        except FileNotFoundError:  # ファイルが見つからない場合のエラー処理
            print("File not found.")
        except IndexError:  # ファイルが空の場合のエラー処理
            print("File is empty.")
        except Exception as e:  # その他のエラー処理
            print(f"Error: {e}")
        time.sleep(1)
    
    # startボタンを有効にする
    start_button.config(state='normal')
    progress_bar.stop()

def stop_sending():
    global sending_flag
    sending_flag = False  # 送信フラグをFalseに設定
    sending_status_label.config(text="Sending messages stopped.")
    progress_bar.stop()

root = tk.Tk()
root.title("Slack Message Sender")
root.geometry("400x250")  # ウィンドウの幅と高さを設定

# Webhook URL入力用エントリー
webhook_url_label = ttk.Label(root, text="Webhook URL:")
webhook_url_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")


webhook_url_entry = ttk.Entry(root, width=45)
webhook_url_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

# ファイル選択ボタン
select_file_button = ttk.Button(root, text="Select txt file", command=select_file)
select_file_button.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

file_path_entry = ttk.Entry(root)
file_path_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

# 開始・停止ボタン
stop_button = ttk.Button(root, text="Stop", command=stop_sending)
stop_button.grid(row=3, column=0, padx=5, pady=5, sticky="ew")

start_button = ttk.Button(root, text="Start", command=start_sending)
start_button.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

# 送信ステータス表示用ラベル
sending_status_label = ttk.Label(root, text="")
sending_status_label.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

# プログレスバー
progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="indeterminate")
progress_bar.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

root.mainloop()
# pyinstaller -F --noconsole  --icon=asyura_logo3.ico slack_bot3.py