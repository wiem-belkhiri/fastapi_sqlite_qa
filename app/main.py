from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Import de la connexion SQLite et de la logique d'initialisation de la base.
from app.database import get_connection, init_db

# Création de l'application FastAPI.
# Le titre et la version aident dans la documentation Swagger /docs.
app = FastAPI(title="QA SQL Practice API", version="1.0.0")


# Modèle Pydantic pour créer un utilisateur.
# Il décrit exactement les champs attendus dans le corps JSON.
class UserCreate(BaseModel): 
    name: str
    email: str


# Modèle Pydantic pour créer un post.
# On attend title, body et user_id.
class PostCreate(BaseModel):
    title: str
    body: str
    user_id: int


# Au démarrage de l'API, on initialise la base SQLite.
# Cela crée les tables si elles n'existent pas et ajoute des données de test.
@app.on_event("startup")
def startup_event():
    init_db()


# Route simple de contrôle pour vérifier que l'API est en ligne.
@app.get("/health")
def health_check():
    return {"status": "ok"}


# Route GET /users : lecture des utilisateurs.
# On exécute une requête SQL SELECT pour récupérer tous les utilisateurs triés par id.
@app.get("/users")
def list_users():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, name, email FROM users ORDER BY id ASC"
        ).fetchall()
        return [dict(row) for row in rows]


# Route GET /users/report : agrégation SQL.
# On récupère pour chaque utilisateur le nombre de posts associés grâce à un LEFT JOIN.
@app.get("/users/report")
def user_post_summary():
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT u.id, u.name, COUNT(p.id) AS post_count
            FROM users u
            LEFT JOIN posts p ON p.user_id = u.id
            GROUP BY u.id, u.name
            ORDER BY u.id ASC
            """
        ).fetchall()
        return [dict(row) for row in rows]


# Route GET /users/{user_id} : lecture d'un utilisateur précis.
# Equivalent d'un SELECT ... WHERE id = ? en SQL.
@app.get("/users/{user_id}")
def get_user(user_id: int):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, name, email FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="User not found")
        return dict(row)


# Route POST /users : création d'un utilisateur.
# Le payload est validé par le modèle UserCreate, puis on envoie un INSERT INTO.
@app.post("/users")
def create_user(user: UserCreate):
    with get_connection() as conn:
        try:
            cursor = conn.execute(
                "INSERT INTO users (name, email) VALUES (?, ?)",
                (user.name, user.email),
            )
            conn.commit()
            user_id = cursor.lastrowid
            return {"id": user_id, "name": user.name, "email": user.email}
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"User creation failed: {str(exc)}") from exc


# Route GET /posts : lecture des posts avec join sur la table users.
# On affiche le titre, le contenu, l'auteur et l'id utilisateur.
@app.get("/posts")
def list_posts():
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT p.id, p.title, p.body, p.user_id, u.name AS author_name
            FROM posts p
            INNER JOIN users u ON u.id = p.user_id
            ORDER BY p.id ASC
            """
        ).fetchall()
        return [dict(row) for row in rows]


# Route POST /posts : création d'un post.
# Avant d'insérer, on vérifie que l'utilisateur cible existe.
@app.post("/posts")
def create_post(post: PostCreate):
    with get_connection() as conn:
        user_exists = conn.execute(
            "SELECT id FROM users WHERE id = ?",
            (post.user_id,),
        ).fetchone()
        if user_exists is None:
            raise HTTPException(status_code=404, detail="User not found")

        cursor = conn.execute(
            "INSERT INTO posts (title, body, user_id) VALUES (?, ?, ?)",
            (post.title, post.body, post.user_id),
        )
        conn.commit()
        return {
            "id": cursor.lastrowid,
            "title": post.title,
            "body": post.body,
            "user_id": post.user_id,
        }


