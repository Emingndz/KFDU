# KFDU v2 — Proje İlerleme Durumu

> Plan: [`proje-plani.md`](proje-plani.md) · Bu dosya **her adımdan sonra** güncellenir (plan §0.2, madde 7).
> Son güncelleme: **2026-09-26** — Analiz ve plan hazırlandı; henüz kod değişikliği yok.

## Bu dosya nasıl güncellenir?

1. Adıma başlarken "🧭 Anlık Durum" tablosunda sıradaki adımı 🟨 yap.
2. Adım bitince:
   - "✅ Adım Kontrol Listesi"nde kutuyu işaretle (`[x]`) ve tarihi yaz,
   - "📝 Adım Günlüğü"nün **en üstüne** şablona uygun yeni girdi ekle,
   - kapanan maddeleri "🧩 Açık Maddeler" ve "🎓 Ödev Gereksinimleri" tablolarında ✅ yap,
   - yeni kararları "🧾 Kararlar"a, plan dışı önerileri "🔀 Plan Dışı Notlar"a yaz,
   - "📊 Faz Özeti" sayacını ve "🧭 Anlık Durum" + "Bağlam özeti"ni güncelle.
3. Kod ile birlikte commit et (plan §0.5).

---

## 🧭 Anlık Durum

| Alan | Değer |
|---|---|
| Proje durumu | 🟨 Faz 0 uygulanıyor |
| Aktif faz | Faz 0 — Güvenlik, temizlik ve hazırlık |
| Sıradaki adım | **F0.4 — Geliştirme ortamı** |
| Çalışma dalı | `v2` |
| Son commit | `7610a0c` (fix(F0.3): sırları koddan çıkar) |
| Backend | v1 — kitap uçları bozuk (BUG-01) |
| Frontend | v1 — tek dosya Vue 3 CDN |
| Açık engeller | 👤 U1 (Gmail şifresi iptali) ve U2 (TMDB anahtarı yenileme) hâlâ acil bekliyor — kodu ilerletmeyi engellemiyor ama en kısa sürede yapılmalı |

### Bağlam özeti (yeni oturum açan uygulayıcı için)

- **Proje:** KFDU — film/kitap sosyal kütüphane platformu. v1: FastAPI + SQLAlchemy + SQLite backend, tek dosya Vue 3 (CDN) frontend; Kocaeli Üniversitesi Yazlab-I Proje II ödevi.
- **Analiz (2026-09-26):** Bulgular planın §2'sinde — SEC-01…09, BUG-01…20, DEBT-01…07; ödev eksikleri Ek A'da.
- **Kitaplar neden bozuk:** Google Books anahtarsız çağrılıyor → HTTP 429 (anonim kota 0) → API `null` dönüyor. Çözüm: Open Library (F1.6).
- **Güvenlik:** GitHub deposu public; kodda Gmail uygulama şifresi, sabit JWT anahtarı, TMDB anahtarı; depoda kullanıcı e-postalı veritabanı → Faz 0 önce yapılır. **F0.3 ile kod tarafı kapandı ama eski Gmail şifresi ve eski TMDB anahtarı hâlâ geçerli/aktif** — U1 ve U2 kullanıcı tarafından yapılana kadar risk devam ediyor (bkz. 👤 Kullanıcı Eylemleri).
- **Durum:** F0.1–F0.3 tamamlandı. `main`: plan dosyaları commit edildi (`ef2ccda`), `legacy-v1` etiketi orada. `v2` dalı aktif: `.gitignore` eklendi, `.pyc`/`sql_app.db` takipten çıkarıldı (`c80451f`), ödev PDF'i `docs/odev/`e taşındı, v1 `config.py`/`security.py`'deki sabit sırlar kaldırıldı ve `backend/.env` (izlenmiyor) + `backend/.env.example` oluşturuldu (`7610a0c`). v1 backend `.env` ile ayakta kalktığı ve `GET /api/v1/movies/popular`'ın HTTP 200 döndüğü doğrulandı (içerik `null` — TMDB anahtarı henüz boş, beklenen). Henüz yeni (v2) backend/frontend kodu yok; bu hâlâ hafifçe yamalı v1 kodu.
- **Ortam:** Node 22.12 kurulu; Faz 2'den önce ≥ 22.18 gerekli (U3 / F0.4).

