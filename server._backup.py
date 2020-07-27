import io
import os
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from PIL import Image
import numpy as np
import time
#import screenpoint
from datetime import datetime
import pyscreenshot
import requests
import logging
import argparse

from subprocess import call
#import ps

from libs.strings import *
from libs.networks import model_detect
import libs.preprocessing as preprocessing
import libs.postprocessing as postprocessing


max_view_size = 700
max_screenshot_size = 400

# Initialize the Flask application.
app = Flask(__name__)
CORS(app)

# Simple probe.
@app.route('/', methods=['GET'])
def hello():
    return 'Hello AR Cut Paste!'

# Ping to wake up the BASNet service.
@app.route('/ping', methods=['GET'])
def ping():
    logging.info('ping')
    return 'pong'

# The paste endpoints handles new paste requests.
@app.route('/cut', methods=['POST'])
def save():
	start = time.time()
	logging.info(' CUT')
	print("here")

	# Convert string of image data to uint8.
	print(request.files)
	if 'data' not in request.files:
		return jsonify({
			'status': 'error',
			'error': 'missing file param `data`'
		}), 400
	data = request.files['data'].read()
	if len(data) == 0:
		return jsonify({'status:': 'error', 'error': 'empty image'}), 400


	# Save debug locally.
	with open('imgtmp.jpg', 'wb') as f:
		f.write(data)

	image = Image.open("imgtmp.jpg")
	print(image.size)

	input_path = 'imgtmp.jpg'
	output_path = 'imgtmp.png'
	model_name = 'u2net'
	preprocessing_method_name = 'none'
	postprocessing_method_name = 'fba'

	model = model_detect(model_name)  # Load model
	print("--model start--")
	
	preprocessing_method = preprocessing.method_detect(preprocessing_method_name)
	postprocessing_method = postprocessing.method_detect(postprocessing_method_name)
	wmode = "file"  # Get work mode
	image = model.process_image(input_path, preprocessing_method, postprocessing_method)
	
	image.save('imgtmp.png')

	# Save to buffer
	buff = io.BytesIO()
	image.save(buff, 'PNG')
	buff.seek(0)
	print("--model end--")

	# Print stats
	logging.info(f'Completed in {time.time() - start:.2f}s')
	print(f'Completed in {time.time() - start:.2f}s')

	return send_file(buff, mimetype='image/png')
	

# The paste endpoints handles new paste requests.
@app.route('/paste', methods=['POST'])
def paste():
    start = time.time()
    logging.info(' PASTE')

    # Convert string of image data to uint8.
    if 'data' not in request.files:
        return jsonify({
            'status': 'error',
            'error': 'missing file param `data`'
        }), 400
    data = request.files['data'].read()
    if len(data) == 0:
        return jsonify({'status:': 'error', 'error': 'empty image'}), 400

    # Save debug locally.
    with open('paste_received.jpg', 'wb') as f:
        f.write(data)

    # Convert string data to PIL Image.
    logging.info(' > loading image...')
    view = Image.open(io.BytesIO(data))

    # Ensure the view image size is under max_view_size.
    if view.size[0] > max_view_size or view.size[1] > max_view_size:
        view.thumbnail((max_view_size, max_view_size))

    # Take screenshot with pyscreenshot.
    logging.info(' > grabbing screenshot...')
    screen = pyscreenshot.grab()
    screen_width, screen_height = screen.size

    # Ensure screenshot is under max size.
    if screen.size[0] > max_screenshot_size or screen.size[1] > max_screenshot_size:
        screen.thumbnail((max_screenshot_size, max_screenshot_size))

    # Finds view centroid coordinates in screen space.
    logging.info(' > finding projected point...')
    view_arr = np.array(view.convert('L'))
    screen_arr = np.array(screen.convert('L'))
    # logging.info(f'{view_arr.shape}, {screen_arr.shape}')

    call(["fcopy.bat", "imgtmp.png"]) 
    
    return jsonify({'status': 'ok'})
    

if __name__ == '__main__':
    os.environ['FLASK_ENV'] = 'development'
    port = int(os.environ.get('PORT', 8082))
    #app.run(debug=True, host='0.0.0.0', port=port)
    app.run(debug=False, port=port)
