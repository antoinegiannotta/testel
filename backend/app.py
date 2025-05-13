import os
import psycopg2
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Connexion à la base de données via les variables d’environnement
def get_db_connection():
    conn = psycopg2.connect(
        dbname=os.environ.get("POSTGRES_DB"),
        user=os.environ.get("POSTGRES_USER"),
        password=os.environ.get("POSTGRES_PASSWORD"),
        host=os.environ.get("DB_HOST", "localhost"),
        port=5432
    )
    return conn

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/messages", methods=["GET"])
def get_messages():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, content, created_at FROM messages ORDER BY created_at DESC;")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    messages = [{"id": r[0], "content": r[1], "created_at": r[2].isoformat()} for r in rows]
    return jsonify(messages), 200

@app.route("/messages", methods=["POST"])
def post_message():
    data = request.get_json()
    content = data.get("content")

    if not content:
        return jsonify({"error": "Message content is required"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO messages (content) VALUES (%s) RETURNING id, created_at;", (content,))
    msg_id, created_at = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"id": msg_id, "content": content, "created_at": created_at.isoformat()}), 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
