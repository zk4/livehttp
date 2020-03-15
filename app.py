
#coding: utf-8
from flask import Flask, json, send_from_directory, render_template,Response
import sys
import os
from pathlib import Path
import mimetypes
import datetime
import time
import random
import threading
import logging
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler,FileSystemEventHandler

app = Flask(__name__)
BASE_DIR="/Users/zk/git/jsPrj/webgl/FunWithWebGL2"

ws_clients =[]

changed=False


@app.route('/iffilechange')
def if_file_change():
    global changed
    if changed:
        changed =False
        return "changed"
    else:
        return "still"


@app.route('/', defaults={'req_path': ''})
@app.route('/<path:req_path>')
def dir_listing(req_path):

    # Joining the base and the requested path
    abs_path = os.path.join(BASE_DIR, req_path)

    # Return 404 if path doesn't exist
    if not os.path.exists(abs_path):
        return "no contents"

    # Check if path is a file and serve
    if os.path.isfile(abs_path):
        content = Path(abs_path).read_bytes()
        ext ="."+ os.path.basename(abs_path).split(".")[-1]
        mimetype= ""
        try:
            mimetype = mimetypes.types_map[ext]
        except Exception as e:
            mimetype= "application/octet-stream"

        if abs_path.endswith(".html"):
            ws_code ='''
            <script>
                var xhr = new XMLHttpRequest();
                setInterval(function() {
                    xhr.open("GET", "/iffilechange",true);
                    xhr.onload = function (e) {
                      if (xhr.readyState === 4) {
                        if (xhr.status === 200) {
                          console.log(xhr.responseText);
                          if (xhr.responseText==="changed"){
                                window.location.reload(false);
                          }
                        } else {
                          console.error(xhr.statusText);
                        }
                      }
                    };

                    xhr.onerror = function (e) {
                      console.error(xhr.statusText);
                    };

                    xhr.send(null);

                    }, 1000); //5 seconds

             </script>

            '''.encode("utf-8")
            content+=ws_code

        return Response(content, mimetype=mimetype)



    # Show directory contents
    files = os.listdir(abs_path)
    if req_path is None or req_path == "":
        req_path="/"
    files = [os.path.join(req_path,f) for f  in files]
    return render_template('files.html',prebase=req_path, files=files)


class MyHandler(FileSystemEventHandler):
    """Logs all the events captured."""

    def on_moved(self, event):
        global changed
        changed =True
        
        print("on_moved:",event.src_path)

    def on_created(self, event):
        global changed
        changed =True
        print("on_created:",event.src_path)


    def on_deleted(self, event):
        global changed
        changed =True
        print("on_deleted:",event.src_path)


    def on_modified(self, event):
        global changed
        changed =True
        print("on_modified:",event.src_path)

def watchfile():
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, BASE_DIR, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == '__main__':
    threading.Thread(target=watchfile).start()
    app.run(host="0.0.0.0",debug=True)



