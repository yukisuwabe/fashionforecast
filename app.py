from PIL.Image import new
from db import db
from db import User
from db import Clothes
from db import Clothing_Image
from flask import Flask
from flask import request
import requests
import json 
import os

app = Flask(__name__)
db_filename = "fashion.db"

app.config["SQLALCHEMY_DABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app)
with app.app_context():
    db.create_all()

def success_response(data, code=200):
    return json.dumps({"success": True, "data": data}), code

def failure_response(message, code=404):
    return json.dumps({"success": False, "error": message}), code

@app.route("/")
def get_default_weather():
    response = requests.get("http://api.openweathermap.org/data/2.5/weather?zip=14853,us&appid=de52b0de5733de9964224287de84c5e6&units=metric")
    return success_response(response.json())

@app.route("/user/", methods=['POST'])
def create_user():
    body = json.loads(request.data)
    new_user = User(
        name = body.get('name'),
        location = body.get('location')
    )
    if not new_user.name:
        return failure_response("Name not provided", 400)
    if not new_user.location:
        return failure_response("Zip Code not provided", 400)
    if new_user.location < 10000:
        return failure_response("Zip Code not valid", 400)
    db.session.add(new_user)
    db.session.commit()
    return success_response(new_user.serialize(), 201)

@app.route("/user/<int:userid>/")
def get_specific_user(userid):
    user = User.query.filter_by(id=userid).first()
    if user is None:
        return failure_response("User does not exist")
    return success_response(user.serialize())
    

@app.route("/<int:userid>/clothing/", methods=['POST'])
def upload_clothing(userid):
    user = User.query.filter_by(id=userid).first()
    if user is None:
        return failure_response("User does not exist")
    body = json.loads(request.data)
    new_clothes = Clothes(
        name = body.get('name'),
        warmth = body.get('warmth'),
        typeOfClothes = body.get('typeOfClothes'),
        user_id = userid
    )
    if not new_clothes.name:
        return failure_response("Name of clothing not provided", 400)
    if not new_clothes.warmth:
        return failure_response("Warmth level of clothing not provided", 400)
    if not new_clothes.typeOfClothes:
        return failure_response("Type of clothing not provided", 400)
    if new_clothes.warmth < 0 or new_clothes.warmth > 10:
        return failure_response("Warmth level must be within the range of 1-10", 400)
    if new_clothes.typeOfClothes != "top" and new_clothes.typeOfClothes != "bottom" and new_clothes.typeOfClothes != "shoes" and new_clothes.typeOfClothes != "jacket":
        return failure_response("Not a valid entry for type of clothing", 400)
    db.session.add(new_clothes)
    db.session.commit()
    return success_response(new_clothes.serialize(), 201)

@app.route("/<int:clothingid>/picture/", methods=['POST'])
def upload_clothing_picture(clothingid):
    clothes = Clothes.query.filter_by(id=clothingid).first()
    if clothes is None:
        return failure_response("Clothing does not exist")
    body = json.loads(request.data)
    image_data = body.get('image_data')
    if image_data is None:
        return failure_response("Image not provided", 400)
    clothing_image = Clothing_Image(image_data = image_data, description_id=clothingid)
    db.session.add(clothing_image)
    db.session.commit()
    return success_response(clothing_image.serialize(), 201)

@app.route("/<int:userid>/clothing/")
def get_clothes(userid):
    user = User.query.filter_by(id=userid).first()
    if user is None:
        return failure_response("User does not exist")
    clothes = {"clothes": [t.serialize() for t in Clothes.query.filter_by(user_id=userid)]}
    return success_response(clothes)

@app.route("/<int:userid>/weather/")
def get_weather(userid):
    user = User.query.filter_by(id=userid).first()
    if user is None:
        return failure_response("User does not exist")
    response = requests.get("http://api.openweathermap.org/data/2.5/weather?zip={},us&appid=de52b0de5733de9964224287de84c5e6&units=metric".format(user.location))
    return success_response(response.json())

@app.route("/<int:userid>/<string:type>/select/")
def select_clothes(userid, type):
    user = User.query.filter_by(id=userid).first()
    if user is None:
        return failure_response("User does not exist")
    if type != "top" and type != "bottom" and type != "shoes" and type != "jacket":
        return failure_response("Not a valid entry for type of clothing", 400)
    response = requests.get("http://api.openweathermap.org/data/2.5/weather?zip={},us&appid=de52b0de5733de9964224287de84c5e6&units=metric".format(user.location))
    response = json.loads(json.dumps(response.json()))
    temp = response.get('main')
    temperature = int(temp.get('temp'))
    if temperature > 30:
        clothing = Clothes.query.filter_by(user_id=userid).filter(Clothes.warmth<3, Clothes.typeOfClothes == type).first()
        if clothing is None:
            clothing = Clothes.query.filter_by(user_id=userid).filter(Clothes.typeOfClothes == type).order_by(Clothes.warmth.asc).first()
    elif temperature > 20:
        clothing = Clothes.query.filter_by(user_id=userid).filter(Clothes.warmth>=3, Clothes.warmth<5, Clothes.typeOfClothes == type).first()
        if clothing is None:
            clothing = Clothes.query.filter_by(user_id=userid).filter(Clothes.typeOfClothes == type).first()
    elif temperature > 10:
        clothing = Clothes.query.filter_by(user_id=userid).filter(Clothes.warmth>=5, Clothes.warmth<8, Clothes.typeOfClothes == type).first()
        if clothing is None:
            clothing = Clothes.query.filter_by(user_id=userid).filter(Clothes.typeOfClothes == type).first()
    else:
        clothing = Clothes.query.filter_by(user_id=userid).filter(Clothes.warmth>=8, Clothes.typeOfClothes == type).first()
        if clothing is None:
            clothing = Clothes.query.filter_by(user_id=userid).filter(Clothes.typeOfClothes == type).order_by(Clothes.warmth.desc).first()
    if clothing is None:
        return failure_response("No clothes of the clothing type", 400)
    return success_response(clothing.serialize())
    

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)