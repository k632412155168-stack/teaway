# Đưa TeaWay lên mạng để mọi người xem

**Lưu ý:** GitHub Pages chỉ chạy được web tĩnh (HTML/CSS/JS). TeaWay dùng Python (Flask) và database, nên cần 2 phần:

1. **GitHub** – nơi lưu code.
2. **Một dịch vụ chạy Python miễn phí** – để có link public.

Chọn 1 trong 2 dịch vụ ở Bước 2.

---

## Bước 1 – Đưa code lên GitHub

1. Vào github.com → **New repository** → đặt tên `teaway` → chọn **Public** → **Create**.
   Không tick “Add a README”.
2. Mở Terminal tại thư mục `teaway` và chạy (thay `TEN-GITHUB` bằng username của bạn):

```
git init
git add .
git commit -m "TeaWay MVP"
git branch -M main
git remote add origin https://github.com/TEN-GITHUB/teaway.git
git push -u origin main
```

Khi được hỏi mật khẩu, GitHub yêu cầu **Personal Access Token** thay cho mật khẩu.
Cách dễ hơn: dùng **GitHub Desktop**, kéo thư mục `teaway` vào, rồi bấm **Publish repository**.

File `.gitignore` đã loại sẵn `.venv/` và `instance/` (database), nên không đẩy nhầm lên GitHub.

---

## Bước 2 (cách A) – Render: nhanh nhất, tự cập nhật khi push code

1. Vào render.com → đăng nhập bằng GitHub.
2. Chọn **New › Blueprint**, rồi chọn repo `teaway`.
   Render đọc file `render.yaml` có sẵn → bấm **Apply**.
3. Chờ vài phút → nhận link dạng `https://teaway-xxxx.onrender.com`.

**Đặc điểm gói Free:**
- Sau 15 phút không ai truy cập, web sẽ “ngủ”. Lần mở tiếp theo mất khoảng 1 phút để khởi động.
- Database **bị reset về dữ liệu mẫu** mỗi lần web ngủ hoặc deploy lại.
  Tài khoản đăng ký và công thức người xem tạo sẽ mất. Tài khoản demo luôn còn.
- Phù hợp để demo, thuyết trình hoặc gửi giảng viên xem.

---

## Bước 2 (cách B) – PythonAnywhere: dữ liệu được giữ lại

1. Đăng ký tài khoản Beginner (miễn phí) tại pythonanywhere.com.
2. Mở tab **Consoles › Bash** và chạy:

```
git clone https://github.com/TEN-GITHUB/teaway.git
cd teaway
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Vào tab **Web › Add a new web app** → **Manual configuration** → chọn bản Python mới nhất.
4. Trong trang Web:
   - **Virtualenv:** điền `/home/TEN-PA/teaway/.venv`
   - **Source code:** điền `/home/TEN-PA/teaway`
5. Bấm vào link **WSGI configuration file**, xóa hết nội dung, rồi dán:

```python
import sys
sys.path.insert(0, "/home/TEN-PA/teaway")
import os
os.environ["SECRET_KEY"] = "doi-chuoi-nay-thanh-chuoi-bi-mat-cua-ban"
from app import app as application
```

6. Bấm **Reload** → web chạy tại `https://TEN-PA.pythonanywhere.com`.

**Đặc điểm gói Free:**
- Web không “ngủ” và database SQLite được giữ lại.
- Web app không dùng sẽ hết hạn sau 1 tháng. Vào tab Web bấm gia hạn (nút “Run until…”) trước khi hết hạn.

(`TEN-PA` = username PythonAnywhere của bạn.)

---

## Cập nhật web sau khi sửa code

```
git add .
git commit -m "Mô tả thay đổi"
git push
```

- **Render:** tự deploy lại sau khi push.
- **PythonAnywhere:** vào Bash, chạy `cd teaway && git pull`, rồi bấm **Reload** ở tab Web.
