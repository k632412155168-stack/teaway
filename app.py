"""
TeaWay – A Digital-first Tea Lifestyle & Creation Platform
Explore Tea. Create Your Way.

Chạy:  python app.py   →  mở http://127.0.0.1:5001
Tài khoản demo:  demo@teaway.vn / tea12345
"""
import json
import os
import re
import unicodedata
from datetime import datetime
from functools import wraps

from flask import (Flask, abort, flash, g, jsonify, redirect, render_template, request, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash

import db as database
import engine
import tea_dna
from db import get_db, now
from seed_data import CATALOG

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(BASE_DIR, "instance"), exist_ok=True)

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get("SECRET_KEY", "teaway-dev-secret-change-me"),
    DATABASE=os.path.join(BASE_DIR, "instance", "teaway.db"),
    SITE_NAME="TeaWay",
    TAGLINE="Explore Tea. Create Your Way.",
)
app.teardown_appcontext(database.close_db)
database.init_db(app)

TEMP_LABELS = {"iced": "Lạnh", "hot": "Nóng", "cold_brew": "Cold Brew"}
DIFF_LABELS = {"Easy": "Dễ", "Medium": "Trung bình", "Advanced": "Nâng cao"}
ROLE_LABELS = {"tea": "Trà nền", "sweetener": "Tạo ngọt", "acid": "Tạo chua", "fruit": "Trái cây",
               "milk": "Sữa/béo", "herb": "Thảo mộc/hoa", "water": "Nước", "ice": "Đá"}
TEA_TYPES = ["Green", "Black", "Oolong", "White", "Matcha", "Herbal"]
FLAVORS = ["Sweet", "Sour", "Bitter", "Floral", "Fruity", "Roasted"]
INGREDIENT_KEYS = ["Đào", "Vải", "Xoài", "Dâu", "Chanh", "Tắc", "Cam", "Sữa", "Mật ong", "Bạc hà", "Sả"]
BUDGETS = [("u15", "Dưới 15K"), ("15-30", "15–30K"), ("30-50", "30–50K"), ("o50", "Trên 50K")]
TIMES = [("5", "Dưới 5 phút"), ("10", "Dưới 10 phút"), ("20", "Dưới 20 phút"), ("30", "Dưới 30 phút")]


# =========================================================================== #
# Tiện ích chung
# =========================================================================== #
def strip_accents(s):
    s = (s or "").replace("đ", "d").replace("Đ", "D")
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").lower()


def loads(s, default):
    try:
        return json.loads(s) if s else default
    except (TypeError, ValueError):
        return default


def taste_tags(taste):
    tags = []
    if taste.get("sweetness", 0) >= 60:
        tags.append("Sweet")
    if taste.get("sweetness", 100) <= 30:
        tags.append("Less sugar")
    if taste.get("acidity", 0) >= 60:
        tags.append("Sour")
    if taste.get("bitterness", 0) >= 55:
        tags.append("Bitter")
    if taste.get("aroma", 50) >= 65:
        tags.append("Fruity")
    if taste.get("aroma", 50) <= 30:
        tags.append("Floral")
    if taste.get("milk", 0) >= 60:
        tags.append("Creamy")
    return tags


def load_recipe(row):
    r = dict(row)
    r["taste"] = loads(r.pop("taste_json"), {})
    r["tags"] = loads(r.pop("tags_json"), [])
    r["ingredients"] = loads(r.pop("ingredients_json"), [])
    r["brewing"] = loads(r.pop("brewing_json"), {})
    r["steps"] = loads(r.pop("steps_json"), [])
    r.update(engine.recipe_flags(r["ingredients"]))
    r["cost_per_serving"] = engine.cost_per_serving(r)
    r["volume_ml"] = engine.nice(engine.liquid_volume(r["ingredients"]) / max(1, r["servings"]))
    r["flavor_tags"] = taste_tags(r["taste"])
    if "Roasted" in r["tags"]:
        r["flavor_tags"].append("Roasted")
    r["kind"] = "recipe"
    return r


def all_recipes():
    return [load_recipe(x) for x in get_db().execute("SELECT * FROM recipes ORDER BY featured DESC, id")]


def get_recipe_by_slug(slug):
    row = get_db().execute("SELECT * FROM recipes WHERE slug = ?", (slug,)).fetchone()
    if not row:
        abort(404)
    return load_recipe(row)


def get_recipe_by_id(rid):
    row = get_db().execute("SELECT * FROM recipes WHERE id = ?", (rid,)).fetchone()
    return load_recipe(row) if row else None


def load_creation(row):
    c = dict(row)
    c["ingredients"] = loads(c.pop("ingredients_json"), [])
    c["steps"] = loads(c.pop("steps_json"), [])
    c["taste"] = loads(c.pop("taste_json"), {})
    c["brewing"] = loads(c.pop("brewing_json"), {})
    c["tags"] = loads(c.pop("tags_json"), [])
    c.update(engine.recipe_flags(c["ingredients"]))
    c["cost_per_serving"] = engine.cost_per_serving(c)
    c["volume_ml"] = engine.nice(engine.liquid_volume(c["ingredients"]) / max(1, c["servings"] or 1))
    c["flavor_tags"] = taste_tags(c["taste"])
    c["kind"] = "creation"
    c["name"] = c["title"]
    c["color"], c["accent"] = palette_for(c["taste"])
    return c


def palette_for(taste):
    """Màu minh họa cho công thức cộng đồng dựa trên hồ sơ vị."""
    if taste.get("milk", 0) >= 60:
        return "#CFAE7F", "#F4E6D2"
    if taste.get("acidity", 0) >= 70:
        return "#C9465B", "#F4BAC3"
    if taste.get("aroma", 50) >= 70:
        return "#E39B62", "#F7D7B5"
    if taste.get("strength", 0) >= 70:
        return "#7B4A2A", "#E2C7A8"
    if taste.get("aroma", 50) <= 30:
        return "#E3BFC0", "#F8EAEA"
    return "#93C29E", "#DDEFE1"


CREATION_SELECT = """
SELECT ur.*, u.name AS author_name,
       (SELECT COUNT(*) FROM likes l WHERE l.user_recipe_id = ur.id) AS like_count,
       (SELECT COUNT(*) FROM comments c WHERE c.user_recipe_id = ur.id) AS comment_count
FROM user_recipes ur JOIN users u ON u.id = ur.user_id
"""


def get_creation(cid):
    row = get_db().execute(CREATION_SELECT + " WHERE ur.id = ?", (cid,)).fetchone()
    if not row:
        abort(404)
    c = load_creation(row)
    user = g.get("user")
    if not c["is_public"] and (not user or user["id"] != c["user_id"]):
        abort(404)
    return c


def vnd(x):
    try:
        return "{:,.0f}".format(float(x)).replace(",", ".") + "đ"
    except (TypeError, ValueError):
        return "–"


