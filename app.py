from io import StringIO
from flask import Flask, request, jsonify, make_response
from api.utils.database import db
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields
from api.routes.EyeData import eyeTracking_routes
from dotenv import dotenv_values
import os
import gzip
import json

app = Flask(__name__)
config = dotenv_values(".env")

#DATABASR_URL = os.getenv("DATABASE_URL")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = config['DATABASE_URL']

db.init_app(app)
with app.app_context():
    db.create_all()

app.register_blueprint(eyeTracking_routes, url_prefix='/api/v1/eye-tracking')

@app.route("/api/v1/test", methods=['GET', 'POST'])
def submit():
    print(request.headers['Content-Type'])
    file = request.data
    aa = gzip.decompress(file).decode()
    tt = aa.split('\n')
    for i in tt:
        qq = json.loads(i)
        print("哈囉你好嗎: ", qq)

    return 'OK'


if __name__ == '__main__':
    app.run(host="0.0.0.0", port="5000")
