"""
Made by Mido.dev
Support me: https://github.com/MidoDev993

Main file. Here you capture and save the data and files obtained.
"""

from mitmproxy import http
from mitmproxy import ctx
from datetime import datetime
from pathlib import Path
#from const import MIMES

import re
import sqlite3
import threading
import browser_interceptor


def remove_chars(text: str) -> str:
    return re.sub(r"[#%&{}\"\\:|<>*?/$!'~@+`=]", "", text)


#VARIABLES----
url = input("#Insert the URL: ")
assert (url != ""), "URL empty"

try:
    dir_files = remove_chars(url)
    dir_files = Path(f"records/{dir_files}/files")
    dir_files.mkdir(exist_ok=True, parents=True) #CREATE A DIRECTORY WHERE ALL THE RECORDS ARE STORED

except Exception as ex:
    print(ex)
    exit()

wait_time = int(input("#Insert recording time. [empty -> no time defined]: ") or 0)
assert wait_time >= 0, "Time cannot be a negative number or a text."

browser_selected = int(input("""
Select a browser:
Empty - Use the system default browser as long as it is in the list.
1 - Chrome
2 - Edge
3 - Firefox
#""") or 0) 
#4 - Safari

assert (browser_selected in list(range(4))), "Please choose a browser from the list"

browser = browser_interceptor.start_browser()
#END------


#DATABASE---
connection_bd = sqlite3.connect(f"{dir_files.parent}/bd.db")
commands = connection_bd.cursor()
commands.executescript("""
CREATE TABLE IF NOT EXISTS "request"(
	"ID" INTEGER PRIMARY KEY AUTOINCREMENT,
    "DATETIME_REQUESTED" TEXT,
	"METHOD" TEXT,
	"URL" TEXT,
	"DOMAIN" TEXT,
	"COOKIES" TEXT,
	"HEADERS" TEXT,
	"JSON" TEXT
);
CREATE TABLE IF NOT EXISTS "response" (
	"ID" INTEGER PRIMARY KEY AUTOINCREMENT,
    "DATETIME_RESPONDED" TEXT,
	"STATUS" TEXT,
	"URL" TEXT,
	"CONTENT_TYPE" TEXT,
	"CONTENT_SAVED_AS" TEXT,
	"HEADERS" TEXT,
	"COOKIES" TEXT,
	"BYTE_LENGTH" INTEGER
);""")
connection_bd.commit()
#END-------------



def request(flow: http.HTTPFlow) -> None:
    time = str(datetime.now())

    try:
        j = str(flow.request.json())

    except Exception as ex:
        j = ""

    try:
        commands.execute("INSERT INTO request (DATETIME_REQUESTED, METHOD, URL, DOMAIN, COOKIES, HEADERS, JSON) VALUES (?,?,?,?,?,?,?);",
                            (
                                time,
                                flow.request.method,
                                flow.request.url,
                                flow.request.pretty_host,
                                str(flow.request.cookies),
                                str(flow.request.headers),
                                j
                            )
                        )

        connection_bd.commit()

    except Exception as ex:
        with open("log.txt", "a") as file:
            file.write(f"[REQUEST][{datetime.now()}]: {ex}\n\n")



n_file = 1
def response(flow: http.HTTPFlow) -> None:
    time = str(datetime.now())
    saved_as = ""

    if flow.response.content:
        global n_file

        ext = remove_chars( Path(flow.request.url).suffix )[0:25]
        if not ext:
            ext = ".bin"

        saved_as = f"{n_file}{ext}"
        n_file += 1
        download_file(saved_as, flow.response.content)


    try:
        commands.execute("INSERT INTO response (DATETIME_RESPONDED,STATUS,URL,CONTENT_TYPE,CONTENT_SAVED_AS,HEADERS,COOKIES,BYTE_LENGTH) VALUES (?,?,?,?,?,?,?,?);",
                            (
                                time,
                                str(flow.response.status_code),
                                flow.request.url,
                                str(flow.response.headers.get("Content-Type")),
                                saved_as,
                                str(flow.response.headers),
                                str(flow.response.cookies),
                                len(flow.response.content)
                            )
                        )
        connection_bd.commit()

    except Exception as ex:
        with open("log.txt", "a") as file:
            file.write(f"[RESPONSE][{datetime.now()}]: {ex}\n\n")



def configure(updated):
    #print(str(updated))
    threading.Thread(target=show_browser).start()



def show_browser() -> None:
    browser.start(proxy_ip=ctx.options.listen_host, proxy_port=ctx.options.listen_port, URL=url, browser=browser_selected)

    if browser.completed:
        ctx.master.shutdown()

    else:
        browser.finish(wait_time)
        ctx.master.shutdown()



def done():
    #build_indexHTML()
    commands.close()
    connection_bd.close()
    print("DONE")



def download_file(filename:str, content) -> None:
    print(f"SAVING FILE [{filename}].....")

    #BY DEFAULT IS SAVED AS BINARY
    #IF THE CONTENT IS PLAIN TEXT CHOOSE "w" MODE
    mode = "wb"
    if isinstance(content, str):
        mode = "w"

    try:
        with open(dir_files.joinpath(filename), mode) as file:
            file.write(content)

    except Exception as ex:
        with open("log.txt", "a") as file:
            file.write(f"[DOWNLOAD FILE][{datetime.now()}]: {ex}\n\n")



def build_indexHTML() -> None:
    print("BUILDING 'index.html'.....")
    
