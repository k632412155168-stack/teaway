"""
Lớp dữ liệu – SQLite (đi kèm Python, không cần cài thêm).
File database được tạo tự động tại instance/teaway.db khi chạy app lần đầu.
"""
import json
import sqlite3
from datetime import datetime

from flask import current_app, g
from werkzeug.security import generate_password_hash

import seed_data

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    bio TEXT DEFAULT '',
    prefs_json TEXT DEFAULT '{}',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tea_dna (
    user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    scores_json TEXT NOT NULL,
    profile_key TEXT NOT NULL,
    confidence INTEGER NOT NULL,
    unfolding INTEGER NOT NULL DEFAULT 0,
    prefs_json TEXT DEFAULT '{}',
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    name_en TEXT,
    description TEXT,
    category TEXT,
    base_tea TEXT,
    temperature TEXT,
    servings INTEGER DEFAULT 1,
    prep_minutes INTEGER,
    difficulty TEXT,
    featured INTEGER DEFAULT 0,
    color TEXT, accent TEXT,
    taste_json TEXT, tags_json TEXT, ingredients_json TEXT,
    brewing_json TEXT, steps_json TEXT,
    storage TEXT,
    status TEXT DEFAULT 'verified'
);

CREATE TABLE IF NOT EXISTS saved_recipes (
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    recipe_id INTEGER REFERENCES recipes(id) ON DELETE CASCADE,
    collection TEXT DEFAULT 'Đã lưu',
    created_at TEXT NOT NULL,
    PRIMARY KEY (user_id, recipe_id)
);

CREATE TABLE IF NOT EXISTS user_recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT DEFAULT '',
    base_recipe_id INTEGER REFERENCES recipes(id),
    parent_user_recipe_id INTEGER REFERENCES user_recipes(id),
    lineage_id INTEGER,
    version_label TEXT DEFAULT 'v1.0',
    category TEXT, tea_base TEXT, temperature TEXT,
    servings INTEGER DEFAULT 1,
    prep_minutes INTEGER DEFAULT 10,
    ingredients_json TEXT NOT NULL,
    steps_json TEXT DEFAULT '[]',
    taste_json TEXT DEFAULT '{}',
    brewing_json TEXT DEFAULT '{}',
    tags_json TEXT DEFAULT '[]',
    is_public INTEGER DEFAULT 0,
    challenge_slug TEXT,
    source_label TEXT DEFAULT 'Community Recipe',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS likes (
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    user_recipe_id INTEGER REFERENCES user_recipes(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, user_recipe_id)
);

CREATE TABLE IF NOT EXISTS comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_recipe_id INTEGER REFERENCES user_recipes(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    body TEXT NOT NULL,
    rating INTEGER,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS follows (
    follower_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    followee_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    PRIMARY KEY (follower_id, followee_id)
);

CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_recipe_id INTEGER, user_id INTEGER, reason TEXT, created_at TEXT
);

CREATE TABLE IF NOT EXISTS workshops (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT UNIQUE, name TEXT, summary TEXT, audience TEXT,
    content_json TEXT, duration TEXT, location TEXT, starts_at TEXT,
    capacity INTEGER, price INTEGER, takeaway TEXT, color TEXT, safety TEXT
);

CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workshop_id INTEGER REFERENCES workshops(id),
    user_id INTEGER,
    name TEXT NOT NULL, phone TEXT NOT NULL, email TEXT,
    seats INTEGER NOT NULL DEFAULT 1,
    note TEXT,
    status TEXT DEFAULT 'pending',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS challenges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT UNIQUE, name TEXT, description TEXT, reward TEXT, ends_at TEXT, rule TEXT
);

CREATE TABLE IF NOT EXISTS game_profiles (
    user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    state_json TEXT NOT NULL,
    xp INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    updated_at TEXT NOT NULL
);
"""


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(app):
    with app.app_context():
        db = get_db()
        db.executescript(SCHEMA)
        if db.execute("SELECT COUNT(*) FROM recipes").fetchone()[0] == 0:
            seed(db)
        db.commit()


def seed(db):
    for r in seed_data.RECIPES:
        db.execute(
            """INSERT INTO recipes (slug, name, name_en, description, category, base_tea, temperature, servings,
               prep_minutes, difficulty, featured, color, accent, taste_json, tags_json, ingredients_json,
               brewing_json, steps_json, storage) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (r["slug"], r["name"], r["name_en"], r["description"], r["category"], r["base_tea"],
             r["temperature"], r["servings"], r["prep_minutes"], r["difficulty"], r["featured"], r["color"],
             r["accent"], json.dumps(r["taste"]), json.dumps(r["tags"], ensure_ascii=False),
             json.dumps(r["ingredients"], ensure_ascii=False), json.dumps(r["brewing"], ensure_ascii=False),
             json.dumps(r["steps"], ensure_ascii=False), r["storage"]))

    for w in seed_data.WORKSHOPS:
        db.execute(
            """INSERT INTO workshops (slug, name, summary, audience, content_json, duration, location, starts_at,
               capacity, price, takeaway, color, safety) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (w["slug"], w["name"], w["summary"], w["audience"], json.dumps(w["content"], ensure_ascii=False),
             w["duration"], w["location"], w["starts_at"], w["capacity"], w["price"], w["takeaway"],
             w["color"], w.get("safety")))

    for c in seed_data.CHALLENGES:
        db.execute("INSERT INTO challenges (slug, name, description, reward, ends_at, rule) VALUES (?,?,?,?,?,?)",
                   (c["slug"], c["name"], c["description"], c["reward"], c["ends_at"], c["rule"]))

    # Tài khoản đội ngũ + tài khoản demo
    cur = db.execute("INSERT INTO users (name, email, password_hash, bio, created_at) VALUES (?,?,?,?,?)",
                     ("Tea Lab Team", "team@teaway.local", generate_password_hash("team-only-account-2026"),
                      "Đội ngũ thử nghiệm công thức.", now()))
    team_id = cur.lastrowid
    db.execute("INSERT INTO users (name, email, password_hash, bio, created_at) VALUES (?,?,?,?,?)",
               ("Demo Tea Lover", "demo@teaway.vn", generate_password_hash("tea12345"),
                "Tài khoản demo – đăng nhập để thử tính năng lưu và sáng tạo.", now()))

    slug_to_id = {row["slug"]: row["id"] for row in db.execute("SELECT id, slug FROM recipes")}
    for c in seed_data.COMMUNITY:
        cur = db.execute(
            """INSERT INTO user_recipes (user_id, title, description, base_recipe_id, version_label, category,
               tea_base, temperature, servings, prep_minutes, ingredients_json, steps_json, taste_json,
               tags_json, is_public, challenge_slug, created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (team_id, c["title"], c["description"], slug_to_id.get(c["base_slug"]) if c["base_slug"] else None,
             c["version_label"], c["category"], c["tea_base"], c["temperature"], 1, c["prep_minutes"],
             json.dumps(c["ingredients"], ensure_ascii=False), json.dumps(c["steps"], ensure_ascii=False),
             json.dumps(c["taste"]), json.dumps(c["tags"], ensure_ascii=False), 1, c["challenge"], now()))
        db.execute("UPDATE user_recipes SET lineage_id = ? WHERE id = ?", (cur.lastrowid, cur.lastrowid))
