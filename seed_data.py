"""
Dữ liệu mẫu cho nền tảng TeaWay.

- CATALOG: danh mục nguyên liệu (đơn vị, giá tham khảo VND/đơn vị, thuộc tính).
- SUBSTITUTIONS: bảng nguyên liệu thay thế cho Ingredient Substitution Engine.
- RECIPES: công thức prototype (đã chuẩn hóa đơn vị, CẦN kiểm thử thực tế trước khi công bố).
- WORKSHOPS, CHALLENGES, COMMUNITY: nội dung minh họa.

Lưu ý: giá, định lượng và thông số pha là số liệu minh họa để kiểm thử sản phẩm,
không phải tỷ lệ chuẩn cho mọi loại trà/syrup.
"""

# --------------------------------------------------------------------------- #
# 1. DANH MỤC NGUYÊN LIỆU
# price = giá tham khảo (VND) cho 1 đơn vị (1 ml hoặc 1 g)
# --------------------------------------------------------------------------- #
CATALOG = {
    # Trà nền (đã ủ, tính theo ml) ------------------------------------------
    "Trà ô long (đã ủ)":       {"unit": "ml", "price": 40,  "category": "Trà nền", "caffeine": True},
    "Trà ô long rang (đã ủ)":  {"unit": "ml", "price": 45,  "category": "Trà nền", "caffeine": True},
    "Trà xanh (đã ủ)":         {"unit": "ml", "price": 30,  "category": "Trà nền", "caffeine": True},
    "Trà lài (đã ủ)":          {"unit": "ml", "price": 35,  "category": "Trà nền", "caffeine": True},
    "Trà đen (đã ủ)":          {"unit": "ml", "price": 30,  "category": "Trà nền", "caffeine": True},
    "Trà trắng (đã ủ)":        {"unit": "ml", "price": 60,  "category": "Trà nền", "caffeine": True},
    "Hojicha (đã ủ)":          {"unit": "ml", "price": 50,  "category": "Trà nền", "caffeine": True},
    "Trà xanh cold brew":      {"unit": "ml", "price": 30,  "category": "Trà nền", "caffeine": True},
    "Hibiscus (đã ủ)":         {"unit": "ml", "price": 25,  "category": "Trà thảo mộc", "caffeine": False},
    "Bột matcha":              {"unit": "g",  "price": 1500, "category": "Trà nền", "caffeine": True},
    # Chất tạo ngọt -----------------------------------------------------------
    "Syrup đường":             {"unit": "ml", "price": 30,  "category": "Chất tạo ngọt"},
    "Mật ong":                 {"unit": "ml", "price": 250, "category": "Chất tạo ngọt", "not_vegan": True,
                                "allergen": "Mật ong – không dùng cho trẻ dưới 12 tháng tuổi"},
    "Syrup vanilla":           {"unit": "ml", "price": 200, "category": "Chất tạo ngọt"},
    "Syrup caramel":           {"unit": "ml", "price": 180, "category": "Chất tạo ngọt"},
    # Trái cây ----------------------------------------------------------------
    "Syrup đào":               {"unit": "ml", "price": 120, "category": "Trái cây"},
    "Đào miếng ngâm":          {"unit": "g",  "price": 150, "category": "Trái cây"},
    "Syrup vải":               {"unit": "ml", "price": 130, "category": "Trái cây"},
    "Vải ngâm":                {"unit": "g",  "price": 180, "category": "Trái cây"},
    "Xoài chín":               {"unit": "g",  "price": 60,  "category": "Trái cây"},
    "Dâu tây":                 {"unit": "g",  "price": 200, "category": "Trái cây"},
    "Puree dâu":               {"unit": "g",  "price": 160, "category": "Trái cây"},
    # Tạo chua ----------------------------------------------------------------
    "Nước cốt chanh":          {"unit": "ml", "price": 100, "category": "Tạo chua"},
    "Nước cốt tắc":            {"unit": "ml", "price": 120, "category": "Tạo chua"},
    "Cam vắt":                 {"unit": "ml", "price": 80,  "category": "Tạo chua"},
    # Sữa ---------------------------------------------------------------------
    "Sữa tươi":                {"unit": "ml", "price": 35,  "category": "Sữa", "dairy": True,
                                "allergen": "Sữa bò (lactose)"},
    "Sữa yến mạch":            {"unit": "ml", "price": 70,  "category": "Sữa",
                                "allergen": "Yến mạch (có thể chứa gluten)"},
    "Foam kem sữa":            {"unit": "ml", "price": 150, "category": "Sữa", "dairy": True,
                                "allergen": "Sữa bò (lactose)"},
    # Thảo mộc, hoa, gia vị --------------------------------------------------
    "Lá bạc hà":               {"unit": "g",  "price": 300, "category": "Thảo mộc"},
    "Sả đập dập":              {"unit": "g",  "price": 40,  "category": "Thảo mộc"},
    "Nụ hồng khô":             {"unit": "g",  "price": 800, "category": "Hoa"},
    "Quế thanh":               {"unit": "g",  "price": 400, "category": "Gia vị"},
    # Nước, đá ----------------------------------------------------------------
    "Nước lọc":                {"unit": "ml", "price": 0,   "category": "Nước"},
    "Nước nóng 75°C":          {"unit": "ml", "price": 0,   "category": "Nước"},
    "Đá":                      {"unit": "g",  "price": 5,   "category": "Đá"},
}

