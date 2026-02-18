import os
from dotenv import load_dotenv

load_dotenv()

from flask import Flask, jsonify
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from flask_cors import CORS

# Base de données
from db import db
from models.blocklist import BlocklistModel

# Blueprints des ressources
from resources.store import blp as StoreBlueprint
from resources.product import blp as ProductBlueprint
from resources.user import blp as UserBlueprint

def create_app(db_url=None):
    """Fabrique de l'application Flask."""
    app = Flask(__name__)

    # --- CORS : autorise les requêtes depuis le frontend Angular ---
    CORS(app, resources={r"/*": {"origins": os.getenv("CORS_ORIGINS", "http://localhost:4200")}})

    # --- Configuration générale ---
    app.config["PROPAGATE_EXCEPTIONS"] = True  # Remonte les exceptions Flask vers l'API

    # --- Configuration OpenAPI / Swagger ---
    app.config["API_TITLE"] = "STORE REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

    # --- Configuration base de données ---
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL", "sqlite:///data.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialisation de SQLAlchemy avec l'application
    db.init_app(app)

    # Création des tables au démarrage (remplace before_first_request, supprimé en Flask 3)
    with app.app_context():
        db.create_all()

    # Initialisation de l'API flask-smorest (génère le Swagger automatiquement)
    api = Api(app)

    # --- Configuration JWT ---
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "8e4ad28fda6e9191bb19487bf00d5f7607643be0c14c25a5a449e93f5730800f")
    jwt = JWTManager(app)

    # Vérifie si le token est révoqué en interrogeant la base de données
    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        return BlocklistModel.query.filter_by(jti=jwt_payload["jti"]).first() is not None

    # Token révoqué (utilisateur déconnecté)
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify({"message": "Le token a été révoqué.", "error": "token_revoked"}), 401

    # Token expiré
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"message": "Le token a expiré.", "error": "token_expired"}), 401

    # Token malformé ou signature incorrecte
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({"message": "Token invalide.", "error": "token_invalid"}), 401

    # Aucun token fourni dans la requête
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({"message": "Token manquant.", "error": "authorization_required"}), 401
    
    # Token non frais (fresh) requis pour certaines opérations sensibles
    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return jsonify({"message": "Le token doit être frais (fresh).", "error": "fresh_token_required"}), 401

    # Enregistrement des blueprints
    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(ProductBlueprint)
    api.register_blueprint(UserBlueprint)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=os.getenv("FLASK_DEBUG", "false").lower() == "true", host="0.0.0.0")
