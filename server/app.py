#!/usr/bin/env python3

import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'instance/app.db')}")

from flask import Flask, make_response, jsonify, request
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Activity, Camper, Signup

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)
api = Api(app)

@app.route('/')
def home():
    return 'Welcome to the MOCK CHALLENGE!!!'

class Campers(Resource):
    def get(self):
        campers = [c.to_dict() for c in Camper.query.all()]

        return campers, 200
    
    def post(self):
        try:
            data = request.get_json()
            new_camper = Camper(
                name = data['name'],
                age = data['age']
            )

            db.session.add(new_camper)
            db.session.commit()

            return new_camper.to_dict(), 201
        except:
            return {"error": "400: Validation error"}, 400
    
api.add_resource(Campers, "/campers")

class CampersById(Resource):
    def get(self, id):
        try:
            camper = Camper.query.filter(Camper.id == id).first()

            camper.activities = []
            for s in camper.signups:
                camper.activities.append(s.activity)
            
            return camper.to_dict(only=("id", "name", "age", "activities")), 200
        except:
            return {"error": "404: Camper not found"}, 404
    
api.add_resource(CampersById, "/campers/<int:id>")

class Activities(Resource):
    def get(self):
        activities = [a.to_dict() for a in Activity.query.all()]

        return activities, 200
    
api.add_resource(Activities, "/activities")


class ActivitiesById(Resource):
    def delete(self, id):
        try:
            activity = Activity.query.filter(Activity.id == id).first()
            act_signups = Signup.query.filter(Signup.activity_id == id).all()

            for a in act_signups:
                db.session.delete(a)
                
            db.session.delete(activity)
            db.session.commit()

            return {"message": "202: delete Successful"}, 204
        except:
            return {"error": "404: Activity not found"}, 404
        
api.add_resource(ActivitiesById, "/activities/<int:id>")


class Signups(Resource):
    def get(self):
        signups = [s.to_dict() for s in Signup.query.all()]

        return signups, 200
    
    def post(self):
        try:
            data = request.get_json()
            
            new_signup = Signup(
                time = data['time'],
                camper_id = data['camper_id'],
                activity_id = data['activity_id']
            )

            db.session.add(new_signup)
            db.session.commit()

            return new_signup.activity.to_dict(), 201
        except:
            return {"error": "400: Validation error"}, 400
    
api.add_resource(Signups, "/signups")

if __name__ == '__main__':
    app.run(port=5555, debug=True)
