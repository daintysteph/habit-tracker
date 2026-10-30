from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Habit tracker is running"

if __name__ == "__main__":
    app.run(debug=True)