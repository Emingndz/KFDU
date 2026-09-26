# KFDU v2 — Proje İlerleme Durumu

> Plan: [`proje-plani.md`](proje-plani.md) · Bu dosya **her adımdan sonra** güncellenir (plan §0.2, madde 7).
> Son güncelleme: **2026-09-27** — F3.3 tamamlandı (İçerik detay sayfası).

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
| Proje durumu | 🟨 Faz 3 uygulanıyor |
| Aktif faz | Faz 3 — Çekirdek Özellikler |
| Sıradaki adım | **F3.4 — İnceleme sayfası ve yorum dizisi** |
| Çalışma dalı | `v2` |
| Son commit | `1c23219` (feat(F3.3): İçerik detay sayfası) |
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
- **Faz 2 ✅ TAMAMLANDI (F2.1–F2.5, 2026-09-26):** `frontend/` sıfırdan `npm create vue@latest` ile kuruldu (v1 `legacy/frontend-v1/`'e taşındı) — Vue 3.5/Router 5/Pinia 4/Vitest 4/ESLint 10/Tailwind 4/TanStack Query/VueUse/lucide-vue-next/vue-sonner. Tasarım sistemi (§3.7 token'ları) + 14 temel bileşen (`components/ui/`: Button/Input/Textarea/Select/Modal/Tabs/Avatar/Badge/Skeleton/EmptyState/ErrorState/Spinner/ConfirmDialog/OtpInput), `useTheme`/`useConfirm` composable'ları. API katmanı (`api/client.ts` — `ApiError`+otomatik URL-encode+401 yönetimi; `api/{auth,users,catalog}.ts`), `stores/{auth,ui}.ts`, `openapi-typescript` ile üretilen `api/schema.d.ts`+`types/index.ts`. Tam rota tablosu + guard (`requiresAuth`/`guestOnly`, `/`+misafir→`/kesfet`) + `AppShell` düzeni (header/bottomnav/footer). Kimlik sayfaları: Login/Register/ForgotPassword (3 adım)/Onboarding (3 adım: tür seçimi + takip önerileri) — hepsi backend kurallarıyla birebir eşleşen istemci doğrulamasıyla (`utils/validation.ts`) ve **gerçek backend'e karşı uçtan uca curl ile doğrulandı** (kayıt/giriş/şifre sıfırlama/tür listesi/takip önerileri/profil güncelleme, test kullanıcısı sonunda temizlendi). **32 frontend testi yeşil**, `lint`/`type-check`/`build` boyunca hep temiz; backend de bu fazda dokunulmamış olmasına rağmen kapanışta tekrar doğrulandı (69 test yeşil, ruff temiz). Ana JS paketi gzip 70 KB (hedef ≤200 KB'nin altında), her yeni sayfa kendi lazy chunk'ında.
  - **D-20 (BaseInput kusur düzeltmesi):** `inheritAttrs:false` + `v-bind="$attrs"` iç `<input>`'a taşındı — önceden `@blur`/`@keyup` gibi dinleyiciler yanlışlıkla dış `<div>`'e bağlanıp hiç tetiklenmiyordu; F2.4'te Caps Lock/alan-dokunma ihtiyacıyla fark edildi, geriye dönük uyumlu.
  - **Bilinçli kapsam sınırlamaları (erken soyutlama yok):** `api/catalog.ts` yalnız genres ile başladı (F3.1 genişletecek); onboarding'in takip butonu sayfaya özel, paylaşılan `FollowButton` değil (F3.6 yapacak).
  - **Kalıcı sınırlama:** Bu oturumda (Faz 2 boyunca) tarayıcı aracı hiç yoktu — tüm doğrulama kod incelemesi + HTTP/modül seviyesi + birim testleri + gerçek backend'e karşı curl ile yapıldı; görsel düzen, klavye gezinme, tema geçişi ve gerçek form deneyimi tarayıcıda elle denenmedi. `docs/ekran-goruntuleri/` bu yüzden oluşturulmadı (plan F2.5'te "mümkünse" diyor — mümkün olmadı). Kullanıcı isterse kendisi tarayıcıda deneyip geri bildirebilir.
