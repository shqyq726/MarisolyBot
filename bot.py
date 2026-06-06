from flask import Flask

app = Flask(name)

@app.route("/")
def home():
return "MarisolyBot is running!"

if name == "main":
app.run(host="0.0.0.0", port=10000)
