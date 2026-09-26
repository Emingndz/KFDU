# KFDU — Kitap ve Film Değerlendirme Uygulaması

Film, dizi ve kitap kütüphaneni oluşturduğun, puanlayıp incelediğin, özel listeler
yaptığın ve takip ettiğin kişilerin aktivitelerini akışta gördüğün sosyal platform.

v2 geliştirmesi devam ediyor — bkz. [`proje-plani.md`](proje-plani.md) ve
[`proje-ilerleme-durumu.md`](proje-ilerleme-durumu.md).

## Backend'i çalıştırma (geçici — Faz 7'de genişleyecek)

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1          # Git Bash: source .venv/Scripts/activate
pip install -r requirements-dev.txt
Copy-Item .env.example .env           # ardından TMDB_API_KEY vb. değerleri doldur
alembic upgrade head
python -m scripts.seed                # demo verisi yükler (--reset: veritabanını sıfırdan kurar)
uvicorn app.main:app --reload         # http://127.0.0.1:8000/docs
```

Testler:

```powershell
pytest
ruff check . ; ruff format .
```

Demo kullanıcılarla giriş (Swagger `/docs` → `/auth/login`): `demo1`…`demo6`,
şifre `Demo1234!`.
