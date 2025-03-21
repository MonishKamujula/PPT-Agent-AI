from flask import Flask, request
from flask_cors import CORS
from ppt_maker import _make_presentation
import json


# app = Flask(__name__)
# CORS(app)

# @app.route("/create_ppt", methods=["POST"])
# def create_ppt():
#     # data = request.get_json()
#     # title = data["title"]
#     # description = data["description"]
#     # status = _make_presentation(title, description)
#     # if status == "SUCCESS!":
#     #     return "success"
#     # else:
#     #     return "error"
#     print("LAMBDA FUNCTION CALLED...")
#     return "success"
    
def handler(event, context):
    print("LAMBDA FUNCTION CALLED...")
    print("EVENT:", event)
    print(type(event))
    data = event["body"]
    print("DATA:", data)
    title = data["title"]
    description = data["description"]
    print("TITLE:", title)
    print("DESCRIPTION:", description)
    try:
        status = _make_presentation(title, description)
        if status != "ERROR":
            return status
        else:
            return "error"
    except Exception as e:
        print(e)
        return "error"

