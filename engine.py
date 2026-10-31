"""
Recipe Engine – Level 1 (rule-based).

Nguyên tắc thiết kế: slider điều chỉnh MỤC TIÊU CẢM QUAN, còn engine quyết định
thành phần nào thay đổi, thay đổi bao nhiêu, trong giới hạn min/max.

Chức năng:
- Điều chỉnh theo slider (Sweetness, Tea Strength, Acidity, Fruitiness, Creaminess)
- Giữ nguyên dung tích bằng cách cân bằng nước lọc
- Scale số khẩu phần (tuyến tính / không tuyến tính)
- Thay thế nguyên liệu
- Tính chi phí
- Ước tính hồ sơ vị sau điều chỉnh
"""
from copy import deepcopy

from seed_data import CATALOG, SUBSTITUTIONS

AXES = ["sweetness", "acidity", "bitterness", "strength", "aroma"]

SLIDERS = {
    "sweetness":  {"role": "sweetener", "label": "Sweetness",    "low": "Ít ngọt",   "high": "Ngọt hơn",
                   "desc": "Điều chỉnh lượng chất tạo ngọt trong công thức."},
    "strength":   {"role": "tea",       "label": "Tea Strength", "low": "Nhẹ",       "high": "Đậm",
                   "desc": "Điều chỉnh lượng trà nền / nồng độ trà."},
    "acidity":    {"role": "acid",      "label": "Acidity",      "low": "Ít chua",   "high": "Chua hơn",
                   "desc": "Điều chỉnh thành phần tạo chua."},
    "fruitiness": {"role": "fruit",     "label": "Fruitiness",   "low": "Nhẹ hương", "high": "Đậm trái cây",
                   "desc": "Điều chỉnh syrup và trái cây."},
    "creaminess": {"role": "milk",      "label": "Creaminess",   "low": "Thanh",     "high": "Béo hơn",
                   "desc": "Điều chỉnh sữa và foam."},
}
ROLE_TO_SLIDER = {v["role"]: k for k, v in SLIDERS.items()}

DEFAULT_MIN_FACTOR = 0.4
DEFAULT_MAX_FACTOR = 1.6
SLIDER_RANGE = 50  # slider từ -50% đến +50%


# --------------------------------------------------------------------------- #
# Tiện ích
# --------------------------------------------------------------------------- #
def price_of(name):
    return CATALOG.get(name, {}).get("price", 0)


def nice(x):
    """Làm tròn định lượng cho dễ đọc."""
    if x is None:
        return 0
    if abs(x) >= 100:
        return round(x)
    r = round(x, 1)
    return int(r) if r == int(r) else r


def is_liquid(ing):
    return ing.get("unit") == "ml" and ing.get("role") != "ice"


def liquid_volume(ingredients):
    return sum(i["qty"] for i in ingredients if is_liquid(i))


def cost_of(ingredients):
    return sum(i["qty"] * price_of(i["name"]) for i in ingredients)


def available_sliders(ingredients):
    roles = {i.get("role") for i in ingredients}
    return [k for k, v in SLIDERS.items() if v["role"] in roles]


def substitution_options(ingredients):
    """{index: [options]} cho các nguyên liệu có thể thay thế."""
    out = {}
    for idx, ing in enumerate(ingredients):
        opts = SUBSTITUTIONS.get(ing["name"])
        if opts:
            out[idx] = opts
    return out


def recipe_flags(ingredients):
    caffeine = any(CATALOG.get(i["name"], {}).get("caffeine") for i in ingredients)
    dairy = any(CATALOG.get(i["name"], {}).get("dairy") for i in ingredients)
    not_vegan = dairy or any(CATALOG.get(i["name"], {}).get("not_vegan") for i in ingredients)
    allergens = []
    for i in ingredients:
        a = CATALOG.get(i["name"], {}).get("allergen")
        if a and a not in allergens:
            allergens.append(a)
    return {"caffeine": caffeine, "dairy_free": not dairy, "vegan": not not_vegan, "allergens": allergens}


def clamp(v, lo=0, hi=100):
    return max(lo, min(hi, v))


