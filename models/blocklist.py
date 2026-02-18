from db import db


class BlocklistModel(db.Model):
    """Stocke les JTI (JWT ID) des tokens révoqués lors d'une déconnexion.
    Permet de persister la liste noire entre les redémarrages du serveur.
    """
    __tablename__ = "blocklist"

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, unique=True)  # UUID du token JWT
