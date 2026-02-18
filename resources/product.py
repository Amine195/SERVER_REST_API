from flask.views import MethodView
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from models.product import ProductModel
from schemas import ProductSchema
from db import db

# Blueprint regroupant tous les endpoints liés aux produits
blp = Blueprint("products", __name__, description="Opérations sur les produits")


@blp.route("/product")
class ProductList(MethodView):

    @jwt_required()
    @blp.response(200, ProductSchema(many=True))
    def get(self):
        return ProductModel.find_all()

    @jwt_required(fresh=True)
    @blp.arguments(ProductSchema)
    @blp.response(201, ProductSchema)
    def post(self, product_data):
        product = ProductModel(**product_data)

        try:
            product.save_to_db()
        except IntegrityError:
            abort(400, message="Le magasin référencé n'existe pas.")
        except SQLAlchemyError:
            abort(500, message="Une erreur s'est produite lors de l'insertion du produit.")

        return product


@blp.route("/product/<int:product_id>")
class Product(MethodView):

    @jwt_required()
    @blp.response(200, ProductSchema)
    def get(self, product_id):
        return db.get_or_404(ProductModel, product_id, description="Produit non trouvé.")

    @jwt_required(fresh=True)
    @blp.arguments(ProductSchema)
    @blp.response(200, ProductSchema)
    def put(self, product_data, product_id):
        product = db.get_or_404(ProductModel, product_id, description="Produit non trouvé.")
        product.name = product_data.get("name", product.name)
        product.price = product_data.get("price", product.price)

        try:
            product.save_to_db()
        except SQLAlchemyError:
            abort(500, message="Une erreur s'est produite lors de la mise à jour du produit.")

        return product

    @jwt_required(fresh=True)
    def delete(self, product_id):
        product = db.get_or_404(ProductModel, product_id, description="Produit non trouvé.")

        try:
            product.remove_from_db()
        except SQLAlchemyError:
            abort(500, message="Une erreur s'est produite lors de la suppression du produit.")

        return {"message": "Produit supprimé."}
