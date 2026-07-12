from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({
        "message": "Backend is running!"
    })

@app.route("/about")
def about():
    return jsonify({
        "name": "Oswin Ranjan",
        "role": "Backend AI Engineer Intern",
    })

if __name__ == "__main__":
    app.run(debug=True)