def fmt_qty(x):
    return engine.nice(x)


def fmt_date(s, fmt="%d/%m/%Y"):
    for pattern in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, pattern).strftime(fmt)
        except (TypeError, ValueError):
            continue
    return s


app.jinja_env.filters.update(vnd=vnd, qty=fmt_qty, date=fmt_date,
                             temp=lambda t: TEMP_LABELS.get(t, t), diff=lambda d: DIFF_LABELS.get(d, d),
                             role=lambda r: ROLE_LABELS.get(r, r))


# =========================================================================== #
# Người dùng & phiên đăng nhập
# =========================================================================== #
@app.before_request
def load_user():
    g.user = None
    uid = session.get("user_id")
    if uid:
        row = get_db().execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()
        if row:
            g.user = dict(row)
            g.user["prefs"] = loads(g.user.get("prefs_json"), {})
        else:
            session.pop("user_id", None)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not g.user:
            flash("Bạn cần đăng nhập để dùng tính năng này.", "info")
            return redirect(url_for("login", next=request.full_path))
        return view(*args, **kwargs)
    return wrapped


def get_user_dna():
    """Tea DNA của người dùng (DB nếu đã đăng nhập, session nếu là khách)."""
    if "dna" in g:
        return g.dna
    dna = None
    if g.user:
        row = get_db().execute("SELECT * FROM tea_dna WHERE user_id = ?", (g.user["id"],)).fetchone()
        if row:
            dna = {"scores": loads(row["scores_json"], {}), "profile_key": row["profile_key"],
                   "confidence": row["confidence"], "unfolding": bool(row["unfolding"]),
                   "prefs": loads(row["prefs_json"], {}), "updated_at": row["updated_at"]}
    if not dna and session.get("dna"):
        dna = session["dna"]
    if dna:
        dna["profile"] = tea_dna.profile_info(dna["profile_key"])
    g.dna = dna
    return dna


def personalized_vector():
    """
    Kết hợp Tea DNA (khẩu vị khai báo) với hành vi thực tế (công thức đã lưu).
    Nếu người dùng đã lưu ≥ 3 công thức: 60% DNA + 40% trung bình hồ sơ vị đã lưu.
    """
    dna = get_user_dna()
    base = dict(dna["scores"]) if dna else None
    if not g.user:
        return base
    rows = get_db().execute("""SELECT r.taste_json FROM saved_recipes s JOIN recipes r ON r.id = s.recipe_id
                               WHERE s.user_id = ?""", (g.user["id"],)).fetchall()
    tastes = [loads(r["taste_json"], {}) for r in rows]
    if len(tastes) < 3:
        return base
    avg = {a: sum(t.get(a, 50) for t in tastes) / len(tastes) for a in engine.AXES}
    if not base:
        return avg
    return {a: round(0.6 * base.get(a, 50) + 0.4 * avg[a]) for a in engine.AXES}


def user_avoid():
    avoid = set()
    dna = get_user_dna()
    if dna:
        avoid |= set(dna.get("prefs", {}).get("avoid", []))
    if g.user:
        avoid |= set(g.user["prefs"].get("avoid", []))
    return avoid


def respects_constraints(recipe, avoid):
    names = " ".join(strip_accents(i["name"]) for i in recipe["ingredients"])
    if "milk" in avoid and not recipe["dairy_free"]:
        return False
    if "caffeine" in avoid and recipe["caffeine"]:
        return False
    if "honey" in avoid and "mat ong" in names:
        return False
    if "sour" in avoid and recipe["taste"].get("acidity", 0) >= 70:
        return False
    for word in (g.user["prefs"].get("avoid_ingredients", []) if g.user else []):
        if word and strip_accents(word) in names:
            return False
    return True


def recommend(limit=4, exclude_ids=()):
    vec = personalized_vector()
    if not vec:
        return []
    avoid = user_avoid()
    out = []
    for r in all_recipes():
        if r["id"] in exclude_ids or not respects_constraints(r, avoid):
            continue
        r["match"] = engine.compatibility(vec, r["taste"])
        out.append(r)
    out.sort(key=lambda r: -r["match"])
    return out[:limit]


@app.context_processor
def inject_globals():
    return {
        "site_name": app.config["SITE_NAME"], "tagline": app.config["TAGLINE"],
        "current_user": g.get("user"), "user_dna": get_user_dna(),
        "nav": request.endpoint or "", "year": datetime.now().year,
    }


# =========================================================================== #
# Trang chủ & giới thiệu
# =========================================================================== #
@app.route("/")
def home():
    recipes = all_recipes()
    vec = personalized_vector()
    for r in recipes:
        r["match"] = engine.compatibility(vec, r["taste"]) if vec else None
    featured = [r for r in recipes if r["featured"]][:4]
    creations = [load_creation(x) for x in get_db().execute(
        CREATION_SELECT + " WHERE ur.is_public = 1 ORDER BY ur.created_at DESC LIMIT 3")]
    workshops = [dict(w) for w in get_db().execute("SELECT * FROM workshops ORDER BY starts_at LIMIT 3")]
    return render_template("index.html", featured=featured, creations=creations, workshops=workshops,
                           recs=recommend(4))


@app.route("/about")
def about():
    return render_template("about.html")


# =========================================================================== #
# EXPLORE – Tea Library
# =========================================================================== #
def filter_recipes(recipes, args):
    q = strip_accents(args.get("q", "").strip())
    teas, temps = args.getlist("tea"), args.getlist("temp")
    flavors, ingrs = args.getlist("flavor"), args.getlist("ingredient")
    diffs, prefs = args.getlist("difficulty"), args.getlist("pref")
    max_time, budget, caffeine = args.get("time"), args.get("budget"), args.get("caffeine")

    def ok(r):
        hay = strip_accents(" ".join([r["name"], r.get("name_en") or "", r.get("description") or "",
                                      " ".join(i["name"] for i in r["ingredients"]), " ".join(r["tags"])]))
        if q and not all(word in hay for word in q.split()):
            return False
        if teas and r["base_tea"] not in teas:
            return False
        if temps and r["temperature"] not in temps:
            return False
        if flavors and not all(f in r["flavor_tags"] for f in flavors):
            return False
        names = strip_accents(" ".join(i["name"] for i in r["ingredients"]))
        if ingrs and not all(strip_accents(k) in names for k in ingrs):
            return False
        if diffs and r["difficulty"] not in diffs:
            return False
        if max_time and r["prep_minutes"] > int(max_time):
            return False
        c = r["cost_per_serving"]
        if budget == "u15" and c >= 15000 or budget == "15-30" and not 15000 <= c < 30000 \
                or budget == "30-50" and not 30000 <= c < 50000 or budget == "o50" and c < 50000:
            return False
        if caffeine == "yes" and not r["caffeine"] or caffeine == "no" and r["caffeine"]:
            return False
        if "dairy_free" in prefs and not r["dairy_free"]:
            return False
        if "vegan" in prefs and not r["vegan"]:
            return False
        if "less_sugar" in prefs and r["taste"].get("sweetness", 100) > 40:
            return False
        return True

    return [r for r in recipes if ok(r)]


