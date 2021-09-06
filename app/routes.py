import os
from flask import render_template, url_for, request, jsonify, redirect, Response
from flask.helpers import flash
from werkzeug.utils import redirect
from app import app
from .core.Source import Video
from .core.proccess import gen_bbox
from os.path import join
import tensorflow as tf
from tensorflow.keras.models import load_model
import cv2


global video
model = None
# model = load_model(join(os.path.abspath(os.path.dirname(
#     __file__)), 'core/model/model.hdf5').replace('\\', '/'))


@app.route('/_upload', methods=['POST', 'GET'])
def upload():
    path = join(os.path.abspath(os.path.dirname(__file__)), 'uploads/')
    if request.method == "POST":
        if 'videoFile' not in request.files:
            flash('No Selected Video')
            return redirect(url_for('index'))

        file = request.files['videoFile']
        if file.filename == '':
            flash("No Selected Video")
            return redirect(url_for('index'))
        else:
            path = path.replace('\\', '/')
            file.save(join(path, file.filename))
            message = {'Message': 'Upload Video', 'File name': join(
                path, file.filename), 'Status': True}
            filename = join(path, file.filename)
            return jsonify({'redirect': url_for("example", file=file.filename)})
            # return jsonify(file.filename)
            # print(file.filename)
            # return render_template('index.html', filename=file.filename)
    # return render_template('index.html')


@app.route('/_selected', methods=['POST', 'GET'])
def selectedVideo():
    if request.method == "POST":
        jsonData = request.get_json()
        file = jsonData['file']
        if file == "CCTV":
            # format cctv : "rtsp://username:password@ip_address"
            file = "rtsp://" + \
                jsonData['username']+":"+jsonData['pass']+"@"+jsonData['ip']
        return jsonify({'redirect': url_for("example", file=file)})
        # return jsonify(file)
        # return render_template('index.html', filename=file)


@app.route('/<file>')
def example(file):
    return render_template('index.html', filename=file)


@app.route('/_listVideo', methods=['POST', 'GET'])
def listVideo():
    list_Video = []
    if request.method == "POST":
        path = join(os.path.abspath(os.path.dirname(__file__)), 'uploads/')
        path = path.replace('\\', '/')
        for f in os.listdir(path):
            list_Video.append(f)
        return jsonify(list_Video)


@app.route('/_load_model', methods=['POST', 'GET'])
def loadModel():
    global model
    if request.method == "GET":
        if model == None:
            return jsonify('Not Loaded')
        else:
            return jsonify("Loaded")

    elif request.method == "POST":
        path = join(os.path.abspath(os.path.dirname(__file__)),
                    'core/model/model.hdf5')
        path = path.replace('\\', '/')
        model = load_model(path)
        return jsonify({'redirect': url_for("index")})


@app.route('/_task', methods=['POST', 'GET'])
def task():
    global video
    if request.method == 'POST':
        del video
        return jsonify({'redirect': url_for("index")})


def gen():
    global video
    while True:
        success, framePre, ori = video.get_frame()
        if success:
            frame = gen_bbox(model, framePre, ori)
            ret, jpeg = cv2.imencode('.jpg', frame)
            frame = jpeg.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            # del video
            break


@app.route('/video_feed/<url>')
def video_feed(url):
    global video
    if url == 'Webcam':
        url = 0
        video = Video(url)
        # video = cv2.VideoCapture(url)
        return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')
    elif url == 'CCTV':
        video = Video(str(url))
        # video = cv2.VideoCapture(str(url))
        return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        path = join(os.path.abspath(os.path.dirname(__file__)), 'uploads/')
        fullURL = join(path, url)
        video = Video(str(fullURL))
        # video = cv2.VideoCapture(str(fullURL))
        # print(url)
        return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/_add_numbers', methods=['POST', 'GET'])
def add_numbers():
    if request.method == "POST":
        jsonData = request.get_json()
        a = int(jsonData['a'])
        b = int(jsonData['b'])
        result = a+b
        print(result)
        return jsonify(result)


@ app.route('/')
def index():
    return render_template('index.html')

# FLASK_DEBUG = 1
# while True:
#         frame, success = video.get_frame()
#         if success:
#             yield (b'--frame\r\n'
#                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
#         # else:
#         #     continue
#             # del video
#             # break