# --------------------------------------------------------------------------- #
# Lõi điều chỉnh
# --------------------------------------------------------------------------- #
def adjust(recipe, servings=1, sliders=None, keep_volume=True, substitutions=None):
    """
    recipe: dict có 'ingredients', 'taste', 'brewing' (tùy chọn), 'servings'
    sliders: {'sweetness': 25, 'strength': -10, ...} (đơn vị %)
    substitutions: {index(str|int): 'Tên nguyên liệu thay thế'}
    Trả về dict kết quả để hiển thị / lưu phiên bản.
    """
    sliders = {k: float(v or 0) for k, v in (sliders or {}).items() if k in SLIDERS}
    substitutions = {int(k): v for k, v in (substitutions or {}).items() if v}
    base_servings = max(1, int(recipe.get("servings") or 1))
    servings = max(1, min(int(servings or 1), 50))

    warnings, notes = [], []
    base = deepcopy(recipe["ingredients"])
    # Đưa công thức gốc về 1 khẩu phần
    for ing in base:
        ing["qty"] = ing["qty"] / base_servings

    # 1) Thay thế nguyên liệu ------------------------------------------------
    working = deepcopy(base)
    for idx, sub_name in substitutions.items():
        if idx >= len(working):
            continue
        ing = working[idx]
        option = next((o for o in SUBSTITUTIONS.get(ing["name"], []) if o["name"] == sub_name), None)
        if not option:
            continue
        ing["substituted_from"] = ing["name"]
        ing["name"] = option["name"]
        ing["qty"] = ing["qty"] * option["ratio"]
        ing["unit"] = CATALOG.get(option["name"], {}).get("unit", ing["unit"])
        notes.append(f"{ing['substituted_from']} → {option['name']} ({option['label']}): {option['note']}")

    # 2) Áp slider lên từng nhóm nguyên liệu --------------------------------
    for ing in working:
        key = ROLE_TO_SLIDER.get(ing.get("role"))
        pct = sliders.get(key, 0) if key else 0
        if not pct:
            continue
        pct = max(-SLIDER_RANGE, min(SLIDER_RANGE, pct))
        factor = 1 + pct / 100
        lo = ing.get("min_factor", DEFAULT_MIN_FACTOR)
        hi = ing.get("max_factor", DEFAULT_MAX_FACTOR)
        if factor < lo or factor > hi:
            factor = max(lo, min(hi, factor))
            warnings.append(f"{ing['name']} đã chạm giới hạn an toàn của công thức ({int(lo*100)}–{int(hi*100)}%).")
        ing["qty"] = ing["qty"] * factor

    # 3) Giữ nguyên dung tích -------------------------------------------------
    base_volume = liquid_volume(base)
    water = [i for i in working if i.get("role") == "water" and i.get("unit") == "ml"]
    delta = liquid_volume(working) - base_volume
    if keep_volume and abs(delta) > 0.01:
        if water:
            w = water[0]
            new_w = w["qty"] - delta
            if new_w < 0:
                warnings.append("Không đủ nước lọc để giữ nguyên dung tích – thể tích ly sẽ tăng.")
                new_w = 0
            notes.append(f"{w['name']}: {nice(w['qty'])} → {nice(new_w)} ml mỗi ly để giữ dung tích.")
            w["qty"] = new_w
        else:
            notes.append("Công thức không có nước lọc để cân bằng – thể tích mới được hiển thị bên dưới.")
    elif not keep_volume and abs(delta) > 0.01:
        notes.append(f"Thể tích thay đổi {'+' if delta > 0 else ''}{nice(delta)} ml so với công thức gốc.")

    # 4) Quy tắc tương tác vị ------------------------------------------------
    s = sliders.get("strength", 0)
    if s >= 25:
        warnings.append("Tăng nồng độ trà nhiều có thể làm vị chát/đắng tăng rõ. Nên tăng lượng lá trà khi ủ, "
                        "giữ nguyên nhiệt độ và thời gian ủ đã kiểm chứng thay vì ủ lâu hơn.")
    if sliders.get("acidity", 0) >= 20 and sliders.get("sweetness", 0) <= 0:
        notes.append("Vị chua tăng mà độ ngọt giữ nguyên – nếu thấy gắt, thử tăng Sweetness thêm 10–15%.")
    if sliders.get("sweetness", 0) <= -40:
        notes.append("Giảm ngọt nhiều có thể làm vị chua và chát nổi hơn.")
    if sliders.get("acidity", 0) and not any(i.get("role") == "acid" for i in working):
        notes.append("Công thức không có thành phần tạo chua nên slider Acidity không có tác dụng.")

    # 5) Brewing guide sau điều chỉnh ---------------------------------------
    brewing = deepcopy(recipe.get("brewing") or {})
    if brewing:
        tea_factor = 1 + max(-SLIDER_RANGE, min(SLIDER_RANGE, s)) / 100
        brewing["leaf_g_adjusted"] = nice(brewing.get("leaf_g", 0) * tea_factor)

    # 6) Scale khẩu phần -----------------------------------------------------
    result = []
    for orig, ing in zip(base, working):
        mode = ing.get("scale", "linear")
        if servings == 1:
            mult = 1
        elif mode == "sublinear":
            mult = servings ** 0.85
        else:
            mult = servings
        item = {
            "name": ing["name"], "unit": ing["unit"], "role": ing.get("role"),
            "qty": nice(ing["qty"] * mult),
            "original_qty": nice(orig["qty"] * servings),
            "original_name": orig["name"],
            "scale": mode,
            "substituted_from": ing.get("substituted_from"),
            "price": price_of(ing["name"]),
        }
        item["changed"] = item["qty"] != item["original_qty"] or bool(item["substituted_from"])
        result.append(item)
    if servings > 1 and any(i["scale"] == "sublinear" for i in result):
        notes.append("Một số nguyên liệu (thảo mộc, gia vị, hoa) được chuyên gia đánh dấu không nhân tuyến tính – "
                     "hãy nếm và điều chỉnh.")

    # 7) Hồ sơ vị ước tính ---------------------------------------------------
    taste = dict(recipe.get("taste") or {})
    est = {
        "sweetness": clamp(taste.get("sweetness", 50) + sliders.get("sweetness", 0) * 0.45
                           - sliders.get("acidity", 0) * 0.05),
        "acidity": clamp(taste.get("acidity", 50) + sliders.get("acidity", 0) * 0.45
                         - sliders.get("sweetness", 0) * 0.08),
        "bitterness": clamp(taste.get("bitterness", 50) + s * 0.35 - sliders.get("creaminess", 0) * 0.1),
        "strength": clamp(taste.get("strength", 50) + s * 0.5 - sliders.get("creaminess", 0) * 0.1),
        "aroma": clamp(taste.get("aroma", 50) + sliders.get("fruitiness", 0) * 0.3),
        "milk": clamp(taste.get("milk", 0) + sliders.get("creaminess", 0) * 0.5),
    }
    est = {k: round(v) for k, v in est.items()}

    total_cost = sum(i["qty"] * i["price"] for i in result)
    orig_cost = sum(i["original_qty"] * price_of(i["original_name"]) for i in result)
    volume = sum(i["qty"] for i in result if i["unit"] == "ml" and i["role"] != "ice")
    orig_volume = sum(i["original_qty"] for i in result
                      if CATALOG.get(i["original_name"], {}).get("unit") == "ml" and i["role"] != "ice")

    return {
        "servings": servings,
        "ingredients": result,
        "volume_ml": nice(volume),
        "original_volume_ml": nice(orig_volume),
        "volume_per_serving": nice(volume / servings),
        "cost": round(total_cost),
        "original_cost": round(orig_cost),
        "cost_per_serving": round(total_cost / servings),
        "taste": est,
        "original_taste": {k: taste.get(k, 0) for k in est},
        "brewing": brewing,
        "warnings": warnings,
        "notes": notes,
        "sliders": sliders,
    }


