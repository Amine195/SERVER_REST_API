from marshmallow import Schema, fields


# --- Schémas de base (sans relations imbriquées) ---

class PlainStoreSchema(Schema):
    """Schéma minimal pour un magasin (sans ses produits)."""
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, error_messages={"required": "Le nom est requis."})
    created_at = fields.DateTime(dump_only=True)


class PlainProductSchema(Schema):
    """Schéma minimal pour un produit (sans son magasin)."""
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, error_messages={"required": "Le nom est requis."})
    price = fields.Float(required=True, error_messages={"required": "Le prix est requis."})
    created_at = fields.DateTime(dump_only=True)


# --- Schémas complets (avec relations imbriquées) ---

class StoreSchema(PlainStoreSchema):
    """Schéma complet d'un magasin, incluant la liste de ses produits."""
    products = fields.List(fields.Nested(PlainProductSchema), dump_only=True)


class ProductSchema(PlainProductSchema):
    """Schéma complet d'un produit, incluant son magasin parent."""
    # store_id : requis en entrée (POST/PUT), jamais renvoyé en sortie
    store_id = fields.Int(
        required=True,
        load_only=True,
        error_messages={"required": "L'identifiant du magasin est requis."}
    )
    store = fields.Nested(PlainStoreSchema, dump_only=True)


# --- Schéma utilisateur ---

class UserSchema(Schema):
    """Schéma pour l'inscription et la connexion d'un utilisateur."""
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True, error_messages={"required": "Le nom d'utilisateur est requis."})
    # Mot de passe : accepté en entrée uniquement, jamais renvoyé en réponse
    password = fields.Str(
        required=True,
        load_only=True,
        error_messages={"required": "Le mot de passe est requis."}
    )