# --------------------------------------------------------------------------- #
# 2. NGUYÊN LIỆU THAY THẾ
# label: Best Match | Flavor Twist | Budget Option | Unavailable
# ratio: hệ số quy đổi định lượng (khởi điểm – cần kiểm thử)
# --------------------------------------------------------------------------- #
SUBSTITUTIONS = {
    "Đào miếng ngâm": [
        {"name": "Xoài chín", "label": "Flavor Twist", "ratio": 1.0,
         "note": "Vị ngọt đậm hơn, cần cân chỉnh lại syrup."},
        {"name": "Vải ngâm", "label": "Flavor Twist", "ratio": 1.0,
         "note": "Thêm hương hoa, vị thanh hơn đào."},
    ],
    "Syrup đào": [
        {"name": "Syrup vải", "label": "Flavor Twist", "ratio": 1.0,
         "note": "Đổi sang hương vải, ngọt thơm hơn."},
    ],
    "Nước cốt chanh": [
        {"name": "Nước cốt tắc", "label": "Best Match", "ratio": 1.0,
         "note": "Hương citrus khác, hơi đắng vỏ – cần thử tỷ lệ."},
        {"name": "Cam vắt", "label": "Flavor Twist", "ratio": 2.0,
         "note": "Ít chua hơn nhiều, thêm vị ngọt cam."},
    ],
    "Nước cốt tắc": [
        {"name": "Nước cốt chanh", "label": "Best Match", "ratio": 1.0,
         "note": "Chua sắc hơn, mất hương vỏ tắc."},
    ],
    "Mật ong": [
        {"name": "Syrup đường", "label": "Budget Option", "ratio": 1.0,
         "note": "Vị ngọt trung tính hơn, mất hương hoa của mật ong."},
    ],
    "Syrup đường": [
        {"name": "Mật ong", "label": "Flavor Twist", "ratio": 0.8,
         "note": "Ngọt hơn syrup nên dùng ít hơn; thêm hương hoa."},
    ],
    "Syrup vanilla": [
        {"name": "Syrup đường", "label": "Budget Option", "ratio": 1.0,
         "note": "Giữ độ ngọt nhưng mất hương vanilla."},
    ],
    "Syrup caramel": [
        {"name": "Syrup đường", "label": "Budget Option", "ratio": 1.0,
         "note": "Mất hậu vị caramel rang."},
        {"name": "Mật ong", "label": "Flavor Twist", "ratio": 0.8,
         "note": "Ngọt thơm kiểu hoa thay vì kiểu rang."},
    ],
    "Trà ô long (đã ủ)": [
        {"name": "Trà đen (đã ủ)", "label": "Flavor Twist", "ratio": 1.0,
         "note": "Vị trà mạnh hơn, hậu vị khác (malty)."},
        {"name": "Trà xanh (đã ủ)", "label": "Budget Option", "ratio": 1.0,
         "note": "Nhẹ và tươi hơn, ít hương rang."},
    ],
    "Trà lài (đã ủ)": [
        {"name": "Trà xanh (đã ủ)", "label": "Best Match", "ratio": 1.0,
         "note": "Giữ nền trà xanh nhưng mất hương hoa nhài."},
    ],
    "Trà xanh (đã ủ)": [
        {"name": "Trà lài (đã ủ)", "label": "Flavor Twist", "ratio": 1.0,
         "note": "Thêm hương hoa nhài."},
    ],
    "Sữa tươi": [
        {"name": "Sữa yến mạch", "label": "Best Match", "ratio": 1.0,
         "note": "Không sữa bò; khác độ béo và hương ngũ cốc."},
    ],
    "Sữa yến mạch": [
        {"name": "Sữa tươi", "label": "Budget Option", "ratio": 1.0,
         "note": "Béo hơn, có lactose."},
    ],
    "Dâu tây": [
        {"name": "Puree dâu", "label": "Best Match", "ratio": 0.8,
         "note": "Kiểm tra lượng đường sẵn có trong puree, có thể cần giảm ngọt."},
    ],
    "Sả đập dập": [
        {"name": "Lá bạc hà", "label": "Flavor Twist", "ratio": 0.3,
         "note": "Mát hơn, mất hương sả."},
    ],
    "Lá bạc hà": [
        {"name": "Sả đập dập", "label": "Flavor Twist", "ratio": 3.0,
         "note": "Hương ấm, thơm kiểu Việt."},
    ],
    "Bột matcha": [
        {"name": None, "label": "Unavailable", "ratio": 0,
         "note": "Chưa có phương án thay thế giữ được vị matcha."},
    ],
}

