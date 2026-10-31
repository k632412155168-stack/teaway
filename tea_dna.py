"""
TEA DNA – hệ thống nhận diện khẩu vị (công cụ phân loại sở thích tiêu dùng,
KHÔNG phải bài kiểm tra tâm lý hay đánh giá tính cách khoa học).

5 trục (0–100):
    sweetness  : Dry (0)    ↔ Sweet (100)
    acidity    : Soft (0)   ↔ Bright (100)
    bitterness : Smooth (0) ↔ Bold (100)
    strength   : Light (0)  ↔ Strong (100)
    aroma      : Floral (0) ↔ Fruity (100)
Thêm thuộc tính phụ "milk" (độ béo) để phân biệt nhóm Creamy.

Quy tắc phân loại: 0–39 nghiêng cực thứ nhất, 40–60 cân bằng, 61–100 nghiêng cực thứ hai.
"""
import math

AXES = {
    "sweetness":  {"label": "Sweetness",    "low": "Dry",    "high": "Sweet"},
    "acidity":    {"label": "Acidity",      "low": "Soft",   "high": "Bright"},
    "bitterness": {"label": "Bitterness",   "low": "Smooth", "high": "Bold"},
    "strength":   {"label": "Tea Strength", "low": "Light",  "high": "Strong"},
    "aroma":      {"label": "Aroma",        "low": "Floral", "high": "Fruity"},
}
ALL_DIMS = list(AXES) + ["milk"]

SCALE_TO_SCORE = {1: 0, 2: 25, 3: 50, 4: 75, 5: 100}

# --------------------------------------------------------------------------- #
# Câu hỏi
#   type "scale": thang 1–5 → điểm 0–100 cho các trục trong "axes" (trọng số)
#   type "choice": mỗi lựa chọn đóng góp điểm cho một hoặc nhiều trục
#   type "pref" / "avoid": lưu ràng buộc, không tính điểm trục
# --------------------------------------------------------------------------- #
QUESTIONS = [
    {"id": "q1", "type": "scale", "text": "Khi uống trà trái cây, bạn thích độ ngọt như thế nào?",
     "low": "Ít ngọt", "high": "Rất ngọt", "axes": {"sweetness": 1.5}},
    {"id": "q2", "type": "choice", "text": "Một ly trà sữa 100% đường ở quán, với bạn là…",
     "options": [
         {"key": "a", "label": "Quá ngọt, mình thường gọi 30–50% đường", "scores": {"sweetness": 15}},
         {"key": "b", "label": "Vừa đủ", "scores": {"sweetness": 60}},
         {"key": "c", "label": "Có khi mình còn muốn ngọt hơn", "scores": {"sweetness": 92}},
     ]},
    {"id": "q3", "type": "scale", "text": "Bạn thích độ chua trong đồ uống ở mức nào?",
     "low": "Ít chua", "high": "Rất chua", "axes": {"acidity": 1.5}},
    {"id": "q4", "type": "choice", "text": "Gọi trà chanh / trà tắc, bạn thường…",
     "options": [
         {"key": "a", "label": "Dặn bớt chanh, sợ chua", "scores": {"acidity": 15}},
         {"key": "b", "label": "Uống như quán pha", "scores": {"acidity": 55}},
         {"key": "c", "label": "Xin thêm chanh / tắc", "scores": {"acidity": 90}},
     ]},
    {"id": "q5", "type": "scale", "text": "Bạn chấp nhận vị đắng của trà đến mức nào?",
     "low": "Không thích đắng", "high": "Đắng càng rõ càng hay", "axes": {"bitterness": 1.5}},
    {"id": "q6", "type": "scale", "text": "Bạn có thích hậu vị chát (se đầu lưỡi) của trà không?",
     "low": "Không thích", "high": "Rất thích", "axes": {"bitterness": 1.0, "strength": 0.5}},
    {"id": "q7", "type": "scale", "text": "Độ đậm trà bạn yêu thích?",
     "low": "Nhẹ", "high": "Đậm", "axes": {"strength": 1.5}},
    {"id": "q8", "type": "choice", "text": "Bạn thường uống trà nguyên bản hay trà pha chế?",
     "options": [
         {"key": "a", "label": "Trà nguyên bản, không đường", "scores": {"strength": 85, "sweetness": 15}},
         {"key": "b", "label": "Cả hai tùy hôm", "scores": {"strength": 55, "sweetness": 50}},
         {"key": "c", "label": "Chủ yếu trà pha chế, trà trái cây, trà sữa", "scores": {"strength": 30, "sweetness": 70}},
     ]},
    {"id": "q9", "type": "choice", "text": "Bạn thường thích hương nào hơn?",
     "options": [
         {"key": "fruit", "label": "Trái cây: đào, vải, cam, dâu", "scores": {"aroma": 92}},
         {"key": "flower", "label": "Hoa: nhài, hồng, lavender", "scores": {"aroma": 12}},
         {"key": "roast", "label": "Rang: gạo rang, hạt, caramel",
          "scores": {"aroma": 45, "strength": 80, "bitterness": 65}},
         {"key": "herb", "label": "Thảo mộc: bạc hà, sả, rosemary", "scores": {"aroma": 25}},
     ]},
    {"id": "q10", "type": "scale", "text": "Bạn thích sữa và độ béo trong đồ uống đến mức nào?",
     "low": "Không cần sữa", "high": "Càng béo càng thích", "axes": {"milk": 1.0}},
    {"id": "q11", "type": "pref", "text": "Bạn thích trà nóng hay lạnh?",
     "options": [
         {"key": "iced", "label": "Lạnh"}, {"key": "hot", "label": "Nóng"}, {"key": "both", "label": "Cả hai"},
     ]},
    {"id": "q12", "type": "avoid", "text": "Có vị hoặc thành phần nào bạn muốn tránh? (có thể chọn nhiều)",
     "options": [
         {"key": "milk", "label": "Sữa bò"}, {"key": "caffeine", "label": "Caffeine"},
         {"key": "honey", "label": "Mật ong"}, {"key": "sour", "label": "Vị quá chua"},
     ]},
]

