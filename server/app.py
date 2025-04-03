#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

class RestaurantResource(Resource):

    def get(self):
        restaurant_dict = [restaurant.to_dict(rules=('-restaurant_pizzas',)) for restaurant in Restaurant.query.all()]
        return restaurant_dict, 200


class RestaurantByID(Resource):

    def get(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()
        if restaurant:
            return restaurant.to_dict(), 200
        
        return {"error": "Restaurant not found"}, 404

    def delete(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()
        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()

            return "", 204
        
        return {"error": "Restaurant not found"}, 404

class PizzaResource(Resource):

    def get(self):
        pizza_dicts = [pizza.to_dict(rules=('-restaurant_pizzas',)) for pizza in Pizza.query.all()]
        return pizza_dicts, 200


class RestaurantPizzaResource(Resource):

    def post(self):
        json = request.get_json()
        try:
            new_pizza = RestaurantPizza(
                price=json['price'],
                restaurant_id=json['restaurant_id'],
                pizza_id=json['pizza_id'],
            )
            db.session.add(new_pizza)
            db.session.commit()

            return new_pizza.to_dict(), 201
        except:
            return {"errors": ["validation errors"]}, 400


api.add_resource(RestaurantResource, '/restaurants')
api.add_resource(RestaurantByID, '/restaurants/<int:id>')
api.add_resource(PizzaResource, '/pizzas')
api.add_resource(RestaurantPizzaResource, '/restaurant_pizzas')


if __name__ == "__main__":
    app.run(port=5555, debug=True)
