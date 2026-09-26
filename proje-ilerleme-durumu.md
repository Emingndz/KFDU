# KFDU v2 — Proje İlerleme Durumu

> Plan: [`proje-plani.md`](proje-plani.md) · Bu dosya **her adımdan sonra** güncellenir (plan §0.2, madde 7).
> Son güncelleme: **2026-09-26** — F2.3 tamamlandı (API katmanı, oturum, router, uygulama iskeleti).

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
| Proje durumu | 🟨 Faz 2 uygulanıyor |
| Aktif faz | Faz 2 — Frontend Temeli |
| Sıradaki adım | **F2.4 — Kimlik sayfaları ve onboarding** |
| Çalışma dalı | `v2` |
| Son commit | `e104538` (feat(F2.3): API katmanı, oturum, router ve uygulama iskeleti) |
| Backend | v1 — kitap uçları bozuk (BUG-01) |
| Frontend | v1 — tek dosya Vue 3 CDN |
| Açık engeller | 👤 U1 (Gmail şifresi iptali) ve U2 (TMDB anahtarı yenileme) hâlâ acil bekliyor — kodu ilerletmeyi engellemiyor ama en kısa sürede yapılmalı |

### Bağlam özeti (yeni oturum açan uygulayıcı için)

- **Proje:** KFDU — film/kitap/dizi sosyal kütüphane platformu. v1: FastAPI + SQLAlchemy + SQLite backend, tek dosya Vue 3 (CDN) frontend; Kocaeli Üniversitesi Yazlab-I Proje II ödevi. v1 analiz bulguları planın §2'sinde (SEC-01…09, BUG-01…20, DEBT-01…07); ödev eksikleri Ek A'da. `legacy-v1` git etiketi ve `backend/legacy_backup/sql_app_v1.db` v1'in tam yedeğidir.
- **Faz 0 ✅ (güvenlik/temizlik/hazırlık):** Sırlar koddan temizlendi (`config.py`/`security.py`), `.gitignore` + `.env`/`.env.example`, `v2` dalı açıldı. F0.5 (git geçmişi temizliği) kullanıcı kararıyla atlandı (D-14); `v2`+`legacy-v1` push edildi (D-15).
- **⚠️ Hâlâ açık güvenlik riski:** Kod tarafı kapandı ama **eski Gmail uygulama şifresi ve eski TMDB anahtarı hâlâ geçerli** — U1 (Gmail şifresi iptali) ve U2 (TMDB anahtarı yenileme) kullanıcı tarafından yapılana kadar risk sürüyor. Her ikisi de hâlâ ⬜ (yapılmadı).
- **✅ Node.js 24.19.0'a güncellendi (2026-09-26, U3 tamamlandı):** Kullanıcı onayıyla `winget install OpenJS.NodeJS.LTS` çalıştırıldı (eski `OpenJS.NodeJS.22` paketiyle çakışmaması için önce kaldırılmaya çalışıldı, iki kurulum da kayıt defterinde/PATH'te tek "Node.js 24.19.0" olarak sonuçlandı — temiz). Faz 2'nin önkoşulu artık karşılanıyor.
- **Faz 1 ✅ TAMAMLANDI (F1.1–F1.11, 2026-09-26):** Yeni modüler backend sıfırdan kuruldu — `app/core/` (config/database/errors/security/deps/events/http/cache/rate_limit/pagination/logging/email) + 8 modül: `auth`, `users`, `catalog` (TMDB/Open Library/Google Books sağlayıcıları), `library`, `social`, `lists`, `stats`. Eski backend yalnız referans olarak `legacy/backend-v1/`'de duruyor, yeni kod ona bağımlı değil (F1.11'de doğrulandı). **69 test yeşil, kapsam %80** (hedef ≥%70). `ruff check`+`format` temiz. `scripts/seed.py` ile demo veri (6 kullanıcı, 40 kütüphane girişi, 12 inceleme, 3 liste) gerçek ortamda yüklendi ve doğrulandı. **Kitaplar artık çalışıyor** (BUG-01 kapandı, Open Library ile). Tüm OpenAPI uçları Türkçe özetli, doğru etiketli, `tag-fonksiyon` biçiminde operationId'li.
- **Bilinen sınırlamalar / takip maddeleri (Faz 1'den kalan):**
  - **D-16:** Ek C kanonik tür verisi `core/genres.py`'de (planın önerdiği gibi yalnız `catalog/genres.py`'de değil) — `users` modülünün `catalog`'a bağımlı olmadan `favorite_genres` doğrulaması yapabilmesi için gerekliydi.
  - **D-17 (önemli teknik düzeltme):** SQLite, `DateTime(timezone=True)` olsa bile okurken tzinfo düşürüyordu → `core/database.py`'de `UTCDateTime` TypeDecorator ile çözüldü (PostgreSQL'de no-op).
  - **D-18:** TMDB fixture'ları (3 dosya) gerçek API'den değil, bilinen şemaya göre elle yazıldı — U2 sonrası gerçek API'den yeniden yakalanması önerilir (düşük öncelik).
  - **D-19:** U6 — v1'in gerçek verisi (3 kullanıcı, 12 etkileşim, 7 liste) kullanıcı kararıyla yeni DB'ye aktarılmadı; yalnızca yedekte duruyor.
  - **TMDB canlı doğrulama eksik:** Film/dizi kodu yazıldı ve mock'lu testlerle doğrulandı ama gerçek TMDB çağrısı U2'yi bekliyor. U2 tamamlanınca `python -m scripts.seed --reset` tekrar çalıştırılırsa filmler otomatik eklenir.
  - Sosyal modülün inceleme-okuma uçları (`list_content_reviews`/`list_user_reviews`) feed kadar agresif N+1-optimize edilmedi (bilinçli sadelik tercihi, küçük ölçek için yeterli).
