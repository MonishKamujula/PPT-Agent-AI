from flask import Flask, request
from flask_cors import CORS
from ppt_maker import _make_presentation
import awsgi


app = Flask(__name__)
CORS(app)

@app.route("/create_ppt", methods=["POST"])
def create_ppt():
    data = request.get_json()
    title = data["title"]
    description = data["description"]
    status = _make_presentation(title, description)
    if status == "SUCCESS!":
        return "success"
    else:
        return "error"
    


if __name__ == "__main__":
    app.run(port=5001, debug=False)