---

## 📊 Faz Özeti

| Faz | Başlık | Durum | İlerleme | Başlangıç | Bitiş |
|---|---|---|---|---|---|
| 0 | Güvenlik, temizlik, hazırlık | 🟨 Devam ediyor | 3/5 | 2026-09-26 | – |
| 1 | Backend temeli | ⬜ Başlamadı | 0/11 | – | – |
| 2 | Frontend temeli | ⬜ Başlamadı | 0/5 | – | – |
| 3 | Çekirdek özellikler (ilk kullanılabilir v2) | ⬜ Başlamadı | 0/10 | – | – |
| 4 | Çağ atlatma paketi | ⬜ Başlamadı | 0/9 | – | – |
| 5 | Akıllı öneriler | ⬜ Başlamadı | 0/6 | – | – |
| 6 | KFDU Asistan (NVIDIA LLM) | ⬜ Başlamadı | 0/9 | – | – |
| 7 | Kalite, test, CI, yayın | ⬜ Başlamadı | 0/9 | – | – |
| **Toplam** | | | **0/64** | | |

Durum simgeleri: ⬜ Başlamadı · 🟨 Devam ediyor · ✅ Tamamlandı · ⛔ Engellendi · ⏭️ Atlandı (kullanıcı onayıyla)

---

## 👤 Kullanıcı Eylemleri ve Kararları

