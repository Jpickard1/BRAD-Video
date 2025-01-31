# STANDARD python imports
import os
import re
import sys
import json
import shutil
import logging
import time
from difflib import SequenceMatcher
from itertools import filterfalse
from urllib.parse import urlparse
from pathlib import Path
import random
from rich import print

# Imports for building RESTful API
from flask import Flask, request, jsonify, Blueprint, send_from_directory
from flask import flash, redirect, url_for
from flask import Blueprint, jsonify
from werkzeug.utils import secure_filename

# For the Video RAG
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings

# Used to get list of OpenAI models
from openai import OpenAI

# Imports for BRAD library
from BRAD.agent import Agent, AgentFactory
from BRAD.utils import delete_dirs_without_log, strip_root_path
from BRAD.rag import create_database
from BRAD import llms # import load_nvidia, load_openai
from BRAD.endpoints import parse_log_for_one_query

PREVIOUS_NODE = None
DEFAULT_SESSION_EXTN = 'Video-Chat'

bp = Blueprint('network-endpoints', __name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

###############################################################################
#                                  GLOBALS                                    #
###############################################################################

NVIDIA_LLM_MODELS = [
    "meta/llama3-70b-instruct",
    "mistralai/mistral-7b-instruct-v0.3",
    "microsoft/phi-3.5-mini-instruct",
    "google/gemma-2-2b-it"
]

EMBEDDINGS_MODEL = HuggingFaceEmbeddings(model_name='BAAI/bge-base-en-v1.5')

UPLOAD_FOLDER = None
DATABASE_FOLDER = None
ALLOWED_EXTENSIONS = None
TOOL_MODULES = None
DATA_FOLDER = None
CACHE = None
LOG_PATH = None
def set_globals(data_folder, upload_folder, database_folder, allowed_extensions, tool_modules, cache):
    '''
    :nodoc:
    '''
    global UPLOAD_FOLDER, DATABASE_FOLDER, ALLOWED_EXTENSIONS, TOOL_MODULES, DATA_FOLDER, CACHE
    
    # Set the global values
    DATA_FOLDER = upload_folder
    UPLOAD_FOLDER = upload_folder
    DATABASE_FOLDER = database_folder
    ALLOWED_EXTENSIONS = allowed_extensions
    TOOL_MODULES = tool_modules
    CACHE = cache
    CACHE.set('rag_db', "DCMB", timeout=0)

PATH_TO_OUTPUT_DIRECTORIES = None
DEFAULT_SESSION = None
def set_global_output_path(output_path, default_session):
    '''
    :nodoc:
    '''
    global PATH_TO_OUTPUT_DIRECTORIES, DEFAULT_SESSION
    PATH_TO_OUTPUT_DIRECTORIES = output_path
    DEFAULT_SESSION = default_session




###############################################################################
#                               HELPER METHODS                                #
###############################################################################

def convert_path_auto(file_path):
    """
    This doesn't work correctly, but it should do the following:

    Convert the given path to match the operating system's expected format.
    - On Windows, it converts to use backslashes (\).
    - On Linux/macOS, it converts to use forward slashes (/).
    """
    # This line is an artificat of previously using a single rag database
    file_path = file_path.replace("rag_db", CACHE.get('rag_db'))
    # TODO: ask my good friend and the senior developer Ram to fix this
    file_path = file_path.replace("\\", "/")
    return file_path
    # Use pathlib to handle the conversion based on OS
    # p = Path(path)
    
    # Auto-detect the OS and convert accordingly
    # if sys.platform.startswith("win"):
    #     return str(p)  # Windows default (backslashes)
    # else:
    #     return p.as_posix()  # Unix default (forward slashes)

def initiate_start():
    '''
    Initializer method for important health checks before starting backend
    '''

    initial_agent = AgentFactory(
        tool_modules = ['RAG'],
        interactive  = False,
        persist_directory = None, # DATABASE_FOLDER,
        db_name = None, # CACHE.get('rag_name'),
        llm_choice = None, # CACHE.get('LLMChoice'),
        gui=True,
        config='config.json'
    ).get_agent()
    try:
        delete_dirs_without_log(initial_agent)
    except:
        print('Issue removing directories')

    log_path = initial_agent.state['config'].get('log_path')
    LOG_PATH = log_path
    default_session = os.path.join(log_path, DEFAULT_SESSION_EXTN)
    set_global_output_path(log_path, default_session)

    # default agent to be used
    default_agent = AgentFactory(
        tool_modules=TOOL_MODULES, 
        start_path=default_session, 
        interactive=False, 
        persist_directory=DATABASE_FOLDER,
        db_name=CACHE.get('rag_name'),
        llm_choice=CACHE.get('LLMChoice'),
        gui=True,
        config='config.json'
    ).get_agent()
    
###############################################################################
#
#                                  ENDPOINT
#
###############################################################################

@bp.route("/invoke/chat", methods=['POST'])
def ep_invoke_chat():
    return invoke_chat(request)

def invoke_chat(request):
    """
    Invoke a query using the BRAD agent.

    This function handles an incoming request from the user, extracts the message, and sends it to the BRAD agent for processing. 
    It then returns a JSON response containing both the BRAD agent's reply and the associated log stages.

    **Input Request Structure**:
    The input request should be a JSON object with the following format:
    json

    >>> {
    >>>     "message": "Your query here"
    >>> }

    **Output Response Structure**:
    The response will be a JSON object containing the agent's response and a log of the processing stages:

    >>> { 
    >>>      "response": "Generated response from BRAD agent", 
    >>>      "response-log": { 
    >>>          "stage_1": "log entry for stage 1", 
    >>>          "stage_2": "log entry for stage 2", 
    >>>          ...
    >>>      },
    >>>      "llm-usage": {
    >>>          "llm-calls": number of new llm calls,
    >>>          "api-fees":  cost of api fees,
    >>>      }
    >>> }


    :param request: A Flask request object containing JSON data with the user message.
    :type request: flask.Request
    :return: A JSON response containing the agent's reply and the log of query stages.
    :rtype: dict
    """
    request_data = request.json
    brad_session = request_data.get("session", None)
    brad_query = request_data.get("message")

    # session_path = os.path.join(PATH_TO_OUTPUT_DIRECTORIES, brad_session) if brad_session else None
    brad = AgentFactory(
        session_path="output-logs/Video-Chat", 
        llm_choice=CACHE.get('LLMChoice'),
        temperature=CACHE.get('Temperature'),
        gui=True,
        config='config.json'
    ).get_agent()

    persist_directory = os.path.join(os.getcwd(), "data", "RAG_Database", CACHE.get('rag_db'))

    # Load the database
    vectordb = Chroma(
        persist_directory=persist_directory,  # Path where the database was saved
        embedding_function=EMBEDDINGS_MODEL,  # Embedding model
        collection_name="default"  # Ensure this matches what was used during writing
    )
    brad.state['databases']['RAG'] = vectordb

    brad_response = brad.invoke(brad_query)
    print(f"{brad_response=}")
    brad_name = brad.chatname

    agent_response_log = brad.chatlog[list(brad.chatlog.keys())[-1]]
    passed_log_stages, llm_usage = parse_log_for_one_query(agent_response_log)

    brad.save_state()

    # Parse the BRAD log file to identify which video to jump into and where
    log_file_path = os.path.join(os.getcwd(), "output-logs", "Video-Chat", "log.json")
    with open(log_file_path, 'r') as file:
        log_file = json.load(file)
    sorted_keys = sorted(map(int, log_file.keys()))
    second_to_last_key = str(sorted_keys[-2])  # Convert back to string to index the dictionary
    second_to_last_entry = log_file[second_to_last_key]
    sources = second_to_last_entry['process']['sources']
    source_locations = second_to_last_entry['process']['source_locations']
    documents = second_to_last_entry["process"]["steps"][0]["docs-to-gui"]

    # Dictionary to store sources and associated start times
    source_timing_map = {}

    # Iterate over all documents to extract source and timing information
    for document in documents:
        source_location = document["source"]
        source_text = document["text"]
        timed_transcript = source_location.split(".")[0] + "_minute.json"
        print(f"{timed_transcript=}")
        timed_transcript = convert_path_auto(timed_transcript)
        print(f"{timed_transcript=}")
        
        # Ensure the transcript file exists
        if not os.path.exists(timed_transcript):
            print(f"Timed transcript file not found: {timed_transcript}")
            continue

        # Read the timed transcript file
        with open(timed_transcript, "r") as file:
            transcript_data = json.load(file)

        # Find the start time point for the closest match to the source_text
        best_start_time = None
        best_match_ratio = 0

        for entry in transcript_data:
            transcript_text = entry["text"]
            start_time = entry["start"]
            match_ratio = SequenceMatcher(None, transcript_text, source_text).ratio()
            if match_ratio > best_match_ratio:
                best_match_ratio = match_ratio
                best_start_time = start_time
                best_match_text = transcript_text

        # Save the starting point if a match was found
        if best_start_time is not None:
            if source_location not in source_timing_map:
                source_timing_map[source_location] = []
            source_timing_map[source_location].append(best_start_time)

    print(f"{source_timing_map=}")
    print(f"{best_match_text=}")
    best_source = max(source_timing_map, key=lambda k: len(source_timing_map[k]))
    best_time = source_timing_map[best_source][0]
    best_time = int(best_time)
    print(f"{best_time=}")
    best_source = best_source.replace('\\', '/')
    print(f"{best_source=}")
    source_video = best_source.split('.')[0].split('/')[-1]
    print(f"{source_video=}")
    
    response_data = {
        "response": brad_response,
        "session-name": brad_name,
        "response-log": passed_log_stages,
        "response-log-dict": llm_usage.get('process'),
        "llm-usage": llm_usage,
        "video":source_video,
        "time":best_time
    }

    return jsonify(response_data)


@bp.route("/databases/available", methods=['GET'])
def ep_databases_available():
    return databases_available()

def databases_available():
    """
    Retrieve a list of available retrieval-augmented generation (RAG) databases.

    This endpoint lists all available databases stored in the designated database folder. The function checks the folder for subdirectories, which represent the databases, and returns the list in JSON format. If no databases are found, the response includes "None" as the first entry in the list.

    This is a `GET` request and does not require any parameters.

    Example request:

    >>> GET /databases/available
    
    A JSON object is returned with the list of available databases. In case of errors (e.g., folder not found), an error message is returned.

    Example success response:

    >>> {
    >>>     "databases": ["None", "database1", "database2"]
    >>> }

    Example error response (if folder is not found):

    >>> {
    >>>     "error": "Directory not found"
    >>> }
    
    :return: A JSON response containing a list of available databases or an error message.
    :rtype: dict
    """
    # Auth: Joshua Pickard
    #       jpic@umich.edu
    # Date: October 17, 2024    
    
    # Get list of directories at this location
    try:
        databases = [name for name in os.listdir(DATABASE_FOLDER) 
                         if os.path.isdir(os.path.join(DATABASE_FOLDER, name))]
        databases.remove("DCMB")
        databases.insert(0, "DCMB")
        # Return the list of open sessions as a JSON response
        response = jsonify({"databases": databases})
        return response
    
    except FileNotFoundError:
        return jsonify({"error": "Directory not found"})
    
    except Exception as e:
        return jsonify({"error": str(e)})
    
@bp.route("/video/databases/set", methods=['POST'])
def ep_databases_set():
    return databases_set(request)

def databases_set(request):
    """
    Set the active retrieval-augmented generation (RAG) database for the BRAD agent.

    This uses the flask system cache to set the active database and llm hosts and updates it.

    This endpoint allows users to select and set an available database from the server. The selected database will be loaded and set as the active RAG database for the BRAD agent. If "None" is selected, it will disconnect the current database.

    **Request Structure**:
    The input should be a JSON object containing the name of the database to be set.

    Example request:

    >>> {
    >>>     "database": "database_name"
    >>> }

    If the database name is `"None"`, the current RAG database will be disconnected.

    **Response Structure**:
    A JSON response is returned indicating whether the database was successfully set or if an error occurred.

    Example success response:

    >>> {
    >>>     "success": True,
    >>>     "message": "Database set to database_name"
    >>> }

    Example response for disconnecting the database:

    >>> {
    >>>     "success": True,
    >>>     "message": "Database set to None"
    >>> }

    Example error response (if the directory is not found):

    >>> {
    >>>     "error": "Directory not found"
    >>> }

    :param request: The HTTP POST request containing the database name in JSON format.
    :type request: flask.Request
    :return: A JSON response with a success message or an error message.
    :rtype: dict
    """
    # Auth: Joshua Pickard
    #       jpic@umich.edu
    # Date: October 17, 2024
    
    # Get list of directories at this location

    try:

        request_data = request.json
        logger.info(f"{request_data=}")
        database_name = request_data.get("database")
        logger.info(f"{database_name=}")

        rag_database = CACHE.get('rag_db')
        if rag_database != database_name:
            CACHE.set('rag_db', database_name, timeout=0)
        
        logger.info(f"{CACHE.get('rag_db')=}")
        
        return jsonify({"success": True, "message": f"Database set to {database_name}"}), 200

    except FileNotFoundError:
        return jsonify({"error": "Directory not found"})

    except Exception as e:
        return jsonify({"error": str(e)})

