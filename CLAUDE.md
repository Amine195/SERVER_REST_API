# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commandes

```bash
# Activer l'environnement virtuel (Windows)
.venv\Scripts\activate

# Lancer l'application
python app.py
# → http://localhost:5000
# → Swagger UI : http://localhost:5000/swagger-ui
```

Variables d'environnement optionnelles :

| Variable | Défaut | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite:///data.db` | URI de connexion à la base |
| `JWT_SECRET_KEY` | `"changez-moi-en-production"` | Clé de signature des tokens JWT |
| `CORS_ORIGINS` | `http://localhost:4200` | Origine(s) autorisée(s) par CORS |
| `FLASK_DEBUG` | `false` | Active le mode debug Flask |

## Architecture

API REST Flask pour la gestion de magasins et de produits, avec authentification JWT.

**Stack :** Flask 3.1 + flask-smorest (OpenAPI/Swagger auto) + SQLAlchemy 2.0 + Marshmallow 4 + flask-jwt-extended + flask-cors + SQLite

**Relations de données :**
- `Store` (1) → (N) `Product` (via `store_id` FK, cascade delete)
- `User` stocke les comptes ; `BlocklistModel` stocke les tokens révoqués

**Flux d'une requête :**
```
HTTP → JWT vérifié (app.py) → Blueprint (resources/) → Validation Marshmallow (schemas.py) → Méthode modèle (models/) → SQLAlchemy → SQLite
```

### Fichiers clés

| Fichier | Rôle |
|---|---|
| `app.py` | Factory `create_app()`, config ORM, gestion JWT, enregistrement des blueprints |
| `db.py` | Instance SQLAlchemy partagée |
| `schemas.py` | Schémas Marshmallow pour validation/sérialisation |
| `models/store.py` | Modèle ORM + méthodes `find_all`, `save_to_db`, `remove_from_db` |
| `models/product.py` | Modèle ORM + mêmes méthodes |
| `models/user.py` | Modèle ORM utilisateur + `save_to_db` |
| `models/blocklist.py` | Modèle ORM pour les tokens JWT révoqués (persistés en DB) |
| `resources/store.py` | Blueprint `stores` — CRUD `/store` (protégé JWT) |
| `resources/product.py` | Blueprint `products` — CRUD `/product` (protégé JWT) |
| `resources/user.py` | Blueprint `users` — `/register`, `/login`, `/logout` |

### Conventions

- Les messages d'erreur et descriptions API sont en **français**
- Le modèle `Store` a un nom **unique** (contrainte DB), géré avec `IntegrityError` → 400
- `Product` possède les champs `name`, `price` (Float) et `store_id` (FK obligatoire)
- Les `created_at` sont auto-générés côté modèle (`default=db.func.now()`)
- Les mots de passe sont hashés avec `pbkdf2_sha256` (passlib) — jamais stockés en clair
- La blocklist JWT est persistée en base de données (table `blocklist`) pour survivre aux redémarrages
- Tous les endpoints `/store` et `/product` nécessitent un token JWT valide (`@jwt_required()`)
- Ajouter un nouveau domaine métier = créer `models/xxx.py` + `resources/xxx.py` + schémas dans `schemas.py` + enregistrer le blueprint dans `create_app()`