@app.route("/explore")
def explore():
    recipes = all_recipes()
    vec = personalized_vector()
    for r in recipes:
        r["match"] = engine.compatibility(vec, r["taste"]) if vec else None
    results = filter_recipes(recipes, request.args)
    sort = request.args.get("sort", "match" if vec else "featured")
    if sort == "match" and vec:
        results.sort(key=lambda r: -(r["match"] or 0))
    elif sort == "cost":
        results.sort(key=lambda r: r["cost_per_serving"])
    elif sort == "time":
        results.sort(key=lambda r: r["prep_minutes"])
    active = sum(len(request.args.getlist(k)) for k in request.args if k not in ("sort", "q"))
    return render_template("explore.html", results=results, total=len(recipes), args=request.args,
                           tea_types=TEA_TYPES, flavors=FLAVORS, ingredient_keys=INGREDIENT_KEYS,
                           budgets=BUDGETS, times=TIMES, temp_labels=TEMP_LABELS, diff_labels=DIFF_LABELS,
                           sort=sort, active_filters=active)


@app.route("/recipes/<slug>")
def recipe_detail(slug):
    r = get_recipe_by_slug(slug)
    dna = get_user_dna()
    r["match"] = engine.compatibility(personalized_vector(), r["taste"]) if dna or g.user else None
    saved, collections = None, []
    if g.user:
        saved = get_db().execute("SELECT collection FROM saved_recipes WHERE user_id=? AND recipe_id=?",
                                 (g.user["id"], r["id"])).fetchone()
        collections = [x["collection"] for x in get_db().execute(
            "SELECT DISTINCT collection FROM saved_recipes WHERE user_id = ?", (g.user["id"],))]
    variants = [load_creation(x) for x in get_db().execute(
        CREATION_SELECT + " WHERE ur.base_recipe_id = ? AND ur.is_public = 1 ORDER BY ur.created_at DESC LIMIT 3",
        (r["id"],))]
    similar = sorted((x for x in all_recipes() if x["id"] != r["id"]),
                     key=lambda x: -engine.compatibility(r["taste"], x["taste"]))[:3]
    return render_template("recipe_detail.html", r=r, saved=saved, collections=collections,
                           variants=variants, similar=similar, axes=tea_dna.AXES)


@app.route("/recipes/<slug>/save", methods=["POST"])
@login_required
def save_recipe(slug):
    r = get_recipe_by_slug(slug)
    db = get_db()
    if request.form.get("action") == "remove":
        db.execute("DELETE FROM saved_recipes WHERE user_id=? AND recipe_id=?", (g.user["id"], r["id"]))
        flash("Đã bỏ lưu công thức.", "info")
    else:
        coll = (request.form.get("collection") or "Đã lưu").strip()[:40] or "Đã lưu"
        db.execute("""INSERT INTO saved_recipes (user_id, recipe_id, collection, created_at) VALUES (?,?,?,?)
                      ON CONFLICT(user_id, recipe_id) DO UPDATE SET collection = excluded.collection""",
                   (g.user["id"], r["id"], coll, now()))
        flash(f"Đã lưu vào bộ sưu tập “{coll}”.", "success")
    db.commit()
    return redirect(request.referrer or url_for("recipe_detail", slug=slug))


# =========================================================================== #
# CREATE – Smart Recipe
# =========================================================================== #
def smart_payload(r):
    return {
        "ingredients": r["ingredients"], "taste": r["taste"], "brewing": r.get("brewing") or {},
        "servings": r.get("servings") or 1,
    }


@app.route("/recipes/<slug>/customize")
def smart_recipe(slug):
    r = get_recipe_by_slug(slug)
    return render_smart(r, source="recipe", source_id=r["id"])


@app.route("/creations/<int:cid>/customize")
def smart_creation(cid):
    c = get_creation(cid)
    return render_smart(c, source="creation", source_id=c["id"])


def render_smart(r, source, source_id):
    sliders = {k: engine.SLIDERS[k] for k in engine.available_sliders(r["ingredients"])}
    subs = engine.substitution_options(r["ingredients"])
    initial = engine.adjust(smart_payload(r), servings=1)
    return render_template("smart_recipe.html", r=r, sliders=sliders, subs=subs, initial=initial,
                           source=source, source_id=source_id, axes=tea_dna.AXES)


def resolve_source(source, sid):
    if source == "recipe":
        r = get_recipe_by_id(int(sid))
        if not r:
            abort(404)
        return r
    return get_creation(int(sid))


@app.route("/api/adjust", methods=["POST"])
def api_adjust():
    data = request.get_json(silent=True) or {}
    r = resolve_source(data.get("source"), data.get("id"))
    result = engine.adjust(smart_payload(r), servings=data.get("servings", 1), sliders=data.get("sliders"),
                           keep_volume=bool(data.get("keep_volume", True)), substitutions=data.get("subs"))
    return jsonify(result)


def version_label(lineage_labels, major=False):
    best = (1, 0)
    for lab in lineage_labels:
        m = re.match(r"v(\d+)\.(\d+)", lab or "")
        if m:
            best = max(best, (int(m.group(1)), int(m.group(2))))
    return f"v{best[0] + 1}.0" if major else f"v{best[0]}.{best[1] + 1}"


def lineage_for(db, user_id, base_recipe_id=None, parent=None):
    """Trả về (lineage_id hoặc None, nhãn phiên bản kế tiếp, parent_user_recipe_id)."""
    if parent and parent["user_id"] == user_id:
        labels = [x[0] for x in db.execute("SELECT version_label FROM user_recipes WHERE lineage_id = ?",
                                           (parent["lineage_id"],))]
        return parent["lineage_id"], labels, parent["id"]
    if parent:  # Tạo phiên bản từ công thức của người khác → nhánh mới, ghi nhận tác giả gốc
        return None, None, parent["id"]
    if base_recipe_id:
        row = db.execute("""SELECT lineage_id FROM user_recipes WHERE user_id=? AND base_recipe_id=?
                            AND parent_user_recipe_id IS NULL ORDER BY id LIMIT 1""",
                         (user_id, base_recipe_id)).fetchone()
        if row:
            labels = [x[0] for x in db.execute("SELECT version_label FROM user_recipes WHERE lineage_id = ?",
                                               (row["lineage_id"],))]
            return row["lineage_id"], labels, None
        return None, ["v1.0"], None  # Công thức gốc được coi là v1.0
    return None, None, None


