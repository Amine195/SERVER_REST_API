from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, get_jwt, jwt_required
from passlib.hash import pbkdf2_sha256
from sqlalchemy.exc import SQLAlchemyError

from models.blocklist import BlocklistModel
from models.user import UserModel
from schemas import UserSchema
from db import db

# Blueprint regroupant les endpoints d'authentification
blp = Blueprint("users", __name__, description="Opérations sur les utilisateurs")


@blp.route("/register")
class UserRegister(MethodView):

    # Créer un nouveau compte utilisateur
    @blp.arguments(UserSchema)
    def post(self, user_data):
        # Vérifie que le nom d'utilisateur n'est pas déjà pris
        if UserModel.query.filter_by(username=user_data["username"]).first():
            abort(409, message="Un utilisateur avec ce nom d'utilisateur existe déjà.")

        user = UserModel(
            username=user_data["username"],
            password=pbkdf2_sha256.hash(user_data["password"])  # Hash sécurisé du mot de passe
        )

        try:
            user.save_to_db()
        except SQLAlchemyError:
            abort(500, message="Erreur lors de la création de l'utilisateur.")

        return {"message": "Utilisateur créé avec succès."}, 201


@blp.route("/login")
class UserLogin(MethodView):

    # Connexion : retourne un token JWT si les identifiants sont corrects
    @blp.arguments(UserSchema)
    def post(self, user_data):
        user = UserModel.query.filter_by(username=user_data["username"]).first()

        # Vérifie le mot de passe avec le hash stocké
        if user and pbkdf2_sha256.verify(user_data["password"], user.password):
            access_token = create_access_token(identity=str(user.id), fresh=True)
            refresh_token = create_refresh_token(identity=str(user.id))
            return {"access_token": access_token, "refresh_token": refresh_token}, 200

        abort(401, message="Nom d'utilisateur ou mot de passe incorrect.")

@blp.route("/refresh")
class TokenRefresh(MethodView):

    # Actualisation du token JWT (utilisé après expiration)
    @jwt_required(refresh=True)
    def post(self):
        current_user_id = get_jwt_identity()
        new_access_token = create_access_token(identity=current_user_id, fresh=False)
        jti = get_jwt()["jti"]
        db.session.add(BlocklistModel(jti=jti))
        db.session.commit()

        return {"access_token": new_access_token}, 200

@blp.route("/logout")
class UserLogout(MethodView):

    # Déconnexion : révoque le token JWT en l'ajoutant à la blocklist DB
    @jwt_required()
    def post(self):
        jti = get_jwt()["jti"]  # Identifiant unique du token actuel
        db.session.add(BlocklistModel(jti=jti))
        db.session.commit()

        return {"message": "Déconnexion réussie."}, 200
