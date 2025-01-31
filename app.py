# STANDARD python imports
import os
import json
import logging
import shutil
import logging

# Imports for building RESTful API
from flask import Flask
from flask_caching import Cache

# Import from BRAD
import sys
sys.path.append('../BRAD') # TODO: change this to work from PIP
# from BRAD.endpoints import bp as brad_endpoints_bp  # Import the Blueprint
# from BRAD.endpoints import set_globals, initiate_start
from BRAD.agent import Agent
from BRAD.constants import TOOL_MODULES

# Video endpoints
from video_endpoints import bp as video_endpoints_bp
from video_endpoints import set_globals as set_globals_network
from video_endpoints import initiate_start as initiate_start_network

# Modify BRAD configs on the fly
CONFIG_FILE = "config.json"
script_dir = os.path.abspath(os.path.dirname(__file__))
with open(CONFIG_FILE, "r") as file:
    config = json.load(file)
if config.get("log_path") == "output-logs":
    config["log_path"] = os.path.join(script_dir, "output-logs")
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file, indent=4)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configue caching
cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})


# def create_app():
# Directory structure
UPLOAD_FOLDER = '/usr/src/uploads'
DATABASE_FOLDER = '/usr/src/RAG_Database/'

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

# Redundant
TOOL_MODULES = TOOL_MODULES


# Set up app
app = Flask(__name__)

print(f"{app.root_path=}")

# set cache for the app
cache.init_app(app)
CACHE = cache

# Data directories setup
DATA_FOLDER = os.path.join(app.root_path, 'data')
UPLOAD_FOLDER = os.path.join(DATA_FOLDER, 'uploads')
DATABASE_FOLDER = os.path.join(DATA_FOLDER, 'RAG_Database')
print(f"{DATA_FOLDER=}")
print(f"{UPLOAD_FOLDER=}")
print(f"{DATABASE_FOLDER=}")

if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(DATABASE_FOLDER):
    os.makedirs(DATABASE_FOLDER)

# set_globals(DATA_FOLDER, UPLOAD_FOLDER, DATABASE_FOLDER, ALLOWED_EXTENSIONS, TOOL_MODULES, CACHE)
set_globals_network(DATA_FOLDER, UPLOAD_FOLDER, DATABASE_FOLDER, ALLOWED_EXTENSIONS, TOOL_MODULES, CACHE)

# initiate_start()
initiate_start_network()

# Register the Blueprint for the endpoints
# app.register_blueprint(brad_endpoints_bp)
app.register_blueprint(video_endpoints_bp)


