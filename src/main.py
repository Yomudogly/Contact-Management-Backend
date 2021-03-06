"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from models import db, Person


app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/people', methods=['GET'])
def handle_people():
    people = Person.query.all()
    people = list(map(lambda x: x.serialize(), people))

    return jsonify(people), 200

@app.route('/person', methods=['POST'])
def handle_add_person():
    body = request.get_json()
    if body is None:
        raise APIException("You need to specify the request body as a json object", status_code=400)
    if 'full_name' not in body:
        raise APIException('You need to specify the name', status_code=400)
    if 'email' not in body:
        raise APIException('You need to specify the email', status_code=400)
    if 'address' not in body:
        raise APIException('You need to specify the address', status_code=400)
    if 'phone' not in body:
        raise APIException('You need to specify the phone', status_code=400)

    person = Person(full_name=body['full_name'], email=body['email'], address=body['address'], phone=body['phone'])
    db.session.add(person)
    db.session.commit()
    return jsonify(person.serialize()), 200


@app.route('/person/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def handle_person(id: int):
    if request.method == 'PUT':
        body = request.get_json()
        Person.query.filter_by(id=id).update({'full_name':body['full_name'], 'email':body['email'], 'address':body['address'], 'phone':body['phone']})
        person = Person.query.get(id)
        if person:
            db.session.commit()
            return jsonify(message=person.full_name +  " with id " + str(id) + " was successfully updated"), 200
        else:
            return jsonify(message="Person with id " + str(id) + " does not exist"), 404
    if request.method == 'GET':
        #body = request.get_json()
        person = Person.query.get(id)
        if person:
            return jsonify(person.serialize()), 200
        else:
            return jsonify(message="Person with id " + str(id) + " does not exist"), 404
    if request.method == 'DELETE':
        person = Person.query.get(id)
        if person:
            db.session.delete(person)
            db.session.commit()
            return jsonify(message=person.full_name + " was successfully deleted"), 200
        else:
            return jsonify(message="Person with id " + str(id) + " does not exist")

        

    return "Invalid Method", 404


# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