- **Faz 1 kapanışı (2026-09-26):** Kullanıcı `v2`'yi push etmeyi (yapıldı, `origin/v2` güncel) ve Faz 2'ye geçmeyi onayladı. F2.1'in önkoşulu (Node ≥22.18) kontrol edildiğinde eksik çıktı (U3 yapılmamıştı); kullanıcı Node güncellemesini bizzat onayladı ve gerçekleştirdi (yukarı bkz.).
- **F2.1 tamamlandı:** `frontend/` sıfırdan `npm create vue@latest` ile kuruldu (v1 `legacy/frontend-v1/`'e taşındı). Vue 3.5/Router 5/Pinia 4/Vitest 4/ESLint 10/Prettier — hepsi planın istediği sürümlerle eşleşiyor (create-vue'nün güncel şablonu). Tailwind 4 + `@tailwindcss/vite`, `openapi-typescript` (TS 6 peer uyuşmazlığı nedeniyle `--legacy-peer-deps` ile kuruldu — işlevsel sorun yok), TanStack Query, VueUse, lucide-vue-next, vue-sonner, fontsource Inter kuruldu. `vite.config.ts`'de `/api`+`/media` backend'e (8000) proxy'leniyor. `npm run dev/lint/type-check/build/test:unit` hepsi yeşil. **Not:** Bu oturumda tarayıcı aracı (claude-in-chrome / built-in browser) mevcut değildi — `npm run dev`'in gerçekten açıldığı yalnızca HTTP yanıtı ve loglarıyla doğrulandı, görsel/konsol kontrolü yapılamadı (F2.1'de gerçek bir UI yok — create-vue'nün varsayılan "You did it!" sayfası duruyor, F2.3'te değişecek).
- **F2.2 tamamlandı:** `src/styles/main.css` (§3.7 — Tailwind v4 `@theme` token'ları, açık/koyu CSS değişkenleri), `useTheme` (`useColorMode` sarmalayıcı, Sistem/Açık/Koyu), `useConfirm` (modül-seviyeli tekil durum + Promise tabanlı onay), 13 temel bileşen (`components/ui/`), `App.vue`'ya `Toaster`+`ConfirmDialog` eklendi, `/_ui` vitrin sayfası (yalnız DEV). 9 yeni test (BaseAvatar + useConfirm). **Not:** `Spinner` bileşeni ESLint'in "çok kelimeli bileşen adı" kuralına takıldığı için `BaseSpinner` olarak adlandırıldı (plan metninde "Spinner" geçiyordu). Bu oturumda tarayıcı aracı yok — `/_ui`'nin açık/koyu tema ve klavye gezinme kabul kriteri yalnızca kod/HTTP seviyesinde doğrulandı, gerçek görsel/klavye testi yapılamadı.
- **F2.3 tamamlandı:** `openapi-typescript` betiğindeki hatalı URL (`/api/v1/openapi.json`, 404 veriyordu) `/openapi.json` olarak düzeltildi (FastAPI'nin varsayılan OpenAPI yolu, router prefix'inden bağımsız — kök seviyede) ve `src/api/schema.d.ts` (3958 satır) yeniden üretildi; `src/types/index.ts` bu şemadan tip takma adları (`MeOut`, `TokenOut`, `RegisterIn`… + elle yazılan genel `Page<T>`/`CursorPage<T>`, `backend/app/core/pagination.py`'deki gerçek şemayla birebir doğrulandı) türetiyor. `src/api/client.ts`: `ApiError` sınıfı + `api<T>()` fonksiyonu (§3.6.3 iskeletinden) — sorgu parametrelerini otomatik URL-encode eder ve boş/undefined değerleri atlar (BUG-11 kapandı), Pinia `useAuthStore`'dan token okuyup `Authorization: Bearer` ekler, 401'de `handleUnauthorized()` çağırır (çıkış yapar + `/giris?redirect=...`'e yönlendirir + tek toast — art arda gelen 401'ler 1 sn'lik pencerede tekilleştirilir, BUG-06 frontend tarafı kapandı). `client.ts`↔`stores/auth.ts`↔`api/auth.ts`/`api/users.ts` arasında döngüsel import var ama tüm döngüsel referanslar yalnızca fonksiyon gövdelerinde (çalışma zamanında) kullanılıyor, modül değerlendirme anında değil — bu yüzden güvenli (ES modül canlı bağlama kuralı); `npm run build` bunu doğruladı (uyarısız). `src/api/auth.ts` + `src/api/users.ts`: ham istek fonksiyonları (§5.1/§5.2 tam kapsamı) + yakın vadede ihtiyaç duyulan composable'lar (`useLogin`, `useRegister`, `useChangePassword` vb.; `useMe`, `useUpdateMe`, `useSuggestions`) — henüz tüketicisi olmayan `getProfile`/`followUser`/`searchUsers` gibi uçlar için yalnız ham fonksiyon var, composable'ları Faz 3 ilgili sayfalarında eklenecek (erken soyutlama yok). `stores/auth.ts` (`token`→`localStorage['kfdu_token']`, `me`, `isAuthenticated`, `login/register/logout/fetchMe`) + `stores/ui.ts` (mobil menü). `main.ts`: `VueQueryPlugin` eklendi (`staleTime:60000`, `refetchOnWindowFocus:false`, yalnız 5xx'te 1 kez retry). `router/index.ts`: §3.6.7'nin tam rota tablosu (henüz yapılmamış tüm sayfalar `ComingSoonPage` ile), `RouteMeta` genişletmesi (`requiresAuth`/`guestOnly`/`title`), global guard (token var+`me` yok→`fetchMe()`, başarısızsa çıkış; `/`+misafir→`/kesfet` — bu özel kural `requiresAuth`'tan ÖNCE kontrol edilir, aksi halde misafir `/`'de girişe değil `/kesfet`'e yönlenme kuralı hiç tetiklenmezdi; korumalı rota+girişsiz→`/giris?redirect=`; `guestOnly`+girişli→`/`), `scrollBehavior`, `afterEach`→`document.title`. Düzen: `AppShell`+`AppHeader` (logo, Akış/Keşfet, arama kısayolu→şimdilik `/kesfet`'e yönlendiren buton — tam arama F3.2'de, kullanıcı menüsü: Profilim/Ayarlar/Tema/Çıkış, misafirde Giriş/Kayıt) + `AppBottomNav` (<768px, yalnız şu an işlevsel olan Akış/Keşfet/Profil — Öneriler/Bildirimler ilgili fazda eklenecek, henüz yapılmamış sayfalara link vermemek için bilinçli tercih) + `RouteProgress` (basit opacity tabanlı yükleniyor çubuğu). `App.vue` artık `<AppShell/>` render ediyor, create-vue'nün "You did it!" yer tutucusu kaldırıldı; `App.spec.ts` buna göre güncellendi (gerçek Pinia+router ile mount edilen duman testi).
- **Sırada:** F2.4 — Kimlik sayfaları ve onboarding (§3.6.4'teki form kuralları + Login/Register/ForgotPassword/Onboarding sayfaları).

---

## 📊 Faz Özeti

| Faz | Başlık | Durum | İlerleme | Başlangıç | Bitiş |
|---|---|---|---|---|---|
| 0 | Güvenlik, temizlik, hazırlık | ✅ Tamamlandı (F0.4 sonradan kapandı) | 5/5 | 2026-09-26 | 2026-09-26 |
| 1 | Backend temeli | ✅ Tamamlandı | 11/11 | 2026-09-26 | 2026-09-26 |
| 2 | Frontend temeli | 🟨 Devam ediyor | 3/5 | 2026-09-26 | – |
| 3 | Çekirdek özellikler (ilk kullanılabilir v2) | ⬜ Başlamadı | 0/10 | – | – |
| 4 | Çağ atlatma paketi | ⬜ Başlamadı | 0/9 | – | – |
| 5 | Akıllı öneriler | ⬜ Başlamadı | 0/6 | – | – |
| 6 | KFDU Asistan (NVIDIA LLM) | ⬜ Başlamadı | 0/9 | – | – |
| 7 | Kalite, test, CI, yayın | ⬜ Başlamadı | 0/9 | – | – |
| **Toplam** | | | **19/64** | | |

Durum simgeleri: ⬜ Başlamadı · 🟨 Devam ediyor · ✅ Tamamlandı · ⛔ Engellendi · ⏭️ Atlandı (kullanıcı onayıyla)

---

## 👤 Kullanıcı Eylemleri ve Kararları

| # | Eylem / karar | Ne zaman | Durum |
|---|---|---|---|
| U1 | **ACİL — Gmail uygulama şifresini iptal et:** https://myaccount.google.com/apppasswords (şifre public depoda açıkta) | Hemen | ⬜ |
| U2 | TMDB API anahtarını yenile (https://www.themoviedb.org/settings/api) ve yenisini `backend/.env`'ye yaz | F0.3 | ⬜ |
| U3 | Node.js'i 24 LTS'e güncelle (en az 22.18): https://nodejs.org veya `winget install OpenJS.NodeJS.LTS` | F0.4 (Faz 2'den önce) | ✅ Yapıldı (2026-09-26) — Node 24.19.0 |
| U4 | `backend/.env` değerlerini doldur (TMDB; isteğe bağlı yeni SMTP uygulama şifresi; `CONTACT_EMAIL`) | F0.3 | ⬜ |
| U5 | Karar: Git geçmişi temizlensin mi? (F0.5 — force push gerektirir) | Faz 0 | ✅ Hayır — atlandı (2026-09-26) |
| U6 | Karar: v1 verileri (3 kullanıcı, 12 etkileşim, 7 liste) yeni veritabanına taşınsın mı? (F1.10) | Faz 1 | ✅ Hayır — atlandı (2026-09-26) |
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
- [x] F0.4 — Geliştirme ortamı (👤 U3) — ✅ (2026-09-26, Node 24.19.0 kurulumuyla tamamlandı)
- [⏭️] F0.5 — (Opsiyonel, 🛑 U5) Git geçmişinden sırları temizleme — kullanıcı onayıyla atlandı (2026-09-26); ileride istenirse ayrıca yapılabilir
- [x] 🏁 Faz 0 kapanışı — ✅ (2026-09-26): `v2` dalı ve `legacy-v1` etiketi origin'e push edildi

### Faz 1 — Backend Temeli

- [x] F1.1 — Bağımlılıklar ve proje iskeleti — ✅ (2026-09-26)
- [x] F1.2 — Çekirdek altyapı — ✅ (2026-09-26)
- [x] F1.3 — Veri modeli ve Alembic — ✅ (2026-09-26)
- [x] F1.4 — Kimlik doğrulama modülü — ✅ (2026-09-26)
- [x] F1.5 — Kullanıcılar ve takip — ✅ (2026-09-26)
- [x] F1.6 — Katalog: TMDB + Open Library (+ Google Books) — **kitaplar düzelir** — ✅ (2026-09-26)
- [x] F1.7 — Kütüphane: durum, puan, favori, inceleme yazma — ✅ (2026-09-26)
- [x] F1.8 — Sosyal: aktiviteler, akış, beğeni, yorum, bildirim — ✅ (2026-09-26)
- [x] F1.9 — Özel listeler — ✅ (2026-09-26)
- [x] F1.10 — Profil özeti, platform vitrinleri ve demo verisi — ✅ (2026-09-26); U6 (eski veri aktarımı): kullanıcı "hayır, atla" dedi (D-19)
- [x] F1.11 — Faz 1 kapanışı 🏁 — ✅ (2026-09-26)

### Faz 2 — Frontend Temeli

- [x] F2.1 — Vite + Vue 3 + TypeScript iskeleti — ✅ (2026-09-26)
- [x] F2.2 — Tasarım sistemi ve temel UI bileşenleri — ✅ (2026-09-26)
- [x] F2.3 — API katmanı, oturum, router ve uygulama iskeleti — ✅ (2026-09-26)
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
| SEC-05 | Güvensiz şifre sıfırlama (süresiz, e-postaya bağsız, deneme sınırsız) | F1.4 | ✅ | `cf0ff06` |
| SEC-06 | Kullanıcı e-postaları API'de açık; kimliksiz kullanıcı araması | F1.5 | ✅ | `90c6ed0` |
| SEC-07 | Giriş/sıfırlamada hız sınırı yok | F1.4 | ✅ | `cf0ff06` |
| SEC-08 | Girdi doğrulama yok (puan aralığı, metin uzunluğu, parola kuralı) | F1.4, F1.7 | ✅ | `919615a` |
| SEC-09 | CORS `*` + credentials | F1.2 | ✅ | `845b3e8` |
| BUG-01 | Kitaplar çalışmıyor (Google Books 429 → `null`) | F1.6 | ✅ | `8c12de7` |
| BUG-02 | Film detayında yönetmen/oyuncu/süre/tür yok | F1.6, F3.3 | 🟡 backend ✅; frontend gösterimi F3.3 | `8c12de7` |
| BUG-03 | Aynı kullanıcı adıyla kayıt → 500; yanlış/İngilizce hata | F1.4 | ✅ | `cf0ff06` |
| BUG-04 | İki kez takip / takip etmeyeni bırakma → 500 | F1.5 | ✅ | `90c6ed0` |
| BUG-05 | E-posta değişince oturum kırılıyor (JWT sub = e-posta) | F1.2 | ✅ (F1.4'te doğrulandı — `sub`=id) | `cf0ff06` |
| BUG-06 | 30 dk token, 401 yönetimi yok; 401 yerine 403 | F1.2, F2.3 | ✅ (backend F1.4: 7 gün token, 401+WWW-Authenticate; frontend F2.3: `client.ts` 401'de çıkış+yönlendirme+tekil toast) | `cf0ff06` |
| BUG-07 | Kırık yer tutucu görseller (via.placeholder.com) | F2.2, F3.9 | 🟡 bileşen düzeyi ✅ (BaseAvatar kırık/yok görselde deterministik baş harf); tüm sayfalarda kullanım F3.9 | `f3e2894` |
| BUG-08 | Detay açmak arama tipini değiştirip gereksiz çağrı yapıyor | Faz 2–3 (F3.2) | 🔴 | |
| BUG-09 | Başkasının profilinde film durumları kitap etiketiyle | F3.6 | 🔴 | |
| BUG-10 | Şifre sıfırlamada "(Demo: undefined)" | F2.4 | 🔴 | |
| BUG-11 | Arama sorguları URL-encode edilmiyor | F2.3 | ✅ (`client.ts`'teki `api()` tüm sorgu parametrelerini `URLSearchParams` ile otomatik kodluyor) | `e104538` |
| BUG-12 | Akışta göreli tarih/aksiyon metni/alıntı yok | F1.8, F3.5 | 🟡 backend ✅ (`created_at`+`excerpt`+`card_type` API'de var); arayüz F3.5 | `9286a24` |
| BUG-13 | Akışta sayfalama yok, N+1 sorgular | F1.8, F3.5 | ✅ backend (imleçli sayfalama + N+1 giderildi, testle doğrulandı) | `9286a24` |
| BUG-14 | Arama "daha fazla" çalışmıyor; kitap sayfa ofseti hatalı | F1.6, F3.2 | 🟡 backend ✅ (doğru sayfalama); arayüz F3.2 | `8c12de7` |
| BUG-15 | Kitap yıl filtresi sessizce filtresiz sonuç dönüyor | F1.6 | ✅ | `8c12de7` |
| BUG-16 | `requirements.txt` eksik (temiz kurulum çöker) | F1.1 | ✅ | `61c08c2` |
| BUG-17 | Migrasyon yok; artık tablolar; eşsizlik kısıtı yok | F1.3 | ✅ | `0f29f74` |
| BUG-18 | Dış API çağrılarında timeout yok | F1.2, F1.6 | ✅ (F1.2 altyapı + F1.6 tüm sağlayıcılar `request_json` kullanıyor) | `8c12de7` |
| BUG-19 | Yetki hataları 400; yorum–aktivite aidiyeti kontrol edilmiyor | F1.8, F1.9 | ✅ | `51373cc` |
| BUG-20 | Durum değerleri film/kitap için tutarsız | F1.7, F3.1 | 🟡 backend ✅ (`LibraryStatus` tek ortak enum); arayüz etiketleri F3.1 | `919615a` |
| DEBT-01 | Tek dosya frontend, bileşen ve router yok | Faz 2–3 | ✅ (v2: bileşenler F2.2, gerçek rota tablosu+guard F2.3; v1 dosyası `legacy/frontend-v1/`'de yalnız referans) | `e104538` |
| DEBT-02 | 32 `alert/confirm`, 10 `console.log` | Faz 2–3 | 🟡 altyapı ✅ (vue-sonner toast + ConfirmDialog hazır); eski `alert/confirm` kaldırma Faz 3 sayfalarında | `f3e2894` |
| DEBT-03 | Eskimiş API'ler ve bakımsız kütüphaneler | F1.2, F1.3 | ✅ (F1.2: PyJWT+pwdlib+pydantic v2; F1.3: SQLAlchemy 2 tipli `Mapped[]` modeller) | `0f29f74` |
| DEBT-04 | Kopya kod (film/kitap uçları, içerik oluşturma) | F1.6, F1.7 | ✅ (tek `get_or_create_content` + tek `upsert_entry`, film/kitap ayrımı yok) | `919615a` |
| DEBT-05 | Ham dış API JSON'u frontend'e gidiyor | F1.6 | ✅ | `8c12de7` |
| DEBT-06 | `print` loglama; test/lint/README/`.env.example` yok | F1.2, Faz 7 | 🟡 kısmi (loglama + test/lint altyapısı hazır; README Faz 7'de) | `845b3e8` |
| DEBT-07 | Açılışta `create_all` (migrasyon yok) | F1.3 | ✅ | `0f29f74` |

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
| REQ-2.2.1a | Film verisi TMDb (başlık, özet, yıl, yönetmen, oyuncular, türler, kapak) | F1.6 | ✅ | `8c12de7` (respx testleri + fixture) |
| REQ-2.2.1b | Kitap verisi Open Library / Google Books (başlık, yazar, açıklama, sayfa, kapak) | F1.6 | ✅ | `8c12de7` (gerçek sunucuda canlı doğrulandı) |
| REQ-2.2.1c | Manuel veri girişi yok | F1.6 | ✅ | `8c12de7` (tüm içerik `catalog` modülünden upsert edilir) |
| REQ-3 | Tutarlı ve verimli veritabanı | F1.3 | ⬜ | |

---

## 🧾 Kararlar

| Tarih | ID | Karar | Durum |
|---|---|---|---|
| 2026-09-26 | D-01 … D-13 | Plan §12.1'deki mimari, teknoloji, veri modeli, AI ve git kararları | ✅ Kullanıcı "devam et" ile onayladı |
| 2026-09-26 | D-14 | F0.5 (git geçmişi temizliği) atlansın — U1/U2 asıl çözüm, F0.5 yalnız kozmetik | ✅ Kullanıcı kararı |
| 2026-09-26 | D-15 | `v2` dalı ve `legacy-v1` etiketi origin'e (public GitHub) push edilsin | ✅ Kullanıcı onayı, uygulandı |
| 2026-09-26 | D-16 | Ek C kanonik tür verisi plandaki gibi yalnız `catalog/genres.py`'de değil, `core/genres.py`'de tutulacak (ham tablo + `GENRE_KEYS`); `catalog/genres.py` (F1.6) bunun üzerine TMDB/OL yardımcılarını ekleyecek | ✅ Uygulayıcı kararı — §3.5.2 bağımlılık kuralı (`users` yalnız `core`'u içe aktarabilir, `catalog`'u içe aktaramaz) `favorite_genres` doğrulamasını `catalog`'a bağımlı kılmadan mümkün kılmak için gerekliydi. Veri tekrarı yok, tek kaynak `core/genres.py`. |
| 2026-09-26 | D-17 | `core/database.py`'ye `UTCDateTime` TypeDecorator eklendi | ✅ Uygulayıcı kararı — canlı testte bulunan gerçek hata: SQLite, `DateTime(timezone=True)` olsa bile okurken tzinfo'yu düşürüyor; `datetime.now(UTC) - row.fetched_at` gibi Python-seviyesi çıkarma işlemleri `TypeError` fırlatıyordu. Bu, F1.7/F1.8'de de (rated_at, 60 dk aktivite penceresi vb.) tekrar edecek bir hataydı; kökten düzeltildi. PostgreSQL'de no-op (zaten tz-aware döner). Alembic'te yeni migration gerekmedi (`alembic check` temiz). |
| 2026-09-26 | D-18 | TMDB fixture'ları (`tmdb_movie_detail_27205.json`, `tmdb_search_movie.json`, `tmdb_tv_detail_1396.json`) gerçek API'den yakalanmadı, TMDB'nin bilinen genel şemasına göre elle yazıldı | ⚠️ Geçici — U2 (TMDB anahtarı yenileme) tamamlanınca gerçek API'den yeniden yakalanması önerilir (düşük öncelik; testler zaten yeşil, yalnızca fixture'ların gerçekliği artar) |
| 2026-09-26 | D-19 | F1.10 / U6: v1'deki eski veriler (3 kullanıcı, 12 etkileşim, 7 liste) yeni veritabanına aktarılmasın | ✅ Kullanıcı kararı — "Hayır, atla" seçildi; `scripts/migrate_legacy_db.py` yazılmadı. Eski veri `legacy-v1` etiketi + `backend/legacy_backup/sql_app_v1.db` içinde güvende, istenirse ileride ayrıca aktarılabilir. |

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
| Backend test kapsamı (genel) | ≥ %75 (F1.11 ara hedefi ≥ %70) | **%80** | 2026-09-26 (F1.11) |
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
| Node.js | 24.19.0 | ✅ güncellendi (2026-09-26, U3 tamamlandı) |
| npm | 11.20.0 | |
| Git | 2.47.1.windows.1 | ✓ |
| Git uzak depo | GitHub (public) | |
| Backend venv | `backend/.venv` | ✓ oluşturuldu (F0.4) |

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

### [2026-09-26] F2.3 — API katmanı, oturum, router ve uygulama iskeleti — ✅

- **Yapılanlar:**
  - **Düzeltme:** `package.json`'daki `gen:api` betiği planın literal URL'iyle (`http://127.0.0.1:8000/api/v1/openapi.json`) 404 veriyordu; FastAPI'nin OpenAPI şeması her zaman kök seviyede yayınlanır (router prefix'inden etkilenmez) — `http://127.0.0.1:8000/openapi.json` olarak düzeltildi. `npm run gen:api` çalıştırıldı → `src/api/schema.d.ts` (3958 satır) üretildi.
  - `src/types/index.ts`: şemadan tip takma adları (`MeOut`, `ProfileOut`, `PublicUserOut`, `RegisterIn`, `LoginIn`, `TokenOut`, `ResetRequestIn/VerifyIn/ConfirmIn`, `ChangePasswordIn`, `MeUpdateIn`, `EmailChangeIn`, `DeleteAccountIn`…) + elle yazılan genel `Page<T>`/`CursorPage<T>` (backend `core/pagination.py`'deki `Page[T]`/`CursorPage[T]` Pydantic modelleriyle alan alan doğrulandı — `items/page/page_size/total/has_next` ve `items/next_cursor`).
  - `src/api/client.ts`: `ApiError` sınıfı (`status/code/message/errors[]`) + `api<T>(path, {method,body,query,signal})` — sorgu parametrelerini `URLSearchParams` ile otomatik kodlar, boş string/`undefined` değerleri atlar (**BUG-11 kapandı**); `FormData` gövdesini olduğu gibi, diğer gövdeleri JSON olarak gönderir; `useAuthStore().token` varsa `Authorization: Bearer` ekler; 204'te `undefined` döner; başarısız yanıtı `ApiError`'a çevirir; 401'de `handleUnauthorized()` — çıkış yapar, `router.currentRoute`'un `fullPath`'ini `redirect` sorgu parametresiyle `/giris`'e yönlendirir, "Oturumun sona erdi" toast'unu 1 sn'lik pencerede tekilleştirir (art arda gelen 401'ler tek toast — **BUG-06 frontend tarafı kapandı**).
  - **Döngüsel import notu:** `client.ts` → `stores/auth.ts` → `api/auth.ts`/`api/users.ts` → `client.ts` gerçek bir döngü oluşturuyor; tüm taraflar döngüsel bağlamı yalnızca fonksiyon gövdelerinde (çağrı anında) kullanıyor, hiçbiri modül değerlendirme anında (top-level) kullanmıyor — ES modüllerinin "canlı bağlama" kuralı sayesinde güvenli. Başlangıçta dinamik `import()` ile bu döngüden kaçınmayı denedim; `npm run build` "ineffective dynamic import" uyarısı verdi (bu modüller zaten başka yollardan statik olarak ana pakete giriyor, dinamik import hiçbir kod bölme kazancı sağlamıyordu) — statik import'a geri dönüldü, uyarı kayboldu, derleme temiz.
  - `src/api/auth.ts` + `src/api/users.ts`: §5.1/§5.2'nin tam uç kapsamı için ham istek fonksiyonları; composable'lar (`useLogin/useRegister/useRequestPasswordReset/useVerifyPasswordReset/useConfirmPasswordReset/useChangePassword/useLogoutAllDevices`, `useMe/useUpdateMe/useSuggestions`) yalnız yakın vadede (F2.3 kendisi + F2.4 onboarding) tüketicisi olanlar için yazıldı; `getProfile/followUser/unfollowUser/searchUsers` gibi Faz 3'e kadar tüketicisi olmayanlar ham fonksiyon olarak bırakıldı (erken/spekülatif soyutlama yok — mimari tercihe uygun).
  - `stores/auth.ts` (Pinia setup-store): `token` (`localStorage['kfdu_token']` ile senkron), `me`, `isAuthenticated` (token varlığına göre), `login/register/logout/fetchMe/setMe`. `stores/ui.ts`: `mobileMenuOpen` + toggle/close.
  - `main.ts`: `VueQueryPlugin` eklendi — `staleTime:60_000`, `refetchOnWindowFocus:false`, `retry`: yalnız `ApiError.status>=500`'de ve yalnız 1 kez.
  - `router/index.ts`: §3.6.7'nin tam rota tablosu (`/giris,/kayit,/sifremi-unuttum,/hosgeldin,/,/kesfet,/film/:id,/kitap/:id,/dizi/:id,/inceleme/:id,/u/:username,/liste/:id,/ayarlar,/bildirimler,/kisi/:id,/yazar/:id,/ozet/:year?,/oneriler,/asistan/:conversationId?,/_ui(DEV),/:pathMatch(.*)*`) — henüz sayfası yapılmamış her rota geçici `ComingSoonPage` kullanıyor (F2.4/F3.x/F4.x/F5.x/F6.x'te gerçek sayfalarla değişecek). `RouteMeta` TS modül genişletmesiyle `requiresAuth?/guestOnly?/title?` eklendi. Global `beforeEach` guard: token var+`me` yok→önce `fetchMe()` dener (başarısızsa çıkış+`/giris`'e yönlendir); **`/`+girişsiz→`/kesfet`** kuralı `requiresAuth` kontrolünden ÖNCE ayrı bir özel durum olarak ele alındı (aksi halde `/`'nin `requiresAuth` bayrağıyla çakışıp misafiri her zaman `/giris`'e yönlendirirdi, spesifikasyon `/kesfet` istiyor — bu yüzden `/` rotasının meta'sında `requiresAuth` YOK, yalnızca bu özel kural devrede); `requiresAuth`+girişsiz→`/giris?redirect=<hedef>` (geri dönüş, LoginPage F2.4'te bu parametreyi okuyup kullanacak); `guestOnly`+girişli→`/`. `scrollBehavior` (kayıtlı konum > hash > en üst). `afterEach`→`document.title = "{başlık} · KFDU"`. Basit bir `routeLoading` ref'i (`composables/useRouteProgress.ts`) ile `RouteProgress` bileşeni rotalar arası geçici bir yükleniyor çubuğu gösteriyor.
  - Düzen bileşenleri (`components/layout/`): `AppShell` (üst menü + `<RouterView>` + altbilgi: TMDB/Open Library atıfları + mobil alt menü), `AppHeader` (logo, Akış/Keşfet linkleri, arama ikonu→şimdilik `/kesfet`'e yönlendiriyor — tam arama kutusu/kısayolu F3.2'nin DiscoverPage'iyle birlikte gelecek, dışa tıklayınca kapanan kullanıcı menüsü: Profilim/Ayarlar/Tema seçimi/Çıkış, misafirde Giriş/Kayıt butonları), `AppBottomNav` (<768px, yalnız şu an gerçekten işlevsel olan Akış/Keşfet/kendi Profili — Öneriler ve Bildirimler ilgili fazda (F5.5/F4.2) eklenecek; henüz yapılmamış sayfalara mobil linkler vermemek bilinçli bir tercih), `RouteProgress` (opacity geçişli ince üst çubuk).
  - `App.vue` artık `<AppShell/>` render ediyor; create-vue'nün varsayılan "You did it!" yer tutucusu kaldırıldı. `App.spec.ts` buna göre yeniden yazıldı: gerçek `Pinia`+bellek içi test `router`'ıyla mount edilip `<header>` varlığı ve "KFDU" metni doğrulanıyor (önceki "You did it!" metnini arayan test artık anlamsızdı).
  - `src/api/client.spec.ts` (yeni, 6 test): sorgu kodlama (boş/undefined atlanıyor), token varsa `Authorization` başlığı, `detail/code/errors` alanlarıyla `ApiError`'a çevirme, gövdesiz hatada genel mesaj, 204→`undefined`, 401'de tek çıkış+tek toast+doğru yönlendirme (mock `fetch`+mock `@/stores/auth`+mock `@/router`+mock `vue-sonner`, `vi.hoisted` ile mock referans sırası sorunu çözüldü).
- **Değişen dosyalar:** `frontend/package.json` (`gen:api` URL düzeltmesi), `frontend/src/api/{schema.d.ts,client.ts,client.spec.ts,auth.ts,users.ts}` (yeni), `frontend/src/types/index.ts` (yeni), `frontend/src/stores/{auth,ui}.ts` (yeni), `frontend/src/router/index.ts`, `frontend/src/composables/useRouteProgress.ts` (yeni), `frontend/src/components/layout/{AppShell,AppHeader,AppBottomNav,RouteProgress}.vue` (yeni), `frontend/src/pages/ComingSoonPage.vue` (yeni), `frontend/src/App.vue`, `frontend/src/main.ts`, `frontend/src/__tests__/App.spec.ts`.
- **Doğrulama:** `npm run lint` (oxlint+eslint) → temiz ✓ · `npm run type-check` (`vue-tsc --build`) → temiz ✓ · `npm run test:unit -- run` → **16 passed** (6 yeni client.ts testi + güncellenmiş App.spec.ts) ✓ · `npm run build` → başarılı, döngüsel import uyarısı yok (JS 180.60 KB, gzip 64.98 KB) ✓ · gerçek backend (`GET /api/v1/health` → 200) + gerçek Vite dev sunucusu ayakta iken: `curl http://localhost:5173/` → 200, doğru `<title>KFDU</title>` ve mount noktası ✓; `main.ts`/`App.vue`/`router/index.ts`/`client.ts`/`stores/auth.ts`/`AppShell.vue` modülleri Vite üzerinden tek tek istendi, hepsi 200 (sunucu tarafı dönüşüm hatası yok) ✓. **Not:** Bu oturumda tarayıcı aracı yok — guard yönlendirmelerinin (`/`→`/kesfet`, korumalı rota→`/giris?redirect=`) ve `AppHeader` kullanıcı menüsünün gerçek tarayıcıda görsel/etkileşimli doğrulaması yapılamadı; yalnızca kod incelemesi + HTTP/modül seviyesi + birim testleriyle doğrulandı. Dev sunucusu doğrulama sonrası durduruldu (port 5173 boş, artık process yok).
- **Kapanan maddeler:** BUG-06 (tam), BUG-11, DEBT-01
- **Commit:** `e104538`
- **Notlar / sorunlar:** `router/beforeEach` guard'ının kendisi için (guard mantığının izole testi) otomatik test yazılmadı — plan bu adım için yalnızca `client.ts` testlerini açıkça istiyordu (§9/F2.3 madde 8), guard'ın "korumalı rotada girişe yönlenir" davranışı F2.4'te gerçek LoginPage ile uçtan uca (redirect parametresini okuyup kullanma dahil) doğrulanacak.
- **Sonraki adım:** F2.4 — Kimlik sayfaları ve onboarding

### [2026-09-26] F2.2 — Tasarım sistemi ve temel UI bileşenleri — ✅

- **Yapılanlar:** `src/styles/main.css` §3.7'den birebir (marka/tür/durum renk token'ları, `--radius-card`, açık/koyu `:root`/`.dark` değişkenleri, `@theme inline` köprüsü) + `body` için taban bg/fg (token'ların gerçekten uygulanması için gerekliydi, planın CSS özetinde yoktu ama işlevsel olarak zorunlu). `main.ts`: `@fontsource-variable/inter`, `vue-sonner/style.css`, `main.css` içe aktarıldı. `composables/useTheme.ts` (`useColorMode`, Sistem/Açık/Koyu). `composables/useConfirm.ts` (modül-seviyeli paylaşılan `state` + `resolver`, `confirm()` bir `Promise<boolean>` döndürür). 13 bileşen: `BaseButton` (variant×5/size×3/loading/ikon slot/`to` ile RouterLink), `BaseInput` (etiket/ipucu/hata/karakter sayacı/şifre göster-gizle, `useId()`), `BaseTextarea`, `BaseSelect`, `BaseModal` (Teleport, Esc, Tab focus tuzağı, kapanınca odak eski yerine döner, `role=dialog`+`aria-modal`), `BaseTabs` (`role=tablist/tab`, ←/→ ile gezinme), `BaseAvatar` (isimden hash ile deterministik gradyan + baş harfler, `@error` ile kırık görsel fallback'i — via.placeholder yok), `BaseBadge`, `BaseSkeleton`, `EmptyState`, `ErrorState`, `BaseSpinner`, `ConfirmDialog`. `App.vue`'ya `<Toaster rich-colors position="top-center">` + `<ConfirmDialog>` eklendi (ana içerik "You did it!" hâlâ duruyor — F2.3'te AppShell ile değişecek). `pages/UiShowcasePage.vue` tüm bileşenleri iki temada gösteriyor; `router/index.ts`'e yalnızca `import.meta.env.DEV` iken eklenen `/_ui` rotası.
- **Değişen dosyalar:** `frontend/src/styles/main.css`, `composables/{useTheme,useConfirm}.ts`, `components/ui/*.vue` (13 dosya), `App.vue`, `main.ts`, `router/index.ts`, `pages/UiShowcasePage.vue`, `__tests__/{BaseAvatar,useConfirm}.spec.ts` (yeni).
- **Doğrulama:** `npm run type-check` → temiz ✓ · `npm run lint` → temiz (bir tur "Spinner çok kelimeli değil" hatası bulundu, `BaseSpinner`'a yeniden adlandırılıp düzeltildi) ✓ · `npm run test:unit` → 10 passed (9 yeni) ✓ · `npm run build` → başarılı (CSS 33 KB, JS 126 KB gzip 47 KB) ✓ · dev sunucusunda `/_ui` → HTTP 200 ✓ (tarayıcı aracı yok, görsel/klavye kontrolü yapılamadı).
- **Kapanan maddeler:** BUG-07 (bileşen düzeyi), DEBT-02 (altyapı)
- **Commit:** `f3e2894`
- **Notlar / sorunlar:** Tarayıcı aracı (claude-in-chrome / built-in browser) bu oturumda mevcut değil — `/_ui`'nin "açık ve koyu temada düzgün, klavyeyle gezilebilir" kabul kriteri yalnızca statik/HTTP seviyesinde doğrulanabildi. Kullanıcı isterse kendisi `/_ui`'yi tarayıcıda açıp gözden geçirebilir.
- **Sonraki adım:** F2.3

### [2026-09-26] F2.1 — Vite + Vue 3 + TypeScript iskeleti — ✅

- **Yapılanlar:** `git mv frontend legacy/frontend-v1` (v1'in tek dosyalık Vue 3 CDN arayüzü referans olarak korundu). Kökte `npm create vue@latest frontend -- --ts --router --pinia --vitest --eslint --prettier --bare` (bayraklar sorunsuz çalıştı). `npm install`; ek olarak `@tanstack/vue-query @vueuse/core lucide-vue-next vue-sonner @fontsource-variable/inter` ve dev bağımlılığı olarak `tailwindcss @tailwindcss/vite openapi-typescript` (`--legacy-peer-deps` ile — `openapi-typescript@7.13`'ün `typescript@^5` peer aralığı henüz TS 6'yı içermiyor, gerçek bir işlev sorunu yok, CLI çalışıyor). `vite.config.ts`: `tailwindcss()` eklentisi, `server.port=5173`, `/api`+`/media` proxy → `127.0.0.1:8000`. `package.json`'a `gen:api` betiği eklendi. `frontend/.env.example` (`VITE_API_URL=/api/v1`). `index.html`: `lang="tr"`, başlık "KFDU", `favicon.svg` (yeni basit SVG ikon, eski `favicon.ico` silindi), `theme-color`. create-vue'nün varsayılan `.prettierrc.json`'ı zaten plana uyuyordu (semi:false, singleQuote, printWidth:100) — değiştirilmedi. Kullanılmayan demo dosyası `stores/counter.ts` kaldırıldı (App.vue onu kullanmıyordu). Mevcut `src/__tests__/App.spec.ts` zaten "test bulunamadı" hatasını önlüyor, ayrı bir `smoke.spec.ts` eklenmedi (yinelenen olurdu).
- **Değişen dosyalar:** `frontend/**` (yeni iskelet, 24 dosya), `legacy/frontend-v1/**` (taşındı).
- **Doğrulama:** `npm run type-check` → temiz ✓ · `npm run lint` (oxlint+eslint) → temiz ✓ · `npm run test:unit -- --run` → 1 passed ✓ · `npm run build` → başarılı (87 KB JS, gzip 34 KB) ✓ · `npm run dev` → `http://localhost:5173` 858ms'de hazır, `curl` ile HTTP 200 ve `lang="tr"` doğrulandı ✓ (tarayıcı aracı bu oturumda yok, görsel kontrol yapılamadı — yukarı bağlam özetine not düşüldü).
- **Kapanan maddeler:** —
- **Commit:** `123467f`
- **Notlar / sorunlar:** Tarayıcı aracı mevcut değildi (bkz. bağlam özeti). `lucide-vue-next` upstream'de `@lucide/vue` lehine "deprecated" işaretli ama plan açıkça `lucide-vue-next` istiyor ve sürüm (1.x) eşleşiyor — büyük bir uyumsuzluk olmadığı için değiştirilmedi.
- **Sonraki adım:** F2.2

### [2026-09-26] U3 — Node.js güncellemesi (F0.4 tam kapanışı) — ✅

- **Yapılanlar:** Sistemde tek bir Node kurulumu olduğu doğrulandı (v22.12.0; kullanıcının hatırladığı ikinci v24 kurulumu yoktu — kayıt defteri, PATH, Program Files, `winget list` ile kapsamlı kontrol edildi). Kullanıcının açık onayıyla `winget uninstall OpenJS.NodeJS.22` denendi (yönetici izni olmadığı için 1603 ile başarısız oldu), ardından `winget install OpenJS.NodeJS.LTS` çalıştırıldı; Windows UAC yönetici onayı istedi, kullanıcı ekranından onayladı, kurulum tamamlandı.
- **Doğrulama:** `node -v` → `v24.19.0` ✓ · `npm -v` → `11.20.0` ✓ · `where.exe node` → tek konum (`C:\Program Files\nodejs\node.exe`) ✓ · kayıt defterinde tek "Node.js 24.19.0" girdisi, eski 22 girdisi yok ✓ — PATH çakışması veya çifte kurulum yok.
- **Kapanan maddeler:** F0.4 (artık tam ✅), U3
- **Commit:** (bu adımın ilerleme güncellemesiyle birlikte)
- **Notlar / sorunlar:** Sistem genelinde yazılım kurulumu/kaldırma — kullanıcının açık talebi ve onayı üzerine yapıldı.
- **Sonraki adım:** F2.1

### [2026-09-26] F1.11 — 🏁 Faz 1 kapanışı — ✅

- **Yapılanlar:** OpenAPI kontrolü: 67 uç, hepsinde Türkçe `summary`, doğru `tags`, `response_model`; `operationId`'ler `tag-fonksiyon` biçiminde, çakışma yok. `ruff check .`+`ruff format --check .` temiz. `pytest --cov=app --cov-report=term-missing` → **%80 genel kapsam** (hedef ≥%70). `git grep` ile yeni kodun `legacy/` içe aktarmadığı doğrulandı. Kök `README.md`'ye geçici "Backend'i çalıştırma" bölümü eklendi (kurulum adımları + demo giriş bilgisi).
- **Değişen dosyalar:** `README.md`.
- **Doğrulama:** 67 uç OpenAPI kontrolünden geçti ✓ · `pytest --cov` → 69 passed, %80 kapsam ✓ (düşük kapsamlı dosyalar: `google_books.py` %40 — opsiyonel/kullanılmıyor; `tmdb.py` %59 ve `social/service.py` %51 — sırasıyla U2 ve bilinçli sadelik nedeniyle, ayrıntı bağlam özetinde) · `git grep -nE "(from|import) legacy|legacy/backend-v1" -- backend/app` → boş ✓
- **Kapanan maddeler:** —
- **Commit:** `c5e3fa9`
- **Notlar / sorunlar:** Yok.
- **Sonraki adım:** Kullanıcıya Faz 1 özeti sunulacak, `v2` dalını push etmek için izin istenecek, sonra Faz 2 (frontend) — önkoşul U3 (Node güncellemesi).

### [2026-09-26] F1.10 — Profil özeti, platform vitrinleri ve demo verisi — ✅

- **Yapılanlar:** `stats/service.py`: `get_profile_summary` (tamamlanan film/dizi/kitap, puan, inceleme, liste, favori sayıları), `get_top_rated` (Bayes: `skor = v/(v+m)·R + m/(v+m)·C`, `m=3`, en az 1 oy — DB'den GROUP BY ile toplanıp Python'da sıralanıyor), `get_popular` (son `days` günde kütüphane girişi + 2×inceleme + genel listeye ekleme toplamı; sonuç <5 ise tüm zamana genişler). `stats/router.py` (§5.7). `scripts/seed.py`: idempotent (demo1 varsa çıkar), `--reset` (yalnız `ENV=dev`, `kfdu.db` sil + `alembic upgrade head`), 6 demo kullanıcı + takipler, 10 film/10 kitap başlıkla aranır (bulunamayan/servis kullanılamayan `AppError` yakalanıp loglanır, atlanır), servis fonksiyonlarıyla (`upsert_entry`/`create_review`/`create_list`/`add_item`/`like_activity`/`add_comment`) ~40 giriş/~12 inceleme (biri spoiler, ikisi 200+ karakter)/3 liste (biri gizli)/birkaç beğeni-yorum.
- **Değişen dosyalar:** `backend/app/modules/stats/{schemas,service,router}.py` (yeni), `backend/scripts/seed.py` (yeni), `backend/app/main.py` (router kaydı), `backend/tests/test_stats.py` (yeni, 3 test).
- **Doğrulama:** `pytest` → 69 passed (3 yeni) ✓ · `ruff check .` + `ruff format --check .` → temiz ✓ · **`python -m scripts.seed --reset` gerçek ortamda çalıştırıldı:** "6 demo kullanıcı oluşturuldu", "10/20 içerik bulundu" (10 kitap ✅ Open Library, 10 film TMDB anahtarı boş olduğu için `TMDB_NOT_CONFIGURED` ile atlandı ve loglandı), "40 kütüphane girişi, 12 inceleme oluşturuldu", "3 liste oluşturuldu", "9 beğeni, 8 yorum eklendi" ✓ · gerçek sunucu: `GET /feed?scope=global` dolu (liste/puan/inceleme kartları görünüyor) ✓, `GET /platform/top-rated?type=book` sonuç döndürüyor ✓, `GET /platform/top-rated?type=movie` boş ama HTTP 200 (beklenen — film yok) ✓, `GET /platform/popular` ✓, `GET /users/demo1/summary` doğru sayaçlar ✓
- **Kapanan maddeler:** REQ-2.1.3b (backend)
- **Commit:** `dcec8b7`
- **Kullanıcı kararı:** U6 — eski v1 verisinin (3 kullanıcı, 12 etkileşim, 7 liste) aktarımı **"hayır, atla"** ile reddedildi (D-19). `scripts/migrate_legacy_db.py` yazılmadı.
- **Notlar / sorunlar:** Movie tarafı U2'ye (TMDB anahtar yenileme) bağlı kalmaya devam ediyor — kod tarafı tam hazır, U2 tamamlanınca `python -m scripts.seed --reset` tekrar çalıştırılırsa filmler de otomatik eklenecek.
- **Sonraki adım:** F1.11 (🏁 Faz 1 kapanışı)

### [2026-09-26] F1.9 — Özel listeler — ✅

- **Yapılanlar:** `lists/schemas.py` (`ListCreateIn/UpdateIn`, `ListItemIn/NoteIn`, `ReorderIn`, `ListOut/Detail`, `MyListOut`). `lists/service.py`: CRUD (sahiplik kontrolü, gizli liste başkasına 404), `add_item` (`get_or_create_content`; zaten varsa mevcut öğeyi 200 ile döner, yeniyse 201 — `position = max+1`), `update_item_note`, `remove_item`, `reorder_items` (verilen kimlik kümesi mevcut öğelerle birebir aynı olmalı), `my_lists` (`contains` bayrağı tek ek sorgu), `list_user_lists`. `lists.created/item_added/item_removed/visibility_changed` olayları yayınlanıyor — F1.8'de yazılan dinleyiciler ilk kez gerçek veriyle çalıştı. `lists/router.py` (§5.6): `/lists/mine` `/lists/{list_id}`'den önce tanımlı.
- **Değişen dosyalar:** `backend/app/modules/lists/{schemas,service,router}.py` (yeni), `backend/app/main.py` (router kaydı), `backend/tests/test_lists.py` (yeni, 6 test).
- **Doğrulama:** `pytest` → 66 passed (6 yeni) ✓ · `ruff check .` + `ruff format --check .` → temiz ✓ · testte doğrulandı: public listeye ekleme/oluşturma → `Activity(verb=list_add/list_create)` oluşur; gizliye çevirince o listenin tüm aktiviteleri silinir.
- **Kapanan maddeler:** BUG-19 (tam)
- **Commit:** `51373cc`
- **Notlar / sorunlar:** Yok.
- **Sonraki adım:** F1.10

### [2026-09-26] F1.8 — Sosyal: aktiviteler, akış, beğeni, yorum, bildirim — ✅

- **Yapılanlar:** `social/handlers.py`: `register_handlers()` §3.5.2'deki 8 olayın tamamına abone (`library.log_changed/log_removed/status_changed`, `users.followed`, `lists.created/item_added/item_removed/visibility_changed` — sonuncular F1.9'u bekliyor). `log` aktivitesi (actor,content) başına tek; `status` aktivitesi 60 dk içinde günceller, dışında yeni açar. `social/service.py`: `_hydrate_activities` tüm kart alanlarını (aktör, içerik, liste bilgisi+kapaklar, beğeni sayısı+`liked_by_me`, yorum sayısı+son 2 önizleme, log kartları için puan+inceleme) birkaç toplu sorguyla dolduruyor — döngü içinde sorgu yok. `get_feed`/`list_user_activities` imleçli sayfalama. `like_activity`/`unlike_activity` idempotent + bildirim tekilleştirme. Yorum CRUD + yetki (`sahip veya aktivite sahibi silebilir`). Bildirim listesi/sayaç/okundu-işaretle. İnceleme okuma (`list_content_reviews` new/popular, `get_review_detail`, `list_user_reviews`).
- **Değişen dosyalar:** `backend/app/modules/social/{handlers,schemas,service,router}.py` (yeni), `backend/app/main.py` (router + `register_handlers()`), `backend/tests/conftest.py` (`register_handlers()` çağrısı), `backend/tests/test_social.py` (yeni, 9 test).
- **Doğrulama:** `pytest` → 60 passed (9 yeni) ✓ · `ruff check .` + `ruff format --check .` → temiz ✓ · **N+1 testi:** `before_cursor_execute` sayacıyla 15 kartlık akışın gerçek SQL sorgu sayısı ölçüldü, ≤12 sınırının içinde ✓ · gerçek sunucu: kayıt → Open Library kitabını puanla → `GET /feed?scope=global` akışta `card_type:"rating"` kartı gösteriyor → `GET /notifications/unread-count` çalışıyor ✓
- **Kapanan maddeler:** BUG-13 (backend, tam), BUG-12/BUG-19 (backend kısmı)
- **Commit:** `9286a24`
- **Notlar / sorunlar:** İnceleme okuma uçları feed kadar agresif optimize edilmedi (bilinçli sadelik tercihi — bkz. bağlam özeti). `lists.*` olay dinleyicileri F1.9'da gerçek bir yayıncı bulacak.
- **Sonraki adım:** F1.9

### [2026-09-26] F1.7 — Kütüphane: durum, puan, favori, inceleme yazma — ✅

- **Yapılanlar:** `catalog/service.py`'ye genel `content_to_summary()` eklendi (library ve sonraki modüller reuse edecek). `library/schemas.py`: `LibraryStatus`, `EntryUpdateIn`, `EntryOut`, `ContentState` (+ `PlatformStats`, `MeState`, `FriendEntry`), `LookupIn/EntryOut`, `Review*`. `library/service.py`: `upsert_entry` (`model_fields_set` ile kısmi güncelleme; `is_empty` → satır silinir; `in_progress`/`completed` → `started_at`/`finished_at` otomatik boşsa; `log_changed`/`log_removed`/`status_changed` olayları commit'ten önce), `delete_entry`, `get_state` (platform ortalama+dağılım tek gruplu sorgu, takip edilenlerin puanları), `lookup` (tek sorgu, JOIN+IN), `list_user_library`, `create/update/delete_review` (409/403). `library/router.py` (§5.4).
- **Değişen dosyalar:** `backend/app/modules/catalog/service.py` (`content_to_summary` eklendi), `backend/app/modules/library/{schemas,service,router}.py` (yeni), `backend/app/main.py` (router kaydı), `backend/tests/test_library.py` (yeni, 10 test).
- **Doğrulama:** `pytest` → 51 passed (10 yeni) ✓ · `ruff check .` + `ruff format --check .` → temiz ✓
- **Kapanan maddeler:** SEC-08 (tam), BUG-20 (backend), DEBT-04 (tam)
- **Commit:** `919615a`
- **Notlar / sorunlar:** `delete_review`'da silme sonrası `_has_review` kontrolü yanlış sonuç veriyordu (autoflush=False) — `db.flush()` ekleyerek düzeltildi, testte doğrulandı. `library.*` olayları şu an dinleyicisiz (no-op) — F1.8 `social/handlers.py` ile dinleyecek.
- **Sonraki adım:** F1.8 — **oturum kullanım limiti nedeniyle burada duraklatıldı, sonraki oturum buradan devam etsin**

### [2026-09-26] F1.6 — Katalog: TMDB + Open Library (+ Google Books) — ✅

- **Yapılanlar:** `catalog/genres.py` (core/genres üzerine TMDB/OL yardımcıları). `catalog/schemas.py` (ContentType/Source, Person, Providers, ContentSummary/Detail, GenreOut, DiscoverParams). `providers/tmdb.py`: search/discover/trending/collection/detail/similar; TR özet boşsa en-US'ye düşer; fragman seçimi (resmî + TR öncelikli); TR izleme platformları; anahtar yoksa 503. `providers/openlibrary.py`: search/discover/trending/detail (2 çağrı: key-search + work.json)/similar (yazarın diğer eserleri + konu); `description` string/`{"value"}` biçimleri; kapak URL'si; puan ×2. `providers/google_books.py` (opsiyonel). `catalog/service.py`: `resolve_source` (`^OL\d+W$` ile OL/Google ayrımı), `get_or_create_content` (7 gün tazelik, DB upsert), `get_detail`, arama/keşfet/trend/koleksiyon/benzer (§6.5 ttl_cache süreleriyle), `genres()`, `search_best()` (F6.3 için, `difflib` başlık benzerliği ≥0.6). `catalog/router.py` (§5.3) — statik yollar (`search/discover/trending/collections/{name}/genres`) `{type}/{external_id}`'den önce. **Kritik düzeltme (D-17):** `core/database.py`'ye `UTCDateTime` TypeDecorator eklendi — canlı testte `datetime.now(UTC) - row.fetched_at` çıkarma işleminin `TypeError` fırlattığı görüldü (SQLite, timezone=True olsa bile tzinfo'yu okurken düşürüyor); artık okuma sırasında UTC geri ekleniyor, PostgreSQL'de no-op.
- **Değişen dosyalar:** `backend/app/modules/catalog/**` (genres, schemas, service, router, providers/{tmdb,openlibrary,google_books}.py — yeni), `backend/app/core/database.py` (`UTCDateTime`), `backend/app/main.py` (router kaydı), `backend/tests/fixtures/*.json` (7 dosya — 4'ü Open Library'den gerçek yakalandı, 3'ü TMDB U2 beklediği için elle yazıldı — bkz. D-18), `backend/tests/test_catalog_{normalize,api}.py` (yeni, 17 test).
- **Doğrulama:** `pytest` → 41 passed (17 yeni) ✓ · `ruff check .` + `ruff format --check .` → temiz ✓ · `alembic check` → değişiklik yok (UTCDateTime aynı DDL'i üretiyor) ✓ · **Gerçek sunucu (Open Library, anahtarsız):** `GET /catalog/search?q=sefiller&type=book` → kapaklı/yazarlı sonuçlar ✓ · `GET /catalog/book/OL45804W` → tam normalize detay (yazar, açıklama, sayfa sayısı, tür) ✓ · ikinci çağrı DB önbellekten (hızlı, hatasız) ✓ · `GET /catalog/book/OL45804W/similar` ✓ · `GET /catalog/genres?type=book` ✓ · **TMDB (anahtar boş):** `GET /catalog/movie/27205` → 503 `TMDB_NOT_CONFIGURED` (beklenen, U2 bekliyor) ✓
- **Kapanan maddeler:** BUG-01, BUG-15, BUG-18 (tam), DEBT-05, REQ-2.2.1a/b/c (tam); BUG-02/BUG-14/DEBT-04 kısmi (backend tarafı)
- **Commit:** `8c12de7`
- **Notlar / sorunlar:** D-18 — TMDB fixture'ları elle yazıldı, U2 sonrası gerçek API'den yeniden yakalanması önerilir (düşük öncelik). TMDB'nin canlı uçtan uca doğrulaması (movie/tv detay, discover, trending, collections) U2 tamamlanana kadar bekliyor; kod respx-mock'lu testlerle doğrulandı.
- **Sonraki adım:** F1.7

### [2026-09-26] F1.5 — Kullanıcılar ve takip — ✅

- **Yapılanlar:** `core/genres.py` eklendi — Ek C'nin tamamı (`GenreEntry` + `GENRE_TABLE`, 30 tür) ve türetilmiş `GENRE_LABELS`/`GENRE_KEYS` (bkz. D-16 kararı). `users/schemas.py` genişletildi: `ProfileOut`, `PublicUserWithFollowOut`, `MeUpdateIn` (kısmi güncelleme + `favorite_genres ⊆ GENRE_KEYS` doğrulaması), `EmailChangeIn`, `DeleteAccountIn`. `users/avatars.py`: tür (jpg/png/webp) ve boyut (≤2MB) doğrulama, Pillow ile merkezden kare kırpma, 256×256 WEBP (kalite 85), `media/avatars/{user_id}_{uuid8}.webp`. `users/service.py`: `get_profile` (takip sayaçları + `is_following`/`follows_me` tek `db.get` sorgusuyla), `update_me` (`model_dump(exclude_unset=True)` ile yalnız gönderilen alanlar), `change_email` (şifre doğrulama + 409), `follow`/`unfollow` (idempotent, kendini takip → 400 `CANNOT_FOLLOW_SELF`, `users.followed` olayı commit'ten ÖNCE yayınlanıyor — §3.5.2), `list_followers`/`list_following` (N+1'siz — sayfa + tek ek sorguyla `is_following` kümesi), `search_users` (≥2 karakter, kimlik ister), `suggestions` (LEFT JOIN + GROUP BY ile takipçi sayısına göre), `delete_account` (şifre doğrula, avatar dosyasını sil, satırı sil → DB cascade). `users/router.py` (§5.2): `/me`, `/search`, `/suggestions` yolları `/{username}`'den ÖNCE tanımlandı (aksi halde `/{username}` bunları yutar).
- **Değişen dosyalar:** `backend/app/core/genres.py` (yeni), `backend/app/modules/users/{schemas,avatars,service,router}.py`, `backend/app/main.py` (router kaydı), `backend/tests/test_users.py` (yeni, 8 test).
- **Doğrulama:** `pytest` → 30 passed (8 yeni) ✓ · `ruff check .` + `ruff format --check .` → temiz ✓ · OpenAPI şemasında tüm `/users/*` uçları doğru yolda ve doğru sırada kayıtlı ✓
- **Kapanan maddeler:** SEC-06, BUG-04
- **Commit:** `90c6ed0`
- **Notlar / sorunlar:** D-16 kararı (yukarı bkz.) — Ek C verisinin konumu planın literal ifadesinden ("catalog/genres.py: Ek C → GENRES") küçük bir sapma; F1.6'da `catalog/genres.py` bu ortak veriyi kullanacak şekilde kurulacak, veri tekrarı olmayacak.
- **Sonraki adım:** F1.6

### [2026-09-26] F1.4 — Kimlik doğrulama modülü — ✅

- **Yapılanlar:** `users/deps.py` (`get_current_user`/`get_optional_user`, `OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token", auto_error=False)`, 401 yanıtlarında `WWW-Authenticate: Bearer`), `users/validation.py` (kullanıcı adı regex + ayrılmış adlar, §4.2), `users/schemas.py` (`PublicUserOut`, `MeOut` — F1.5 genişletecek). `auth/schemas.py`: `RegisterIn` (kullanıcı adı/e-posta/şifre gücü/şifre eşleşme doğrulaması), `LoginIn`, `TokenOut`, `ResetRequestIn/VerifyIn/ConfirmIn`, `ChangePasswordIn`. `auth/service.py`: `register` (409 EMAIL_TAKEN/USERNAME_TAKEN), `login` (401 INVALID_CREDENTIALS, 403 USER_INACTIVE, bcrypt→Argon2 otomatik yükseltme), şifre sıfırlama akışı (15 dk geçerlilik, e-postaya bağlı, son 15 dk'da ≤3 istek, `hmac.compare_digest` ile kod doğrulama, 5 yanlış denemede 429, `sha256(code+SECRET_KEY)` ile hash), `change_password`/`logout_all` (`token_version` artırımı → eski token'lar geçersiz). `auth/router.py` (§5.1, prefix `/auth`): login 10/dk/IP, reset request 10/saat/IP (`slowapi`). `app/main.py`'ye router eklendi. `core/errors.py`'nin `AppError`'ına opsiyonel `headers` parametresi eklendi. `tests/conftest.py`'ye `user_factory` fixture + `auth_headers()` yardımcı fonksiyonu eklendi.
- **Değişen dosyalar:** `backend/app/modules/auth/{schemas,service,router}.py` (yeni), `backend/app/modules/users/{deps,schemas,validation}.py` (yeni), `backend/app/core/errors.py` (headers desteği), `backend/app/main.py` (router kaydı), `backend/tests/conftest.py`, `backend/tests/test_auth.py` (yeni, 13 test).
- **Doğrulama:** `pytest` → 22 passed (13 yeni) ✓ · `ruff check .` + `ruff format --check .` → temiz ✓ · gerçek sunucu: `/auth/register` → 201 ✓, `/auth/token` (OAuth2 form) → 200 ✓, token ile `/auth/logout-all` → 204 ✓, tokensiz aynı uç → 401 + `WWW-Authenticate: Bearer` ✓, `/docs` → 200, OpenAPI `securitySchemes` içinde `OAuth2PasswordBearer` ✓.
- **Kapanan maddeler:** SEC-05, SEC-07, SEC-08 (kimlik kısmı), BUG-03, BUG-05, BUG-06 (backend kısmı)
- **Commit:** `cf0ff06`
- **Notlar / sorunlar:** REQ-2.1.1 (Ek A) maddeleri henüz ✅ işaretlenmedi — plan §9/F3.10 gereği bu maddeler frontend (F2.4) tamamlanınca kanıtla kapatılacak; backend tarafı burada bitti. `users/schemas.py` kasıtlı olarak yarım (F1.5 tamamlayacak).
- **Sonraki adım:** F1.5

### [2026-09-26] F1.3 — Veri modeli ve Alembic — ✅

- **Yapılanlar:** §4.2'deki 12 tablo ilgili modüllerin `models.py`'sine SQLAlchemy 2 `Mapped[]`/`mapped_column` ile yazıldı: `auth` (PasswordResetCode), `users` (User, Follow), `catalog` (Content), `library` (LibraryEntry, Review), `social` (Activity, ActivityLike, ActivityComment, Notification), `lists` (UserList, ListItem). Tüm CHECK (`status/rating/verb/type` vb.) ve UNIQUE kısıtları §4.2'deki adlarla; tüm FK'ler `ondelete="CASCADE"`. `Base.type_annotation_map`e `datetime -> DateTime(timezone=True)` eklendi (tüm tablolarda tekrarsız timezone-aware zaman). `app/models_registry.py` tüm modelleri içe aktarıyor. `alembic init`, `env.py` (`settings.DATABASE_URL`, `target_metadata=Base.metadata`, `render_as_batch=True`, `compare_type=True`), ilk migration autogenerate edildi (tüm CHECK kısıtları otomatik doğru üretildi, elle ekleme gerekmedi) ve `alembic upgrade head` ile `backend/kfdu.db` oluşturuldu. `tests/conftest.py`'ye `models_registry` import'u (tabloları `Base.metadata`'ya kaydetmek için) ve ham `Session` veren `db` fixture'ı eklendi. `tests/test_models.py` yazıldı.
- **Değişen dosyalar:** `backend/app/modules/{auth,users,catalog,library,social,lists}/models.py`, `backend/app/models_registry.py`, `backend/app/core/database.py` (type_annotation_map), `backend/alembic/` (env.py, versions/fa1eb17da6a0_v2_ilk_sema.py, script.py.mako, README), `backend/alembic.ini`, `backend/tests/conftest.py`, `backend/tests/test_models.py`.
- **Doğrulama:** `alembic revision --autogenerate` → 12 tablo + tüm CHECK/UNIQUE/index'ler algılandı ✓ · `alembic upgrade head` → hatasız, `kfdu.db` oluştu ✓ · `alembic check` → "No new upgrade operations detected." ✓ · `pytest` → 9 passed (4 yeni model testi: yinelenen giriş, puan 11, kendini takip → `IntegrityError`; kullanıcı silinince giriş+inceleme cascade siliniyor) ✓ · `ruff check .` + `ruff format --check .` → temiz ✓
- **Kapanan maddeler:** BUG-17, DEBT-07, DEBT-03 (tam)
- **Commit:** `0f29f74`
- **Notlar / sorunlar:** Mimari tercih gereği (bkz. hafıza: sade mimari) modeller arası gezinme için `relationship()` tanımlanmadı; cascade silme tamamen DB seviyesinde (`ON DELETE CASCADE` + `PRAGMA foreign_keys=ON`) sağlanıyor — servis katmanı doğrudan `select()`/`delete()` sorguları kullanacak.
- **Sonraki adım:** F1.4

### [2026-09-26] F1.2 — Çekirdek altyapı — ✅

- **Yapılanlar:** §3.5.9 + Ek E'ye göre tüm `app/core/` modülleri yazıldı: `config.py` (tam `Settings`, `SECRET_KEY` zorunlu), `database.py` (engine, `TimestampMixin`, SQLite pragma dinleyicisi), `errors.py` (`AppError` + `bad_request/not_found/forbidden/conflict`, doğrulama/HTTP/genel hata yakalayıcılar, küçük Türkçe pydantic mesaj çeviri sözlüğü), `security.py` (pwdlib Argon2+bcrypt, PyJWT), `deps.py`, `events.py`, `http.py` (`request_json` — 1 yeniden deneme, `ExternalServiceError`, anahtar maskeleme), `cache.py` (`ttl_cache`), `rate_limit.py` (slowapi), `pagination.py` (`Page`/`CursorPage`, PEP 695 generics), `logging.py`, `email.py`. `app/main.py`: `create_app()` — CORS (allowlist + `allow_credentials=False`), tüm hata yakalayıcılar, rate limit middleware, `/media` static, `GET /api/v1/health`. `tests/conftest.py` (bellek içi SQLite + `StaticPool`, `get_db` override, `clear_all_caches()`, `client` fixture), `test_health.py`, `test_errors.py`.
- **Değişen dosyalar:** `backend/app/core/*.py` (12 dosya), `backend/app/main.py`, `backend/tests/conftest.py`, `backend/tests/test_health.py`, `backend/tests/test_errors.py`.
- **Doğrulama:** `pytest` → 5 passed ✓ · `ruff check .` → "All checks passed!" ✓ · `ruff format --check .` → temiz ✓ · gerçek sunucu: `GET /api/v1/health` → 200 `{"status":"ok","db":true,"tmdb":false,"book_provider":"openlibrary","llm":"disabled"}` ✓ · `GET /docs` → 200 ✓ · bilinmeyen rota → 404 `{"detail":"Not Found","code":"NOT_FOUND"}` ✓
- **Kapanan maddeler:** SEC-02 (kalıcı), SEC-09, BUG-18 (yalnız altyapı — sağlayıcı kullanımı F1.6), DEBT-03 (kısmen — SQLAlchemy 2 tipli modeller F1.3'te), DEBT-06 (loglama; test/lint zaten F1.1'de, README Faz 7)
- **Commit:** `845b3e8`
- **Notlar / sorunlar:** Starlette'in `TestClient` + `httpx` kombinasyonu için bir deprecation uyarısı var ("httpx2" öner) — davranışı etkilemiyor, ileride Starlette güncellemesiyle kendiliğinden çözülecek, şimdilik aksiyon almadım.
- **Sonraki adım:** F1.3

### [2026-09-26] F1.1 — Bağımlılıklar ve proje iskeleti — ✅

- **Yapılanlar:** v1 backend kodu `git mv` ile `legacy/backend-v1/`'e taşındı. Yeni `backend/requirements.txt` + `requirements-dev.txt` (§3.2 sürümleri) yazıldı, `.venv` içine kuruldu. `backend/pyproject.toml` (ruff + pytest ayarları) eklendi. §3.4 modül iskeleti (`app/core/`, `app/modules/{auth,users,catalog,catalog/providers,library,social,lists,stats}/`, `tests/`, `tests/fixtures/`, `scripts/`) boş `__init__.py` dosyalarıyla oluşturuldu. `tests/test_smoke.py` (`import app`) eklendi.
- **Değişen dosyalar:** `legacy/backend-v1/**` (taşındı, 32 dosya); `backend/requirements.txt`, `backend/requirements-dev.txt`, `backend/pyproject.toml`, `backend/app/**/__init__.py` (11 adet), `backend/tests/__init__.py`, `backend/tests/fixtures/__init__.py`, `backend/tests/test_smoke.py`, `backend/scripts/__init__.py`.
- **Doğrulama:** `pip install -r requirements-dev.txt` → başarılı · `pip check` → "No broken requirements found" ✓ · `pytest` → 1 passed ✓ · `ruff check .` → "All checks passed!" ✓ · `ruff format --check .` → "15 files already formatted" ✓
- **Kapanan maddeler:** BUG-16
- **Commit:** `61c08c2`
- **Notlar / sorunlar:** Yok.
- **Sonraki adım:** F1.2

### [2026-09-26] F0.5 (atlandı) + 🏁 Faz 0 kapanışı — ✅

- **Yapılanlar:** Kullanıcıya Faz 0 özeti sunuldu, iki karar soruldu: (1) F0.5 (opsiyonel git geçmişi temizliği) yapılsın mı — kullanıcı **hayır, atla** dedi (D-14); (2) `v2` + `legacy-v1` origin'e push edilsin mi — kullanıcı **evet** dedi (D-15). `git push -u origin v2` ve `git push origin legacy-v1` çalıştırıldı.
- **Değişen dosyalar:** Kod değişikliği yok; yalnızca git push (yeni uzak dal + etiket) ve ilerleme dosyası güncellemesi.
- **Doğrulama:** Push çıktısı: `v2 -> v2` (yeni dal), `legacy-v1 -> legacy-v1` (yeni etiket), hata yok.
- **Kapanan maddeler:** —
- **Commit:** `dfe2088` (özet notu; push işleminin kendisi bir commit üretmez)
- **Notlar / sorunlar:** F0.4 hâlâ kısmi (Node bekliyor) ama Faz 1'i engellemediği için kullanıcı onayıyla Faz 1'e geçiliyor. U1/U2/U3 hâlâ açık — her fırsatta hatırlatılacak.
- **Sonraki adım:** F1.1

### [2026-09-26] F0.4 — Geliştirme ortamı — 🟡 kısmi

- **Yapılanlar:** Araç sürümleri kaydedildi (aşağıda). `backend/.venv` sanal ortamı oluşturuldu ve aktivasyonu doğrulandı. Kökte `.vscode/extensions.json` (6 önerilen eklenti) eklendi.
- **Değişen dosyalar:** `.vscode/extensions.json` (yeni); `backend/.venv/` (yeni, izlenmiyor).
- **Doğrulama:** `node -v` → `v22.12.0` (yetersiz) · `npm -v` → `11.20.0` · `python --version` → `3.13.1` · `git --version` → `2.47.1.windows.1` · venv aktifken `python -c "import sys; print(sys.prefix)"` → `...\backend\.venv` ✓
- **Kapanan maddeler:** —
- **Commit:** `8628d89`
- **Notlar / sorunlar:** ⛔ **Kabul kriteri tam sağlanmadı:** Node.js hâlâ `22.12.0`, gerekli `≥22.18`. Bu adım Node güncellemesi (👤 U3) tamamlanana kadar tam ✅ sayılmayacak. Faz 0'ın geri kalanını (F0.4 dışında) ve Faz 1'i engellemiyor; yalnızca Faz 2 (frontend) öncesi kesin şart.
- **Sonraki adım:** 🏁 Faz 0 kapanışı

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
