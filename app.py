
#coding: utf-8
from flask import Flask, json, send_from_directory, render_template,Response
from flask_sockets import Sockets
import sys
import os
from pathlib import Path
import mimetypes
import datetime
import time
import random

app = Flask(__name__)
sockets = Sockets(app)
BASE_DIR="/Users/zk/git/jsPrj/webgl/FunWithWebGL2"

@sockets.route('/ws/echo')
def echo_socket(ws):
    print("websocket............")
    while not ws.closed:

        now = datetime.datetime.now().isoformat() + 'Z'
        ws.send(now)  #发送数据
        time.sleep(1)

@app.route('/', defaults={'req_path': ''})
@app.route('/<path:req_path>')
def dir_listing(req_path):

    # Joining the base and the requested path
    abs_path = os.path.join(BASE_DIR, req_path)

    # Return 404 if path doesn't exist
    print(abs_path)
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
                var ws = new WebSocket("ws://127.0.0.1:5000/ws/echo");

                ws.onmessage = function (event) {
                    content = event.data;
                    console.log(content);

                };
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

if __name__ == '__main__':
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
    print('server start')
    server.serve_forever()