def cost_per_serving(recipe):
    return round(cost_of(recipe["ingredients"]) / max(1, int(recipe.get("servings") or 1)))


def compatibility(user_scores, taste):
    """% phù hợp giữa Tea DNA (0–100/trục) và hồ sơ vị công thức."""
    if not user_scores or not taste:
        return None
    diffs = [abs(user_scores.get(a, 50) - taste.get(a, 50)) for a in AXES]
    return round(100 - sum(diffs) / len(diffs))


def diff_ingredients(parent_ings, child_ings):
    """So sánh hai danh sách nguyên liệu (phục vụ Compare Versions)."""
    rows = []
    pmap = {i["name"]: i for i in parent_ings}
    seen = set()
    for c in child_ings:
        p = pmap.get(c["name"])
        if p:
            seen.add(c["name"])
            status = "same" if nice(p["qty"]) == nice(c["qty"]) else ("up" if c["qty"] > p["qty"] else "down")
            rows.append({"name": c["name"], "unit": c["unit"], "before": nice(p["qty"]), "after": nice(c["qty"]),
                         "status": status})
        else:
            rows.append({"name": c["name"], "unit": c["unit"], "before": None, "after": nice(c["qty"]),
                         "status": "added"})
    for p in parent_ings:
        if p["name"] not in seen and p["name"] not in {c["name"] for c in child_ings}:
            rows.append({"name": p["name"], "unit": p["unit"], "before": nice(p["qty"]), "after": None,
                         "status": "removed"})
    return rows