# --------------------------------------------------------------------------- #
# Hồ sơ Tea DNA (vector nguyên mẫu)
# --------------------------------------------------------------------------- #
PROFILES = {
    "honey_bloom": {"name": "Honey Bloom", "tagline": "The Sweet & Fruity Explorer",
                    "vector": {"sweetness": 82, "acidity": 35, "bitterness": 28, "strength": 40, "aroma": 78, "milk": 30},
                    "summary": "Thích đồ uống ngọt, thơm trái cây, dễ uống.",
                    "pairs": "đào, vải, xoài, mật ong và trà nhẹ", "color": "#E39B62"},
    "citrus_spark": {"name": "Citrus Spark", "tagline": "The Bright Refresher",
                     "vector": {"sweetness": 45, "acidity": 85, "bitterness": 25, "strength": 35, "aroma": 80, "milk": 10},
                     "summary": "Ưa vị chua tươi, thơm sáng, cảm giác sảng khoái.",
                     "pairs": "chanh, cam, tắc, berry", "color": "#D6C24A"},
    "roasted_soul": {"name": "Roasted Soul", "tagline": "The Deep Roast Lover",
                     "vector": {"sweetness": 18, "acidity": 25, "bitterness": 78, "strength": 85, "aroma": 45, "milk": 20},
                     "summary": "Thích vị trà rõ, ít ngọt, hậu vị rang.",
                     "pairs": "ô long rang, hojicha, trà đen", "color": "#7B4A2A"},
    "petal_whisper": {"name": "Petal Whisper", "tagline": "The Gentle Florist",
                      "vector": {"sweetness": 35, "acidity": 25, "bitterness": 15, "strength": 25, "aroma": 12, "milk": 15},
                      "summary": "Ưa hương hoa dịu, vị nhẹ và thanh.",
                      "pairs": "hoa nhài, hoa hồng, vải, trà trắng", "color": "#E3BFC0"},
    "velvet_matcha": {"name": "Velvet Matcha", "tagline": "The Smooth Intensity",
                      "vector": {"sweetness": 45, "acidity": 18, "bitterness": 35, "strength": 80, "aroma": 40, "milk": 85},
                      "summary": "Thích độ đậm nhưng không muốn vị gắt.",
                      "pairs": "matcha latte, sữa yến mạch, vanilla", "color": "#7FA14F"},
    "sugar_muse": {"name": "Sugar Muse", "tagline": "The Dessert Dreamer",
                   "vector": {"sweetness": 95, "acidity": 30, "bitterness": 12, "strength": 30, "aroma": 60, "milk": 75},
                   "summary": "Rất thích ngọt, thiên về dessert drinks.",
                   "pairs": "caramel, vanilla, trà sữa, foam kem", "color": "#D98BA0"},
    "berry_rebel": {"name": "Berry Rebel", "tagline": "The Tangy Adventurer",
                    "vector": {"sweetness": 60, "acidity": 88, "bitterness": 25, "strength": 40, "aroma": 90, "milk": 10},
                    "summary": "Thích chua rõ, hương berry.",
                    "pairs": "dâu, hibiscus, mâm xôi", "color": "#C9465B"},
    "lemon_theory": {"name": "Lemon Theory", "tagline": "The Clean Citrus Mind",
                     "vector": {"sweetness": 22, "acidity": 75, "bitterness": 35, "strength": 50, "aroma": 65, "milk": 5},
                     "summary": "Chua thanh, citrus, ít ngọt.",
                     "pairs": "trà xanh chanh, tắc, bạc hà", "color": "#A6BF57"},
    "tea_minimalist": {"name": "Tea Minimalist", "tagline": "The Pure Leaf Purist",
                       "vector": {"sweetness": 8, "acidity": 25, "bitterness": 55, "strength": 72, "aroma": 30, "milk": 5},
                       "summary": "Ít ngọt, thích vị trà nguyên bản.",
                       "pairs": "trà xanh, ô long, cold brew không đường", "color": "#71866A"},
    "creamy_cloud": {"name": "Creamy Cloud", "tagline": "The Soft & Silky",
                     "vector": {"sweetness": 70, "acidity": 12, "bitterness": 20, "strength": 40, "aroma": 50, "milk": 90},
                     "summary": "Thích béo, mịn, êm.",
                     "pairs": "trà sữa, foam kem, sữa yến mạch", "color": "#CFAE7F"},
    "garden_muse": {"name": "Garden Muse", "tagline": "The Herbal Wanderer",
                    "vector": {"sweetness": 35, "acidity": 45, "bitterness": 30, "strength": 40, "aroma": 22, "milk": 10},
                    "summary": "Thích hương hoa và thảo mộc tự nhiên.",
                    "pairs": "sả, bạc hà, hoa cúc, trà lài", "color": "#93C29E"},
    "tropical_soul": {"name": "Tropical Soul", "tagline": "The Sunshine Seeker",
                      "vector": {"sweetness": 75, "acidity": 58, "bitterness": 18, "strength": 30, "aroma": 95, "milk": 20},
                      "summary": "Thích trái cây nhiệt đới, hương rõ.",
                      "pairs": "xoài, chanh dây, dứa, vải", "color": "#F2B33D"},
    "amber_classic": {"name": "Amber Classic", "tagline": "The Timeless Brewer",
                      "vector": {"sweetness": 38, "acidity": 30, "bitterness": 62, "strength": 78, "aroma": 50, "milk": 45},
                      "summary": "Thích trà đen, ô long, vị truyền thống.",
                      "pairs": "trà đen, ô long sữa, trà đen cam quế", "color": "#B4532F"},
}
DIM_WEIGHTS = {"sweetness": 1.2, "acidity": 1.0, "bitterness": 1.0, "strength": 1.0, "aroma": 1.0, "milk": 0.8}


