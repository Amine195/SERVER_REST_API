from db import db


class StoreModel(db.Model):
    """Représente un magasin en base de données."""
    __tablename__ = "stores"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)  # Nom unique obligatoire
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())

    # Un magasin possède plusieurs produits ; suppression en cascade
    products = db.relationship(
        "ProductModel",
        back_populates="store",
        lazy="select",
        cascade="all, delete-orphan"
    )

    @classmethod
    def find_all(cls):
        """Retourne tous les magasins, triés du plus récent au plus ancien."""
        return cls.query.order_by(cls.created_at.desc()).all()

    def save_to_db(self):
        """Ajoute ou met à jour le magasin en base de données."""
        db.session.add(self)
        db.session.commit()

    def remove_from_db(self):
        """Supprime le magasin de la base de données."""
        db.session.delete(self)
        db.session.commit()