| # | Eylem / karar | Ne zaman | Durum |
|---|---|---|---|
| U1 | **ACİL — Gmail uygulama şifresini iptal et:** https://myaccount.google.com/apppasswords (şifre public depoda açıkta) | Hemen | ⬜ |
| U2 | TMDB API anahtarını yenile (https://www.themoviedb.org/settings/api) ve yenisini `backend/.env`'ye yaz | F0.3 | ⬜ |
| U3 | Node.js'i 24 LTS'e güncelle (en az 22.18): https://nodejs.org veya `winget install OpenJS.NodeJS.LTS` | F0.4 (Faz 2'den önce) | ⬜ |
| U4 | `backend/.env` değerlerini doldur (TMDB; isteğe bağlı yeni SMTP uygulama şifresi; `CONTACT_EMAIL`) | F0.3 | ⬜ |
| U5 | Karar: Git geçmişi temizlensin mi? (F0.5 — force push gerektirir) | Faz 0 | ⬜ |
| U6 | Karar: v1 verileri (3 kullanıcı, 12 etkileşim, 7 liste) yeni veritabanına taşınsın mı? (F1.10) | Faz 1 | ⬜ |
| U7 | NVIDIA API anahtarı al (https://build.nvidia.com → "Get API Key") ve `backend/.env` → `NVIDIA_API_KEY` | F6.1 | ⬜ |
| U8 | Karar: LLM model seçimi (`check_llm.py` tablosuna göre) | F6.1 | ⬜ |
| U9 | (Opsiyonel) Google Books API anahtarı | İstenirse | ⬜ |
| U10 | Karar: lisans (MIT önerilir) | F7.7 | ⬜ |
| U11 | Karar: canlıya alma yöntemi (opsiyonel) | F7.8 | ⬜ |
| U12 | Faz sonlarında: `v2` dalını push etme ve `main`e birleştirme onayları | Her 🏁 | ⬜ |

---

## ✅ Adım Kontrol Listesi

### Faz 0 — Güvenlik, Temizlik ve Hazırlık

- [x] F0.1 — Yedekleme ve çalışma dalı — ✅ (2026-09-26)
- [x] F0.2 — `.gitignore` ve depo temizliği — ✅ (2026-09-26)
- [x] F0.3 — Sırları koddan çıkarma (👤 U1, U2, U4) — ✅ kod tarafı (2026-09-26); 👤 anahtar iptali/yenileme hâlâ bekliyor
- [ ] F0.4 — Geliştirme ortamı (👤 U3)
- [ ] F0.5 — (Opsiyonel, 🛑 U5) Git geçmişinden sırları temizleme
- [ ] 🏁 Faz 0 kapanışı

### Faz 1 — Backend Temeli

- [ ] F1.1 — Bağımlılıklar ve proje iskeleti
- [ ] F1.2 — Çekirdek altyapı
- [ ] F1.3 — Veri modeli ve Alembic
- [ ] F1.4 — Kimlik doğrulama modülü
- [ ] F1.5 — Kullanıcılar ve takip
- [ ] F1.6 — Katalog: TMDB + Open Library (+ Google Books) — **kitaplar düzelir**
- [ ] F1.7 — Kütüphane: durum, puan, favori, inceleme yazma
- [ ] F1.8 — Sosyal: aktiviteler, akış, beğeni, yorum, bildirim
- [ ] F1.9 — Özel listeler
- [ ] F1.10 — Profil özeti, platform vitrinleri ve demo verisi (🛑 U6)
- [ ] F1.11 — Faz 1 kapanışı 🏁

### Faz 2 — Frontend Temeli

- [ ] F2.1 — Vite + Vue 3 + TypeScript iskeleti
- [ ] F2.2 — Tasarım sistemi ve temel UI bileşenleri
- [ ] F2.3 — API katmanı, oturum, router ve uygulama iskeleti
- [ ] F2.4 — Kimlik sayfaları ve onboarding
- [ ] F2.5 — Faz 2 kapanışı 🏁

### Faz 3 — Çekirdek Özellikler

- [ ] F3.1 — İçerik bileşenleri ve yardımcılar
- [ ] F3.2 — Keşfet sayfası
- [ ] F3.3 — İçerik detay sayfası
- [ ] F3.4 — İnceleme sayfası ve yorum dizisi
- [ ] F3.5 — Akış (feed) sayfası
- [ ] F3.6 — Profil sayfası
- [ ] F3.7 — Listeler
- [ ] F3.8 — Ayarlar sayfası
- [ ] F3.9 — UX cilası
- [ ] F3.10 — Faz 3 kapanışı: ilk kullanılabilir v2 🏁 (`main`e ilk birleştirme)

### Faz 4 — Çağ Atlatma Paketi

- [ ] F4.1 — Diziler (TV)
- [ ] F4.2 — Bildirim merkezi
- [ ] F4.3 — Kişi ve yazar sayfaları
- [ ] F4.4 — Kitap ↔ film köprüsü (uyarlamalar)
- [ ] F4.5 — İstatistikler ve Yıllık Özet
- [ ] F4.6 — Hedefler ve rozetler
- [ ] F4.7 — Veri dışa / içe aktarma (Letterboxd, Goodreads)
- [ ] F4.8 — PWA
- [ ] F4.9 — Faz 4 kapanışı 🏁

### Faz 5 — Akıllı Öneriler

- [ ] F5.1 — Zevk profili
- [ ] F5.2 — Öneri motoru
- [ ] F5.3 — "Ne izlesem / ne okusam?" sihirbazı ve "Beni şaşırt"
- [ ] F5.4 — Kişi önerileri
- [ ] F5.5 — Öneriler arayüzü
- [ ] F5.6 — Faz 5 kapanışı 🏁

### Faz 6 — KFDU Asistan

- [ ] F6.1 — NVIDIA anahtarı, LLM istemcisi, model seçimi (👤 U7, 🛑 U8)
- [ ] F6.2 — Niyet çıkarımı ve kural tabanlı yedek
- [ ] F6.3 — Katalog eşleme (grounding)
- [ ] F6.4 — Yanıt üretimi, konuşma kaydı, hız sınırı
- [ ] F6.5 — Asistan arayüzü
- [ ] F6.6 — (Opsiyonel, 🛑) Akışlı yanıt (SSE)
- [ ] F6.7 — "Kullanıcılar ne diyor?" AI inceleme özeti
- [ ] F6.8 — (Opsiyonel) Kitap tanıtımını Türkçeleştirme
- [ ] F6.9 — Değerlendirme ve Faz 6 kapanışı 🏁

### Faz 7 — Kalite, Test, CI, Dağıtım ve Dokümantasyon

- [ ] F7.1 — Backend test kapsamı
- [ ] F7.2 — Frontend birim ve E2E testleri
- [ ] F7.3 — Performans
- [ ] F7.4 — Güvenlik gözden geçirmesi
- [ ] F7.5 — Sürekli entegrasyon (GitHub Actions)
- [ ] F7.6 — Docker ve tek komutla çalıştırma
- [ ] F7.7 — Dokümantasyon (🛑 U10)
- [ ] F7.8 — (Opsiyonel, 🛑 U11) Canlıya alma
- [ ] F7.9 — Final: v2.0.0 🏁

---

## 🧩 Açık Maddeler (güvenlik · hata · teknik borç)

Ayrıntılar planın §2 bölümündedir. Durum: 🔴 Açık · ✅ Kapalı · ⏭️ Kapsam dışı (onaylı)

| ID | Özet | Hedef adım | Durum | Kapandığı commit |
|---|---|---|---|---|
| SEC-01 | Gmail uygulama şifresi ve adresi kodda (public depo) | 👤 U1 + F0.3 | 🟡 kod tarafı ✅ (`7610a0c`) — **eski şifre hâlâ geçerli, U1 iptali bekliyor** | |
| SEC-02 | Sabit JWT `SECRET_KEY` (token sahteciliği mümkün) | F0.3, F1.2 | ✅ | `7610a0c` |
| SEC-03 | TMDB anahtarı kodda | 👤 U2 + F0.3 | 🟡 kod tarafı ✅ (`7610a0c`) — eski anahtar hâlâ geçerli, U2 yenileme bekliyor | |
| SEC-04 | Veritabanı ve `__pycache__` depoda, `.gitignore` yok | F0.2 (+ F0.5) | ✅ (güncel ağaç; geçmiş için F0.5 opsiyonel) | `c80451f` |
| SEC-05 | Güvensiz şifre sıfırlama (süresiz, e-postaya bağsız, deneme sınırsız) | F1.4 | 🔴 | |
| SEC-06 | Kullanıcı e-postaları API'de açık; kimliksiz kullanıcı araması | F1.5 | 🔴 | |
| SEC-07 | Giriş/sıfırlamada hız sınırı yok | F1.4 | 🔴 | |
| SEC-08 | Girdi doğrulama yok (puan aralığı, metin uzunluğu, parola kuralı) | F1.4, F1.7 | 🔴 | |
| SEC-09 | CORS `*` + credentials | F1.2 | 🔴 | |
| BUG-01 | Kitaplar çalışmıyor (Google Books 429 → `null`) | F1.6 | 🔴 | |
| BUG-02 | Film detayında yönetmen/oyuncu/süre/tür yok | F1.6, F3.3 | 🔴 | |
| BUG-03 | Aynı kullanıcı adıyla kayıt → 500; yanlış/İngilizce hata | F1.4 | 🔴 | |
| BUG-04 | İki kez takip / takip etmeyeni bırakma → 500 | F1.5 | 🔴 | |
| BUG-05 | E-posta değişince oturum kırılıyor (JWT sub = e-posta) | F1.2 | 🔴 | |
| BUG-06 | 30 dk token, 401 yönetimi yok; 401 yerine 403 | F1.2, F2.3 | 🔴 | |
| BUG-07 | Kırık yer tutucu görseller (via.placeholder.com) | F2.2, F3.9 | 🔴 | |
| BUG-08 | Detay açmak arama tipini değiştirip gereksiz çağrı yapıyor | Faz 2–3 (F3.2) | 🔴 | |
| BUG-09 | Başkasının profilinde film durumları kitap etiketiyle | F3.6 | 🔴 | |
| BUG-10 | Şifre sıfırlamada "(Demo: undefined)" | F2.4 | 🔴 | |
| BUG-11 | Arama sorguları URL-encode edilmiyor | F2.3 | 🔴 | |
| BUG-12 | Akışta göreli tarih/aksiyon metni/alıntı yok | F1.8, F3.5 | 🔴 | |
| BUG-13 | Akışta sayfalama yok, N+1 sorgular | F1.8, F3.5 | 🔴 | |
| BUG-14 | Arama "daha fazla" çalışmıyor; kitap sayfa ofseti hatalı | F1.6, F3.2 | 🔴 | |
| BUG-15 | Kitap yıl filtresi sessizce filtresiz sonuç dönüyor | F1.6 | 🔴 | |
| BUG-16 | `requirements.txt` eksik (temiz kurulum çöker) | F1.1 | 🔴 | |
| BUG-17 | Migrasyon yok; artık tablolar; eşsizlik kısıtı yok | F1.3 | 🔴 | |
| BUG-18 | Dış API çağrılarında timeout yok | F1.2, F1.6 | 🔴 | |
| BUG-19 | Yetki hataları 400; yorum–aktivite aidiyeti kontrol edilmiyor | F1.8, F1.9 | 🔴 | |
| BUG-20 | Durum değerleri film/kitap için tutarsız | F1.7, F3.1 | 🔴 | |
| DEBT-01 | Tek dosya frontend, bileşen ve router yok | Faz 2–3 | 🔴 | |
| DEBT-02 | 32 `alert/confirm`, 10 `console.log` | Faz 2–3 | 🔴 | |
| DEBT-03 | Eskimiş API'ler ve bakımsız kütüphaneler | F1.2, F1.3 | 🔴 | |
| DEBT-04 | Kopya kod (film/kitap uçları, içerik oluşturma) | F1.6, F1.7 | 🔴 | |
| DEBT-05 | Ham dış API JSON'u frontend'e gidiyor | F1.6 | 🔴 | |
| DEBT-06 | `print` loglama; test/lint/README/`.env.example` yok | F1.2, Faz 7 | 🔴 | |
| DEBT-07 | Açılışta `create_all` (migrasyon yok) | F1.3 | 🔴 | |

---

## 🎓 Ödev Gereksinimleri (plan Ek A)

F3.10'da her satır kanıtıyla (sayfa / uç / test) ✅ yapılır.

| ID | Gereksinim (kısa) | Hedef adım | Durum | Kanıt |
|---|---|---|---|---|
| REQ-1.2 | Dinamik, kullanıcı dostu, mobil uyumlu arayüz | Faz 2–3 | ⬜ | |
| REQ-2.1.1a | Kayıt: kullanıcı adı, e-posta, şifre, şifre tekrarı | F1.4, F2.4 | ⬜ | |
| REQ-2.1.1b | Giriş: e-posta + şifre | F1.4, F2.4 | ⬜ | |
| REQ-2.1.1c | Net hata mesajları | F1.2, F1.4, F2.4 | ⬜ | |
| REQ-2.1.1d | Şifremi unuttum (e-posta) | F1.4, F2.4 | ⬜ | |
| REQ-2.1.2a | Takip edilenlerin aktiviteleri (yeniden eskiye) | F1.8, F3.5 | ⬜ | |
| REQ-2.1.2b | Kart başlığı: avatar, ad (link), aksiyon metni, göreli tarih | F3.5 | ⬜ | |
| REQ-2.1.2c | Türe göre gövde, afiş ön planda | F3.5 | ⬜ | |
| REQ-2.1.2d | Beğen / Yorum Yap | F1.8, F3.4, F3.5 | ⬜ | |
| REQ-2.1.2e | Puanlama kartı: büyük afiş + yıldız / x/10 | F3.5 | ⬜ | |
| REQ-2.1.2f | İnceleme kartı: 150–200 karakter alıntı + "…daha fazlasını oku" | F3.4, F3.5 | ⬜ | |
| REQ-2.1.2g | Sayfalama: ilk 10–15 + sonsuz kaydırma / daha fazla yükle | F1.8, F3.5 | ⬜ | |
| REQ-2.1.3a | Arama → detay (kapak, başlık, yıl) | F1.6, F3.2 | ⬜ | |
| REQ-2.1.3b | Vitrin: En Yüksek Puanlılar, En Popülerler | F1.10, F3.2 | ⬜ | |
| REQ-2.1.3c | Filtre: tür, yıl, puan | F1.6, F3.2 | ⬜ | |
| REQ-2.1.4a | Künye: kapak, özet, yıl, süre/sayfa, yönetmen/yazar, türler | F1.6, F3.3 | ⬜ | |
| REQ-2.1.4b | Platform puanı: ortalama + oy sayısı | F1.7, F3.3 | ⬜ | |
| REQ-2.1.4c | 1–10 puan bileşeni (güncellenebilir) | F1.7, F3.1, F3.3 | ⬜ | |
| REQ-2.1.4d | İzledim/İzlenecek · Okudum/Okunacak butonları | F1.7, F3.1, F3.3 | ⬜ | |
| REQ-2.1.4e | "Özel Listeye Ekle" menüsü | F1.9, F3.1, F3.7 | ⬜ | |
| REQ-2.1.4f | Yorumlar listesi (ad, metin, tarih) | F1.8, F3.3 | ⬜ | |
| REQ-2.1.4g | Yorum ekleme alanı + Gönder | F1.7, F3.3 | ⬜ | |
| REQ-2.1.4h | Yalnız kendi yorumunu düzenle/sil | F1.7, F1.8, F3.3, F3.4 | ⬜ | |
| REQ-2.1.5a | Profil: kullanıcı adı, avatar, biyografi | F1.5, F3.6 | ⬜ | |
| REQ-2.1.5b | Kendi profili: Profili Düzenle, Yeni Özel Liste | F3.6, F3.7 | ⬜ | |
| REQ-2.1.5c | Başkasının profili: Takip Et / Takipten Çık | F1.5, F3.6 | ⬜ | |
| REQ-2.1.5d | Sekmeli kütüphane (4 sekme) | F1.7, F3.6 | ⬜ | |
| REQ-2.1.5e | Özel listeler | F1.9, F3.6, F3.7 | ⬜ | |
| REQ-2.1.5f | Son aktiviteler (yorum + puan) | F1.8, F3.6 | ⬜ | |
| REQ-2.2.1a | Film verisi TMDb (başlık, özet, yıl, yönetmen, oyuncular, türler, kapak) | F1.6 | ⬜ | |
| REQ-2.2.1b | Kitap verisi Open Library / Google Books (başlık, yazar, açıklama, sayfa, kapak) | F1.6 | ⬜ | |
| REQ-2.2.1c | Manuel veri girişi yok | F1.6 | ⬜ | |
| REQ-3 | Tutarlı ve verimli veritabanı | F1.3 | ⬜ | |

---

## 🧾 Kararlar

| Tarih | ID | Karar | Durum |
|---|---|---|---|
| 2026-09-26 | D-01 … D-13 | Plan §12.1'deki mimari, teknoloji, veri modeli, AI ve git kararları | ⏳ Kullanıcı "başla" dediğinde onaylanmış sayılır |

---

## 🔀 Plan Dışı Notlar / Öneriler

Uygulama sırasında ortaya çıkan, planda olmayan ihtiyaç veya öneriler buraya yazılır ve kullanıcıya sorulur (plan §0.3, madde 2).

| Tarih | Adım | Not / öneri | Kullanıcı kararı |
|---|---|---|---|
| – | – | – | – |

---

## 📈 Ölçümler

| Ölçüm | Hedef | Değer | Tarih |
|---|---|---|---|
| Backend test kapsamı (servisler) | ≥ %75 | – | – |
| Lighthouse Performans (mobil: Keşfet / Detay / Akış) | ≥ 85 | – | – |
| Lighthouse Erişilebilirlik (mobil) | ≥ 90 | – | – |
| İlk yük JavaScript (gzip) | ≤ 200 KB | – | – |
| Asistan niyet doğruluğu (LLM / yedek mod) | ≥ 12/15 / ≥ 9/15 | – | – |
| Asistan yanıt süresi p50 | < 6 sn | – | – |

---

## 🖥️ Ortam Bilgisi

| Araç | Sürüm | Not |
|---|---|---|
| İşletim sistemi | Windows 11 Pro | |
| Python | 3.13.1 | ✓ |
| Node.js | 22.12.0 | ⚠️ ≥ 22.18 gerekli (U3 / F0.4) |
| npm | 11.20.0 | |
| Git uzak depo | GitHub (public) | |

---

## 📝 Adım Günlüğü (en yeni en üstte)

**Şablon:**

```markdown
### [YYYY-AA-GG] F?.? — Başlık — ✅ / ⛔ / ⏭️
- **Yapılanlar:** …
- **Değişen dosyalar:** …
- **Doğrulama:** komut → sonuç özeti
- **Kapanan maddeler:** SEC-…, BUG-…, REQ-…
- **Commit:** `abc1234`
- **Notlar / sorunlar:** …
- **Sonraki adım:** F?.?
```

### [2026-09-26] F0.3 — Sırları koddan çıkarma — ✅ (kod tarafı)

- **Yapılanlar:** `backend/.env.example` (Ek E içeriği, boş değerler) ve `backend/.env` (izlenmiyor; yeni üretilen rastgele `SECRET_KEY` + kullanıcının dolduracağı boş TMDB/SMTP alanları) oluşturuldu. `config.py`: `TMDB_API_KEY`/`SMTP_USER`/`SMTP_PASSWORD` varsayılanları boşaltıldı, varsayılansız `SECRET_KEY: str` eklendi, `SettingsConfigDict(env_file=".env", ...)` ile `.env` okuma etkinleştirildi. `security.py`: sabit `SECRET_KEY` sabiti kaldırıldı, yerine `settings.SECRET_KEY` kullanıldı. v1 backend geçici olarak ayağa kaldırılıp doğrulandı, sonra durduruldu.
- **Değişen dosyalar:** `backend/app/core/config.py`, `backend/app/core/security.py`, `backend/.env.example` (yeni), `backend/.env` (yeni, izlenmiyor).
- **Doğrulama:** `git grep -nE '(SMTP_PASSWORD|TMDB_API_KEY|SECRET_KEY)[^=\n]*=\s*"[^"]{8,}"' -- backend` → boş ✓ · `git grep -n "@gmail.com" -- backend` → boş ✓ · `python -m uvicorn main:app --port 8000` + `GET /api/v1/movies/popular` → HTTP 200 (içerik `null`, TMDB anahtarı boş olduğu için beklenen) ✓
- **Kapanan maddeler:** SEC-02 tam kapandı. SEC-01 ve SEC-03 yalnızca **kod tarafı** kapandı — eski Gmail uygulama şifresi ve eski TMDB anahtarı hâlâ geçerli olduğu için gerçek risk, kullanıcı U1/U2'yi yapana kadar sürüyor.
- **Commit:** `7610a0c`
- **Notlar / sorunlar:** ⚠️ **U1 ve U2 hâlâ yapılmadı.** Kullanıcıya tekrar hatırlatıldı: (1) https://myaccount.google.com/apppasswords → eski KFDU şifresini sil; (2) https://www.themoviedb.org/settings/api → anahtarı yenile, yenisini `backend/.env` → `TMDB_API_KEY`'e kendisi yazsın.
- **Sonraki adım:** F0.4

### [2026-09-26] F0.2 — `.gitignore` ve depo temizliği — ✅

- **Yapılanlar:** Kökte plandaki içerikle `.gitignore` oluşturuldu. 30 adet izlenen `.pyc` dosyası ve `backend/sql_app.db` `git rm --cached` ile takipten çıkarıldı (dosyalar diskte kaldı). Ödev şartname PDF'i `docs/odev/2025-2026-Yazlab-Proje2.pdf`'e taşındı (`git mv`).
- **Değişen dosyalar:** `.gitignore` (yeni); 30 `.pyc` + `backend/sql_app.db` (takipten çıkarıldı); `2025-2026 Yazlab Proje2.pdf` → `docs/odev/2025-2026-Yazlab-Proje2.pdf` (taşındı).
- **Doğrulama:** `git ls-files | grep -E '\.pyc$|\.db$'` → boş ✓ · `backend/app/core/config.py` hâlâ izleniyor ✓ · PDF `docs/odev/` altında ✓
- **Kapanan maddeler:** SEC-04 (güncel ağaç için; geçmiş commit'ler için opsiyonel F0.5 gerekir)
- **Commit:** `c80451f`
- **Notlar / sorunlar:** Yok.
- **Sonraki adım:** F0.3

### [2026-09-26] F0.1 — Yedekleme ve çalışma dalı — ✅

- **Yapılanlar:** Git durumu kontrol edildi (yalnızca iki plan dosyası izlenmiyordu, beklenen durumla eşleşti). Plan dosyaları `main` üzerinde commit edildi. `legacy-v1` etiketi o commit'e eklendi. `v2` çalışma dalı açıldı ve etkinleştirildi. v1 veritabanı `backend/legacy_backup/sql_app_v1.db` olarak yedeklendi.
- **Değişen dosyalar:** `proje-plani.md`, `proje-ilerleme-durumu.md` (main'e commit); `backend/legacy_backup/sql_app_v1.db` (yeni, izlenmiyor — commit edilmedi).
- **Doğrulama:** `git tag -l legacy-v1` → `legacy-v1` ✓ · `git branch --show-current` → `v2` ✓ · `test -f backend/legacy_backup/sql_app_v1.db` → mevcut ✓
- **Kapanan maddeler:** —
- **Commit:** `ef2ccda` (docs: v2 proje planı ve ilerleme takibi — plan dosyaları; ardından tag/branch/yedek işlemleri, dosya değişikliği yok)
- **Notlar / sorunlar:** U1 (Gmail uygulama şifresi iptali) hâlâ kullanıcı tarafından yapılmadı — acil, hatırlatıldı. `backend/legacy_backup/` F0.2'de `.gitignore`'a eklenecek.
- **Sonraki adım:** F0.2

### [2026-09-26] Hazırlık — Analiz ve plan — ✅

- **Yapılanlar:** v1 kodunun tamamı incelendi (backend ~1.600 satır Python; frontend ~4.000 satır HTML/JS/CSS). Ödev şartnamesi (PDF) okundu. Dış servisler canlı test edildi: TMDB ✓, Google Books ✗ (HTTP 429, anonim kota 0 — kitapların bozulma nedeni), Open Library ✓ (arama, konu, trend, eser detayı; konu anahtarları doğrulandı), NVIDIA NIM model listesi ✓ (82 model), via.placeholder.com ✗ (kapanmış). Geçici olarak ayağa kaldırılan v1 backend'de kitap uçlarının `null` döndüğü ve kullanıcı aramasının e-posta sızdırdığı doğrulandı. Veritabanı şeması incelendi. npm/PyPI güncel sürümleri ve Node gereksinimleri kontrol edildi. `proje-plani.md` ve bu dosya oluşturuldu.
- **Değişen dosyalar:** `proje-plani.md` (yeni), `proje-ilerleme-durumu.md` (yeni). Kod değişikliği yok.
- **Doğrulama:** —
- **Kapanan maddeler:** —
- **Commit:** — (plan dosyaları F0.1'in ilk maddesinde commit edilecek)
- **Notlar / sorunlar:** Public depoda sızmış sırlar var → **U1 acil**. Node sürümü Faz 2 için yetersiz (U3).
- **Sonraki adım:** F0.1 (kullanıcı "başla" dediğinde)
