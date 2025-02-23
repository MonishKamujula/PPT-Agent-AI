from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from agents import _run_demo_loop

app = Flask(__name__)
CORS(app)  # Enable CORS for API requests
messages = []
last_agent = None
def _add_messages(message, last_agent):
    messages.append({"role": "user", "content": message})
    last_agent = last_agent
@app.route('/')
def home():
    return "Hello, World!"

@app.route('/check', methods=['GET'])
def check():
    return jsonify({'message': f'Working!'}), 200

@app.route('/predict')
def main():
    # first get the input from the user

    message_content = request.args.get('text')

    _add_messages(message_content, last_agent)
    content, role ,new_agent = _run_demo_loop(messages, last_agent)
    print("Printing content:", content)
    return content

if __name__ == '__main__':
    app.run(debug=True)