# --------------------------------------------------------------------------- #
# 3. CÔNG THỨC PROTOTYPE
# role: tea | sweetener | acid | fruit | milk | herb | water | ice
# scale: linear (nhân tuyến tính) | sublinear (chuyên gia đánh dấu – không nhân thẳng)
# taste: 0–100 trên 5 trục + milk (độ béo)
#   sweetness: Dry(0) → Sweet(100)   | acidity: Soft(0) → Bright(100)
#   bitterness: Smooth(0) → Bold(100) | strength: Light(0) → Strong(100)
#   aroma: Floral(0) → Fruity(100)
# --------------------------------------------------------------------------- #
RECIPES = [
    {
        "slug": "tra-dao-o-long", "name": "Trà đào ô long", "name_en": "Peach Oolong Tea",
        "description": "Ô long thơm nhẹ, đào ngọt mềm và chút chanh để vị sáng hơn. Công thức nền dùng để thử Smart Recipe.",
        "category": "Trà trái cây", "base_tea": "Oolong", "temperature": "iced",
        "servings": 1, "prep_minutes": 10, "difficulty": "Easy", "featured": 1,
        "color": "#E39B62", "accent": "#F7D7B5",
        "taste": {"sweetness": 65, "acidity": 35, "bitterness": 30, "strength": 60, "aroma": 80, "milk": 0},
        "tags": ["Fruity", "Peach", "Bestseller"],
        "ingredients": [
            {"name": "Trà ô long (đã ủ)", "qty": 150, "unit": "ml", "role": "tea"},
            {"name": "Syrup đào", "qty": 25, "unit": "ml", "role": "fruit"},
            {"name": "Đào miếng ngâm", "qty": 40, "unit": "g", "role": "fruit"},
            {"name": "Syrup đường", "qty": 20, "unit": "ml", "role": "sweetener"},
            {"name": "Nước cốt chanh", "qty": 5, "unit": "ml", "role": "acid"},
            {"name": "Nước lọc", "qty": 180, "unit": "ml", "role": "water"},
            {"name": "Đá", "qty": 100, "unit": "g", "role": "ice"},
        ],
        "brewing": {"tea": "Ô long", "leaf_g": 6, "water_ml": 200, "temp": 90, "minutes": 3},
        "steps": [
            "Ủ 6 g ô long với 200 ml nước 90°C trong 3 phút, lọc bã, để nguội rồi lấy 150 ml trà nền.",
            "Cho syrup đào, syrup đường và nước cốt chanh vào bình lắc.",
            "Thêm trà nền, nước lọc và đá, lắc đều 10–15 giây.",
            "Rót ra ly, xếp đào miếng lên trên và dùng ngay.",
        ],
        "storage": "Dùng ngay sau khi pha. Trà nền đã ủ bảo quản ngăn mát, dùng trong 24 giờ.",
    },
    {
        "slug": "tra-vai-lai", "name": "Trà vải lài", "name_en": "Lychee Jasmine Tea",
        "description": "Hương nhài dịu quyện vải ngọt thơm – thanh, nhẹ và dễ uống.",
        "category": "Trà trái cây", "base_tea": "Green", "temperature": "iced",
        "servings": 1, "prep_minutes": 10, "difficulty": "Easy", "featured": 1,
        "color": "#E9A8A6", "accent": "#FBE4E2",
        "taste": {"sweetness": 70, "acidity": 30, "bitterness": 20, "strength": 45, "aroma": 55, "milk": 0},
        "tags": ["Floral", "Lychee", "Summer"],
        "ingredients": [
            {"name": "Trà lài (đã ủ)", "qty": 160, "unit": "ml", "role": "tea"},
            {"name": "Syrup vải", "qty": 25, "unit": "ml", "role": "fruit"},
            {"name": "Vải ngâm", "qty": 50, "unit": "g", "role": "fruit"},
            {"name": "Syrup đường", "qty": 15, "unit": "ml", "role": "sweetener"},
            {"name": "Nước cốt chanh", "qty": 5, "unit": "ml", "role": "acid"},
            {"name": "Nước lọc", "qty": 150, "unit": "ml", "role": "water"},
            {"name": "Đá", "qty": 100, "unit": "g", "role": "ice"},
        ],
        "brewing": {"tea": "Trà lài", "leaf_g": 5, "water_ml": 200, "temp": 80, "minutes": 3},
        "steps": [
            "Ủ 5 g trà lài với 200 ml nước 80°C trong 3 phút, lọc bã, để nguội.",
            "Cho syrup vải, syrup đường, nước cốt chanh vào bình lắc.",
            "Thêm 160 ml trà nền, nước lọc, đá và lắc đều.",
            "Rót ra ly, thêm vải ngâm.",
        ],
        "storage": "Dùng ngay. Vải ngâm sau khi mở nắp bảo quản ngăn mát.",
    },
    {
        "slug": "tra-xoai-lai", "name": "Trà xoài lài", "name_en": "Mango Jasmine Tea",
        "description": "Xoài chín xay mịn cùng trà lài và chút tắc – nhiệt đới, đậm trái cây.",
        "category": "Trà trái cây", "base_tea": "Green", "temperature": "iced",
        "servings": 1, "prep_minutes": 12, "difficulty": "Easy", "featured": 0,
        "color": "#F2B33D", "accent": "#FCE7B6",
        "taste": {"sweetness": 68, "acidity": 45, "bitterness": 18, "strength": 40, "aroma": 88, "milk": 0},
        "tags": ["Fruity", "Mango", "Tropical"],
        "ingredients": [
            {"name": "Trà lài (đã ủ)", "qty": 150, "unit": "ml", "role": "tea"},
            {"name": "Xoài chín", "qty": 60, "unit": "g", "role": "fruit"},
            {"name": "Syrup đường", "qty": 15, "unit": "ml", "role": "sweetener"},
            {"name": "Nước cốt tắc", "qty": 8, "unit": "ml", "role": "acid"},
            {"name": "Nước lọc", "qty": 140, "unit": "ml", "role": "water"},
            {"name": "Đá", "qty": 120, "unit": "g", "role": "ice"},
        ],
        "brewing": {"tea": "Trà lài", "leaf_g": 5, "water_ml": 200, "temp": 80, "minutes": 3},
        "steps": [
            "Ủ trà lài, lọc bã, để nguội.",
            "Xay xoài chín với 50 ml nước lọc đến khi mịn.",
            "Cho xoài xay, syrup, tắc, trà nền, phần nước còn lại và đá vào bình lắc.",
            "Lắc đều và rót ra ly.",
        ],
        "storage": "Dùng ngay; xoài xay để lâu dễ tách lớp.",
    },
    {
        "slug": "tra-dau-hibiscus", "name": "Trà dâu hibiscus", "name_en": "Strawberry Hibiscus Tea",
        "description": "Hibiscus đỏ mọng, chua sáng cùng dâu tây – không caffeine.",
        "category": "Trà thảo mộc", "base_tea": "Herbal", "temperature": "iced",
        "servings": 1, "prep_minutes": 12, "difficulty": "Easy", "featured": 1,
        "color": "#C9465B", "accent": "#F4BAC3",
        "taste": {"sweetness": 55, "acidity": 82, "bitterness": 10, "strength": 35, "aroma": 88, "milk": 0},
        "tags": ["Berry", "Caffeine-free", "Bright"],
        "ingredients": [
            {"name": "Hibiscus (đã ủ)", "qty": 180, "unit": "ml", "role": "tea"},
            {"name": "Dâu tây", "qty": 50, "unit": "g", "role": "fruit"},
            {"name": "Mật ong", "qty": 15, "unit": "ml", "role": "sweetener"},
            {"name": "Nước cốt chanh", "qty": 8, "unit": "ml", "role": "acid"},
            {"name": "Nước lọc", "qty": 120, "unit": "ml", "role": "water"},
            {"name": "Đá", "qty": 100, "unit": "g", "role": "ice"},
        ],
        "brewing": {"tea": "Hibiscus", "leaf_g": 3, "water_ml": 200, "temp": 95, "minutes": 5},
        "steps": [
            "Ủ 3 g hibiscus khô với 200 ml nước 95°C trong 5 phút, lọc bã, để nguội.",
            "Dằm nhẹ dâu tây cùng mật ong dưới đáy ly.",
            "Thêm chanh, trà hibiscus, nước lọc và đá, khuấy đều.",
        ],
        "storage": "Dâu tây rửa sạch, dùng trong ngày.",
    },
    {
        "slug": "tra-chanh-mat-ong", "name": "Trà chanh mật ong bạc hà", "name_en": "Honey Lemon Mint Tea",
        "description": "Trà xanh, chanh tươi, mật ong và bạc hà – sảng khoái cho ngày nóng.",
        "category": "Trà trái cây", "base_tea": "Green", "temperature": "iced",
        "servings": 1, "prep_minutes": 8, "difficulty": "Easy", "featured": 0,
        "color": "#D6C24A", "accent": "#F3EDB8",
        "taste": {"sweetness": 50, "acidity": 75, "bitterness": 25, "strength": 40, "aroma": 70, "milk": 0},
        "tags": ["Citrus", "Lemon", "Fresh"],
        "ingredients": [
            {"name": "Trà xanh (đã ủ)", "qty": 180, "unit": "ml", "role": "tea"},
            {"name": "Mật ong", "qty": 20, "unit": "ml", "role": "sweetener"},
            {"name": "Nước cốt chanh", "qty": 15, "unit": "ml", "role": "acid"},
            {"name": "Lá bạc hà", "qty": 2, "unit": "g", "role": "herb", "scale": "sublinear"},
            {"name": "Nước lọc", "qty": 120, "unit": "ml", "role": "water"},
            {"name": "Đá", "qty": 120, "unit": "g", "role": "ice"},
        ],
        "brewing": {"tea": "Trà xanh", "leaf_g": 3, "water_ml": 200, "temp": 80, "minutes": 2},
        "steps": [
            "Ủ trà xanh 80°C trong 2 phút, lọc bã, để nguội.",
            "Hòa mật ong với chanh, vò nhẹ lá bạc hà cho vào.",
            "Thêm trà nền, nước lọc và đá, khuấy đều.",
        ],
        "storage": "Dùng ngay để giữ hương bạc hà.",
    },
    {
        "slug": "tra-tac-sa", "name": "Trà tắc sả", "name_en": "Kumquat Lemongrass Tea",
        "description": "Tắc thơm vỏ, sả ấm – một ly trà rất Việt Nam.",
        "category": "Trà trái cây", "base_tea": "Green", "temperature": "iced",
        "servings": 1, "prep_minutes": 10, "difficulty": "Easy", "featured": 0,
        "color": "#A6BF57", "accent": "#E4EDC4",
        "taste": {"sweetness": 55, "acidity": 70, "bitterness": 25, "strength": 40, "aroma": 55, "milk": 0},
        "tags": ["Citrus", "Herbal", "Budget"],
        "ingredients": [
            {"name": "Trà xanh (đã ủ)", "qty": 170, "unit": "ml", "role": "tea"},
            {"name": "Nước cốt tắc", "qty": 15, "unit": "ml", "role": "acid"},
            {"name": "Sả đập dập", "qty": 10, "unit": "g", "role": "herb", "scale": "sublinear"},
            {"name": "Syrup đường", "qty": 20, "unit": "ml", "role": "sweetener"},
            {"name": "Nước lọc", "qty": 120, "unit": "ml", "role": "water"},
            {"name": "Đá", "qty": 120, "unit": "g", "role": "ice"},
        ],
        "brewing": {"tea": "Trà xanh", "leaf_g": 3, "water_ml": 200, "temp": 80, "minutes": 2},
        "steps": [
            "Ủ trà xanh cùng sả đập dập trong 3 phút, lọc bã, để nguội.",
            "Thêm syrup, nước cốt tắc, nước lọc và đá, khuấy đều.",
            "Trang trí bằng vài lát tắc.",
        ],
        "storage": "Trà ủ sả dùng trong 24 giờ, bảo quản ngăn mát.",
    },
    {
        "slug": "matcha-latte-yen-mach", "name": "Matcha latte sữa yến mạch", "name_en": "Oat Matcha Latte",
        "description": "Matcha đậm, êm nhờ sữa yến mạch và chút vanilla – không sữa bò.",
        "category": "Trà sữa", "base_tea": "Matcha", "temperature": "iced",
        "servings": 1, "prep_minutes": 5, "difficulty": "Medium", "featured": 1,
        "color": "#7FA14F", "accent": "#E3EBCF",
        "taste": {"sweetness": 45, "acidity": 15, "bitterness": 40, "strength": 78, "aroma": 40, "milk": 85},
        "tags": ["Creamy", "Dairy-free", "Matcha"],
        "ingredients": [
            {"name": "Bột matcha", "qty": 3, "unit": "g", "role": "tea"},
            {"name": "Nước nóng 75°C", "qty": 40, "unit": "ml", "role": "water"},
            {"name": "Sữa yến mạch", "qty": 180, "unit": "ml", "role": "milk"},
            {"name": "Syrup vanilla", "qty": 10, "unit": "ml", "role": "sweetener"},
            {"name": "Đá", "qty": 120, "unit": "g", "role": "ice"},
        ],
        "brewing": {"tea": "Matcha", "leaf_g": 3, "water_ml": 40, "temp": 75, "minutes": 0.5},
        "steps": [
            "Rây 3 g matcha, thêm 40 ml nước 75°C, đánh bằng chổi tre khoảng 20 giây đến khi mịn.",
            "Cho đá, syrup vanilla và sữa yến mạch vào ly.",
            "Rót matcha lên trên tạo lớp, khuấy trước khi uống.",
        ],
        "storage": "Matcha đã đánh nên dùng ngay; bột matcha bảo quản kín, tránh ánh sáng.",
    },
    {
        "slug": "hojicha-sua-caramel", "name": "Hojicha sữa caramel", "name_en": "Caramel Hojicha Milk",
        "description": "Trà rang hojicha thơm khói, sữa béo và caramel ngọt ấm.",
        "category": "Trà sữa", "base_tea": "Green", "temperature": "iced",
        "servings": 1, "prep_minutes": 8, "difficulty": "Easy", "featured": 0,
        "color": "#A2683B", "accent": "#EBD3BC",
        "taste": {"sweetness": 58, "acidity": 10, "bitterness": 40, "strength": 70, "aroma": 45, "milk": 80},
        "tags": ["Roasted", "Creamy"],
        "ingredients": [
            {"name": "Hojicha (đã ủ)", "qty": 120, "unit": "ml", "role": "tea"},
            {"name": "Sữa tươi", "qty": 150, "unit": "ml", "role": "milk"},
            {"name": "Syrup caramel", "qty": 15, "unit": "ml", "role": "sweetener"},
            {"name": "Đá", "qty": 100, "unit": "g", "role": "ice"},
        ],
        "brewing": {"tea": "Hojicha", "leaf_g": 4, "water_ml": 150, "temp": 90, "minutes": 2},
        "steps": [
            "Ủ 4 g hojicha với 150 ml nước 90°C trong 2 phút, lọc bã.",
            "Cho caramel và đá vào ly, thêm sữa tươi.",
            "Rót 120 ml hojicha lên trên, khuấy đều.",
        ],
        "storage": "Dùng ngay. Sữa tươi bảo quản ngăn mát sau khi mở.",
    },
    {
        "slug": "o-long-rang-nguyen-ban", "name": "Ô long rang nguyên bản", "name_en": "Pure Roasted Oolong",
        "description": "Không đường, không topping – để vị trà rang tự nói.",
        "category": "Trà nguyên bản", "base_tea": "Oolong", "temperature": "hot",
        "servings": 1, "prep_minutes": 5, "difficulty": "Medium", "featured": 0,
        "color": "#7B4A2A", "accent": "#E2C7A8",
        "taste": {"sweetness": 5, "acidity": 15, "bitterness": 65, "strength": 82, "aroma": 40, "milk": 0},
        "tags": ["Roasted", "No sugar", "Classic"],
        "ingredients": [
            {"name": "Trà ô long rang (đã ủ)", "qty": 250, "unit": "ml", "role": "tea"},
        ],
        "brewing": {"tea": "Ô long rang", "leaf_g": 5, "water_ml": 250, "temp": 95, "minutes": 1},
        "steps": [
            "Tráng ấm và chén bằng nước sôi.",
            "Cho 5 g ô long rang vào ấm, tráng nhanh 5 giây rồi bỏ nước.",
            "Rót 250 ml nước 95°C, ủ 1 phút, rót ra chén. Có thể ủ thêm 2–3 lần, mỗi lần tăng 15–20 giây.",
        ],
        "storage": "Lá trà khô bảo quản kín, nơi khô ráo.",
    },
    {
        "slug": "tra-trang-hoa-hong", "name": "Trà trắng hoa hồng", "name_en": "White Tea & Rose",
        "description": "Trà trắng thanh mảnh cùng nụ hồng khô – nhẹ như một lời thì thầm.",
        "category": "Trà hoa", "base_tea": "White", "temperature": "hot",
        "servings": 1, "prep_minutes": 6, "difficulty": "Easy", "featured": 0,
        "color": "#E3BFC0", "accent": "#F8EAEA",
        "taste": {"sweetness": 25, "acidity": 15, "bitterness": 10, "strength": 25, "aroma": 10, "milk": 0},
        "tags": ["Floral", "Light", "Less sugar"],
        "ingredients": [
            {"name": "Trà trắng (đã ủ)", "qty": 220, "unit": "ml", "role": "tea"},
            {"name": "Nụ hồng khô", "qty": 2, "unit": "g", "role": "herb", "scale": "sublinear"},
            {"name": "Mật ong", "qty": 8, "unit": "ml", "role": "sweetener"},
        ],
        "brewing": {"tea": "Trà trắng", "leaf_g": 3, "water_ml": 250, "temp": 80, "minutes": 4},
        "steps": [
            "Cho 3 g trà trắng và nụ hồng khô vào ấm.",
            "Rót 250 ml nước 80°C, ủ 4 phút.",
            "Lọc ra chén, thêm mật ong nếu muốn.",
        ],
        "storage": "Hoa khô bảo quản kín, tránh ẩm.",
    },
    {
        "slug": "tra-den-cam-que", "name": "Trà đen cam quế", "name_en": "Orange Cinnamon Black Tea",
        "description": "Trà đen ấm, cam tươi và quế – hợp những ngày se lạnh.",
        "category": "Trà trái cây", "base_tea": "Black", "temperature": "hot",
        "servings": 1, "prep_minutes": 8, "difficulty": "Easy", "featured": 0,
        "color": "#B4532F", "accent": "#F2CDB8",
        "taste": {"sweetness": 45, "acidity": 50, "bitterness": 50, "strength": 75, "aroma": 62, "milk": 0},
        "tags": ["Spiced", "Citrus", "Winter"],
        "ingredients": [
            {"name": "Trà đen (đã ủ)", "qty": 200, "unit": "ml", "role": "tea"},
            {"name": "Cam vắt", "qty": 40, "unit": "ml", "role": "acid"},
            {"name": "Quế thanh", "qty": 1, "unit": "g", "role": "herb", "scale": "sublinear"},
            {"name": "Mật ong", "qty": 15, "unit": "ml", "role": "sweetener"},
        ],
        "brewing": {"tea": "Trà đen", "leaf_g": 4, "water_ml": 220, "temp": 95, "minutes": 4},
        "steps": [
            "Ủ trà đen cùng quế thanh với nước 95°C trong 4 phút, lọc bã.",
            "Thêm cam vắt và mật ong, khuấy đều.",
            "Trang trí bằng một lát cam.",
        ],
        "storage": "Dùng nóng ngay sau khi pha.",
    },
    {
        "slug": "o-long-sua-foam", "name": "Ô long sữa foam kem", "name_en": "Oolong Milk Tea with Cream Foam",
        "description": "Trà sữa ô long béo nhẹ với lớp foam kem mịn.",
        "category": "Trà sữa", "base_tea": "Oolong", "temperature": "iced",
        "servings": 1, "prep_minutes": 10, "difficulty": "Medium", "featured": 0,
        "color": "#CFAE7F", "accent": "#F4E6D2",
        "taste": {"sweetness": 60, "acidity": 10, "bitterness": 30, "strength": 65, "aroma": 40, "milk": 82},
        "tags": ["Creamy", "Milk tea"],
        "ingredients": [
            {"name": "Trà ô long (đã ủ)", "qty": 150, "unit": "ml", "role": "tea"},
            {"name": "Sữa tươi", "qty": 100, "unit": "ml", "role": "milk"},
            {"name": "Syrup đường", "qty": 20, "unit": "ml", "role": "sweetener"},
            {"name": "Foam kem sữa", "qty": 40, "unit": "ml", "role": "milk"},
            {"name": "Đá", "qty": 100, "unit": "g", "role": "ice"},
        ],
        "brewing": {"tea": "Ô long", "leaf_g": 7, "water_ml": 200, "temp": 90, "minutes": 4},
        "steps": [
            "Ủ ô long đậm (7 g/200 ml, 90°C, 4 phút), lọc bã, để nguội.",
            "Lắc trà nền với syrup, sữa tươi và đá.",
            "Rót ra ly, phủ foam kem lên trên.",
        ],
        "storage": "Foam kem dùng trong ngày, bảo quản ngăn mát.",
    },
    {
        "slug": "tra-xanh-cold-brew-bac-ha", "name": "Trà xanh cold brew bạc hà", "name_en": "Mint Green Cold Brew",
        "description": "Ủ lạnh qua đêm cho vị trà ngọt hậu, ít chát; bạc hà mát nhẹ.",
        "category": "Cold brew", "base_tea": "Green", "temperature": "cold_brew",
        "servings": 1, "prep_minutes": 10, "difficulty": "Easy", "featured": 0,
        "color": "#93C29E", "accent": "#DDEFE1",
        "taste": {"sweetness": 20, "acidity": 20, "bitterness": 18, "strength": 45, "aroma": 25, "milk": 0},
        "tags": ["Cold brew", "Fresh", "Less sugar"],
        "ingredients": [
            {"name": "Trà xanh cold brew", "qty": 300, "unit": "ml", "role": "tea"},
            {"name": "Lá bạc hà", "qty": 3, "unit": "g", "role": "herb", "scale": "sublinear"},
            {"name": "Mật ong", "qty": 10, "unit": "ml", "role": "sweetener"},
        ],
        "brewing": {"tea": "Trà xanh (cold brew)", "leaf_g": 8, "water_ml": 1000, "temp": 5, "minutes": 480},
        "steps": [
            "Cho 8 g trà xanh vào 1 lít nước lọc lạnh, ủ ngăn mát 8 giờ (thời gian 10 phút chưa tính thời gian ủ).",
            "Lọc bã, lấy 300 ml trà.",
            "Vò nhẹ bạc hà, thêm mật ong nếu muốn, khuấy đều.",
        ],
        "storage": "Trà cold brew bảo quản ngăn mát, dùng trong 48 giờ.",
    },
]