def insert_creation(db, data):
    cur = db.execute(
        """INSERT INTO user_recipes (user_id, title, description, base_recipe_id, parent_user_recipe_id,
           lineage_id, version_label, category, tea_base, temperature, servings, prep_minutes,
           ingredients_json, steps_json, taste_json, brewing_json, tags_json, is_public, challenge_slug,
           created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (data["user_id"], data["title"], data.get("description", ""), data.get("base_recipe_id"),
         data.get("parent_user_recipe_id"), data.get("lineage_id"), data["version_label"],
         data.get("category"), data.get("tea_base"), data.get("temperature"), data.get("servings", 1),
         data.get("prep_minutes", 10), json.dumps(data["ingredients"], ensure_ascii=False),
         json.dumps(data.get("steps", []), ensure_ascii=False), json.dumps(data.get("taste", {})),
         json.dumps(data.get("brewing", {}), ensure_ascii=False),
         json.dumps(data.get("tags", []), ensure_ascii=False), int(bool(data.get("is_public"))),
         data.get("challenge_slug") or None, now()))
    new_id = cur.lastrowid
    if not data.get("lineage_id"):
        db.execute("UPDATE user_recipes SET lineage_id = ? WHERE id = ?", (new_id, new_id))
    return new_id


@app.route("/api/save-version", methods=["POST"])
def api_save_version():
    if not g.user:
        return jsonify({"ok": False, "login": url_for("login")}), 401
    data = request.get_json(silent=True) or {}
    source = resolve_source(data.get("source"), data.get("id"))
    res = engine.adjust(smart_payload(source), servings=data.get("servings", 1), sliders=data.get("sliders"),
                        keep_volume=bool(data.get("keep_volume", True)), substitutions=data.get("subs"))
    db = get_db()
    if source["kind"] == "recipe":
        lineage_id, labels, parent_id = lineage_for(db, g.user["id"], base_recipe_id=source["id"])
        base_id = source["id"]
    else:
        lineage_id, labels, parent_id = lineage_for(db, g.user["id"], parent=source)
        base_id = source.get("base_recipe_id")
    label = version_label(labels, major=bool(data.get("major"))) if labels else "v1.0"
    note = (data.get("note") or "").strip()[:60]
    base_name = source["name"]
    title = (data.get("title") or "").strip()[:80] or f"{base_name} {label}" + (f" – {note}" if note else "")
    steps = list(source["steps"])
    if res["notes"]:
        steps.append("Ghi chú điều chỉnh: " + " ".join(res["notes"]))
    ingredients = [{"name": i["name"], "qty": i["qty"], "unit": i["unit"], "role": i["role"],
                    "scale": i["scale"]} for i in res["ingredients"]]
    new_id = insert_creation(db, {
        "user_id": g.user["id"], "title": title, "description": note or f"Phiên bản cá nhân hóa từ {base_name}.",
        "base_recipe_id": base_id, "parent_user_recipe_id": parent_id, "lineage_id": lineage_id,
        "version_label": label, "category": source.get("category"),
        "tea_base": source.get("base_tea") or source.get("tea_base"), "temperature": source.get("temperature"),
        "servings": res["servings"], "prep_minutes": source.get("prep_minutes") or 10,
        "ingredients": ingredients, "steps": steps, "taste": res["taste"], "brewing": res["brewing"],
        "tags": source.get("tags", []), "is_public": data.get("is_public"),
    })
    db.commit()
    return jsonify({"ok": True, "id": new_id, "label": label, "url": url_for("creation_detail", cid=new_id)})


# =========================================================================== #
# CREATE – Recipe Studio
# =========================================================================== #
@app.route("/create")
def create_home():
    lineages = []
    if g.user:
        rows = [load_creation(x) for x in get_db().execute(
            CREATION_SELECT + " WHERE ur.user_id = ? ORDER BY ur.lineage_id, ur.id", (g.user["id"],))]
        grouped = {}
        for c in rows:
            grouped.setdefault(c["lineage_id"], []).append(c)
        lineages = sorted(grouped.values(), key=lambda v: v[-1]["created_at"], reverse=True)
    return render_template("create.html", recipes=all_recipes(), lineages=lineages)


@app.route("/create/studio", methods=["GET", "POST"])
@login_required
def studio():
    db = get_db()
    mode, prefill, parent, base = "new", None, None, None
    edit_id, fork_id, from_slug = request.values.get("edit"), request.values.get("fork"), request.values.get("from")

    if edit_id:
        parent = get_creation(int(edit_id))
        if parent["user_id"] != g.user["id"]:
            abort(403)
        mode, prefill = "edit", parent
    elif fork_id:
        parent = get_creation(int(fork_id))
        mode, prefill = "fork", parent
    elif from_slug:
        base = get_recipe_by_slug(from_slug)
        mode, prefill = "from", base

    challenges = [dict(c) for c in db.execute("SELECT * FROM challenges ORDER BY ends_at")]

    if request.method == "POST":
        f = request.form
        ingredients = []
        for name, qty, unit, role in zip(f.getlist("ing_name"), f.getlist("ing_qty"), f.getlist("ing_unit"),
                                         f.getlist("ing_role")):
            name = name.strip()
            try:
                q = float(qty.replace(",", "."))
            except (ValueError, AttributeError):
                q = 0
            if name and q > 0:
                ing = {"name": name[:60], "qty": engine.nice(q), "unit": unit if unit in ("ml", "g") else "ml",
                       "role": role if role in ROLE_LABELS else "herb"}
                if ing["role"] == "herb":
                    ing["scale"] = "sublinear"
                ingredients.append(ing)
        title = f.get("title", "").strip()[:80]
        errors = []
        if not title:
            errors.append("Hãy đặt tên cho công thức.")
        if not ingredients:
            errors.append("Công thức cần ít nhất một nguyên liệu có định lượng.")
        taste = {}
        for axis in list(tea_dna.AXES) + ["milk"]:
            try:
                taste[axis] = max(0, min(100, int(f.get(f"taste_{axis}", 50))))
            except ValueError:
                taste[axis] = 50
        challenge = f.get("challenge") or None
        if challenge and not errors:
            rule = db.execute("SELECT rule FROM challenges WHERE slug = ?", (challenge,)).fetchone()
            cost = engine.cost_of(ingredients) / max(1, int(f.get("servings") or 1))
            if rule and rule["rule"] == "cost_under_30k" and cost >= 30000:
                errors.append(f"Thử thách Create Under 30K yêu cầu chi phí dưới 30.000đ/ly (hiện {vnd(cost)}).")
            if rule and rule["rule"] == "less_sugar" and taste["sweetness"] > 40:
                errors.append("Less Sugar Challenge yêu cầu Sweetness ≤ 40.")
            if challenge and not f.get("is_public"):
                errors.append("Bài dự thi cần được đăng công khai.")
        if errors:
            for e in errors:
                flash(e, "error")
            prefill = {"title": title, "description": f.get("description", ""), "ingredients": ingredients,
                       "steps": [s for s in f.get("steps", "").splitlines() if s.strip()], "taste": taste,
                       "category": f.get("category"), "tea_base": f.get("tea_base"),
                       "temperature": f.get("temperature"), "prep_minutes": f.get("prep_minutes"),
                       "servings": f.get("servings"), "tags": [t.strip() for t in f.get("tags", "").split(",")],
                       "is_public": f.get("is_public"), "challenge_slug": challenge}
            return render_template("studio.html", mode=mode, prefill=prefill, parent=parent, base=base,
                                   catalog=CATALOG, roles=ROLE_LABELS, challenges=challenges, posted=True,
                                   axes=tea_dna.AXES, temp_labels=TEMP_LABELS, tea_types=TEA_TYPES)

        if mode in ("edit", "fork"):
            lineage_id, labels, parent_id = lineage_for(db, g.user["id"], parent=parent)
            base_id = parent.get("base_recipe_id")
        elif mode == "from":
            lineage_id, labels, parent_id = lineage_for(db, g.user["id"], base_recipe_id=base["id"])
            base_id = base["id"]
        else:
            lineage_id, labels, parent_id, base_id = None, None, None, None
        label = version_label(labels, major=bool(f.get("major"))) if labels else "v1.0"
        try:
            servings = max(1, min(20, int(f.get("servings") or 1)))
            prep = max(1, min(600, int(f.get("prep_minutes") or 10)))
        except ValueError:
            servings, prep = 1, 10
        new_id = insert_creation(db, {
            "user_id": g.user["id"], "title": title, "description": f.get("description", "").strip()[:400],
            "base_recipe_id": base_id, "parent_user_recipe_id": parent_id, "lineage_id": lineage_id,
            "version_label": label, "category": f.get("category"), "tea_base": f.get("tea_base"),
            "temperature": f.get("temperature"), "servings": servings, "prep_minutes": prep,
            "ingredients": ingredients, "steps": [s.strip() for s in f.get("steps", "").splitlines() if s.strip()],
            "taste": taste, "tags": [t.strip() for t in f.get("tags", "").split(",") if t.strip()][:6],
            "is_public": f.get("is_public"), "challenge_slug": challenge,
            "brewing": (prefill or {}).get("brewing", {}) if mode != "new" else {},
        })
        db.commit()
        flash(f"Đã lưu “{title}” ({label}).", "success")
        return redirect(url_for("creation_detail", cid=new_id))

    return render_template("studio.html", mode=mode, prefill=prefill, parent=parent, base=base, catalog=CATALOG,
                           roles=ROLE_LABELS, challenges=challenges, axes=tea_dna.AXES, temp_labels=TEMP_LABELS,
                           tea_types=TEA_TYPES, preselect=request.args.get("challenge"))


@app.route("/creations/<int:cid>")
def creation_detail(cid):
    c = get_creation(cid)
    db = get_db()
    parent, parent_kind = None, None
    if c["parent_user_recipe_id"]:
        row = db.execute(CREATION_SELECT + " WHERE ur.id = ?", (c["parent_user_recipe_id"],)).fetchone()
        if row:
            parent, parent_kind = load_creation(row), "creation"
    elif c["base_recipe_id"]:
        parent, parent_kind = get_recipe_by_id(c["base_recipe_id"]), "recipe"
    diff = engine.diff_ingredients(parent["ingredients"], c["ingredients"]) if parent else []
    versions = [load_creation(x) for x in db.execute(
        CREATION_SELECT + " WHERE ur.lineage_id = ? AND (ur.is_public = 1 OR ur.user_id = ?) ORDER BY ur.id",
        (c["lineage_id"], g.user["id"] if g.user else -1))]
    comments = db.execute("""SELECT c.*, u.name FROM comments c JOIN users u ON u.id = c.user_id
                             WHERE c.user_recipe_id = ? ORDER BY c.created_at""", (cid,)).fetchall()
    liked = following = False
    if g.user:
        liked = bool(db.execute("SELECT 1 FROM likes WHERE user_id=? AND user_recipe_id=?",
                                (g.user["id"], cid)).fetchone())
        following = bool(db.execute("SELECT 1 FROM follows WHERE follower_id=? AND followee_id=?",
                                    (g.user["id"], c["user_id"])).fetchone())
    challenge = db.execute("SELECT * FROM challenges WHERE slug = ?", (c["challenge_slug"],)).fetchone() \
        if c["challenge_slug"] else None
    vec = personalized_vector()
    c["match"] = engine.compatibility(vec, c["taste"]) if vec else None
    return render_template("creation_detail.html", c=c, parent=parent, parent_kind=parent_kind, diff=diff,
                           versions=versions, comments=comments, liked=liked, following=following,
                           challenge=challenge, axes=tea_dna.AXES)


@app.route("/creations/<int:cid>/like", methods=["POST"])
@login_required
def like_creation(cid):
    get_creation(cid)
    db = get_db()
    if db.execute("SELECT 1 FROM likes WHERE user_id=? AND user_recipe_id=?", (g.user["id"], cid)).fetchone():
        db.execute("DELETE FROM likes WHERE user_id=? AND user_recipe_id=?", (g.user["id"], cid))
    else:
        db.execute("INSERT INTO likes (user_id, user_recipe_id) VALUES (?,?)", (g.user["id"], cid))
    db.commit()
    return redirect(request.referrer or url_for("creation_detail", cid=cid))


@app.route("/creations/<int:cid>/comment", methods=["POST"])
@login_required
def comment_creation(cid):
    get_creation(cid)
    body = request.form.get("body", "").strip()[:500]
    rating = request.form.get("rating")
    rating = int(rating) if rating and rating.isdigit() and 1 <= int(rating) <= 5 else None
    if body:
        get_db().execute("INSERT INTO comments (user_recipe_id, user_id, body, rating, created_at) VALUES (?,?,?,?,?)",
                         (cid, g.user["id"], body, rating, now()))
        get_db().commit()
        flash("Đã gửi bình luận.", "success")
    return redirect(url_for("creation_detail", cid=cid) + "#comments")


@app.route("/creations/<int:cid>/report", methods=["POST"])
@login_required
def report_creation(cid):
    get_creation(cid)
    get_db().execute("INSERT INTO reports (user_recipe_id, user_id, reason, created_at) VALUES (?,?,?,?)",
                     (cid, g.user["id"], request.form.get("reason", "")[:300], now()))
    get_db().commit()
    flash("Cảm ơn bạn. Đội ngũ kiểm duyệt sẽ xem xét nội dung này.", "info")
    return redirect(url_for("creation_detail", cid=cid))


@app.route("/creations/<int:cid>/visibility", methods=["POST"])
@login_required
def toggle_visibility(cid):
    c = get_creation(cid)
    if c["user_id"] != g.user["id"]:
        abort(403)
    get_db().execute("UPDATE user_recipes SET is_public = ? WHERE id = ?", (0 if c["is_public"] else 1, cid))
    get_db().commit()
    flash("Đã chuyển sang " + ("riêng tư." if c["is_public"] else "công khai."), "success")
    return redirect(url_for("creation_detail", cid=cid))


@app.route("/creations/<int:cid>/delete", methods=["POST"])
@login_required
def delete_creation(cid):
    c = get_creation(cid)
    if c["user_id"] != g.user["id"]:
        abort(403)
    db = get_db()
    db.execute("UPDATE user_recipes SET parent_user_recipe_id = NULL WHERE parent_user_recipe_id = ?", (cid,))
    db.execute("DELETE FROM user_recipes WHERE id = ?", (cid,))
    rest = db.execute("SELECT MIN(id) FROM user_recipes WHERE lineage_id = ?", (cid,)).fetchone()[0]
    if rest:
        db.execute("UPDATE user_recipes SET lineage_id = ? WHERE lineage_id = ?", (rest, cid))
    db.commit()
    flash("Đã xóa phiên bản.", "info")
    return redirect(url_for("my_space"))


@app.route("/users/<int:uid>/follow", methods=["POST"])
@login_required
def follow_user(uid):
    db = get_db()
    if uid != g.user["id"]:
        if db.execute("SELECT 1 FROM follows WHERE follower_id=? AND followee_id=?", (g.user["id"], uid)).fetchone():
            db.execute("DELETE FROM follows WHERE follower_id=? AND followee_id=?", (g.user["id"], uid))
        else:
            db.execute("INSERT INTO follows (follower_id, followee_id) VALUES (?,?)", (g.user["id"], uid))
        db.commit()
    return redirect(request.referrer or url_for("community"))


# =========================================================================== #
# TEA DNA
# =========================================================================== #
@app.route("/tea-dna", methods=["GET", "POST"])
def tea_dna_quiz():
    if request.method == "POST":
        answers = {}
        for q in tea_dna.QUESTIONS:
            answers[q["id"]] = request.form.getlist(q["id"]) if q["type"] == "avoid" else request.form.get(q["id"])
        res = tea_dna.compute(answers)
        stamp = now()
        session["dna"] = {"scores": res["scores"], "profile_key": res["profile_key"],
                          "confidence": res["confidence"], "unfolding": res["unfolding"],
                          "prefs": res["prefs"], "updated_at": stamp}
        if g.user:
            db = get_db()
            db.execute("""INSERT INTO tea_dna (user_id, scores_json, profile_key, confidence, unfolding, prefs_json,
                          updated_at) VALUES (?,?,?,?,?,?,?) ON CONFLICT(user_id) DO UPDATE SET
                          scores_json=excluded.scores_json, profile_key=excluded.profile_key,
                          confidence=excluded.confidence, unfolding=excluded.unfolding,
                          prefs_json=excluded.prefs_json, updated_at=excluded.updated_at""",
                       (g.user["id"], json.dumps(res["scores"]), res["profile_key"], res["confidence"],
                        int(res["unfolding"]), json.dumps(res["prefs"]), stamp))
            db.commit()
        return redirect(url_for("tea_dna_result"))
    return render_template("tea_dna.html", questions=tea_dna.QUESTIONS)


@app.route("/tea-dna/result")
def tea_dna_result():
    dna = get_user_dna()
    if not dna:
        return redirect(url_for("tea_dna_quiz"))
    rows = tea_dna.axis_rows(dna["scores"])
    return render_template("tea_dna_result.html", dna=dna, rows=rows, profile=dna["profile"],
                           recs=recommend(4), all_profiles=tea_dna.PROFILES)


@app.route("/tea-dna/manual", methods=["POST"])
def tea_dna_manual():
    """Người dùng tự điều chỉnh hồ sơ thủ công."""
    dna = get_user_dna()
    if not dna:
        return redirect(url_for("tea_dna_quiz"))
    scores = dict(dna["scores"])
    for axis in tea_dna.AXES:
        try:
            scores[axis] = max(0, min(100, int(request.form.get(axis, scores.get(axis, 50)))))
        except ValueError:
            pass
    best_key = tea_dna.nearest_profile(scores)
    stamp = now()
    new = {"scores": scores, "profile_key": best_key, "confidence": dna["confidence"],
           "unfolding": dna["unfolding"], "prefs": dna.get("prefs", {}), "updated_at": stamp}
    session["dna"] = new
    if g.user:
        get_db().execute("""UPDATE tea_dna SET scores_json=?, profile_key=?, updated_at=? WHERE user_id=?""",
                         (json.dumps(scores), best_key, stamp, g.user["id"]))
        get_db().commit()
    flash("Đã cập nhật hồ sơ Tea DNA theo điều chỉnh của bạn.", "success")
    return redirect(url_for("tea_dna_result"))


@app.route("/tea-dna/reset", methods=["POST"])
def tea_dna_reset():
    session.pop("dna", None)
    if g.user:
        get_db().execute("DELETE FROM tea_dna WHERE user_id = ?", (g.user["id"],))
        get_db().commit()
    flash("Đã xóa hồ sơ Tea DNA.", "info")
    return redirect(request.referrer or url_for("tea_dna_quiz"))


# =========================================================================== #
# COMMUNITY
# =========================================================================== #
@app.route("/community")
def community():
    tab = request.args.get("tab", "for-you")
    db = get_db()
    rows = [load_creation(x) for x in db.execute(CREATION_SELECT + " WHERE ur.is_public = 1")]
    vec = personalized_vector()
    for c in rows:
        c["match"] = engine.compatibility(vec, c["taste"]) if vec else None
    if tab == "trending":
        rows.sort(key=lambda c: -(c["like_count"] * 2 + c["comment_count"]))
    elif tab == "new":
        rows.sort(key=lambda c: c["created_at"], reverse=True)
    elif tab == "following":
        if g.user:
            ids = {x[0] for x in db.execute("SELECT followee_id FROM follows WHERE follower_id = ?", (g.user["id"],))}
            rows = [c for c in rows if c["user_id"] in ids]
        else:
            rows = []
    elif vec:
        rows.sort(key=lambda c: -(c["match"] or 0))
    else:
        rows.sort(key=lambda c: (-(c["like_count"]), c["created_at"]))
    challenges = []
    for ch in db.execute("SELECT * FROM challenges ORDER BY ends_at"):
        ch = dict(ch)
        ch["entries"] = db.execute("SELECT COUNT(*) FROM user_recipes WHERE challenge_slug=? AND is_public=1",
                                   (ch["slug"],)).fetchone()[0]
        challenges.append(ch)
    return render_template("community.html", tab=tab, creations=rows, challenges=challenges)


@app.route("/challenges/<slug>")
def challenge_detail(slug):
    ch = get_db().execute("SELECT * FROM challenges WHERE slug = ?", (slug,)).fetchone()
    if not ch:
        abort(404)
    entries = [load_creation(x) for x in get_db().execute(
        CREATION_SELECT + " WHERE ur.challenge_slug = ? AND ur.is_public = 1", (slug,))]
    entries.sort(key=lambda c: -c["like_count"])
    return render_template("challenge.html", ch=ch, entries=entries)


# =========================================================================== #
# WORKSHOPS
# =========================================================================== #
def seats_taken(wid):
    return get_db().execute("SELECT COALESCE(SUM(seats),0) FROM bookings WHERE workshop_id=? AND status!='cancelled'",
                            (wid,)).fetchone()[0]


@app.route("/workshops")
def workshops():
    ws = []
    for w in get_db().execute("SELECT * FROM workshops ORDER BY starts_at"):
        w = dict(w)
        w["left"] = w["capacity"] - seats_taken(w["id"])
        ws.append(w)
    return render_template("workshops.html", workshops=ws)


@app.route("/workshops/<slug>", methods=["GET", "POST"])
def workshop_detail(slug):
    db = get_db()
    w = db.execute("SELECT * FROM workshops WHERE slug = ?", (slug,)).fetchone()
    if not w:
        abort(404)
    w = dict(w)
    w["content"] = loads(w["content_json"], [])
    w["left"] = w["capacity"] - seats_taken(w["id"])
    form = {}
    if request.method == "POST":
        form = request.form
        name, phone, email = form.get("name", "").strip(), form.get("phone", "").strip(), form.get("email", "").strip()
        try:
            seats = int(form.get("seats", 1))
        except ValueError:
            seats = 0
        errors = []
        if len(name) < 2:
            errors.append("Vui lòng nhập họ tên.")
        if not re.fullmatch(r"(\+84|0)\d{9,10}", phone.replace(" ", "")):
            errors.append("Số điện thoại chưa đúng định dạng (VD: 0901234567).")
        if email and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            errors.append("Email chưa đúng định dạng.")
        if not 1 <= seats <= 5:
            errors.append("Mỗi lượt đặt từ 1 đến 5 chỗ.")
        elif seats > w["left"]:
            errors.append(f"Chỉ còn {w['left']} chỗ.")
        if not form.get("agree"):
            errors.append("Bạn cần đồng ý với chính sách hủy và hoàn tiền.")
        if errors:
            for e in errors:
                flash(e, "error")
        else:
            cur = db.execute("""INSERT INTO bookings (workshop_id, user_id, name, phone, email, seats, note, created_at)
                                VALUES (?,?,?,?,?,?,?,?)""",
                             (w["id"], g.user["id"] if g.user else None, name, phone, email, seats,
                              form.get("note", "")[:300], now()))
            db.commit()
            flash(f"Đặt chỗ thành công! Mã đặt chỗ #TW{cur.lastrowid:04d}. Tổng tạm tính {vnd(seats * w['price'])}. "
                  "Đội ngũ sẽ liên hệ để xác nhận và hướng dẫn thanh toán.", "success")
            return redirect(url_for("workshop_detail", slug=slug))
    elif g.user:
        form = {"name": g.user["name"], "email": g.user["email"]}
    return render_template("workshop_detail.html", w=w, form=form)


# =========================================================================== #
# PLAY – Tea Garden
# =========================================================================== #
@app.route("/play")
def play():
    return render_template("garden.html", recipes=all_recipes())


@app.route("/api/game/state", methods=["GET", "POST"])
def game_state():
    if not g.user:
        return jsonify({"ok": False, "guest": True}), 401
    db = get_db()
    if request.method == "GET":
        row = db.execute("SELECT state_json FROM game_profiles WHERE user_id = ?", (g.user["id"],)).fetchone()
        return jsonify({"ok": True, "state": loads(row["state_json"], None) if row else None})
    state = request.get_json(silent=True) or {}
    raw = json.dumps(state)
    if len(raw) > 100_000:
        return jsonify({"ok": False, "error": "state too large"}), 400
    db.execute("""INSERT INTO game_profiles (user_id, state_json, xp, level, updated_at) VALUES (?,?,?,?,?)
                  ON CONFLICT(user_id) DO UPDATE SET state_json=excluded.state_json, xp=excluded.xp,
                  level=excluded.level, updated_at=excluded.updated_at""",
               (g.user["id"], raw, int(state.get("xp", 0)), int(state.get("level", 1)), now()))
    db.commit()
    return jsonify({"ok": True})


# =========================================================================== #
# MY TEA SPACE
# =========================================================================== #
def passport_badges(uid):
    db = get_db()
    one = lambda sql, *p: db.execute(sql, p).fetchone()[0]
    saved = one("SELECT COUNT(*) FROM saved_recipes WHERE user_id=?", uid)
    created = one("SELECT COUNT(*) FROM user_recipes WHERE user_id=?", uid)
    comments = one("SELECT COUNT(*) FROM comments WHERE user_id=?", uid)
    bookings = one("SELECT COUNT(*) FROM bookings WHERE user_id=?", uid)
    level = one("SELECT COALESCE(MAX(level),0) FROM game_profiles WHERE user_id=?", uid)
    has_dna = one("SELECT COUNT(*) FROM tea_dna WHERE user_id=?", uid)
    teas = {r[0] for r in db.execute("""SELECT r.base_tea FROM saved_recipes s JOIN recipes r ON r.id=s.recipe_id
                                         WHERE s.user_id=?""", (uid,))}
    challenge_rows = db.execute("""SELECT DISTINCT c.name FROM user_recipes u JOIN challenges c ON c.slug=u.challenge_slug
                                   WHERE u.user_id=?""", (uid,)).fetchall()
    badges = [
        {"name": "DNA Decoder", "desc": "Hoàn thành bài test Tea DNA", "done": has_dna > 0, "icon": "dna"},
        {"name": "Recipe Collector", "desc": "Lưu 3 công thức", "done": saved >= 3, "icon": "bookmark",
         "progress": f"{min(saved, 3)}/3"},
        {"name": "First Creation", "desc": "Tạo công thức đầu tiên", "done": created >= 1, "icon": "spark"},
        {"name": "Version Explorer", "desc": "Tạo 3 phiên bản công thức", "done": created >= 3, "icon": "layers",
         "progress": f"{min(created, 3)}/3"},
        {"name": "Tea Around the World", "desc": "Lưu công thức từ 4 loại trà nền", "done": len(teas) >= 4,
         "icon": "globe", "progress": f"{min(len(teas), 4)}/4"},
        {"name": "Community Voice", "desc": "Bình luận lần đầu", "done": comments >= 1, "icon": "chat"},
        {"name": "Workshop Goer", "desc": "Đặt chỗ một workshop", "done": bookings >= 1, "icon": "cup"},
        {"name": "Leaf Keeper", "desc": "Đạt cấp 2 trong Tea Garden", "done": level >= 2, "icon": "leaf"},
    ]
    stamps = [r[0] for r in challenge_rows]
    return badges, stamps


@app.route("/my-space")
@login_required
def my_space():
    db = get_db()
    uid = g.user["id"]
    saved_rows = db.execute("""SELECT r.*, s.collection FROM saved_recipes s JOIN recipes r ON r.id=s.recipe_id
                               WHERE s.user_id=? ORDER BY s.created_at DESC""", (uid,)).fetchall()
    collections = {}
    for row in saved_rows:
        r = load_recipe({k: row[k] for k in row.keys() if k != "collection"})
        collections.setdefault(row["collection"], []).append(r)
    mine = [load_creation(x) for x in db.execute(CREATION_SELECT + " WHERE ur.user_id=? ORDER BY ur.id DESC", (uid,))]
    badges, stamps = passport_badges(uid)
    bookings = db.execute("""SELECT b.*, w.name AS workshop_name, w.starts_at, w.slug FROM bookings b
                             JOIN workshops w ON w.id=b.workshop_id WHERE b.user_id=? ORDER BY b.created_at DESC""",
                          (uid,)).fetchall()
    game = db.execute("SELECT xp, level FROM game_profiles WHERE user_id=?", (uid,)).fetchone()
    dna = get_user_dna()
    rows = tea_dna.axis_rows(dna["scores"]) if dna else []
    return render_template("my_space.html", collections=collections, mine=mine, badges=badges, stamps=stamps,
                           bookings=bookings, game=game, dna=dna, rows=rows, recs=recommend(3),
                           prefs=g.user["prefs"], tab=request.args.get("tab", "overview"))


@app.route("/my-space/preferences", methods=["POST"])
@login_required
def update_preferences():
    f = request.form
    prefs = {
        "avoid": f.getlist("avoid"),
        "avoid_ingredients": [x.strip() for x in f.get("avoid_ingredients", "").split(",") if x.strip()][:10],
        "allergies": f.get("allergies", "").strip()[:200],
        "units": f.get("units", "metric"),
    }
    db = get_db()
    db.execute("UPDATE users SET prefs_json=?, name=?, bio=? WHERE id=?",
               (json.dumps(prefs, ensure_ascii=False), (f.get("name") or g.user["name"]).strip()[:60],
                f.get("bio", "").strip()[:200], g.user["id"]))
    db.commit()
    flash("Đã lưu sở thích.", "success")
    return redirect(url_for("my_space", tab="settings"))


@app.route("/my-space/clear-data", methods=["POST"])
@login_required
def clear_preference_data():
    db = get_db()
    db.execute("UPDATE users SET prefs_json='{}' WHERE id=?", (g.user["id"],))
    db.execute("DELETE FROM tea_dna WHERE user_id=?", (g.user["id"],))
    db.commit()
    session.pop("dna", None)
    flash("Đã xóa toàn bộ dữ liệu sở thích và Tea DNA.", "info")
    return redirect(url_for("my_space", tab="settings"))


# =========================================================================== #
# Tài khoản
# =========================================================================== #
def safe_next(target):
    return target if target and target.startswith("/") and not target.startswith("//") else url_for("my_space")


def attach_guest_dna(uid):
    """Nếu khách đã làm Tea DNA trước khi đăng nhập, lưu kết quả vào tài khoản."""
    dna = session.get("dna")
    if not dna:
        return
    db = get_db()
    if db.execute("SELECT 1 FROM tea_dna WHERE user_id=?", (uid,)).fetchone():
        return
    db.execute("""INSERT INTO tea_dna (user_id, scores_json, profile_key, confidence, unfolding, prefs_json, updated_at)
                  VALUES (?,?,?,?,?,?,?)""", (uid, json.dumps(dna["scores"]), dna["profile_key"],
                                              dna["confidence"], int(dna["unfolding"]),
                                              json.dumps(dna.get("prefs", {})), dna["updated_at"]))
    db.commit()


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        pw = request.form.get("password", "")
        errors = []
        if len(name) < 2:
            errors.append("Tên cần ít nhất 2 ký tự.")
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            errors.append("Email chưa hợp lệ.")
        if len(pw) < 8:
            errors.append("Mật khẩu cần ít nhất 8 ký tự.")
        if not errors and get_db().execute("SELECT 1 FROM users WHERE email=?", (email,)).fetchone():
            errors.append("Email đã được đăng ký.")
        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("auth.html", mode="register", form=request.form)
        cur = get_db().execute("INSERT INTO users (name, email, password_hash, created_at) VALUES (?,?,?,?)",
                               (name, email, generate_password_hash(pw), now()))
        get_db().commit()
        session["user_id"] = cur.lastrowid
        attach_guest_dna(cur.lastrowid)
        flash(f"Chào mừng {name} đến với {app.config['SITE_NAME']}!", "success")
        return redirect(safe_next(request.args.get("next")))
    return render_template("auth.html", mode="register", form={})


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        row = get_db().execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        if not row or not check_password_hash(row["password_hash"], request.form.get("password", "")):
            flash("Email hoặc mật khẩu không đúng.", "error")
            return render_template("auth.html", mode="login", form=request.form)
        session["user_id"] = row["id"]
        attach_guest_dna(row["id"])
        flash(f"Chào mừng trở lại, {row['name']}!", "success")
        return redirect(safe_next(request.args.get("next")))
    return render_template("auth.html", mode="login", form={})


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("dna", None)
    flash("Đã đăng xuất.", "info")
    return redirect(url_for("home"))


# =========================================================================== #
# Lỗi
# =========================================================================== #
@app.errorhandler(404)
def not_found(_e):
    return render_template("error.html", code=404, message="Không tìm thấy trang bạn cần."), 404


@app.errorhandler(403)
def forbidden(_e):
    return render_template("error.html", code=403, message="Bạn không có quyền thực hiện thao tác này."), 403


if __name__ == "__main__":
    # Mặc định cổng 5001 (trên Mac, cổng 5000 hay bị AirPlay Receiver chiếm)
    port = int(os.environ.get("PORT", 5001))
    print(f"\n  TeaWay đang chạy tại:  http://127.0.0.1:{port}")
    print("  Tài khoản demo:         demo@teaway.vn / tea12345\n")
    app.run(host="127.0.0.1", port=port, debug=os.environ.get("FLASK_DEBUG", "1") == "1")
