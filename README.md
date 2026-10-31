# TeaWay – Explore Tea. Create Your Way.

Website MVP cho nền tảng Digital-first Tea Lifestyle & Creation, viết bằng **Python (Flask) + SQLite**.
Không cần cài database – file dữ liệu tự tạo khi chạy lần đầu.

## Chạy trong PyCharm (khoảng 2 phút)

1. Giải nén `teaway.zip` → mở PyCharm → **File › Open** → chọn thư mục `teaway`.
2. Mở **Terminal** trong PyCharm (Mac) và chạy:
   ```
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
   Sau đó vào **Settings › Project › Python Interpreter › Add Interpreter › Add Local Interpreter › Existing**
   và chọn `teaway/.venv/bin/python` để nút ▶ Run dùng đúng môi trường.
3. Mở `app.py` → bấm nút ▶ **Run** (hoặc chuột phải › Run 'app').
4. Mở trình duyệt: **http://127.0.0.1:5001**

Tài khoản demo: `demo@teaway.vn` / `tea12345` (hoặc tự đăng ký).

Yêu cầu: Python 3.9 trở lên. Muốn reset dữ liệu về ban đầu: tắt server, xóa thư mục `instance/`, chạy lại.

## Cấu trúc thư mục

```
teaway/
├── app.py              # Chạy file này. Toàn bộ route (trang + API)
├── db.py               # Schema SQLite + nạp dữ liệu mẫu
├── engine.py           # Recipe Engine (rule-based): slider, giữ dung tích, scale, thay thế, cost
├── tea_dna.py          # Tea DNA: câu hỏi, chấm điểm 5 trục, 13 hồ sơ, độ tự tin
├── seed_data.py        # Nguyên liệu (giá), 13 công thức, 5 workshop, 6 thử thách
├── requirements.txt
├── render.yaml       # Cấu hình deploy Render (xem DEPLOY.md)
├── instance/teaway.db  # Tự tạo khi chạy lần đầu
├── static/
│   ├── css/style.css   # Design system: Forest, Sage, Cream, Terracotta, Ivory
│   └── js/             # main.js, smart_recipe.js, studio.js, garden.js
└── templates/          # 20 trang Jinja2
```

## Các trang

| URL | Chức năng |
|---|---|
| `/` | Home: hero, 6 dịch vụ, Tea DNA, công thức nổi bật, cộng đồng, workshop |
| `/explore` | Tea Library: tìm kiếm không dấu + 9 nhóm bộ lọc kết hợp được |
| `/recipes/<slug>` | Recipe Detail: nguyên liệu, bước pha, brewing guide, dị ứng, cost, Save vào bộ sưu tập |
| `/recipes/<slug>/customize` | **Smart Recipe**: slider, số ly, giữ dung tích, thay nguyên liệu, so sánh, lưu phiên bản |
| `/create`, `/create/studio` | Recipe Studio: tạo mới, sửa (tạo v1.x / v2.0), “Create my version” có ghi nhận tác giả |
| `/tea-dna` | Bài test 12 câu → hồ sơ, điểm 5 trục, độ tự tin, chỉnh tay, gợi ý |
| `/community` | For You, Trending, New, Challenges, Following; like, bình luận + sao, báo cáo |
| `/workshops` | Danh sách, trang chi tiết, đặt chỗ (kiểm tra số chỗ, SĐT, chính sách hủy) |
| `/play` | Tea Garden: trồng → chế biến → Blending Lab → Tea House → Journal, daily tasks, 5 cấp |
| `/my-space` | Tea DNA, My Recipes, Collections, Tea Passport (huy hiệu), Preferences, xóa dữ liệu |

## Ghi chú

- Công thức, giá nguyên liệu, lịch workshop là **dữ liệu minh họa** – cần kiểm thử thực tế trước khi công bố.
- Bản MVP chưa tích hợp cổng thanh toán; đặt chỗ workshop lưu ở trạng thái “chờ xác nhận”.
- Đổi tên thương hiệu: sửa `SITE_NAME` trong `app.py`.
- Trước khi đưa lên mạng: đặt biến môi trường `SECRET_KEY` và tắt `debug=True`.

## Chia sẻ online

Xem hướng dẫn đưa lên GitHub và tạo link public trong `DEPLOY.md`.