# --------------------------------------------------------------------------- #
# 4. WORKSHOP (minh họa – địa điểm, lịch và giá là giả định)
# --------------------------------------------------------------------------- #
WORKSHOPS = [
    {
        "slug": "from-leaf-to-cup", "name": "From Leaf to Cup",
        "summary": "Tìm hiểu hành trình từ búp trà đến chén trà và thử các bước chế biến cơ bản.",
        "audience": "Người mới bắt đầu, Tea Explorer",
        "content": ["Các loại trà chính và khác biệt chế biến", "Thử làm héo, vò, sao lá trà",
                    "Nếm so sánh trà xanh – ô long – trà đen"],
        "duration": "120 phút", "location": "Tea Lab, Quận 3, TP.HCM (địa điểm minh họa)",
        "starts_at": "2026-11-21 09:00", "capacity": 20, "price": 350000,
        "takeaway": "Một túi trà tự chế biến 20 g và sổ tay ghi chép vị", "color": "#71866A",
    },
    {
        "slug": "blend-your-tea", "name": "Blend Your Tea",
        "summary": "Phối trà nền với hoa, trái cây khô và thảo mộc để tạo hỗn hợp của riêng bạn.",
        "audience": "Tea Creator, nhóm bạn",
        "content": ["Nguyên tắc cân bằng hương", "Thực hành phối 3 công thức", "Đặt tên và đóng gói blend"],
        "duration": "90 phút", "location": "Tea Lab, Quận 3, TP.HCM (địa điểm minh họa)",
        "starts_at": "2026-11-28 14:00", "capacity": 16, "price": 390000,
        "takeaway": "Hũ trà blend 50 g mang tên bạn", "color": "#C88F67",
    },
    {
        "slug": "trong-vi-nha", "name": "Tr(ồng vị nh)à – Tea & Art",
        "summary": "Pha một ly trà đặc trưng và tự trang trí chiếc cốc mang dấu ấn cá nhân.",
        "audience": "Experience Seeker, cặp đôi, gia đình",
        "content": ["Pha 1 công thức theo Tea DNA của bạn", "Vẽ và trang trí cốc sứ", "Chụp ảnh thẻ công thức"],
        "duration": "120 phút", "location": "Tea Lab, Quận 3, TP.HCM (địa điểm minh họa)",
        "starts_at": "2026-12-05 09:30", "capacity": 18, "price": 420000,
        "takeaway": "Cốc sứ tự trang trí (nung sau 7 ngày)", "color": "#B4532F",
    },
    {
        "slug": "my-signature-tea", "name": "My Signature Tea",
        "summary": "Làm việc cùng Tea Specialist để sáng tạo công thức đồ uống của riêng bạn.",
        "audience": "Tea Creator, chủ quán nhỏ",
        "content": ["Đọc hồ sơ Tea DNA", "Thử nghiệm 3 phiên bản trong Smart Recipe", "Chốt công thức và tính cost"],
        "duration": "120 phút", "location": "Tea Lab, Quận 3, TP.HCM (địa điểm minh họa)",
        "starts_at": "2026-12-12 14:00", "capacity": 12, "price": 490000,
        "takeaway": "Recipe card in sẵn và công thức lưu trong My Tea Space", "color": "#263D32",
    },
    {
        "slug": "kombucha-lab", "name": "Kombucha Lab",
        "summary": "Tìm hiểu lên men có kiểm soát dưới sự hướng dẫn của chuyên gia an toàn thực phẩm.",
        "audience": "Người đã có kinh nghiệm pha trà",
        "content": ["Vệ sinh dụng cụ và kiểm soát môi trường", "Theo dõi pH, áp suất, dấu hiệu nhiễm bẩn",
                    "Bảo quản và nhận biết khi nào phải bỏ mẻ"],
        "duration": "150 phút", "location": "Tea Lab, Quận 3, TP.HCM (địa điểm minh họa)",
        "starts_at": "2026-12-19 09:00", "capacity": 12, "price": 550000,
        "takeaway": "Bộ hướng dẫn an toàn đã được chuyên gia xác minh", "color": "#C9465B",
        "safety": "Nền tảng không đăng thông số lên men trực tuyến. Toàn bộ quy trình chỉ thực hiện trong buổi workshop có chuyên gia giám sát.",
    },
]

