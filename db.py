from flask_sqlalchemy import SQLAlchemy
import base64
import boto3
from io import BytesIO
from mimetypes import guess_extension, guess_type
import os 
from PIL import Image
import random
import re
import string

from sqlalchemy.orm import backref

db = SQLAlchemy()

EXTENSIONS = ["png", "jpg", "jpeg", "gif"]
BASE_DIR = os.getcwd()
S3_BUCKET = "fashionforecast"
S3_BASE_URL = f"https://{S3_BUCKET}.s3-us-east-2.amazonaws.com"


class User(db.Model):
    _tablename_ = "user"
    id = db.Column(db.Integer, primary_key= True)
    name = db.Column(db.String, nullable= False)
    location = db.Column(db.Integer, nullable=False)
    clothings = db.relationship("Clothes", cascade="delete")

    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.location = kwargs.get("location")
    
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "location": self.location,
            "clothings": [t.sub_serialize() for t in self.clothings]
        }
    
    def sub_serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "location": self.location
        }
    
class Clothes(db.Model):
    _tablename_ = "clothes"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    warmth = db.Column(db.Integer, nullable=False)
    typeOfClothes = db.Column(db.String, nullable=False)
    picture = db.relationship("Clothing_Image", cascade="delete")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.warmth = kwargs.get("warmth")
        self.typeOfClothes = kwargs.get("typeOfClothes")
        self.user_id = kwargs.get("user_id")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "warmth": self.warmth,
            "typeOfClothes": self.typeOfClothes,
            "users": User.query.filter_by(id=self.user_id).first().sub_serialize(),
            "pictures": [p.sub_serialize() for p in self.picture]
        }

    def sub_serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "warmth": self.warmth,
            "typeOfClothes": self.typeOfClothes
        }


    
class Clothing_Image(db.Model):
    _tablename_ = "clothing_image"
    id = db.Column(db.Integer, primary_key=True)
    base_url = db.Column(db.String, nullable=True)
    salt = db.Column(db.String, nullable=False)
    extension = db.Column(db.String, nullable=False)
    width = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Integer, nullable=False)
    description_id = db.Column(db.Integer, db.ForeignKey("clothes.id"), nullable=False)

    def __init__(self, **kwargs):
        self.create(kwargs.get('image_data'))
        self.description_id = kwargs.get('description_id')

    def serialize(self):
        return {
            "url": f"{self.base_url}/{self.salt}.{self.extension}",
            "description": Clothes.query.filter_by(id=self.description_id).first().sub_serialize()
        }
    
    def sub_serialize(self):
        return {
            "url": f"{self.base_url}/{self.salt}.{self.extension}"
        }
    def create(self, image_data):
        try:
            ext = guess_extension(guess_type(image_data)[0])[1:]
            if ext not in EXTENSIONS:
                raise Exception(f"Extension {ext} not supported!")
            

            salt = "".join(
                random.SystemRandom().choice(
                    string.ascii_uppercase + string.digits
                )
                for _ in range(16)
            )

            img_str = re.sub("^data:image/.+;base64,", "", image_data)
            img_data = base64.b64decode(img_str)
            img = Image.open(BytesIO(img_data))

            self.base_url = S3_BASE_URL
            self.salt = salt
            self.extension = ext
            self.width = img.width
            self.height = img.height

            img_filename = f"{salt}.{ext}"
            self.upload(img, img_filename)
        except Exception as e:
            print(f"Unable to create image due to {e}")

    def upload (self, img, img_filename):
        try:
            img_temploc = f"{BASE_DIR}/{img_filename}"
            img.save(img_temploc)

            s3_client = boto3.client("s3")
            s3_client.upload_file(img_temploc, S3_BUCKET, img_filename)

            s3_resource = boto3.resource("s3")
            object_acl = s3_resource.ObjectAcl(S3_BUCKET, img_filename)
            object_acl.put(ACL="public-read")

            os.remove(img_temploc)

        except Exception as e:
            print(f"Unable to upload image due to {e}")