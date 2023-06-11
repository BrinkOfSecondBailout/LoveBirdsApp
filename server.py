from flask import Flask, render_template
from flask_app import app
from flask_app.controllers import users, attributes, images, messages, wallnotes

if __name__=="__main__":
    app.run(debug=True, host="localhost", port=8000)