def lean(axis, score):
    info = AXES[axis]
    if score < 40:
        return info["low"]
    if score > 60:
        return info["high"]
    return "Balanced"


def compute(answers):
    """
    answers: dict {qid: value} (scale: "1".."5", choice/pref: key, avoid: list[key])
    Trả về dict: scores, profile_key, confidence, unfolding, prefs
    """
    contrib = {d: [] for d in ALL_DIMS}  # list (score, weight)
    answered, scored_q = 0, 0
    prefs = {"temperature": "both", "avoid": []}

    for q in QUESTIONS:
        val = answers.get(q["id"])
        if q["type"] in ("scale", "choice"):
            scored_q += 1
        if val in (None, "", []):
            continue
        if q["type"] == "scale":
            try:
                score = SCALE_TO_SCORE[int(val)]
            except (ValueError, KeyError):
                continue
            answered += 1
            for axis, w in q["axes"].items():
                contrib[axis].append((score, w))
        elif q["type"] == "choice":
            opt = next((o for o in q["options"] if o["key"] == val), None)
            if not opt:
                continue
            answered += 1
            for axis, score in opt["scores"].items():
                contrib[axis].append((score, 1.0))
        elif q["type"] == "pref":
            prefs["temperature"] = val
        elif q["type"] == "avoid":
            prefs["avoid"] = list(val) if isinstance(val, (list, tuple)) else [val]

    scores, spreads = {}, []
    for d in ALL_DIMS:
        items = contrib[d]
        if items:
            tw = sum(w for _, w in items)
            mean = sum(s * w for s, w in items) / tw
            scores[d] = round(mean)
            if len(items) > 1:
                var = sum(w * (s - mean) ** 2 for s, w in items) / tw
                spreads.append(math.sqrt(var))
        else:
            scores[d] = 50 if d != "milk" else 20

    # Hồ sơ gần nhất (khoảng cách Euclid có trọng số)
    dists = []
    for key, p in PROFILES.items():
        d = math.sqrt(sum(DIM_WEIGHTS[k] * (scores[k] - p["vector"][k]) ** 2 for k in ALL_DIMS))
        dists.append((d, key))
    dists.sort()
    best_d, best_key = dists[0]
    second_d = dists[1][0]

    completeness = answered / scored_q if scored_q else 0
    consistency = 1 - min(1, (sum(spreads) / len(spreads)) / 50) if spreads else 0.6
    separation = min(1, (second_d - best_d) / 25)
    fit = max(0, 1 - best_d / 120)
    confidence = round(100 * (0.4 * completeness + 0.25 * consistency + 0.15 * separation + 0.2 * fit))

    return {
        "scores": scores,
        "profile_key": best_key,
        "confidence": confidence,
        "unfolding": confidence < 55 or completeness < 0.7,
        "prefs": prefs,
        "runner_up": dists[1][1],
    }


def nearest_profile(scores):
    """Hồ sơ gần nhất với một bộ điểm (dùng khi người dùng chỉnh tay)."""
    full = {d: scores.get(d, 50 if d != "milk" else 20) for d in ALL_DIMS}
    return min(PROFILES, key=lambda k: sum(
        DIM_WEIGHTS[d] * (full[d] - PROFILES[k]["vector"][d]) ** 2 for d in ALL_DIMS))


def profile_info(key):
    return PROFILES.get(key)


def axis_rows(scores):
    rows = []
    for axis, info in AXES.items():
        s = scores.get(axis, 50)
        rows.append({"axis": axis, "label": info["label"], "low": info["low"], "high": info["high"],
                     "score": s, "lean": lean(axis, s)})
    return rows
