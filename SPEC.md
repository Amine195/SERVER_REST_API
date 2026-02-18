# SPEC.md — Spécifications du projet STORE REST API

## Vue d'ensemble

API REST pour la gestion de magasins (`Store`) et de leurs produits (`Product`).
Chaque magasin peut contenir plusieurs produits. Un produit appartient obligatoirement à un magasin.
L'accès aux ressources est protégé par authentification JWT.

---

## Modèles de données

### Store (Magasin)

| Champ        | Type        | Contraintes              |
|--------------|-------------|--------------------------|
| `id`         | Integer     | PK, auto-incrémenté      |
| `name`       | String(80)  | Obligatoire, **unique**  |
| `created_at` | DateTime    | Auto-généré              |

### Product (Produit)

| Champ        | Type        | Contraintes                        |
|--------------|-------------|------------------------------------|
| `id`         | Integer     | PK, auto-incrémenté                |
| `name`       | String(80)  | Obligatoire                        |
| `price`      | Float       | Obligatoire                        |
| `store_id`   | Integer     | FK → `stores.id`, obligatoire      |
| `created_at` | DateTime    | Auto-généré                        |

**Relation :** `Store` (1) ↔ (N) `Product` — suppression en cascade

### User (Utilisateur)

| Champ      | Type        | Contraintes             |
|------------|-------------|-------------------------|
| `id`       | Integer     | PK, auto-incrémenté     |
| `username` | String(80)  | Obligatoire, **unique** |
| `password` | String(256) | Hash pbkdf2_sha256      |

### Blocklist (Tokens révoqués)

| Champ  | Type       | Contraintes         |
|--------|------------|---------------------|
| `id`   | Integer    | PK, auto-incrémenté |
| `jti`  | String(36) | UUID JWT, unique    |

---

## Authentification

Tous les endpoints `/store` et `/product` requièrent un token JWT dans le header :

```
Authorization: Bearer <access_token>
```

Le token est obtenu via `POST /login`. Il est révoqué via `POST /logout` (persisté en DB).

---

## Endpoints API

Base URL : `http://localhost:5000`
Documentation interactive : `http://localhost:5000/swagger-ui`

### Authentification

| Méthode | Route       | Auth | Description                          |
|---------|-------------|------|--------------------------------------|
| `POST`  | `/register` | Non  | Créer un compte utilisateur          |
| `POST`  | `/login`    | Non  | Connexion — retourne un token JWT    |
| `POST`  | `/logout`   | Oui  | Déconnexion — révoque le token       |

#### POST /register — Corps
```json
{ "username": "alice", "password": "monMotDePasse" }
```
#### Réponse (201)
```json
{ "message": "Utilisateur créé avec succès." }
```

#### POST /login — Corps
```json
{ "username": "alice", "password": "monMotDePasse" }
```
#### Réponse (200)
```json
{ "access_token": "eyJ..." }
```

---

### Stores

| Méthode  | Route             | Auth | Description                        |
|----------|-------------------|------|------------------------------------|
| `GET`    | `/store`          | Oui  | Lister tous les magasins           |
| `POST`   | `/store`          | Oui  | Créer un magasin                   |
| `GET`    | `/store/<id>`     | Oui  | Obtenir un magasin par ID          |
| `PUT`    | `/store/<id>`     | Oui  | Modifier un magasin                |
| `DELETE` | `/store/<id>`     | Oui  | Supprimer un magasin               |

#### POST /store — Corps
```json
{ "name": "Mon Magasin" }
```

#### Réponse (201)
```json
{
  "id": 1,
  "name": "Mon Magasin",
  "created_at": "2026-02-18T10:00:00",
  "products": []
}
```

---

### Products

| Méthode  | Route              | Auth | Description                        |
|----------|--------------------|------|------------------------------------|
| `GET`    | `/product`         | Oui  | Lister tous les produits           |
| `POST`   | `/product`         | Oui  | Créer un produit                   |
| `GET`    | `/product/<id>`    | Oui  | Obtenir un produit par ID          |
| `PUT`    | `/product/<id>`    | Oui  | Modifier un produit                |
| `DELETE` | `/product/<id>`    | Oui  | Supprimer un produit               |

#### POST /product — Corps
```json
{ "name": "Chaise", "price": 49.99, "store_id": 1 }
```

#### Réponse (201)
```json
{
  "id": 1,
  "name": "Chaise",
  "price": 49.99,
  "created_at": "2026-02-18T10:05:00",
  "store": { "id": 1, "name": "Mon Magasin", "created_at": "2026-02-18T10:00:00" }
}
```

---

## Codes de réponse HTTP

| Code | Signification                                              |
|------|------------------------------------------------------------|
| 200  | Succès (GET, PUT, logout)                                  |
| 201  | Ressource créée (POST store/product/register)              |
| 400  | Données invalides ou nom de magasin déjà existant          |
| 401  | Non authentifié (token manquant, expiré ou révoqué)        |
| 404  | Ressource non trouvée                                      |
| 409  | Conflit — nom d'utilisateur déjà pris                      |
| 422  | Validation échouée (champ obligatoire manquant)            |
| 500  | Erreur interne lors de l'écriture en base de données       |

---

## Validation

- `Store.name` : obligatoire, unique — doublon → 400
- `Product.name` : obligatoire
- `Product.price` : obligatoire, type Float
- `Product.store_id` : obligatoire, doit référencer un magasin existant — sinon → 500
- `User.username` : obligatoire, unique — doublon → 409
- `User.password` : obligatoire en entrée, jamais renvoyé en réponse
- Les champs `id` et `created_at` sont en lecture seule (ignorés en entrée)

---

## Configuration

| Variable d'env  | Défaut                        | Description                   |
|-----------------|-------------------------------|-------------------------------|
| `DATABASE_URL`  | `sqlite:///data.db`           | URI de connexion à la base    |
| `JWT_SECRET_KEY`| `changez-moi-en-production`   | Clé de signature JWT          |
| `FLASK_DEBUG`   | `false`                       | Mode debug Flask              |

---

## Stack technique

| Composant        | Version | Rôle                              |
|------------------|---------|-----------------------------------|
| Python           | 3.14    | Langage                           |
| Flask            | 3.1     | Framework web                     |
| flask-smorest    | 0.46    | Blueprints + génération OpenAPI   |
| SQLAlchemy       | 2.0     | ORM                               |
| flask-sqlalchemy | 3.1     | Intégration SQLAlchemy/Flask      |
| Marshmallow      | 4.x     | Validation et sérialisation       |
| flask-jwt-extended | 4.x   | Authentification JWT              |
| passlib          | —       | Hash sécurisé des mots de passe   |
| SQLite           | —       | Base de données (développement)   |
