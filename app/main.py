from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.database import get_connection, init_db

app = FastAPI(title="QA SQL Practice API", version="1.0.0")


class UserCreate(BaseModel):
    name: str
    email: str


class PostCreate(BaseModel):
    title: str
    body: str
    user_id: int


@app.on_event("startup")
def startup_event():
    init_db()


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/users")
def list_users():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, name, email FROM users ORDER BY id ASC"
        ).fetchall()
        return [dict(row) for row in rows]


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


