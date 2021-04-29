#coding: utf-8
from .logx import setup_logging
import logging
import argparse
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
from flask_cors import CORS

setup_logging()
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)
cors = CORS(app, resource={
    r"/*":{
        "origins":"*"
    }
})

BASE_DIR="."

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

                    }, 1000); 

             </script>

            '''.encode("utf-8")
            content+=ws_code

        return Response(content, mimetype=mimetype)



    # Show directory contents
    files = os.listdir(abs_path)
    if req_path is None or req_path == "":
        req_path="/"
    files = [f+"/" if os.path.isdir(os.path.join(abs_path, f)) else f for f  in files]
    return render_template('files.html',header=abs_path, files=files)


class MyHandler(FileSystemEventHandler):
    """Logs all the events captured."""

    def on_moved(self, event):
        global changed
        changed =True
        
        logger.info("on_moved:" +event.src_path)

    def on_created(self, event):
        global changed
        changed =True
        logger.info("on_created:" +event.src_path)


    def on_deleted(self, event):
        global changed
        changed =True
        logger.info("on_deleted:" +event.src_path)


    def on_modified(self, event):
        global changed
        changed =True
        logger.info("on_modified:" +event.src_path)

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


def main(args):
    global BASE_DIR
    BASE_DIR=os.path.realpath(".")
    threading.Thread(target=watchfile).start()
    print("server rnning at  http://localhost:"+str(args.port))
    app.run(host="0.0.0.0",port=args.port)

def entry_point():
    parser = createParse()
    mainArgs=parser.parse_args()
    main(mainArgs)


def createParse():
    parser = argparse.ArgumentParser( formatter_class=argparse.ArgumentDefaultsHelpFormatter, description="")
    parser.add_argument('-d', '--dir',  help="dir")

    parser.add_argument('port', nargs='?', default=5000, type=int)
    return parser