# --------------------------------------------------------------------------- #
# 5. THỬ THÁCH CỘNG ĐỒNG
# --------------------------------------------------------------------------- #
CHALLENGES = [
    {"slug": "create-under-30k", "name": "Create Under 30K",
     "description": "Tạo một đồ uống có chi phí nguyên liệu dưới 30.000đ/ly.", "reward": "Badge: Smart Spender",
     "ends_at": "2026-11-30", "rule": "cost_under_30k"},
    {"slug": "less-sugar", "name": "Less Sugar Challenge",
     "description": "Sáng tạo công thức ngon mà vẫn ít đường (Sweetness ≤ 40).", "reward": "Badge: Sugar Wise",
     "ends_at": "2026-12-15", "rule": "less_sugar"},
    {"slug": "summer-tea", "name": "Summer Tea",
     "description": "Một ly trà lạnh, sảng khoái cho mùa hè Sài Gòn.", "reward": "Featured recipe trên trang chủ",
     "ends_at": "2026-12-31", "rule": None},
    {"slug": "one-ingredient-three-ways", "name": "One Ingredient, Three Ways",
     "description": "Dùng một nguyên liệu để tạo 3 công thức khác nhau.", "reward": "+100 Garden XP",
     "ends_at": "2027-01-15", "rule": None},
    {"slug": "mystery-ingredient", "name": "Mystery Ingredient",
     "description": "Nguyên liệu bí mật tháng này: sả. Hãy biến nó thành một ly trà bất ngờ.",
     "reward": "Danh hiệu: Flavor Detective", "ends_at": "2026-11-30", "rule": None},
    {"slug": "tea-around-the-world", "name": "Tea Around the World",
     "description": "Thử ít nhất 4 loại trà nền khác nhau (xanh, đen, ô long, trắng).",
     "reward": "Tea Passport stamp", "ends_at": "2027-02-28", "rule": None},
]