- **Faz 2 kapanışı (2026-09-26):** Kullanıcı `v2`'yi push etmeyi (yapıldı, `origin/v2` güncel, `55a8ac1`) ve Faz 3'e geçmeyi onayladı.
- **F3.1 tamamlandı (2026-09-27):** `utils/{format,content}.ts` (relativeTime/formatDate/formatRuntime/formatPages/formatRating/formatCount; typeLabel/contentPath/contentKey/statusLabel/statusOptions — §4.2'nin durum-etiketi tablosuyla birebir, film=dizi etiketleri kitaptan farklı). `api/library.ts` + `api/lists.ts` (§5.4/§5.6'nın tam ham fonksiyon kapsamı + yalnız gerekli composable'lar: `useMyLists`/`useAddListItem`/`useRemoveListItem`/`useCreateList`). `composables/useContentActions.ts`: kütüphane durumu/puan/favori için tek noktadan yönetim — yerel `overlay` ref'iyle iyimser güncelleme (TanStack cache'i değil, çünkü henüz `content-state` sorgusunu dolduran bir tüketici sayfa yok — F3.3'te gerçek `useContentState` ile entegre edilecek), hata olursa geri alır + toast, misafiri `/giris?redirect=`'e yönlendirir, başarıda `content-state`/`library`/`user-summary`/`recs` sorgularını geçersiz kılar (§3.6.2 tablosuna göre). 10 bileşen (`components/content/`): `StarRating` (5 yıldız = 1-10, yarım yıldız yarım butonlarla, hover önizleme, aynı değere tıklayınca temizler, `role=slider`+tam klavye desteği), `RatingDisplay`, `RatingHistogram` (saf CSS 10 çubuk), `GenreChips` (saf sunum, etiket çözümlemesi çağırana bırakıldı), `PosterCard` (kırık poster görselinde `ImageOff` düşen görünüm — BaseAvatar'daki BUG-07 desenini içerik kartlarına taşıdı), `ContentGrid`/`ContentRow` (duyarlı ızgara/yatay şerit + iskelet/boş/hata durumları), `LibraryButtons`/`FavoriteButton` (saf sunum, durumu prop olarak alır — `useContentActions` ile kablolamak çağırana kalmış), `AddToListMenu` (`GET /lists/mine` + tıkla-ekle/çıkar + satır içi "yeni liste" formu, gerçek backend'e karşı curl ile doğrulandı: oluştur→ekle→`contains:true`→çıkar→`contains:false`→sil, hepsi 2xx). Hepsi `/_ui` vitrinine eklendi. 28 yeni test (`format`/`content`/`StarRating`).
- **F3.2 tamamlandı (2026-09-27):** `api/catalog.ts` genişletildi: `useSearch`/`useDiscover` (`useInfiniteQuery`, `initialPageParam`+`getNextPageParam` ile TanStack v5 sözleşimi), `useTrending`, `useCollection`. `api/stats.ts` (yeni): `usePlatformTopRated`/`usePlatformPopular` (`/platform/top-rated`+`/platform/popular`). `api/users.ts`: `useUserSearch` (infinite), `useFollowUser`/`useUnfollowUser` (ikinci kez ihtiyaç duyulunca eklendi — onboarding'in yerel takip mantığı ile aynı deseni tekrarlamak yerine composable'a çıkarıldı, ama görsel `FollowButton` bileşeni hâlâ F3.6'ya kalıyor). `api/library.ts`: `useLibraryLookup` (sayfadaki içerik anahtarları için toplu kişisel durum sorgusu, yalnız girişliyken etkin). `PosterCard`in `myState` prop'u genişletildi (yalnız favori değil, artık `status`/`rating` da destekliyor → ★ puan / ✓ tamamlandı / 🔖 planlandı rozetleri); `ContentGrid`'e `lookup` prop'u eklendi, her karta `contentKey`'iyle doğru kişisel durumu eşliyor. `FilterPanel` (yeni): tür/yıl aralığı/asgari puan (kaydırıcı)/sıralama/dil, "Uygula"/"Temizle", kaldırılabilir aktif filtre çipleri. `UserCard` (yeni, `components/users/`): avatar+ad+kullanıcı adı+bio+takip butonu. `DiscoverPage.vue` (`/kesfet`): büyük arama kutusu (350ms debounce, `@vueuse/core`'un `useDebounce`'ı), Film/Kitap/Kullanıcı sekmesi, tüm durum URL'de (`q/tur/tur_id/yil_min/yil_max/puan_min/sirala/dil` — planın literal Türkçe parametre adlarıyla birebir, `router.replace` ile geri/ileri ve link paylaşımı bozulmadan), üç mod: arama (metin varken `useSearch`), keşif (filtre varken ama metin yokken `useDiscover`), vitrin (ikisi de yokken 2 platform şeridi + film'de 3 ek şerit/kitapta 1 ek şerit + "Türlere Göz At" çip ızgarası — tıklayınca ilgili tür filtre olarak uygulanır). Sonsuz kaydırma gerçek IntersectionObserver ile (`@vueuse/core`'un `useIntersectionObserver`'ı), buton değil.
  - **Bilinçli basitleştirmeler:** (1) "Platformda En Yüksek Puanlılar"/"En Popülerler" şeritleri planın istediği gibi kendi İÇ sekmesine sahip değil, sayfanın ana Film/Kitap sekmesini takip ediyor (aynı seçimi iki kez ayrı ayrı sormamak için). (2) `FilterPanel` "masaüstünde satır içi / mobilde alt çekmece" yerine HER ekran boyutunda aynı satır-içi katlanır panel olarak render ediliyor — 360px'te kullanılabilir ama gerçek bir bottom-sheet değil. (3) Kullanıcı aramasında `PublicUserOut` `is_following` taşımadığı için (yalnız `ProfileOut`/`PublicUserWithFollowOut` taşıyor) önceden takip edilen biri başlangıçta "Takip et" gösterir; tıklanınca oturum için yerel işaretlenir (backend `follow` zaten idempotent, yanlış bir işlem olmuyor, yalnızca başlangıç görseli tam doğru değil). (4) Vitrin şeritleri (TMDB'ye bağlı olanlar) `TMDB_NOT_CONFIGURED` 503 aldığında `ErrorState` değil boş satır gösteriyor (U2 çözülene kadar zaten beklenen bir durum, ayrı bir hata banner'ı eklemek gerekmedi).
  - **Gerçek backend'e karşı uçtan uca (curl, kitap tarafı — TMDB U2'yi bekliyor):** `search?type=book&q=fox` ✓, `discover?type=book&genre=fiction&sort=rating` ✓, `platform/top-rated?type=book` ✓, `platform/popular?type=book` ✓, `trending?type=book` ✓, `users/search?q=demo` (geçerli token ile) ✓, `library/lookup` (toplu) ✓ — hepsi `ContentSummary`/`Page<T>`/`PublicUserOut`/`LookupEntryOut` şemalarıyla birebir eşleşti. **Gözlem (kod hatası değil):** `discover?type=book&min_rating=X` (tür filtresi OLMADAN, yalnız puan) Open Library'de bazen yavaş/zaman aşımına uğruyor — kök neden `openlibrary.py`'nin bu durumda çok geniş bir `ratings_average:[X TO 5]` sorgusuna düşmesi (F1.6'dan kalan, dış servisin kendi performansı, bu adımda dokunulmadı); `genre` ile birlikte kullanılınca hızlı çalışıyor.
- **F3.3 tamamlandı (2026-09-27):** `api/catalog.ts`: `useContentDetail`, `useSimilarContent`. `api/library.ts`: `useContentState` (§3.6.2'nin `['content-state',type,id]` anahtarıyla — F3.1'de "gerçek tüketici olunca değerlendirilecek" notu bırakılmıştı, artık gerçek ilk tüketici bu), `useCreateReview`/`useUpdateReview`/`useDeleteReview`. `api/social.ts` (yeni): `useContentReviews` (infinite, "Daha fazla" butonuyla — otomatik kaydırma değil, plan bunu böyle istiyor), `useReviewDetail` (F3.4 de kullanacak), `useLikeActivity`/`useUnlikeActivity`. 7 yeni bileşen: `CastRow`, `WatchProviders` (yalnız düz metin rozetler — `Providers` şeması logo URL'si değil yalnız platform adı stringleri taşıyor, gerçek logo yok), `ReviewEditor` (kendi incelemem: yoksa yaz formu, varsa göster+Düzenle/Sil — Düzenle mevcut metni yükleyip aynı formu tekrar açıyor), `ReviewItem` (başkalarının incelemeleri; spoiler bulanıklığı, 200 karakter kesme, beğeni — kendi incelemem genel listede TEKRAR görünmesin diye `ReviewList` kendi incelemeyi filtreliyor), `ReviewList` (Yeni/Popüler + Daha fazla), `TrailerModal` (BaseModal + youtube-nocookie iframe). `ContentDetailPage.vue` (`/film/:id`, `/kitap/:id` — route-level `props` fonksiyonuyla `type` enjekte ediliyor, dizi F4.1'e kadar hâlâ ComingSoon): hero (backdrop/poster/başlık/meta satırı/yönetmen-yazar düz metin/harici puan rozeti), platform puanı+histogram, eylem çubuğu (`StarRating`+`LibraryButtons`+`FavoriteButton`+`AddToListMenu`+Paylaş+Fragman — `useContentActions`'ın `initial` parametresi artık gerçek `useContentState` verisiyle besleniyor), özet (devamını göster), oyuncular, izleme platformları (yalnız film/dizi), incelemeler, arkadaşların (`ContentState.friends`), benzer içerikler, 404/hata durumları, `document.title`.
  - **StarRating↔useContentActions çakışması ve düzeltmesi:** `StarRating` aynı yıldıza tekrar tıklayınca zaten kendi içinde `null` yayıyordu (F3.1); `useContentActions.setRating`'in KENDİ toggle kontrolü de vardı — ikisi çakışınca "temizle" tıklaması sessizce yutuluyordu. Çözüm: `setRating` artık kendi eşitlik kontrolünü yapmıyor, StarRating'in kararını olduğu gibi uyguluyor (StarRating'in kendi toggle'ı tek otorite).
  - **D-21 (backend düzeltmesi — dış servis 404'ü):** `core/http.py`'deki `request_json`, bir dış sağlayıcıdan (TMDB/Open Library) gelen 404'ü sarmalamadan olduğu gibi fırlatıyordu; FastAPI'nin genel yakalayıcısı bunu 500 "Beklenmeyen bir hata oluştu" olarak dönüyordu (canlı testte `catalog/book/OL999999999W` ile bulundu). Artık 404 özel olarak yakalanıp `not_found()` ile temiz `404 NOT_FOUND` olarak dönüyor — frontend'in "Bu içerik bulunamadı" sayfası artık gerçekten tetikleniyor.
  - **D-22 (backend düzeltmesi — sahte "düzenlendi" etiketi):** `social/service.py`'de `is_edited=review.updated_at > review.created_at` kullanılıyordu; ama `TimestampMixin` her iki alanı da AYRI `datetime.now(UTC)` çağrılarıyla dolduruyor (bkz. `core/database.py`), bu yüzden her yeni inceleme oluşturulduğunda mikrosaniyelik farktan dolayı `is_edited` yanlışlıkla `true` çıkıyordu (canlı testte fark edildi). 1 saniyelik tolerans eşiğine çevrildi (`(updated_at - created_at).total_seconds() > 1`) — gerçek düzenlemeler (dakikalar/saatler sonra) doğru tespit ediliyor, oluşturma anındaki mikrosaniye farkı artık yanlış pozitif üretmiyor. Yeni regresyon testi eklendi (`test_review_is_edited_false_until_actually_updated`, DB üzerinden `created_at`'i geriye alarak gerçek zaman beklemeden test ediyor).
  - **Bilinçli kapsam sınırlamaları:** REQ-2.1.4f/g/h (yorumlar) bu adıma dahil değil — ContentDetailPage'de yorum bölümü yok, `CommentThread` F3.4'ün işi (plan da böyle ayırıyor).
  - **Gerçek backend'e karşı uçtan uca (curl, kitap tarafı, iki test kullanıcısıyla):** içerik detayı+benzer içerikler+boş inceleme listesi ✓; inceleme oluştur (uzun metin, kesme testi için) → `is_truncated:true`, `activity_id` dolu ✓; `content-state.me.review_id` doğru güncelleniyor ✓; başka kullanıcı beğeniyor → `likes_count` artıyor ✓; başkası düzenlemeye çalışınca 403 ✓; sahibi düzenliyor → `is_edited:true` (gerçek zaman farkıyla) ✓; sil → 204, `review_id` tekrar `null` ✓. Test kullanıcıları temizlendi. Film tarafı hâlâ U2'yi bekliyor.
- **Sırada:** F3.4 — İnceleme sayfası ve yorum dizisi (`CommentThread`, `LikeButton` — F3.3'te `useLikeActivity`/`useUnlikeActivity` zaten yazıldı, `ReviewPage` `/inceleme/:id`).
- **Sırada:** F3.3 — İçerik detay sayfası (`ContentDetailPage`, `useContentState`'in gerçek ilk tüketicisi — `useContentActions`'ın iyimser katmanı burada TanStack cache'iyle entegrasyonu yeniden değerlendirilecek).

---

## 📊 Faz Özeti

| Faz | Başlık | Durum | İlerleme | Başlangıç | Bitiş |
|---|---|---|---|---|---|
| 0 | Güvenlik, temizlik, hazırlık | ✅ Tamamlandı (F0.4 sonradan kapandı) | 5/5 | 2026-09-26 | 2026-09-26 |
| 1 | Backend temeli | ✅ Tamamlandı | 11/11 | 2026-09-26 | 2026-09-26 |
| 2 | Frontend temeli | ✅ Tamamlandı | 5/5 | 2026-09-26 | 2026-09-26 |
| 3 | Çekirdek özellikler (ilk kullanılabilir v2) | 🟨 Devam ediyor | 3/10 | 2026-09-26 | – |
| 4 | Çağ atlatma paketi | ⬜ Başlamadı | 0/9 | – | – |
| 5 | Akıllı öneriler | ⬜ Başlamadı | 0/6 | – | – |
| 6 | KFDU Asistan (NVIDIA LLM) | ⬜ Başlamadı | 0/9 | – | – |
| 7 | Kalite, test, CI, yayın | ⬜ Başlamadı | 0/9 | – | – |
| **Toplam** | | | **24/64** | | |

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
- [x] F2.4 — Kimlik sayfaları ve onboarding — ✅ (2026-09-26)
- [x] 🏁 F2.5 — Faz 2 kapanışı — ✅ (2026-09-26)

### Faz 3 — Çekirdek Özellikler

- [x] F3.1 — İçerik bileşenleri ve yardımcılar — ✅ (2026-09-27)
- [x] F3.2 — Keşfet sayfası — ✅ (2026-09-27)
- [x] F3.3 — İçerik detay sayfası — ✅ (2026-09-27)
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
| BUG-02 | Film detayında yönetmen/oyuncu/süre/tür yok | F1.6, F3.3 | ✅ | `8c12de7`, `1c23219` |
| BUG-03 | Aynı kullanıcı adıyla kayıt → 500; yanlış/İngilizce hata | F1.4 | ✅ | `cf0ff06` |
| BUG-04 | İki kez takip / takip etmeyeni bırakma → 500 | F1.5 | ✅ | `90c6ed0` |
| BUG-05 | E-posta değişince oturum kırılıyor (JWT sub = e-posta) | F1.2 | ✅ (F1.4'te doğrulandı — `sub`=id) | `cf0ff06` |
| BUG-06 | 30 dk token, 401 yönetimi yok; 401 yerine 403 | F1.2, F2.3 | ✅ (backend F1.4: 7 gün token, 401+WWW-Authenticate; frontend F2.3: `client.ts` 401'de çıkış+yönlendirme+tekil toast) | `cf0ff06` |
| BUG-07 | Kırık yer tutucu görseller (via.placeholder.com) | F2.2, F3.9 | 🟡 bileşen düzeyi ✅ (BaseAvatar kırık/yok görselde deterministik baş harf); tüm sayfalarda kullanım F3.9 | `f3e2894` |
| BUG-08 | Detay açmak arama tipini değiştirip gereksiz çağrı yapıyor | Faz 2–3 (F3.2) | ✅ (v2'de detay ayrı bir rota — `/film/:id` vb. — DiscoverPage'in kendi durumunu hiç etkilemiyor, bu hata sınıfı mimari olarak imkânsız) | `dcffa45` |
| BUG-09 | Başkasının profilinde film durumları kitap etiketiyle | F3.6 | 🔴 | |
| BUG-10 | Şifre sıfırlamada "(Demo: undefined)" | F2.4 | ✅ (v2'de gerçek e-posta/log tabanlı 3 adımlı akış var, "(Demo: ...)" metni yok) | `031befa` |
| BUG-11 | Arama sorguları URL-encode edilmiyor | F2.3 | ✅ (`client.ts`'teki `api()` tüm sorgu parametrelerini `URLSearchParams` ile otomatik kodluyor) | `e104538` |
| BUG-12 | Akışta göreli tarih/aksiyon metni/alıntı yok | F1.8, F3.5 | 🟡 backend ✅ (`created_at`+`excerpt`+`card_type` API'de var); arayüz F3.5 | `9286a24` |
| BUG-13 | Akışta sayfalama yok, N+1 sorgular | F1.8, F3.5 | ✅ backend (imleçli sayfalama + N+1 giderildi, testle doğrulandı) | `9286a24` |
| BUG-14 | Arama "daha fazla" çalışmıyor; kitap sayfa ofseti hatalı | F1.6, F3.2 | ✅ (backend doğru sayfalama; arayüz `useSearch`/`useDiscover` ile gerçek sonsuz kaydırma — `IntersectionObserver` sentinel'i, `has_next`'e göre otomatik `fetchNextPage`) | `8c12de7`, `dcffa45` |
| BUG-15 | Kitap yıl filtresi sessizce filtresiz sonuç dönüyor | F1.6 | ✅ | `8c12de7` |
| BUG-16 | `requirements.txt` eksik (temiz kurulum çöker) | F1.1 | ✅ | `61c08c2` |
| BUG-17 | Migrasyon yok; artık tablolar; eşsizlik kısıtı yok | F1.3 | ✅ | `0f29f74` |
| BUG-18 | Dış API çağrılarında timeout yok | F1.2, F1.6 | ✅ (F1.2 altyapı + F1.6 tüm sağlayıcılar `request_json` kullanıyor) | `8c12de7` |
| BUG-19 | Yetki hataları 400; yorum–aktivite aidiyeti kontrol edilmiyor | F1.8, F1.9 | ✅ | `51373cc` |
| BUG-20 | Durum değerleri film/kitap için tutarsız | F1.7, F3.1 | ✅ (backend `LibraryStatus` tek ortak enum; arayüz `utils/content.ts`'in `statusLabel`'ı §4.2 tablosuyla birebir — film=dizi etiketleri, kitap ayrı) | `919615a`, `77c4b3d` |
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
| REQ-2.1.1a | Kayıt: kullanıcı adı, e-posta, şifre, şifre tekrarı | F1.4, F2.4 | ✅ | `RegisterPage.vue` `031befa` |
| REQ-2.1.1b | Giriş: e-posta + şifre | F1.4, F2.4 | ✅ (v2'de ayrıca kullanıcı adıyla da girilebiliyor) | `LoginPage.vue` `031befa` |
| REQ-2.1.1c | Net hata mesajları | F1.2, F1.4, F2.4 | ✅ | `ApiError`+form/alan hataları, curl ile doğrulandı `031befa` |
| REQ-2.1.1d | Şifremi unuttum (e-posta) | F1.4, F2.4 | ✅ | `ForgotPasswordPage.vue`, uçtan uca curl ile doğrulandı `031befa` |
| REQ-2.1.2a | Takip edilenlerin aktiviteleri (yeniden eskiye) | F1.8, F3.5 | ⬜ | |
| REQ-2.1.2b | Kart başlığı: avatar, ad (link), aksiyon metni, göreli tarih | F3.5 | ⬜ | |
| REQ-2.1.2c | Türe göre gövde, afiş ön planda | F3.5 | ⬜ | |
| REQ-2.1.2d | Beğen / Yorum Yap | F1.8, F3.4, F3.5 | ⬜ | |
| REQ-2.1.2e | Puanlama kartı: büyük afiş + yıldız / x/10 | F3.5 | ⬜ | |
| REQ-2.1.2f | İnceleme kartı: 150–200 karakter alıntı + "…daha fazlasını oku" | F3.4, F3.5 | ⬜ | |
| REQ-2.1.2g | Sayfalama: ilk 10–15 + sonsuz kaydırma / daha fazla yükle | F1.8, F3.5 | ⬜ | |
| REQ-2.1.3a | Arama → detay (kapak, başlık, yıl) | F1.6, F3.2 | ✅ | `ContentDetailPage.vue` (`1c23219`) |
| REQ-2.1.3b | Vitrin: En Yüksek Puanlılar, En Popülerler | F1.10, F3.2 | ✅ | `DiscoverPage.vue`, kitapla curl ile doğrulandı (`dcffa45`) |
| REQ-2.1.3c | Filtre: tür, yıl, puan | F1.6, F3.2 | ✅ | `FilterPanel.vue` + `useDiscover`, curl ile doğrulandı (`dcffa45`) |
| REQ-2.1.4a | Künye: kapak, özet, yıl, süre/sayfa, yönetmen/yazar, türler | F1.6, F3.3 | ✅ | `ContentDetailPage.vue` (`1c23219`) |
| REQ-2.1.4b | Platform puanı: ortalama + oy sayısı | F1.7, F3.3 | ✅ | `ContentDetailPage.vue` + `RatingHistogram` (`1c23219`) |
| REQ-2.1.4c | 1–10 puan bileşeni (güncellenebilir) | F1.7, F3.1, F3.3 | ✅ | `StarRating`+`useContentActions`, curl ile doğrulandı (`1c23219`) |
| REQ-2.1.4d | İzledim/İzlenecek · Okudum/Okunacak butonları | F1.7, F3.1, F3.3 | ✅ | `LibraryButtons` (`1c23219`) |
| REQ-2.1.4e | "Özel Listeye Ekle" menüsü | F1.9, F3.1, F3.7 | ✅ (plan hedefi F3.7 diyordu ama `AddToListMenu` F3.1'de yazılıp F3.3'te gerçek bir sayfaya bağlandı — işlevsel olarak tamam, F3.7/ListPage ayrıca kendi tarafından da kullanacak) | `1c23219` |
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
| 2026-09-27 | D-20 | `BaseInput.vue`'ya `inheritAttrs:false` + `v-bind="$attrs"` (iç `<input>`'a) eklendi | ✅ Uygulayıcı kararı — F2.4'te Caps Lock algılama/alan-dokunma (`@blur`) ihtiyacıyla fark edildi: dışarıdan verilen olay dinleyicileri Vue'nun varsayılan attrs devralma davranışıyla dış `<div>`'e bağlanıp hiç tetiklenmiyordu. Geriye dönük uyumlu (önceki hiçbir kullanım ekstra attr geçirmiyordu). |
| 2026-09-27 | D-21 | `core/http.py`'deki `request_json`, dış sağlayıcıdan (TMDB/Open Library) gelen 404'ü artık `not_found()` ile temiz 404'e çeviriyor (önceden sarmalanmadan fırlatılıp genel yakalayıcıda 500'e dönüşüyordu) | ✅ Uygulayıcı kararı — F3.3'te `ContentDetailPage`'in "Bu içerik bulunamadı" durumunu canlı test ederken bulundu (`catalog/book/OL999999999W` → 500 dönüyordu). Diğer 4xx kodları (400/401/403) eskisi gibi sarmalanmadan fırlatılmaya devam ediyor — yalnızca 404'e özel, dar kapsamlı bir düzeltme. |
| 2026-09-27 | D-22 | `social/service.py`'deki `is_edited` hesaplaması `updated_at > created_at` yerine `(updated_at - created_at).total_seconds() > 1` oldu | ✅ Uygulayıcı kararı — F3.3'te canlı test sırasında bulundu: `TimestampMixin` her iki alanı da ayrı `datetime.now(UTC)` çağrısıyla dolduruyor, bu yüzden her yeni inceleme mikrosaniyelik farktan dolayı yanlışlıkla "düzenlendi" görünüyordu. `TimestampMixin`'in kendisi (12+ tabloyu etkiler) değil, yalnızca bu tek kullanım yeri değiştirildi — daha dar kapsamlı ve düşük riskli. Regresyon testi eklendi. |

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

### [2026-09-27] F3.3 — İçerik detay sayfası — ✅

- **Yapılanlar:**
  - `api/catalog.ts`: `useContentDetail(type,id)` (staleTime 1 saat, §3.6.2'ye uygun), `useSimilarContent`.
  - `api/library.ts`: `useContentState(type,id)` (`['content-state',type,id]`, 30 sn — F3.1'in bıraktığı notu kapatan gerçek ilk tüketici), `useCreateReview`/`useUpdateReview`/`useDeleteReview` (başarıda `content-state`+`reviews` sorgularını geçersiz kılıyor).
  - `api/social.ts` (yeni): `useContentReviews` (infinite, ama "Daha fazla" BUTONUYLA — plan bu bölüm için otomatik kaydırma değil bunu istiyor), `useReviewDetail` (F3.4 de kullanacak), `useLikeActivity`/`useUnlikeActivity`.
  - 7 yeni bileşen (`components/content/`): `CastRow` (fotoğraflı yatay şerit, fotoğrafsızda baş harf düşen görünümü), `WatchProviders` (yalnız düz metin platform adı rozetleri — `Providers` şeması logo URL'si değil string listesi taşıyor, gerçek logo yok), `ReviewEditor` (kendi incelemem: yoksa yaz formu, varsa göster+Düzenle/Sil), `ReviewItem` (başkalarının incelemeleri — spoiler bulanıklığı, 200 karakter kesme+"…devamını oku", beğeni), `ReviewList` (Yeni/Popüler sıralama + Daha fazla; kendi incelemem tekrar görünmesin diye filtreleniyor), `TrailerModal` (BaseModal + youtube-nocookie iframe).
  - `ContentDetailPage.vue` (`/film/:id`, `/kitap/:id` — route-level `props` fonksiyonuyla `type` enjekte ediliyor; `/dizi/:id` hâlâ `ComingSoonPage`, F4.1'i bekliyor): hero, platform puanı+histogram, eylem çubuğu (`StarRating`+`LibraryButtons`+`FavoriteButton`+`AddToListMenu`+Paylaş+Fragman, `useContentActions`'ın `initial`'ı artık gerçek `useContentState`'ten besleniyor), özet, oyuncular, izleme platformları (yalnız film/dizi), incelemeler, arkadaşların, benzer içerikler, 404/hata durumları, `document.title`.
  - **Kusur düzeltmesi (StarRating↔useContentActions):** `StarRating` aynı yıldıza tekrar tıklayınca kendi içinde `null` yayıyordu (F3.1); `useContentActions.setRating`'in KENDİ toggle kontrolü buna karışınca "temizle" tıklaması sessizce yutuluyordu. `setRating` artık kendi eşitlik kontrolünü yapmıyor, StarRating'in kararını olduğu gibi uyguluyor.
  - **D-21 (backend, dış servis 404'ü):** `request_json` bir dış sağlayıcıdan 404 aldığında sarmalamadan fırlatıyordu, genel yakalayıcı bunu 500 yapıyordu (`catalog/book/OL999999999W` ile canlı testte bulundu). Artık temiz `404 NOT_FOUND`.
  - **D-22 (backend, sahte "düzenlendi" etiketi):** `is_edited=updated_at>created_at` her yeni incelemede `TimestampMixin`'in iki ayrı `datetime.now(UTC)` çağrısı yüzünden mikrosaniye farkından dolayı yanlışlıkla `true` çıkıyordu. 1 saniyelik toleransa çevrildi + regresyon testi eklendi (`test_review_is_edited_false_until_actually_updated`).
  - **Bilinçli kapsam sınırlaması:** REQ-2.1.4f/g/h (yorumlar) bu adıma dahil değil — `CommentThread` F3.4'ün işi.
- **Değişen dosyalar:** `backend/app/core/http.py`, `backend/app/modules/social/service.py`, `backend/tests/test_social.py` (D-21/D-22); `frontend/src/api/{catalog,library,social}.ts`, `frontend/src/composables/useContentActions.ts`, `frontend/src/components/content/{CastRow,WatchProviders,ReviewEditor,ReviewItem,ReviewList,TrailerModal}.vue` (yeni), `frontend/src/pages/ContentDetailPage.vue` (yeni), `frontend/src/router/index.ts`.
- **Doğrulama:** Backend: `pytest` → **70 passed** (1 yeni) ✓ · `ruff check`+`format` → temiz ✓. Frontend: `npm run lint` → temiz ✓ · `npm run type-check` → temiz (birkaç `?? []` düzeltmesi sonrası — `ContentDetail`'in `genres_detail`/`cast`/`directors`/`authors`/`providers` alanları backend'de `default_factory=list` olduğu için TS tarafında opsiyonel çıkıyor) ✓ · `npm run test:unit -- run` → 60 passed ✓ · `npm run build` → başarılı, `ContentDetailPage` kendi lazy chunk'ında (32.56 KB, gzip 10.50 KB) ✓ · Vite dev sunucusunda 10 yeni modül + `/kitap/:id` rotası tek tek istendi, hepsi 200 ✓ · **gerçek backend'e karşı uçtan uca (curl, iki test kullanıcısıyla, kitap tarafı):** içerik detayı+benzer içerikler+boş inceleme listesi ✓; uzun inceleme oluştur → `is_truncated:true`+`activity_id` dolu ✓; `content-state.me.review_id` doğru ✓; başkası beğeniyor → `likes_count` artıyor ✓; başkası düzenlemeye çalışınca 403 ✓; sahibi düzenliyor → `is_edited:true` ✓; sil → 204, `review_id` tekrar `null` ✓. Test kullanıcıları temizlendi.
- **Kapanan maddeler:** BUG-02 (tam), REQ-2.1.3a, REQ-2.1.4a/b/c/d/e
- **Commit:** `1c23219`
- **Notlar / sorunlar:** Tarayıcı aracı hâlâ yok — hero/eylem çubuğu/fragman modalının görsel doğrulaması yalnızca kod incelemesi + yukarıdaki testlerle yapıldı. Film tarafının canlı doğrulaması hâlâ U2'yi bekliyor.
- **Sonraki adım:** F3.4 — İnceleme sayfası ve yorum dizisi

### [2026-09-27] F3.2 — Keşfet sayfası — ✅

- **Yapılanlar:**
  - `api/catalog.ts` genişletildi: `useSearch(type,q)`/`useDiscover(type,filters)` (`useInfiniteQuery`, TanStack v5'in zorunlu `initialPageParam`+`getNextPageParam` sözleşimiyle; `Page.has_next`'e göre bir sonraki sayfa numarası), `useTrending(type)`, `useCollection(name)`. Ham `useGenres` artık `MaybeRefOrGetter` kabul edip reaktif (tür değişince tür listesi yeniden çekiliyor).
  - `api/stats.ts` (yeni): `usePlatformTopRated`/`usePlatformPopular` (`/platform/top-rated`, `/platform/popular`).
  - `api/users.ts`: `useUserSearch` (infinite, ≥2 karakterde etkin), `useFollowUser`/`useUnfollowUser` (takip/bırak — onboarding'in yerel mantığını aynen tekrarlamak yerine composable'a çıkarıldı; görsel paylaşılan `FollowButton` bileşeni hâlâ bilinçli olarak F3.6'ya bırakıldı).
  - `api/library.ts`: `useLibraryLookup(keys)` — sayfadaki içerik anahtarları için toplu kişisel durum sorgusu, yalnız girişliyken etkin.
  - `PosterCard`'ın `myState` prop'u genişletildi: yalnız `isFavorite` değil artık `status`/`rating` da alıyor → sağ üstte öncelik sırasıyla ★puan / ✓tamamlandı / 🔖planlandı + ♥favori rozetleri. `ContentGrid`'e `lookup` prop'u eklendi, her karta `contentKey`'iyle doğru satırı eşliyor.
  - `FilterPanel.vue` (yeni): tür (`useGenres`), yıl aralığı (min/max), asgari puan (0-10 kaydırıcı), sıralama (Popülerlik/Puan/En yeni/En eski — backend'in `sort` literal'leriyle birebir: popular/rating/newest/oldest), dil (Türkçe/İngilizce); "Uygula" (taslağı commit eder) / "Temizle" (anında sıfırlar); aktif filtreler kaldırılabilir çipler.
  - `UserCard.vue` (yeni, `components/users/`): avatar+ad+kullanıcı adı+bio+takip butonu.
  - `DiscoverPage.vue` (`/kesfet`): büyük arama kutusu (`@vueuse/core`'un `useDebounce`'ı, 350 ms), Film/Kitap/Kullanıcı sekmesi (Dizi bilinçli olarak yok — plan F4.1'e erteliyor), tüm durum URL'de plandaki **birebir Türkçe parametre adlarıyla** (`q`, `tur`, `tur_id`, `yil_min`, `yil_max`, `puan_min`, `sirala`, `dil`) — `router.replace` ile, geri/ileri ve link paylaşımı bozulmuyor. Üç görünüm modu: **arama** (metin varken `useSearch`, filtreler bu modda uygulanmaz çünkü `/catalog/search` filtre parametresi kabul etmiyor), **keşif** (metin yok ama filtre varken `useDiscover`), **vitrin** (ikisi de yokken: "En Yüksek Puanlılar"+"En Popülerler" + Film sekmesinde 3 ek şerit (Trend/Vizyonda/Yakında) veya Kitap sekmesinde 1 ek şerit (Trend Kitaplar) + "Türlere Göz At" çip ızgarası — tıklanınca o tür filtre olarak uygulanıp keşif moduna geçiyor). Sonsuz kaydırma gerçek `IntersectionObserver` ile (`@vueuse/core`'un `useIntersectionObserver`'ı) — buton değil, plandaki "sonsuz kaydırma" ifadesine birebir.
  - **Bilinçli basitleştirmeler:** (1) "En Yüksek Puanlılar"/"En Popülerler" şeritleri planın istediği kendi iç Film/Kitap sekmesine sahip değil, sayfanın ana sekmesini takip ediyor (aynı seçimi iki ayrı yerde sormamak için — kullanıcı deneyimini bozmuyor, yalnızca UI'da bir sekme daha az var). (2) `FilterPanel` "masaüstünde satır içi / mobilde alt çekmece" yerine her ekran boyutunda aynı satır içi katlanır panel — 360px'te işlevsel ama gerçek bir bottom-sheet bileşeni değil. (3) Kullanıcı aramasında `PublicUserOut` `is_following` alanı taşımıyor (yalnız `ProfileOut`/`PublicUserWithFollowOut` taşıyor); önceden takip edilen biri arama sonucunda başlangıçta "Takip et" gösteriyor, tıklanınca oturum için yerel işaretleniyor (backend `follow` idempotent olduğu için yanlış bir işlem olmuyor, yalnızca ilk görüntüleme tam doğru değil — gerçek çözüm bir backend uç noktası gerektirir, F3.2'nin frontend-only kapsamı dışında). (4) TMDB'ye bağlı vitrin şeritleri `TMDB_NOT_CONFIGURED` 503 aldığında ayrı bir hata banner'ı değil boş satır gösteriyor (U2 çözülene kadar zaten beklenen, dokunulmadı).
- **Değişen dosyalar:** `frontend/src/api/{catalog,stats,users,library}.ts`, `frontend/src/components/content/{PosterCard,ContentGrid,FilterPanel}.vue` (FilterPanel yeni), `frontend/src/components/users/UserCard.vue` (yeni), `frontend/src/pages/DiscoverPage.vue` (yeni), `frontend/src/router/index.ts`.
- **Doğrulama:** `npm run lint` → temiz (2 tur: kullanılmayan `TYPE_TAB`/`showingShowcase` kaldırıldı) ✓ · `npm run type-check` → temiz ✓ · `npm run test:unit -- run` → 60 passed (bu adımda yeni birim testi eklenmedi — plan F3.2 için açıkça test istemiyor, sayfa büyük ölçüde canlı entegrasyona dayanıyor; doğrulama davranışsal/curl tabanlı) ✓ · `npm run build` → başarılı, `DiscoverPage` kendi lazy chunk'ında (19.29 KB, gzip 6.58 KB) ✓ · Vite dev sunucusunda 9 yeni/değişen modül + `/kesfet` rotası tek tek istendi, hepsi 200 ✓ · **gerçek backend'e karşı uçtan uca (curl, kitap tarafı):** `catalog/search?type=book&q=fox` ✓, `catalog/discover?type=book&genre=fiction&sort=rating` ✓, `platform/top-rated?type=book` ✓, `platform/popular?type=book` ✓, `catalog/trending?type=book` ✓, `users/search?q=demo` (geçerli token) ✓, `library/lookup` (toplu) ✓ — hepsi TypeScript tipleriyle birebir eşleşti. **Gözlem (kod hatası değil, dış servis):** `discover?type=book&min_rating=X` (tür filtresi olmadan) Open Library'de bazen zaman aşımına uğruyor — `openlibrary.py`'nin bu durumda çok geniş `ratings_average:[X TO 5]` sorgusuna düşmesinden (F1.6'dan kalan dış servis karakteristiği); `genre` ile birlikte hızlı çalışıyor, ayrıca doğrulandı.
- **Kapanan maddeler:** BUG-08, BUG-14 (tam), REQ-2.1.3b, REQ-2.1.3c (REQ-2.1.3a kısmi — detay sayfası F3.3'ü bekliyor)
- **Commit:** `dcffa45`
- **Notlar / sorunlar:** Tarayıcı aracı hâlâ yok — arama kutusu/sekme geçişleri/filtre panelinin/sonsuz kaydırmanın gerçek görsel-etkileşimli doğrulaması yapılamadı, yalnızca kod incelemesi + HTTP/modül seviyesi + gerçek backend'e karşı curl ile doğrulandı. Film tarafının canlı doğrulaması hâlâ U2'yi (TMDB anahtarı) bekliyor.
- **Sonraki adım:** F3.3 — İçerik detay sayfası

### [2026-09-27] F3.1 — İçerik bileşenleri ve yardımcılar — ✅

- **Yapılanlar:**
  - `utils/format.ts`: `relativeTime` (Intl.RelativeTimeFormat('tr'); <45 sn "az önce", <60 dk dakika, <24 sa saat, <7 gün gün, ≤30 gün hafta, sonrası `formatDate` ile mutlak tarih), `formatDate`, `formatRuntime` (150→"2 sa 30 dk"), `formatPages`, `formatRating`, `formatCount` (1234→"1,2 B", milyon→"M", tr-TR virgüllü ondalık).
  - `utils/content.ts`: `typeLabel`/`contentPath`/`contentKey`; `statusLabel`/`statusOptions` — planın §4.2 durum-etiketi tablosuyla birebir (film/dizi ortak: İzledim/İzliyorum/İzleyeceğim/Yarım bıraktım; kitap ayrı: Okudum/Okuyorum/Okuyacağım/Yarım bıraktım). `LibraryStatus` tipi için ayrı bir yerel tanım YAPILMADI, `types/index.ts`'teki şema kaynaklı olan yeniden kullanıldı (iki farklı dosyada aynı adla iki ayrı tip tanımı olmasın diye).
  - `types/index.ts`: `ContentSummary`, `ContentDetail`, `LibraryStatus`, `EntryOut`, `EntryUpdateIn`, `ContentState`, `LookupEntryOut`, `Review*`, `List*` şema tipleri eklendi.
  - `api/library.ts` (ham): `upsertEntryRequest`/`deleteEntryRequest`/`getContentStateRequest`/`lookupLibraryRequest`/`getUserLibraryRequest`/`create|update|deleteReviewRequest` (§5.4 tam kapsam). `api/lists.ts` (ham + composable): tüm CRUD + sıralama + `useMyLists`/`useAddListItem`/`useRemoveListItem`/`useCreateList` (yalnız `AddToListMenu`'nün gerçekten ihtiyaç duyduğu composable'lar; `getListDetailRequest` gibi F3.7'nin (ListPage) kullanacağı fonksiyonlar ham bırakıldı, composable'ı o zaman eklenecek).
  - `composables/useContentActions.ts`: `status`/`rating`/`isFavorite` computed'ları + `setStatus`/`setRating`/`toggleFavorite` — hepsi "aynı değere tıklayınca temizler" mantığını (StarRating ve LibraryButtons'ın ikisi için de) tek yerden uyguluyor. İyimser güncelleme yerel bir `overlay` ref'iyle yapılıyor (TanStack sorgu önbelleğini doğrudan yamalamak yerine) — çünkü bu adımda `content-state` sorgusunu dolduran gerçek bir tüketici sayfa (ContentDetailPage, F3.3) henüz yok; F3.3'te gerçek `useContentState` composable'ı eklenince bu iyimser katman TanStack cache'iyle entegre edilmesi gerekip gerekmediği yeniden değerlendirilecek. Hata olursa `overlay` eski değerine geri alınır + toast; misafirse `/giris?redirect=`'e yönlendirir (§3.6.5). Başarıda `content-state`/`library`(ben)/`user-summary`(ben)/`recs` sorguları geçersiz kılınır (§3.6.2'nin "geçersiz kılma örnekleri" satırı).
  - 10 bileşen (`components/content/`): **StarRating** (5 yıldız × 2 yarım = 1-10; her yarım ayrı görünmez buton; hover önizleme; `role="slider"` + `aria-valuemin/max/now/text` + ←/→/Home/End/Delete; salt okunur modda hiç buton/slider render etmez). **RatingDisplay** (★×5 + "x/10"). **RatingHistogram** (10 çubuk, saf CSS, `Math.max` ile ölçekleme). **GenreChips** (saf sunum — etiket listesini olduğu gibi çip yapar, tür anahtarı→etiket çözümlemesi bilerek bileşene sokulmadı, çağıran sayfa zaten elindeki veriyle çözüyor). **PosterCard** (sabit en-boy `aspect-[2/3]`, kırık/eksik posterde `ImageOff` ikonlu düşen görünüm — BaseAvatar'ın BUG-07 desenini içerik kartlarına taşıdı; genişlik `size` prop'undan, ContentGrid `!w-full` ile ezip grid hücresini dolduruyor). **ContentGrid**/**ContentRow** (duyarlı ızgara 2→6 sütun / yatay kaydırmalı şerit + ok butonları; ikisi de yükleniyor/boş/veri durumlarını ayrı ayrı ele alıyor). **LibraryButtons**/**FavoriteButton** (saf sunum — durumu prop olarak alır, `update:status`/`update:modelValue` yayar; `useContentActions`'a kablolamak sayfanın işi). **AddToListMenu** (`useMyLists` ile listelerini + `contains` bayrağını çeker, tıkla-ekle/çıkar, satır içi "+ Yeni liste" formu; misafirse girişe yönlendirir). Hepsi `/_ui` vitrinine eklendi (sahte 3 içerikle: film/dizi/kitap birer örnek, kasıtlı `poster_url:null` ile PosterCard'ın düşen görünümünü de gösteriyor).
  - Bileşenler arasında **genişlik çakışması** fark edildi ve çözüldü: `PosterCard`'ın kendi `size`→genişlik varsayılanı `ContentRow`'da (yatay şerit, sabit genişlik gerekiyor) doğru ama `ContentGrid`'de (hücreyi doldurması gerekiyor) yanlıştı; Vue'nun class-birleştirme davranışından yararlanılarak `ContentGrid` `class="!w-full"` ile (Tailwind önemli-değiştirici) bunu eziyor.
- **Değişen dosyalar:** `frontend/src/utils/{format,format.spec,content,content.spec}.ts` (yeni), `frontend/src/types/index.ts`, `frontend/src/api/{library,lists}.ts` (yeni), `frontend/src/composables/useContentActions.ts` (yeni), `frontend/src/components/content/{StarRating,StarRating.spec,RatingDisplay,RatingHistogram,GenreChips,PosterCard,ContentGrid,ContentRow,LibraryButtons,FavoriteButton,AddToListMenu}.{vue,ts}` (yeni, 11 dosya), `frontend/src/pages/UiShowcasePage.vue`.
- **Doğrulama:** `npm run lint` → temiz ✓ · `npm run type-check` → temiz ✓ (bir tur `EntryUpdateIn`'in `is_favorite: boolean|null` ile yerel `OptimisticState.is_favorite: boolean` tipi çakıştı, alan bazlı açık birleştirmeyle düzeltildi) · `npm run test:unit -- run` → **60 passed** (28 yeni: format 12, content 9, StarRating 7 — bkz. tam sayılar dosyalarda) ✓ · `npm run build` → başarılı, ana paket boyutu **değişmedi** (gzip 70.20 KB — yeni bileşenler yalnız DEV-only `/_ui`'den içe aktarılıyor, `import.meta.env.DEV` derleme zamanında `false`'a sabitlenip prod dalı elendiği için ana pakete girmiyor) ✓ · Vite dev sunucusu üzerinden 16 yeni/değişen modül tek tek istendi, hepsi 200 ✓ · **gerçek backend'e karşı uçtan uca (curl, yeni test kullanıcısı `f31test` ile):** `PUT /library/book/OL45804W` (status+rating)→200, `GET .../state`→`ContentState` şeması birebir eşleşti (`content_id`/`platform.{average,count,distribution}`/`me.entry.*`/`me.review_id`/`friends`), favori aç→200, `status:null` gönderip temizleme→200 (kaldırma mantığı doğrulandı); film uçları U2 (TMDB anahtarı) beklediği için `TMDB_NOT_CONFIGURED` 503 verdi (beklenen, kitapla devam edildi) ✓; liste akışı: oluştur→201, `GET /lists/mine?type&external_id`→`contains:false`, öğe ekle→201, tekrar sorgula→`contains:true` + `cover_urls` dolu, öğe sil→204, tekrar sorgula→`contains:false`, listeyi sil→204 ✓. Test kullanıcısı `DELETE /users/me` ile temizlendi. **Not:** Bir ara adımda Türkçe "ı" harfi içeren bir liste başlığı curl/bash kodlama sorunu yüzünden 400 döndürdü — gerçek tarayıcıda `fetch`+`JSON.stringify` UTF-8'i doğru kodladığı için bu yalnızca test betiğinin sorunuydu, ASCII başlıkla tekrarlanınca (ve ayrıca gerçek Türkçe karakterli kayıt/onboarding akışları F2.4'te zaten başarıyla test edildiği için) uygulama kodunda bir düzeltme gerekmedi.
- **Kapanan maddeler:** BUG-20 (tam)
- **Commit:** `77c4b3d`
- **Notlar / sorunlar:** Tarayıcı aracı hâlâ yok — `/_ui`'deki yeni bölümün görsel/klavye/hover doğrulaması yalnızca kod incelemesi + yukarıdaki testlerle yapıldı. `LibraryButtons`/`FavoriteButton`/`AddToListMenu`'nün gerçek bir sayfaya (ContentDetailPage) kablolanması F3.3'e kalıyor; bu adımda yalnızca bileşenlerin kendisi ve `/_ui`'deki yerel/gerçek demo'ları doğrulandı.
- **Sonraki adım:** F3.2 — Keşfet sayfası

### [2026-09-26] F2.5 — 🏁 Faz 2 kapanışı — ✅

- **Yapılanlar:** Tüm doğrulama komutları yeniden çalıştırıldı (yalnız frontend değil, dokunulmamış olsa da backend de dahil — genel proje sağlığını teyit için). Kullanıcıya Faz 2 özeti + iki terminalle çalıştırma yönergesi + denenebilecekler listesi sunuldu, iki karar soruldu: (1) `v2`'yi push et — kullanıcı **evet** dedi; (2) sıradaki adım — kullanıcı **Faz 3'e geç** dedi. `git push origin v2` çalıştırıldı.
- **Ekran görüntüleri:** Plan "mümkünse" diyor — bu oturumda (tüm Faz 2 boyunca) tarayıcı aracı hiç mevcut olmadığı için `/_ui` ve giriş sayfasının ekran görüntüsü alınamadı, `docs/ekran-goruntuleri/` oluşturulmadı. Bunun yerine tüm doğrulama kod incelemesi + `npm run lint/type-check/test/build` + gerçek backend'e karşı curl ile yapıldı (F2.3/F2.4 günlüklerinde ayrıntılı).
- **Değişen dosyalar:** Yalnızca `proje-ilerleme-durumu.md` (bu kapanış özeti + bağlam özeti Faz 2 için kısaltıldı, F1 kapanışında yapıldığı gibi).
- **Doğrulama:** Frontend: `npm run lint` → temiz ✓ · `npm run type-check` → temiz ✓ · `npm run test:unit -- run` → **32 passed** ✓ · `npm run build` → başarılı, ana JS gzip 70.20 KB ✓. Backend (dokunulmadı ama kapanışta yeniden koşuldu): `pytest` → 69 passed ✓ · `ruff check` → "All checks passed!" ✓ · `ruff format --check` → 79 dosya zaten biçimli ✓.
- **Kapanan maddeler:** —
- **Commit:** `55a8ac1` (bu özet notu; push işleminin kendisi ayrı bir commit üretmez)
- **Kullanıcı kararları:** Push = evet (uygulandı, `origin/v2` → `55a8ac1`). Sıradaki adım = Faz 3'e geç.
- **Notlar / sorunlar:** U1 (Gmail şifresi iptali) ve U2 (TMDB anahtarı yenileme) hâlâ ⬜ — hatırlatıldı, kodu ilerletmeyi engellemiyor.
- **Sonraki adım:** F3.1 — İçerik bileşenleri ve yardımcılar

### [2026-09-26] F2.4 — Kimlik sayfaları ve onboarding — ✅

- **Yapılanlar:**
  - `utils/validation.ts`: `validateUsername` (backend `users/validation.py` ile birebir aynı `^[a-z][a-z0-9_.]{2,29}$` regex + aynı ayrılmış ad listesi, büyük harfleri backend gibi sessizce küçültüyor), `validateEmail`, `validatePasswordStrength` (backend `auth/schemas.py` ile birebir aynı kural: ≥8 karakter + en az bir harf + bir rakam), `validatePasswordsMatch`, ayrıca yalnız istemci tarafı `passwordStrength()` (zayıf/orta/güçlü göstergesi). 16 test (`validation.spec.ts`).
  - `api/catalog.ts` (yeni, minimal): yalnız `getGenresRequest`/`useGenres` — F3.1'in geri kalan katalog fonksiyonlarını ekleyeceği dosyanın başlangıcı, şimdiden tüm katalog uçlarını yazmadım (erken/spekülatif kapsam genişletmesi olmasın diye).
  - `components/ui/OtpInput.vue`: 6 kutulu doğrulama kodu girişi — tek hane girilince otomatik ileri, Backspace'te otomatik geri, yapıştırmada tüm kutulara dağıtma, `defineModel`.
  - **Kusur düzeltmesi (BaseInput):** `@blur`/`@keyup`/`@keydown` gibi dışarıdan verilen dinleyiciler Vue'nun varsayılan `$attrs` devralma davranışıyla bileşenin dış `<div>`'ine bağlanıyordu, gerçek `<input>`'a değil — yani hiçbir zaman tetiklenmiyordu. `defineOptions({ inheritAttrs: false })` + `v-bind="$attrs"` iç `<input>`'a taşındı. LoginPage'in Caps Lock uyarısı ve alan-dokunma (blur) takibini gerçekten çalıştırmaya çalışırken fark edildi; geriye dönük uyumlu (var olan hiçbir kullanım ekstra attr geçirmiyordu, davranışları değişmedi).
  - `stores/auth.ts` küçük iyileştirme: `login`/`register` artık `TokenOut.user`'ı doğrudan kullanıyor, ayrı bir `fetchMe()` round-trip'i yapmıyor (gereksiz ağ isteği kaldırıldı).
  - **`LoginPage.vue`** (`/giris`): `login` (e-posta veya kullanıcı adı) + şifre (göster/gizle BaseInput'ta hazır), Caps Lock uyarısı, hata formun üstünde, `route.query.redirect`'i okuyup girişten sonra oraya yönlendiriyor (F2.3'te router guard'ın bıraktığı "geri dönüş" ucu artık kapandı).
  - **`RegisterPage.vue`** (`/kayit`): kullanıcı adı (canlı ipucu + doğrulama), e-posta, şifre (canlı güç göstergesi), şifre tekrarı; `EMAIL_TAKEN`/`USERNAME_TAKEN` 409'ları genel banner yerine ilgili alanın altına yazılıyor (§3.6.4 "alan bazlı sunucu hataları"); başarıda otomatik giriş zaten `authStore.register`'ın içinde olduğu için ekstra adım gerekmiyor, doğrudan `/hosgeldin`'e yönleniyor.
  - **`ForgotPasswordPage.vue`** (`/sifremi-unuttum`): 3 adım — (1) e-posta → her durumda aynı nötr mesaj ("Eğer bu e-posta kayıtlıysa…"), (2) `OtpInput` ile 6 haneli kod → doğrula, "kodu tekrar gönder" 60 sn geri sayımlı, (3) yeni şifre + tekrar → onayla → toast + `/giris`.
  - **`OnboardingPage.vue`** (`/hosgeldin`): (1) film/dizi türleri ≥3 çip (`/catalog/genres?type=movie` + `?type=tv` birleştirilip anahtara göre tekilleştiriliyor — tek tür hem filme hem diziye ait olabiliyor), (2) kitap türleri ≥2 çip + "Atla", (3) `/users/suggestions` takip önerileri + yerinde takip et/bırak butonu → `PATCH /users/me {favorite_genres}` (seçilen tüm türlerin birleşimi) → `/`. Her adımda yükleniyor/hata/veri durumları (`BaseSkeleton`/`ErrorState`) ele alındı.
  - Login/Register, mağaza yan etkisi (token/`me` güncelleme) gerektirdiği için TanStack `useMutation` yerine doğrudan `authStore.login/register` çağrısı + yerel `submitting`/`formError` ref'leriyle yazıldı; şifre sıfırlama adımlarının mağaza yan etkisi olmadığından F2.3'te zaten yazılmış `api/auth.ts` composable'ları (`useRequestPasswordReset` vb.) doğrudan kullanıldı. TanStack Vue Query paketinin kendi tip tanımlarından (`ToRefs<...>`) doğrulandı: `useMutation`/`useQuery`'nin döndürdüğü her alan (`isPending`, `data`, `error`…) gerçek bir `Ref`'tir — hem `<script setup>` hem `<template>` içinde `.value` gerekir (kütüphanenin kendi örnekleri de böyle).
  - `router/index.ts`: `/giris`, `/kayit`, `/sifremi-unuttum`, `/hosgeldin` artık `ComingSoonPage` yerine gerçek sayfalara işaret ediyor.
- **Değişen dosyalar:** `frontend/src/utils/{validation.ts,validation.spec.ts}` (yeni), `frontend/src/api/catalog.ts` (yeni), `frontend/src/components/ui/OtpInput.vue` (yeni), `frontend/src/components/ui/BaseInput.vue` (attrs düzeltmesi), `frontend/src/stores/auth.ts`, `frontend/src/types/index.ts` (`GenreOut` eklendi), `frontend/src/pages/{LoginPage,RegisterPage,ForgotPasswordPage,OnboardingPage}.vue` (yeni), `frontend/src/router/index.ts`.
- **Doğrulama:** `npm run lint` → temiz ✓ · `npm run type-check` → temiz ✓ · `npm run test:unit -- run` → **32 passed** (16 yeni validation testi) ✓ · `npm run build` → başarılı, her yeni sayfa kendi lazy chunk'ında (LoginPage 2.27 KB, RegisterPage 3.54 KB, ForgotPasswordPage 5.84 KB, OnboardingPage 5.96 KB gzip öncesi; ana chunk gzip 70.20 KB) ✓ · Vite dev sunucusu üzerinden tüm yeni modüller (4 sayfa + OtpInput + catalog.ts + validation.ts) tek tek istendi, hepsi 200 ✓ · **gerçek backend'e karşı uçtan uca (curl):** kayıt→201+token, aynı e-postayla ikinci kayıt→409 `EMAIL_TAKEN`, doğru girişte 200, yanlış şifrede 401 `INVALID_CREDENTIALS`; şifre sıfırlama isteği→202 nötr mesaj, kod `backend/uvicorn_err.log`'da bulundu (SMTP yok, dev-modu logu — beklenen), yanlış kodda 400 `INVALID_CODE`, doğru kodda `{"valid":true}`, yeni şifre onayı→200, **yeni şifreyle giriş başarılı, eski şifreyle giriş artık 401** (`token_version` artışı doğru çalışıyor); `/catalog/genres?type=movie|tv|book` üçü de doğru `{key,label}[]`; girişli `/users/suggestions` demo kullanıcılarını döndürdü; `PATCH /users/me {favorite_genres}` kalıcı kaydetti. Test kullanıcısı (`f24test`) sonunda `DELETE /users/me` ile temizlendi — demo verisinde kalıntı yok. **Not:** Bu oturumda hâlâ tarayıcı aracı yok; sayfaların görsel düzeni, klavye gezinme ve gerçek form doldurma deneyimi yalnızca kod incelemesi + yukarıdaki HTTP/modül seviyesi doğrulamayla teyit edildi, tarayıcıda elle denenmedi.
- **Kapanan maddeler:** REQ-2.1.1a, REQ-2.1.1b, REQ-2.1.1c, REQ-2.1.1d, BUG-10
- **Commit:** `031befa`
- **Notlar / sorunlar:** OnboardingPage'in 3. adımında (takip önerileri) paylaşılan bir `FollowButton` bileşeni kullanılmadı, sayfaya özel küçük bir takip et/bırak butonu yazıldı — F3.6 (ProfilePage) gerçek, paylaşılan `FollowButton`'ı ihtiyaç duyduğunda oluşturacak (erken soyutlama yok).
- **Sonraki adım:** F2.5 — 🏁 Faz 2 kapanışı

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
