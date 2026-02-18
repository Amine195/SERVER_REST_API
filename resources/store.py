from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from models.store import StoreModel
from schemas import StoreSchema
from db import db

# Blueprint regroupant tous les endpoints liés aux magasins
blp = Blueprint("stores", __name__, description="Opérations sur les magasins")


@blp.route("/store")
class StoreList(MethodView):

    @jwt_required()
    @blp.response(200, StoreSchema(many=True))
    def get(self):
        return StoreModel.find_all()

    @jwt_required(fresh=True)
    @blp.arguments(StoreSchema)
    @blp.response(201, StoreSchema)
    def post(self, store_data):
        store = StoreModel(**store_data)

        try:
            store.save_to_db()
        except IntegrityError:
            abort(400, message="Un magasin avec le même nom existe déjà.")
        except SQLAlchemyError:
            abort(500, message="Une erreur s'est produite lors de l'insertion du magasin.")

        return store


@blp.route("/store/<int:store_id>")
class Store(MethodView):

    @jwt_required()
    @blp.response(200, StoreSchema)
    def get(self, store_id):
        return db.get_or_404(StoreModel, store_id, description="Magasin non trouvé.")

    @jwt_required(fresh=True)
    @blp.arguments(StoreSchema)
    @blp.response(200, StoreSchema)
    def put(self, store_data, store_id):
        store = db.get_or_404(StoreModel, store_id, description="Magasin non trouvé.")
        store.name = store_data.get("name", store.name)

        try:
            store.save_to_db()
        except IntegrityError:
            abort(400, message="Un magasin avec le même nom existe déjà.")
        except SQLAlchemyError:
            abort(500, message="Une erreur s'est produite lors de la mise à jour du magasin.")

        return store

    @jwt_required(fresh=True)
    def delete(self, store_id):
        store = db.get_or_404(StoreModel, store_id, description="Magasin non trouvé.")

        try:
            store.remove_from_db()
        except SQLAlchemyError:
            abort(500, message="Une erreur s'est produite lors de la suppression du magasin.")

        return {"message": "Magasin supprimé."}