# --------------------------------------------------------------------------- #
# 6. CÔNG THỨC CỘNG ĐỒNG MẪU (của tài khoản demo)
# --------------------------------------------------------------------------- #
COMMUNITY = [
    {
        "title": "Peach Tea v1.1 – Less Sweet", "base_slug": "tra-dao-o-long", "version_label": "v1.1",
        "description": "Bớt 25% đường, tăng nhẹ chanh. Vị trà rõ hơn mà vẫn thơm đào.",
        "category": "Trà trái cây", "tea_base": "Oolong", "temperature": "iced", "prep_minutes": 10,
        "taste": {"sweetness": 48, "acidity": 42, "bitterness": 30, "strength": 60, "aroma": 78, "milk": 0},
        "ingredients": [
            {"name": "Trà ô long (đã ủ)", "qty": 150, "unit": "ml", "role": "tea"},
            {"name": "Syrup đào", "qty": 25, "unit": "ml", "role": "fruit"},
            {"name": "Đào miếng ngâm", "qty": 40, "unit": "g", "role": "fruit"},
            {"name": "Syrup đường", "qty": 15, "unit": "ml", "role": "sweetener"},
            {"name": "Nước cốt chanh", "qty": 6, "unit": "ml", "role": "acid"},
            {"name": "Nước lọc", "qty": 184, "unit": "ml", "role": "water"},
            {"name": "Đá", "qty": 100, "unit": "g", "role": "ice"},
        ],
        "steps": ["Pha như công thức gốc, giảm syrup đường còn 15 ml.", "Tăng chanh lên 6 ml, bù nước lọc để giữ dung tích."],
        "tags": ["Less sugar", "Peach"], "challenge": "less-sugar",
    },
    {
        "title": "Trà tắc sả gừng ấm", "base_slug": None, "version_label": "v1.0",
        "description": "Biến thể nóng của trà tắc sả, thêm chút ấm áp cho mùa mưa.",
        "category": "Trà trái cây", "tea_base": "Green", "temperature": "hot", "prep_minutes": 10,
        "taste": {"sweetness": 45, "acidity": 60, "bitterness": 25, "strength": 45, "aroma": 45, "milk": 0},
        "ingredients": [
            {"name": "Trà xanh (đã ủ)", "qty": 220, "unit": "ml", "role": "tea"},
            {"name": "Nước cốt tắc", "qty": 12, "unit": "ml", "role": "acid"},
            {"name": "Sả đập dập", "qty": 10, "unit": "g", "role": "herb", "scale": "sublinear"},
            {"name": "Mật ong", "qty": 15, "unit": "ml", "role": "sweetener"},
        ],
        "steps": ["Ủ trà xanh cùng sả 3 phút ở 80°C.", "Thêm tắc và mật ong, khuấy đều, dùng nóng."],
        "tags": ["Herbal", "Hot"], "challenge": "mystery-ingredient",
    },
    {
        "title": "Hibiscus Berry Spritz", "base_slug": "tra-dau-hibiscus", "version_label": "v1.0",
        "description": "Không caffeine, chua sáng, dưới 20K một ly.",
        "category": "Trà thảo mộc", "tea_base": "Herbal", "temperature": "iced", "prep_minutes": 12,
        "taste": {"sweetness": 50, "acidity": 85, "bitterness": 10, "strength": 30, "aroma": 90, "milk": 0},
        "ingredients": [
            {"name": "Hibiscus (đã ủ)", "qty": 200, "unit": "ml", "role": "tea"},
            {"name": "Puree dâu", "qty": 30, "unit": "g", "role": "fruit"},
            {"name": "Syrup đường", "qty": 15, "unit": "ml", "role": "sweetener"},
            {"name": "Nước cốt chanh", "qty": 8, "unit": "ml", "role": "acid"},
            {"name": "Nước lọc", "qty": 100, "unit": "ml", "role": "water"},
            {"name": "Đá", "qty": 120, "unit": "g", "role": "ice"},
        ],
        "steps": ["Ủ hibiscus, để nguội.", "Lắc cùng puree dâu, syrup, chanh và đá.", "Rót ra ly, thêm nước lọc."],
        "tags": ["Berry", "Caffeine-free", "Budget"], "challenge": "create-under-30k",
    },
]
