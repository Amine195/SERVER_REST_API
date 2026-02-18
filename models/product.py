from db import db


class ProductModel(db.Model):
    """Représente un produit appartenant à un magasin."""
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())

    # Clé étrangère vers le magasin parent ; suppression en cascade côté DB
    store_id = db.Column(
        db.Integer,
        db.ForeignKey("stores.id", ondelete="CASCADE"),
        nullable=False
    )

    # Relation inverse vers StoreModel
    store = db.relationship("StoreModel", back_populates="products")

    @classmethod
    def find_all(cls):
        """Retourne tous les produits, triés du plus récent au plus ancien."""
        return cls.query.order_by(cls.created_at.desc()).all()

    def save_to_db(self):
        """Ajoute ou met à jour le produit en base de données."""
        db.session.add(self)
        db.session.commit()

    def remove_from_db(self):
        """Supprime le produit de la base de données."""
        db.session.delete(self)
        db.session.commit()
