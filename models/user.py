from db import db


class UserModel(db.Model):
    """Représente un utilisateur de l'application."""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)  # Stocké hashé (pbkdf2_sha256)

    def save_to_db(self):
        """Ajoute ou met à jour l'utilisateur en base de données."""
        db.session.add(self)
        db.session.commit()
