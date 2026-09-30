# KFDU v2 — Proje İlerleme Durumu

> Plan: [`proje-plani.md`](proje-plani.md) · Bu dosya **her adımdan sonra** güncellenir (plan §0.2, madde 7).
> Son güncelleme: **2026-09-30** — F3.10 tamamlandı — 🏁 **Faz 3 kapandı** (ilk kullanılabilir v2). `v2` → `main` birleştirildi ve push edildi (kullanıcı onayıyla).

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
| Proje durumu | 🏁 Faz 3 tamamlandı, `main`e birleştirildi ve push edildi |
| Aktif faz | Faz 4 — Çağ Atlatma Paketi (henüz başlamadı) |
| Sıradaki adım | **F4.1** |
| Çalışma dalı | `v2` (`main` ile senkron, `5701059`) |
| Son commit | `5701059` (docs(F3.10): Faz 3 kapanışı) |
| Backend | v2 — modüler FastAPI (Faz 1'de sıfırdan kuruldu), kitap tarafı çalışıyor, film tarafı U2'yi bekliyor |
| Frontend | v2 — Vue 3 SFC + Router + Pinia + TanStack Query (Faz 2'de sıfırdan kuruldu) |
| Açık engeller | Yok — U1/U2 (👤 Kararlar tablosuna bkz.) kullanıcı kararıyla proje sonuna ertelendi (D-23), kod ilerlemesini engellemiyor |

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
- **Faz 3 🟨 devam ediyor (F3.1–F3.6 tamamlandı, 2026-09-27):** İçerik bileşenleri (`StarRating`/`RatingDisplay`/`RatingHistogram`/`GenreChips`/`PosterCard`/`ContentGrid`/`ContentRow`/`LibraryButtons`/`FavoriteButton`/`AddToListMenu`/`CastRow`/`WatchProviders`/`ActivityCard`/`LikeButton`/`CommentThread` — hepsi `components/content/`), kullanıcı bileşenleri (`UserCard`/`FollowButton`/`ProfileHeader`/`EditProfileModal`/`UserListModal` — `components/users/`), liste bileşenleri (`ListCard`/`CreateListModal` — `components/lists/`), `composables/{useContentActions,useFollowToggle}.ts`, `utils/{content,format,activity}.ts`. API katmanı tamamlandı: `api/catalog.ts` (genres/search/discover/trending/collections/detail/similar), `api/library.ts` (entry CRUD/state/lookup/review CRUD/`useContentState`), `api/lists.ts` (tam CRUD), `api/social.ts` (feed/reviews/comments/likes/user-activities/user-reviews), `api/stats.ts` (top-rated/popular/profile-summary), `api/users.ts` (profile/followers/following/avatar). Sayfalar: **DiscoverPage** `/kesfet` (arama+filtre+vitrin, Film/Kitap/Kullanıcı), **ContentDetailPage** `/film|kitap/:id` (hero+puan+eylem çubuğu+incelemeler+benzer), **ReviewPage** `/inceleme/:id`, **FeedPage** `/` (Takip Ettiklerim/Herkes, gerçek sonsuz kaydırma), **ProfilePage** `/u/:username` (6 sekme: Aktiviteler/Kütüphane/Puanlar/İncelemeler/Listeler/Favoriler, `EditProfileModal` avatar yükleme dahil). 68 frontend testi yeşil.
  - **Mimari desen:** Çoğu bileşen "saf sunum" (durumu prop olarak alır, olay yayar) — `useContentActions`/`useFollowToggle` composable'ları gerçek API çağrılarını+iyimser güncellemeyi üstleniyor. İki composable de **ikinci gerçek ihtiyaç anında** (erken değil) ortak koda çıkarıldı. `useFeed`'in `useLike()`'ı istisna: plan açıkça "akış önbelleğindeki kartı günceller" dediği için TEK yerde gerçek TanStack `setQueriesData` tabanlı önbellek-seviyeli iyimser güncelleme var (diğer her yerde yerel `overlay`/`pendingComments` deseni kullanıldı).
  - **D-21/D-22 (backend düzeltmeleri, F3.3'te canlı testte bulundu):** (1) `core/http.py` dış servisten gelen 404'ü artık `not_found()` ile temiz 404'e çeviriyor (önceden sarmalanmadan 500 oluyordu). (2) `social/service.py`'deki `is_edited` hesaplaması `TimestampMixin`'in iki ayrı `datetime.now(UTC)` çağrısı yüzünden her yeni incelemede yanlışlıkla `true` çıkıyordu; 1 saniyelik toleransa çevrildi + regresyon testi eklendi.
  - **F3.4→F3.5 arası düzeltme:** `CommentThread`'in `compact` modu başlangıçta girdi kutusunu gizliyordu; F3.5'te planın "son 2 yorum + giriş + 'Tüm yorumlar'" ifadesiyle çeliştiği fark edilip girdi kutusu compact'te de gösterilecek şekilde düzeltildi, `expand` olayı eklendi.
  - **Bilinen sınırlamalar:** `WatchProviders` yalnız düz metin rozetler (gerçek logo yok, `Providers` şeması yalnız isim taşıyor). Kullanıcı aramasında/önerilerinde `is_following` başlangıçta bilinmiyor (yalnız `ProfileOut`/`PublicUserWithFollowOut` taşıyor); tıklanınca oturum için yerel işaretleniyor. TMDB'ye bağlı vitrin/detay/arama hâlâ U2'yi bekliyor, kitap tarafı gerçek backend'e karşı her adımda curl ile uçtan uca doğrulandı. `FilterPanel` gerçek bir bottom-sheet değil, her ekran boyutunda aynı satır içi panel. Tarayıcı aracı bu oturumda hiç yok — tüm doğrulama kod incelemesi + lint/type-check/test/build + gerçek backend'e karşı curl ile yapıldı.
- **F3.7 tamamlandı (2026-09-29):** `api/lists.ts` genişletildi: `useListDetail` (`['lists','detail',id]`, 30 sn — diğer mutasyonların zaten kullandığı geniş `['lists']` invalidate'i bu anahtarı da otomatik yakalıyor, ayrıca özel bir invalidate gerekmedi), `useUpdateList`/`useDeleteList`/`useUpdateListItemNote`/`useReorderListItems`. `CreateListModal` → `ListFormModal` olarak yeniden adlandırıldı ve **hem oluşturma hem düzenleme** modunu tek bileşende topluyor (`list?` prop'u verilirse düzenleme — plan tek bir "ListFormModal" adı verdiği için birleştirildi; `ProfilePage`'in "Yeni Liste" akışı davranış değişmeden bu bileşene taşındı). `ListPage.vue` (`/liste/:id`, route-level `props` ile `id` enjekte ediliyor): 4'lü kapak kolajı başlık, sahip bağlantısı, Herkese Açık/Gizli rozeti, açıklama, Paylaş (clipboard); sahibiyse Düzenle (`ListFormModal`), Sil (`useConfirm`, onay → kendi profiline döner), **sıralama modu** (sunucu sırasını yerel bir taslağa kopyalayıp ↑/↓ ile değiştirme, "Sırayı kaydet" ancak o an `PUT /lists/{id}/order` çağırır, "Vazgeç" taslağı atar — sahte/iyimser güncelleme yok, sade invalidate+refetch yeterli görüldü); öğe ızgarasında her kart için not ekle/düzenle (satır içi textarea, tarayıcı `prompt()` kullanılmadı) ve kaldır. Gizli listede sahip olmayan/anonim erişim zaten backend'de (`get_list_detail`) 404 döndürüyordu — frontend `is404` (`ApiError.status===404`) deseni diğer sayfalarla birebir aynı şekilde uygulandı.
  - **Kusur düzeltmesi (kendi kodumda, commit'ten önce yakalandı):** İlk taslakta `PosterCard` grid hücresine `ContentGrid`'in yaptığı gibi `!w-full` ile esnetilmemişti — `ContentGrid.vue` incelenince bu deseni (+`xl:grid-cols-6` kırılım noktasını) kopyalamadığım fark edildi, düzeltildi.
  - **Gerçek backend'e karşı uçtan uca (httpx betiği, iki test kullanıcısıyla, kitap tarafı):** liste oluştur → 2 öğe ekle (201, aynı öğeyi tekrar eklemek 200 idempotent) → detay (sahip/başka kullanıcı/anonim, hepsi herkese açıkken 200) → not güncelle → `PUT /order` ile sırayı ters çevir → detayda yeni sıra doğrulandı → başkası düzenlemeye/öğe silmeye çalışınca 403 → sahibi öğe kaldırır (`item_count` düşüyor) → sahibi başlığı değiştirir + gizliye çevirir → artık başkası/anonim 404, sahibi hâlâ 200 → `/users/{u}/lists` başkasına gizli listeyi göstermiyor ama sahibine gösteriyor → sahibi siler (204) → tekrar 404. 22/22 kontrol geçti, test kullanıcıları temizlendi.
  - **Bilinçli kapsam sınırlaması:** `/_ui` vitrinine liste bileşenleri eklenmedi (F3.6'da da aynı karar alınmıştı — gerçek bir liste ID'si gerektiriyor, sahte veriyle yalnızca iskelet görünürdü); bunun yerine `ProfilePage`'in Listeler sekmesi + gerçek backend doğrulaması kullanıldı.
  - **Süreklilik notu:** Önceki oturum kullanım limitine takılmıştı; bu oturum önce yarım kalan F3.6 ilerleme-durumu commit'ini tamamladı (`d0fc66f`), sonra F3.7'ye buradan devam etti.
- **F3.8 tamamlandı (2026-09-29):** `SettingsPage.vue` (`/ayarlar`): **Profil** (paylaşılan `ProfileForm`), **Hesap** (e-posta değiştir — mevcut şifreyle, `INVALID_PASSWORD`/`EMAIL_TAKEN` alan hatası olarak gösteriliyor), **Güvenlik** (şifre değiştir — başarıda `TokenOut`'tan gelen yeni token+kullanıcı `auth` store'a yazılıyor, eski token'lar `logout-all` deseniyle zaten geçersiz; "Tüm cihazlardan çıkış yap" — kendi oturumunu da düşürdüğü için `useConfirm` ile açıkça uyarıp başarıda yerel `logout()`+`/kesfet`), **Görünüm** (`useTheme`, zaten var olan header'daki tema seçiciyle aynı desen), **Tercihler** (favori türler — Onboarding'deki AYNI akış), **Tehlikeli bölge** (hesabı sil — şifre + tam "SİL" yazma onayı, ikisi de dolmadan buton `disabled`).
  - **Gerçek hata düzeltmesi (kod incelemesinde bulundu, bu adımdan önce de vardı):** `EditProfileModal`'ın kaydet/avatar-kaldır işlemleri `useUpdateMe`/`useRemoveAvatar` çağırıyordu ama **`auth` store'daki `me`'yi hiç güncellemiyordu** — yalnız kullanılmayan bir TanStack `['user','me']` sorgusunu geçersiz kılıyordu (o sorgu hiçbir yerde tüketilmiyor). Sonuç: profil düzenlendikten sonra `AppHeader`/`AppBottomNav`'daki avatar/ad/kullanıcı adı bayatlıyordu — kullanıcı adı değiştirilirse alt gezinmedeki "Profilim" bağlantısı bile artık geçersiz eski kullanıcı adına gidiyordu (sayfa yenilenene kadar). F3.8'in Hesap/Güvenlik/Tercihler bölümleri AYNI sorunu daha da görünür hale getireceği için kökten düzeltildi: `EditProfileModal`'ın içeriği paylaşılan `ProfileForm.vue`'ya çıkarıldı (hem modalde hem Ayarlar'da kullanılıyor) ve artık her başarılı mutasyondan sonra `auth.setMe(...)` çağırıyor; `SettingsPage`'in e-posta/şifre/tercih mutasyonları da aynı deseni izliyor. `api/users.ts`/`api/lists.ts` gibi saf API katmanına DEĞİL, çağıran bileşene eklendi — `stores/auth.ts` zaten `api/users.ts`'den `fetchMeRequest` import ediyor, tersi yönde bir import döngüsel bağımlılık yaratırdı.
  - **Yeniden kullanım:** `components/users/GenreChipPicker.vue` (yeni, saf sunum) — `OnboardingPage`'in İKİ AYRI yerde birebir kopyalanmış tür-çipi düğme bloğu artık bunu kullanıyor (davranış değişmedi), `SettingsPage`'in Tercihler bölümü de aynı bileşeni üçüncü/dördüncü kullanım yeri olarak paylaşıyor.
  - `stores/auth.ts`: `setToken` dışa açıldı (yalnız store içinden çağrılabiliyordu) — şifre değiştirmenin döndürdüğü yeni token'ı yazmak için gerekliydi.
  - `api/users.ts`: `useChangeEmail`, `useDeleteAccount` eklendi (`changeEmailRequest`/`deleteAccountRequest` zaten vardı, yalnız `use*` sarmalayıcıları eksikti). `api/auth.ts`'teki `useChangePassword`/`useLogoutAllDevices` ZATEN yazılmıştı (muhtemelen F1/F2'de ileriye dönük), bu adımda yalnız tüketildi.
  - **Bilinçli plan sapması:** Plan "Hesap" bölümünde e-posta VE kullanıcı adı değişikliğini birlikte listeliyor, ama backend `PATCH /users/me` kullanıcı adını `display_name`/`bio` ile TEK bir uçta topluyor ve bu zaten `ProfileForm`'da (Profil bölümü) çalışıyor. Kullanıcı adını Hesap bölümünde İKİNCİ kez düzenlenebilir yapmak aynı sayfada iki ayrı "kullanıcı adı" alanı göstererek kafa karıştırırdı; bu yüzden Hesap bölümü yalnız e-postaya odaklandı, kullanıcı adı Profil'de kaldı.
  - **Ödev kapsamı notu:** F3.8 Ek A'daki hiçbir REQ/BUG maddesini kapatmıyor — Ayarlar sayfası tamamen v2'nin kendi "ilk kullanılabilir sürüm" hedefinin bir parçası (proje-plani §3.8), ödevin zorunlu gereksinimi değil.
- **F3.9 tamamlandı (2026-09-30):** `NotFoundPage.vue` (`/:pathMatch(.*)*`, eğlenceli boş durum + Akış/Keşfet bağlantıları), `ErrorBoundary.vue` (`onErrorCaptured` → "Sayfayı yenile", rota değişince sıfırlanır, 3 birim testiyle doğrulandı), `OfflineBanner.vue` (`useOnline`), `useKeyboardShortcuts.ts` + `ShortcutsHelpModal.vue` (`/` arama — `useSearchFocus.ts`'in tek-seferlik bayrağıyla sayfalar arası odak yarışı olmadan çözüldü; `g f`/`g k` akış/keşfet; `?` yardım; düzenlenebilir alanlarda ve açık modalde devre dışı — 4 birim testiyle doğrulandı), hepsi `AppShell`'e bağlandı. Tüm `<img>` etiketlerine `loading="lazy"`+`decoding="async"` eklendi (denetimle 7 eksik yer bulundu). **BUG-07 tamamen kapatıldı:** yeni `SafeImage.vue` (saf sunum, kırık/eksik görselde `ImageOff` simgesi) `ActivityCard`/`ListCard`/`ListPage`/`ContentDetailPage`/`ReviewPage`'e uygulandı; `CastRow` kendi baş-harf düşen deseniyle `@error` yakalamaya genişletildi. `git grep -nE "\balert\(|\bconfirm\(|\bprompt\("` → yalnız `useConfirm` tanımları/kullanımları (zaten temizdi).
  - **Lighthouse (mobil, 360×800) erişilebilirlik — gerçek ölçüm, önce/sonra:** Keşfet **85→96**, İçerik detayı (kitap) **88→97**, Akış (kimlik doğrulamalı Puppeteer betiğiyle) **87→96**. Bulunan ve düzeltilen gerçek sorunlar:
    1. **Karanlık mod kontrast açığı (sistemik):** `text-brand-600` (#6a47ff) hem düz `--bg` (#0e1016, 3.58:1) hem `bg-brand-500/15` rozet zemininde (3.1:1) 4.5:1 eşiğinin altındaydı — elle hesapladığım `--muted` kontrastı doğruydu ama `brand-600`'ü hiç kontrol etmemiştim. Kök nedeni çözmek için `--fg`/`--muted` ile aynı desende tema-duyarlı `--link` token'ı eklendi (`main.css`: ışık modda brand-600, karanlık modda brand-400 — 5.83:1) ve **20 dosyadaki tüm `text-brand-600` kullanımı** `text-link`'e taşındı (tek tek `dark:` sınıfı eklemek yerine tek token'dan yönetim).
    2. **`BaseButton` birincil varyantı + header logosu:** beyaz metin `bg-brand-500` üstünde 4.34:1 idi (4.5:1 gerekli) — ikisi de `bg-brand-600`'e çekildi (5.31:1).
    3. **Etiketsiz form kontrolleri:** `FilterPanel`'in puan kaydırıcısı (`<label for>` eksikti) ve `BaseSelect`'in `label` verilmeden kullanıldığı 2 yer (`ReviewList` sıralama, `ProfilePage` kütüphane sıralaması) — `BaseSelect`'e `ariaLabel` prop'u eklendi, çağıranlar güncellendi.
    4. **Avatar-yalnız profil bağlantıları:** `ActivityCard`/`CommentThread`/`ReviewItem`/`UserCard`/`ReviewPage`'deki avatarı saran çıplak `RouterLink`ler, kullanıcının avatarı yoksa (baş harf düşen `aria-hidden` olduğu için) erişilebilir ada sahip değildi — hepsine `:aria-label="\`${ad} profili\`"` eklendi.
    5. **`LikeButton`:** `aria-label` yalnız "Beğen"/"Beğeniyi geri al" diyordu, görünür beğeni SAYISINI içermiyordu (WCAG 2.5.3 Label in Name ihlali) — sayaç etikete eklendi.
    - **Bilinçli/kalıcı sınırlamalar (kalan iki bulgu):** (a) `aria-prohibited-attr` — Vue DevTools'un kendi enjekte ettiği `vue-devtools__anchor-btn` düğmesi, yalnızca `import.meta.env.DEV`'de var, üretim derlemesinde hiç yok; uygulama koduyla ilgisiz, düzeltilecek bir şey yok. (b) `label-content-name-mismatch` — header'daki kullanıcı menüsü düğmesinde avatarı olmayan kullanıcının baş harfleri (`aria-hidden` olsa da GÖRSEL olarak hâlâ ekranda) `aria-label="Kullanıcı menüsü"` ile birebir eşleşmiyor (yalnız sesli-komut yazılımlarını etkiler, ekran okuyucu/klavye/fare tamamen çalışıyor); dar kapsamlı, kullanıcıya özgü baş harflerin etikete dinamik eklenmesi bu adımın kapsamına orantısız görüldü, kayıt olarak bırakıldı.
  - **Yöntem notu:** Lighthouse CLI + `puppeteer-core` (Akış'ı kimlik doğrulamalı test etmek için — `localStorage`'a token yazılıp sonra Lighthouse'un Node API'sine aynı `page` nesnesi verildi) proje bağımlılıklarına EKLENMEDİ, yalnız scratchpad'te izole bir `npm install` ile geçici olarak kuruldu ve kullanıldı. Bu, projede **ilk kez gerçek bir Chrome ile** (tarayıcı aracı değil, saf CLI/Node) ölçülen sonuç — önceki tüm fazlarda "tarayıcı aracı hiç yok" kısıtı geçerliydi, bu adımda CLI üzerinden headless Chrome ile aşıldı.
- **F3.10 tamamlandı (2026-09-30) — 🏁 Faz 3 kapandı:** Aynı `puppeteer-core` yöntemi genişletilerek gerçek, headless Chrome üzerinden **3 ayrı Node betiğiyle 360×800 mobil görünümde tam bir manuel test turu** yapıldı (plan §F3.10'un 20 maddesi) — bu, projenin FRONTEND tarafında yapılmış ilk gerçek uçtan-uca tarayıcı testi (önceki 9 faz boyunca yalnız kod incelemesi+curl vardı). Ek A izlenebilirlik matrisinin kalan 4 satırı (REQ-1.2, REQ-2.1.4f/g, REQ-3, DEBT-02) kanıtla kapatıldı.
  - **Tur 1 (tek kullanıcı, ~25 adım):** misafir→kayıt→onboarding→akış; Keşfet'te kitap arama+tür/yıl/puan filtresi; içerik detayında puan ver+kütüphane durumu+inceleme yaz+listeye ekle+yeni liste oluştur; profil 6 sekmesi; ayarlarda avatar yükle+ad değiştir+tema değiştir; tarayıcı geri/ileri+doğrudan URL yükleme. Ekran görüntüleriyle doğrulandı.
  - **Tur 2 (iki kullanıcı, tek sayfa + kimlik değiştirme deseni):** A bir kitabı puanlayıp 345 karakterlik inceleme yazdı → B takip etti → B'nin "Takip Ettiklerim" akışında A'nın aktivitesi gerçekten göründü → B beğendi (`aria-label` "Beğen · 0" → "Beğeniyi geri al · 1", F3.9'daki etiket düzeltmesi canlı doğrulandı) → B yorum yaptı → "…devamını oku" ekran görüntüsünde doğrulandı → B takipten çıktı → sonsuz kaydırma (Herkes sekmesi, 15→45 aktivite kartı, 2 sayfa daha yüklendi).
  - **Tur 3 (hata/uç durumlar):** misafir puan vermeye çalışınca `/giris?redirect=...`'e yönlendi ✓; hatalı giriş → anlaşılır hata mesajı ✓; şifre sıfırlama uçtan uca (backend log'undan gerçek kod okunup girildi, yeni şifreyle giriş başarılı) ✓; bozuk/geçersiz token ile korumalı sayfa → `/giris`'e yönlendi ✓; **backend'e erişilemezken** (bu sayfa için tüm `/api/v1/` istekleri kasıtlı reddedildi — gerçek backend'e DOKUNULMADI) Keşfet'in vitrin şeritleri sessizce boş kalıyor, açık bir hata mesajı yok — bu F3.2'de TMDB-503'e özel alınmış "ayrı hata banner'ı eklemeye gerek yok" kararının kapsamının, backend TAMAMEN erişilemez olduğunda da geçerli olduğunu doğruluyor (bilinçli sınırlama olarak bırakıldı, aşağıya bkz.).
  - **Bulunan ve düzeltilen 4 gerçek hata (kod incelemesiyle DEĞİL, gerçek tarayıcı etkileşimiyle bulundu):**
    1. **`GET /catalog/discover?type=book&sort=X` (genre/yıl/dil filtresi yokken) → 500:** `openlibrary.py`'nin `discover()`'ı filtre yokken `q="*"` gönderiyordu; Open Library bunu "en az 3 karakter" kuralına göre 422 ile reddediyor, bu da yakalanmadan 500'e dönüşüyordu. Kök neden: boş sorgu (`q=`) Open Library'de TÜM sort değerleriyle 200 dönüyor — `or "*"` düşürüldü. Keşfet'te "Temizle"ye basıp kitap tarafında filtre uygulamaya çalışırken canlı olarak yakalandı.
    2. **Avatar yükleme, hafif bozuk görsellerde → 500:** Pillow'un `.verify()`'ı `UnidentifiedImageError` (zaten `OSError` alt sınıfı) DIŞINDA, örneğin bozuk PNG CRC'sinde düz bir `SyntaxError` da fırlatabiliyor; kod yalnız ilkini yakalıyordu. Yakalama `(OSError, SyntaxError, ValueError)`'a genişletildi, `test_avatar_upload_corrupt_image_returns_422` regresyon testi eklendi. (İlk fark ediliş nedeni ironik: test betiğimin elle yazdığım 1×1 PNG fixture'ı GERÇEKTEN bozuktu — ama bu, üretim kodunun bozuk yüklemeleri düzgün ele almadığını da ortaya çıkardı.)
    3. **Misafir kullanıcı içerik sayfasını açar açmaz `GET /lists/mine` → 401:** `AddToListMenu`'nün `useMyLists` sorgusu kimlik doğrulamadan bağımsız her zaman tetikleniyordu (yalnız "Listeye ekle"ye TIKLANINCA giriş yönlendirmesi vardı, sorgunun kendisi mount'ta zaten ateşleniyordu). `useLibraryLookup`'taki ZATEN VAR OLAN `enabled: auth.isAuthenticated` deseniyle tutarlı hale getirildi.
    4. **360px'te profil sekmeleri taşıyordu:** `BaseTabs` 6 sekmeyi (Aktiviteler…Favoriler) tek satırda `overflow-x-auto` OLMADAN diziyordu; "Listeler"/"Favoriler" ekran dışında kalıp tıklanamıyordu. `overflow-x-auto`+`shrink-0` eklendi — düzeltmeden ÖNCE otomasyon "Listeler" sekmesine tıklayamadı (`not clickable`), düzeltmeden SONRA aynı tıklama (Puppeteer'ın yerleşik "scroll into view" davranışıyla) sorunsuz çalıştı, ekran görüntüsüyle doğrulandı.
  - **Bilinçli sınırlamalar (düzeltilmedi, kayda geçirildi):** (a) Backend tamamen erişilemezken Keşfet'in vitrin şeritleri (`ContentRow`) sessizce boş kalıyor, `ErrorState` göstermiyor — F3.2'nin TMDB-503'e özel kararının doğal bir uzantısı; genel bir "sunucuya ulaşılamıyor" banner'ı Faz 3 kapsamı dışında bırakıldı (gelecekte DEBT olarak değerlendirilebilir). (b) Windows konsolu backend'in dev-modu e-posta loglarını UTF-8 olmayan bir codepage'e yazıyor (Türkçe harfler mojibake oluyor) — yalnız TERMİNAL GÖRÜNÜMÜ etkileniyor, gerçek SMTP e-postası `core/email.py`'de açıkça UTF-8 `MIMEText` kullanıyor, kullanıcıya giden gerçek e-postalar etkilenmiyor; kod değişikliği gerekmedi. (c) Film tarafı hâlâ U2'yi (TMDB anahtarı) bekliyor, tüm test turu kitap tarafında yapıldı.
  - **Temizlik:** Bu adım + önceki adımlarda (F3.7/F3.8) unutulan **9 test kullanıcısı** (`tur1*`/`tur2*`/`tur3*`/`f37test*`) veritabanından silindi (F3.7'nin kendi temizlik betiği sessizce başarısız olmuş — bu, "betik kendini temizledi" varsayımının HER ZAMAN ayrıca doğrulanması gerektiğinin bir hatırlatıcısı).
- **Faz 3 kapanışı (2026-09-30):** Kullanıcı `main`e birleştirmeyi onayladı ("Birleştir ve push et") — `v2` → `main` `--ff-only` ile birleştirildi (`5701059`), hem `main` hem `v2` origin'e push edildi. Çalışma dalı `v2` olarak devam ediyor.
- **D-23 — Öncelik kararı (2026-09-30):** Kullanıcı, U1 (Gmail)/U2 (TMDB) anahtarlarının ve kapsamlı test/QA'nın (Faz 7) proje SONUNA ertelenmesini istedi; Faz 4-5-6 boyunca odak "doğru, çalışan, kullanıcı dostu, gerçekten güzel" özellikler inşa etmek. Fazlar bitince kullanıcı anahtarları kendisi girecek, SONRA eski/legacy veriyi (`legacy-v1` etiketi, `backend/legacy_backup/`) silmemi ayrıca isteyecek (bkz. U13) — bu talep gelmeden legacy veriye dokunulmuyor. Ayrıntı: 👤 Kararlar tablosu D-23.
- **Sırada:** F4.1 (Faz 4 — Çağ Atlatma Paketi).

---

## 📊 Faz Özeti

| Faz | Başlık | Durum | İlerleme | Başlangıç | Bitiş |
|---|---|---|---|---|---|
| 0 | Güvenlik, temizlik, hazırlık | ✅ Tamamlandı (F0.4 sonradan kapandı) | 5/5 | 2026-09-26 | 2026-09-26 |
| 1 | Backend temeli | ✅ Tamamlandı | 11/11 | 2026-09-26 | 2026-09-26 |
| 2 | Frontend temeli | ✅ Tamamlandı | 5/5 | 2026-09-26 | 2026-09-26 |
| 3 | Çekirdek özellikler (ilk kullanılabilir v2) | ✅ Tamamlandı 🏁 | 10/10 | 2026-09-26 | 2026-09-30 |
| 4 | Çağ atlatma paketi | ⬜ Başlamadı | 0/9 | – | – |
| 5 | Akıllı öneriler | ⬜ Başlamadı | 0/6 | – | – |
| 6 | KFDU Asistan (NVIDIA LLM) | ⬜ Başlamadı | 0/9 | – | – |
| 7 | Kalite, test, CI, yayın | ⬜ Başlamadı | 0/9 | – | – |
| **Toplam** | | | **31/64** | | |

Durum simgeleri: ⬜ Başlamadı · 🟨 Devam ediyor · ✅ Tamamlandı · ⛔ Engellendi · ⏭️ Atlandı (kullanıcı onayıyla)

---

## 👤 Kullanıcı Eylemleri ve Kararları

| # | Eylem / karar | Ne zaman | Durum |
|---|---|---|---|
| U1 | Gmail uygulama şifresini iptal et: https://myaccount.google.com/apppasswords (şifre public depoda açıkta) | ⏸️ Kullanıcı kararıyla (D-23) proje sonuna ertelendi | ⬜ |
| U2 | TMDB API anahtarını yenile (https://www.themoviedb.org/settings/api) ve yenisini `backend/.env`'ye yaz | ⏸️ Kullanıcı kararıyla (D-23) proje sonuna ertelendi | ⬜ |
| U3 | Node.js'i 24 LTS'e güncelle (en az 22.18): https://nodejs.org veya `winget install OpenJS.NodeJS.LTS` | F0.4 (Faz 2'den önce) | ✅ Yapıldı (2026-09-26) — Node 24.19.0 |
| U4 | `backend/.env` değerlerini doldur (TMDB; isteğe bağlı yeni SMTP uygulama şifresi; `CONTACT_EMAIL`) | F0.3 | ⬜ |
| U5 | Karar: Git geçmişi temizlensin mi? (F0.5 — force push gerektirir) | Faz 0 | ✅ Hayır — atlandı (2026-09-26) |
| U6 | Karar: v1 verileri (3 kullanıcı, 12 etkileşim, 7 liste) yeni veritabanına taşınsın mı? (F1.10) | Faz 1 | ✅ Hayır — atlandı (2026-09-26) |
| U7 | NVIDIA API anahtarı al (https://build.nvidia.com → "Get API Key") ve `backend/.env` → `NVIDIA_API_KEY` | F6.1 | ⬜ |
| U8 | Karar: LLM model seçimi (`check_llm.py` tablosuna göre) | F6.1 | ⬜ |
| U9 | (Opsiyonel) Google Books API anahtarı | İstenirse | ⬜ |
| U10 | Karar: lisans (MIT önerilir) | F7.7 | ⬜ |
| U11 | Karar: canlıya alma yöntemi (opsiyonel) | F7.8 | ⬜ |
| U12 | Faz sonlarında: `v2` dalını push etme ve `main`e birleştirme onayları | Her 🏁 | ✅ Faz 0/3'te uygulandı, sonraki fazlarda tekrar sorulacak |
| U13 | Karar: `legacy-v1` etiketi/`backend/legacy_backup/sql_app_v1.db` (eski v1 verisi) ne zaman silinsin? | Proje sonu (Faz 7 sonrası) | ⏸️ Kullanıcı kararıyla (D-23) ertelendi — kullanıcı API anahtarlarını kendisi girdikten sonra silme talimatı verecek |

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
- [x] F3.4 — İnceleme sayfası ve yorum dizisi — ✅ (2026-09-27)
- [x] F3.5 — Akış (feed) sayfası — ✅ (2026-09-27)
- [x] F3.6 — Profil sayfası — ✅ (2026-09-27)
- [x] F3.7 — Listeler — ✅ (2026-09-29)
- [x] F3.8 — Ayarlar sayfası — ✅ (2026-09-29)
- [x] F3.9 — UX cilası — ✅ (2026-09-30)
- [x] F3.10 — Faz 3 kapanışı: ilk kullanılabilir v2 🏁 — ✅ (2026-09-30, `main`e ilk birleştirme kullanıcı onayı bekliyor)

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
| BUG-07 | Kırık yer tutucu görseller (via.placeholder.com) | F2.2, F3.9 | ✅ (`SafeImage.vue` tüm kalan sayfalara uygulandı, `CastRow` kendi deseniyle genişletildi) | `f3e2894`, `b204510` |
| BUG-08 | Detay açmak arama tipini değiştirip gereksiz çağrı yapıyor | Faz 2–3 (F3.2) | ✅ (v2'de detay ayrı bir rota — `/film/:id` vb. — DiscoverPage'in kendi durumunu hiç etkilemiyor, bu hata sınıfı mimari olarak imkânsız) | `dcffa45` |
| BUG-09 | Başkasının profilinde film durumları kitap etiketiyle | F3.6 | ✅ (`ProfilePage`'in Kütüphane sekmesi metin etiketi değil tür-bağımsız ✓/🔖 simge rozetleri kullanıyor — bu hata sınıfı yapısal olarak imkânsız; `statusLabel(status,type)` zaten F3.1'den beri doğru tip-farkındalıklı) | `f61e341` |
| BUG-10 | Şifre sıfırlamada "(Demo: undefined)" | F2.4 | ✅ (v2'de gerçek e-posta/log tabanlı 3 adımlı akış var, "(Demo: ...)" metni yok) | `031befa` |
| BUG-11 | Arama sorguları URL-encode edilmiyor | F2.3 | ✅ (`client.ts`'teki `api()` tüm sorgu parametrelerini `URLSearchParams` ile otomatik kodluyor) | `e104538` |
| BUG-12 | Akışta göreli tarih/aksiyon metni/alıntı yok | F1.8, F3.5 | ✅ | `9286a24`, `54750e5` |
| BUG-13 | Akışta sayfalama yok, N+1 sorgular | F1.8, F3.5 | ✅ (backend imleçli sayfalama + N+1 giderildi; arayüz gerçek `IntersectionObserver`) | `9286a24`, `54750e5` |
| BUG-14 | Arama "daha fazla" çalışmıyor; kitap sayfa ofseti hatalı | F1.6, F3.2 | ✅ (backend doğru sayfalama; arayüz `useSearch`/`useDiscover` ile gerçek sonsuz kaydırma — `IntersectionObserver` sentinel'i, `has_next`'e göre otomatik `fetchNextPage`) | `8c12de7`, `dcffa45` |
| BUG-15 | Kitap yıl filtresi sessizce filtresiz sonuç dönüyor | F1.6 | ✅ | `8c12de7` |
| BUG-16 | `requirements.txt` eksik (temiz kurulum çöker) | F1.1 | ✅ | `61c08c2` |
| BUG-17 | Migrasyon yok; artık tablolar; eşsizlik kısıtı yok | F1.3 | ✅ | `0f29f74` |
| BUG-18 | Dış API çağrılarında timeout yok | F1.2, F1.6 | ✅ (F1.2 altyapı + F1.6 tüm sağlayıcılar `request_json` kullanıyor) | `8c12de7` |
| BUG-19 | Yetki hataları 400; yorum–aktivite aidiyeti kontrol edilmiyor | F1.8, F1.9 | ✅ | `51373cc` |
| BUG-20 | Durum değerleri film/kitap için tutarsız | F1.7, F3.1 | ✅ (backend `LibraryStatus` tek ortak enum; arayüz `utils/content.ts`'in `statusLabel`'ı §4.2 tablosuyla birebir — film=dizi etiketleri, kitap ayrı) | `919615a`, `77c4b3d` |
| DEBT-01 | Tek dosya frontend, bileşen ve router yok | Faz 2–3 | ✅ (v2: bileşenler F2.2, gerçek rota tablosu+guard F2.3; v1 dosyası `legacy/frontend-v1/`'de yalnız referans) | `e104538` |
| DEBT-02 | 32 `alert/confirm`, 10 `console.log` | Faz 2–3 | ✅ (vue-sonner toast + ConfirmDialog; `git grep -nE "\balert\(\|\bconfirm\(\|\bprompt\("` → yalnız `useConfirm` tanım/kullanımları, F3.9'da doğrulandı) | `f3e2894` |
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
| REQ-1.2 | Dinamik, kullanıcı dostu, mobil uyumlu arayüz | Faz 2–3 | ✅ (Lighthouse mobil erişilebilirlik: Keşfet 96, Detay 97, Akış 96; 360×800 gerçek tarayıcı turu — F3.10, 20 senaryo) | F3.9/F3.10 |
| REQ-2.1.1a | Kayıt: kullanıcı adı, e-posta, şifre, şifre tekrarı | F1.4, F2.4 | ✅ | `RegisterPage.vue` `031befa` |
| REQ-2.1.1b | Giriş: e-posta + şifre | F1.4, F2.4 | ✅ (v2'de ayrıca kullanıcı adıyla da girilebiliyor) | `LoginPage.vue` `031befa` |
| REQ-2.1.1c | Net hata mesajları | F1.2, F1.4, F2.4 | ✅ | `ApiError`+form/alan hataları, curl ile doğrulandı `031befa` |
| REQ-2.1.1d | Şifremi unuttum (e-posta) | F1.4, F2.4 | ✅ | `ForgotPasswordPage.vue`, uçtan uca curl ile doğrulandı `031befa` |
| REQ-2.1.2a | Takip edilenlerin aktiviteleri (yeniden eskiye) | F1.8, F3.5 | ✅ | `FeedPage.vue` (`54750e5`) |
| REQ-2.1.2b | Kart başlığı: avatar, ad (link), aksiyon metni, göreli tarih | F3.5 | ✅ | `ActivityCard.vue` (`54750e5`) |
| REQ-2.1.2c | Türe göre gövde, afiş ön planda | F3.5 | ✅ | `ActivityCard.vue` — 5 `card_type` gövdesi (`54750e5`) |
| REQ-2.1.2d | Beğen / Yorum Yap | F1.8, F3.4, F3.5 | ✅ | `LikeButton`+`CommentThread` (`54750e5`) |
| REQ-2.1.2e | Puanlama kartı: büyük afiş + yıldız / x/10 | F3.5 | ✅ | `ActivityCard.vue` (`54750e5`) |
| REQ-2.1.2f | İnceleme kartı: 150–200 karakter alıntı + "…daha fazlasını oku" | F3.4, F3.5 | ✅ | `ActivityCard.vue` (`54750e5`) |
| REQ-2.1.2g | Sayfalama: ilk 10–15 + sonsuz kaydırma / daha fazla yükle | F1.8, F3.5 | ✅ | `FeedPage.vue` — 15'er, `IntersectionObserver`+buton (`54750e5`) |
| REQ-2.1.3a | Arama → detay (kapak, başlık, yıl) | F1.6, F3.2 | ✅ | `ContentDetailPage.vue` (`1c23219`) |
| REQ-2.1.3b | Vitrin: En Yüksek Puanlılar, En Popülerler | F1.10, F3.2 | ✅ | `DiscoverPage.vue`, kitapla curl ile doğrulandı (`dcffa45`) |
| REQ-2.1.3c | Filtre: tür, yıl, puan | F1.6, F3.2 | ✅ | `FilterPanel.vue` + `useDiscover`, curl ile doğrulandı (`dcffa45`) |
| REQ-2.1.4a | Künye: kapak, özet, yıl, süre/sayfa, yönetmen/yazar, türler | F1.6, F3.3 | ✅ | `ContentDetailPage.vue` (`1c23219`) |
| REQ-2.1.4b | Platform puanı: ortalama + oy sayısı | F1.7, F3.3 | ✅ | `ContentDetailPage.vue` + `RatingHistogram` (`1c23219`) |
| REQ-2.1.4c | 1–10 puan bileşeni (güncellenebilir) | F1.7, F3.1, F3.3 | ✅ | `StarRating`+`useContentActions`, curl ile doğrulandı (`1c23219`) |
| REQ-2.1.4d | İzledim/İzlenecek · Okudum/Okunacak butonları | F1.7, F3.1, F3.3 | ✅ | `LibraryButtons` (`1c23219`) |
| REQ-2.1.4e | "Özel Listeye Ekle" menüsü | F1.9, F3.1, F3.7 | ✅ (plan hedefi F3.7 diyordu ama `AddToListMenu` F3.1'de yazılıp F3.3'te gerçek bir sayfaya bağlandı — işlevsel olarak tamam, F3.7/ListPage ayrıca kendi tarafından da kullanacak) | `1c23219` |
| REQ-2.1.4f | Yorumlar listesi (ad, metin, tarih) | F1.8, F3.3 | ✅ (plan F3.3 diyordu, gerçekte `CommentThread` F3.4'ün işiydi) | `CommentThread.vue` (`6979589`) |
| REQ-2.1.4g | Yorum ekleme alanı + Gönder | F1.7, F3.3 | ✅ (plan F3.3 diyordu, gerçekte `CommentThread` F3.4'ün işiydi) | `CommentThread.vue` (`6979589`) |
| REQ-2.1.4h | Yalnız kendi yorumunu düzenle/sil | F1.7, F1.8, F3.3, F3.4 | ✅ | `CommentThread.vue`, curl ile 403+yetki kuralı doğrulandı (`6979589`) |
| REQ-2.1.5a | Profil: kullanıcı adı, avatar, biyografi | F1.5, F3.6 | ✅ | `ProfileHeader.vue` (`f61e341`) |
| REQ-2.1.5b | Kendi profili: Profili Düzenle, Yeni Özel Liste | F3.6, F3.7 | ✅ | `EditProfileModal`+`ListFormModal` (`f61e341`, `813b5e9`) |
| REQ-2.1.5c | Başkasının profili: Takip Et / Takipten Çık | F1.5, F3.6 | ✅ | `FollowButton.vue`, curl ile doğrulandı (`f61e341`) |
| REQ-2.1.5d | Sekmeli kütüphane (4 sekme) | F1.7, F3.6 | ✅ (plan 4 diyor ama Ek C'nin kendi metni 7 alt filtre listeliyor — İzlediklerim/İzlenecekler/İzliyorum/Okuduklarım/Okunacaklar/Okuyorum/Yarım Bıraktıklarım — hepsi uygulandı) | `ProfilePage.vue` (`f61e341`) |
| REQ-2.1.5e | Özel listeler | F1.9, F3.6, F3.7 | ✅ | `ListPage.vue`, httpx betiğiyle uçtan uca doğrulandı (`813b5e9`) |
| REQ-2.1.5f | Son aktiviteler (yorum + puan) | F1.8, F3.6 | ✅ | `ProfilePage.vue` Aktiviteler sekmesi, `ActivityCard` (`f61e341`) |
| REQ-2.2.1a | Film verisi TMDb (başlık, özet, yıl, yönetmen, oyuncular, türler, kapak) | F1.6 | ✅ | `8c12de7` (respx testleri + fixture) |
| REQ-2.2.1b | Kitap verisi Open Library / Google Books (başlık, yazar, açıklama, sayfa, kapak) | F1.6 | ✅ | `8c12de7` (gerçek sunucuda canlı doğrulandı) |
| REQ-2.2.1c | Manuel veri girişi yok | F1.6 | ✅ | `8c12de7` (tüm içerik `catalog` modülünden upsert edilir) |
| REQ-3 | Tutarlı ve verimli veritabanı | F1.3 | ✅ (38 FK/indeks/unique kısıtı; `alembic check` temiz — migration/model sürüklenmesi yok; 69+ backend testi gerçek sorgu paternleriyle çalışıyor) | F1.3 |

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
| 2026-09-30 | D-23 | **Öncelik kararı (Faz 3 kapanışından sonra):** Gerçek veri/API anahtarları (U1 Gmail, U2 TMDB) ve kapsamlı test/QA aşaması (Faz 7) proje sonuna ertelensin; Faz 4-5-6 boyunca öncelik "doğru, çalışan, kullanıcı dostu, gerçekten güzel" özellikleri inşa etmek olsun. TMDB gerektiren yerlerde (film verisi) aynı desen korunur: kod yazılır+test edilir (mock/fixture'larla), gerçek canlı doğrulama U2 tamamlanınca yapılır — bu zaten F1.6'dan beri izlenen yöntem. | ✅ Kullanıcı kararı — "gerçek veriler, api keyleri ve test aşaması beklesin ... sonrasında ... eski verileri silmeni isticem." Kullanıcı fazların sonunda API anahtarlarını kendisi girecek, ardından eski/legacy verinin (`legacy-v1` etiketi, `backend/legacy_backup/`) silinmesini AYRICA isteyecek (bkz. U13) — bu istek gelmeden legacy veriye dokunulmayacak. |

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
| Lighthouse Performans (mobil: Keşfet / Detay / Akış) | ≥ 85 | – (yalnız erişilebilirlik kategorisi ölçüldü) | – |
| Lighthouse Erişilebilirlik (mobil) | ≥ 90 | **96 / 97 / 96** | 2026-09-30 (F3.9/F3.10) |
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

### [2026-09-30] F3.10 — Faz 3 kapanışı: ilk kullanılabilir v2 — ✅ 🏁

- **Yapılanlar:**
  - **Ek A izlenebilirlik matrisi tamamlandı:** Kalan 4 satır kanıtla kapatıldı — REQ-1.2 (mobil uyum: Lighthouse 96/97/96 + bu adımın tarayıcı turu), REQ-2.1.4f/g (yorumlar listesi/ekleme — zaten `CommentThread` F3.4'te vardı, satır güncellenmemiş kalmıştı), REQ-3 (veritabanı — 38 FK/indeks/unique kısıtı, `alembic check` temiz), DEBT-02 (32 `alert/confirm` — F3.9'da zaten `git grep` ile doğrulanmıştı, tam ✅'ye çevrildi).
  - **Gerçek tarayıcı testi (projede ilk kez):** F3.9'da Lighthouse için kurulan `puppeteer-core` + headless Chrome yöntemi genişletilip 3 bağımsız Node betiğiyle (`tour1/2/3.mjs`, scratchpad'te izole, proje bağımlılığı DEĞİL) planın 20 maddelik manuel test turu 360×800 mobil görünümde gerçekten çalıştırıldı:
    - **Tur 1** (tek kullanıcı): misafir→kayıt→onboarding (tür seçimi+takip önerileri)→akış; Keşfet'te kitap arama (gerçek sonuçlar)+tür/yıl/puan filtresi (URL senkronizasyonu doğrulandı); içerik detayında puan ver (`aria-valuenow` doğrulandı)+kütüphane durumu+inceleme yaz+"Özel Listeye Ekle"+satır içi yeni liste formu; profilin 6 sekmesi (Aktiviteler/Kütüphane/Puanlar/İncelemeler/Listeler/Favoriler); Ayarlar'da gerçek bir PNG ile avatar yükleme+görünen ad değiştirme+tema değiştirme (`<html>` sınıfı doğrulandı); tarayıcı geri/ileri + doğrudan URL yükleme. ~30 ekran görüntüsü alındı, hepsi elle incelendi.
    - **Tur 2** (iki kullanıcı, tek sayfada kimlik değiştirme deseniyle — iki eşzamanlı sayfa denendi ama Puppeteer/Chrome protokol zaman aşımına uğradı, sıralı tek-sayfa deseni sorunsuz çalıştı): A bir kitaba 9/10 verip 345 karakterlik inceleme yazdı → B, A'yı takip etti → B'nin "Takip Ettiklerim" akışında A'nın aktivitesi GERÇEKTEN göründü (feed+follow sisteminin uçtan uca doğrulanması) → B beğendi (`aria-label`: "Beğen · 0"→"Beğeniyi geri al · 1", F3.9'daki WCAG düzeltmesinin canlı kanıtı) → B yorum yaptı → "…devamını oku" ekran görüntüsünde doğrulandı → B takipten çıktı → sonsuz kaydırma (Herkes sekmesi, kaydırdıkça 15→45 aktivite kartı, 2 sayfa otomatik yüklendi).
    - **Tur 3** (hata/uç durumlar): misafir puan vermeye çalışınca `/giris?redirect=...` ✓; hatalı giriş → anlaşılır hata mesajı ✓; şifre sıfırlama uçtan uca (backend'in dev-modu log çıktısından GERÇEK kod okunup girildi, yeni şifreyle giriş başarılı) ✓; bozuk/geçersiz token'la korumalı sayfa ziyareti → `/giris`'e yönlendi ✓; backend'e erişilemezken (yalnız bu sayfanın `/api/v1/` istekleri reddedildi, gerçek backend'e dokunulmadı) davranış aşağıda not edildi.
  - **Bulunan ve düzeltilen 4 gerçek hata (kod incelemesiyle değil, gerçek tıklama/etkileşimle bulundu):**
    1. `GET /catalog/discover?type=book&sort=X` (genre/yıl/dil filtresi yokken) → **500**: `openlibrary.py` filtre yokken Open Library'ye `q="*"` gönderiyordu, bu da onların "en az 3 karakter" kuralına takılıp 422 veriyordu ve yakalanmadan 500'e dönüşüyordu. Kök neden: boş sorgu (`q=`) TÜM sort değerleriyle 200 dönüyor (doğrudan Open Library'ye karşı doğrulandı) — `or "*"` düşürüldü.
    2. Avatar yükleme, hafif bozuk görsellerde → **500**: Pillow `.verify()` bozuk PNG CRC'sinde `UnidentifiedImageError` değil düz `SyntaxError` fırlatıyordu, kod yalnız ilkini yakalıyordu. `(OSError, SyntaxError, ValueError)`'a genişletildi + regresyon testi (`test_avatar_upload_corrupt_image_returns_422`).
    3. Misafir kullanıcı içerik sayfası açar açmaz `GET /lists/mine` → **401**: `AddToListMenu`'nün `useMyLists`'i kimlik doğrulamadan bağımsız mount'ta ateşleniyordu. `useLibraryLookup`'taki mevcut `enabled: auth.isAuthenticated` deseniyle tutarlı hale getirildi.
    4. 360px'te profil sekmeleri (`BaseTabs`) taşıyordu, "Listeler"/"Favoriler" tıklanamıyordu: `overflow-x-auto`+`shrink-0` eklendi — düzeltmeden önce/sonra otomasyonla doğrulandı (Puppeteer'ın "scroll into view" davranışı artık sekmeye ulaşabiliyor).
  - **Bilinçli sınırlamalar (düzeltilmedi, kayda geçirildi):** (a) Backend tamamen erişilemezken Keşfet'in vitrin şeritleri sessizce boş kalıyor, genel bir hata banner'ı yok — F3.2'nin TMDB-503'e özel kararının doğal bir uzantısı, kapsamlı bir "sunucuya ulaşılamıyor" mekanizması Faz 3 dışına bırakıldı. (b) Windows konsolu dev-modu e-posta loglarını UTF-8 olmayan bir codepage'e yazıyor (Türkçe harfler yalnız TERMİNALDE mojibake oluyor); gerçek SMTP e-postası `core/email.py`'de açıkça UTF-8 kullanıyor, gerçek kullanıcı e-postaları etkilenmiyor, kod değişikliği gerekmedi. (c) Film tarafı hâlâ U2'yi (TMDB anahtarı) bekliyor, tüm tur kitap tarafında yapıldı.
  - **Temizlik:** F3.7/F3.8'den kalan **9 sessizce temizlenmemiş test kullanıcısı** (`tur1*`/`tur2*`/`tur3*`/`f37test*`) veritabanından (avatar dosyaları dahil) silindi — F3.7'nin kendi temizlik betiğinin sessizce başarısız olduğu ortaya çıktı; "betik kendini temizledi" iddiasının ayrıca doğrulanması gerektiğinin somut bir örneği.
- **Değişen dosyalar:** `backend/app/modules/catalog/providers/openlibrary.py`, `backend/app/modules/users/avatars.py`, `backend/tests/test_users.py`, `frontend/src/api/lists.ts`, `frontend/src/components/ui/BaseTabs.vue`.
- **Doğrulama:** Backend: `pytest` → 71 passed ✓ (2 yeni) · `ruff check`+`format` → temiz ✓. Frontend: `lint`/`type-check`/`test:unit` (73 passed) /`build` → hepsi temiz ✓. Yukarıda ayrıntılı 3 tarayıcı turu + Lighthouse (F3.9'dan taşınan) 96/97/96.
- **Kapanan maddeler:** REQ-1.2, REQ-2.1.4f, REQ-2.1.4g, REQ-3, DEBT-02 — **Ek A izlenebilirlik matrisi artık %100 dolu**
- **Commit:** `260bde3` (fix), docs commit aşağıda
- **Notlar / sorunlar:** 🏁 **Faz 3 tamamlandı** (10/10, toplam 31/64). Kullanıcı `main`e birleştirmeyi onayladı; `v2` → `main` `--ff-only` ile birleştirildi ve her ikisi de origin'e push edildi (`5701059`). Film tarafının canlı doğrulaması hâlâ U2'yi (TMDB anahtarı) bekliyor; bu, kod ilerlemesini engellemiyor ama Faz 4 öncesi kullanıcı tarafından yapılması faydalı olur.
- **Sonraki adım:** F4.1

### [2026-09-30] F3.9 — UX cilası — ✅

- **Yapılanlar:**
  - `NotFoundPage.vue` (yeni, `/:pathMatch(.*)*`): `EmptyState` + Akış/Keşfet'e dönüş butonları (`BaseButton`'ın var olan ama hiç kullanılmamış `to` prop'uyla).
  - `ErrorBoundary.vue` (yeni, `components/layout/`): `onErrorCaptured` ile alt bileşen hatalarını yakalayıp "Sayfayı yenile" (tam sayfa reload) gösteriyor; rota değişince `failed` bayrağı sıfırlanıyor (aksi halde `RouterView` tamamen `v-if` arkasında kilitli kalırdı). `ErrorState` bilerek yeniden kullanılmadı çünkü onun butonu "Tekrar dene" diyor (sorgu-yeniden-deneme anlamı), burada gerçekten sayfa yenileme gerekiyor.
  - `OfflineBanner.vue` (yeni): `@vueuse/core`'un `useOnline()`'ı, `!isOnline` iken sabit bir uyarı şeridi.
  - `composables/useSearchFocus.ts` (yeni): modül seviyeli tek-seferlik bayrak (`requestSearchFocus`/`consumeSearchFocusRequest`) — reaktif bir token yerine bilinçli tercih edildi, çünkü DiscoverPage henüz mount olmadan `router.push` sonrası bir reaktif izleyici kurulumunu KAÇIRABİLİRDİ; bayrak DiscoverPage `onMounted`'da tüketildiği için zamanlama yarışı yok.
  - `composables/useKeyboardShortcuts.ts` (yeni): `/` (zaten `/kesfet`'teyse `getElementById` ile doğrudan odakla, değilse bayrağı işaretleyip yönlendir), `g` sonra `f`/`k` (1 sn pencere), `?` (yardım modalı). Düzenlenebilir alanlarda (`input`/`textarea`/`contenteditable`), değiştirici tuşlarla (Ctrl/Alt/Meta) VE açık bir modal varken (`[role="dialog"]` sorgusu) devre dışı.
  - `ShortcutsHelpModal.vue` (yeni) — `AppShell`'in altbilgisine "Klavye kısayolları" bağlantısıyla keşfedilebilir kılındı (aksi halde tamamen gizli bir özellik olurdu).
  - Tüm `<img>` etiketleri tek tek tarandı (`awk` betiğiyle) — 7 yerde (`ActivityCard` ×5, `ListCard`, `ListPage`) `loading="lazy"`/`decoding="async"` eksikti, eklendi. `ContentDetailPage`/`ReviewPage`'in de eksik olduğu bulundu, eklendi.
  - **BUG-07 tamamen kapatıldı:** `components/ui/SafeImage.vue` (yeni, saf sunum — `src`/`alt` alır, hata veya eksikse `ImageOff` simgesi; `PosterCard`'ın F3.1'den beri kullandığı desenin genelleştirilmiş hali) `ActivityCard` (poster ×4 + koleksiyon kapakları), `ListCard`, `ListPage`, `ContentDetailPage` (hero poster), `ReviewPage` (mini künye) içindeki çıplak `<img>`lerin yerini aldı. `CastRow` SafeImage'a taşınmadı (kendi baş-harf-düşen deseni farklı) ama `@error` yakalaması eklendi.
  - `git grep -nE "\balert\(|\bconfirm\(|\bprompt\(" -- frontend/src` → yalnız `useConfirm`/`ConfirmDialog` tanım ve kullanımları — zaten temizdi, ekstra iş gerekmedi.
  - **Erişilebilirlik + Lighthouse turu (planın kabul kriteri: mobilde ≥90, Keşfet/Detay/Akış):** Chrome bu makinede kurulu olduğu keşfedilince (`C:/Program Files/Google/Chrome/`), Lighthouse CLI headless Chrome ile **gerçek** ölçüm için kullanıldı — tarayıcı ARACI değil, saf CLI/Node (proje bağımlılığı olarak eklenmedi, scratchpad'te izole kuruldu). Akış kimlik doğrulama gerektirdiği için `puppeteer-core` ile `localStorage`'a gerçek bir test token'ı yazılıp aynı `page` nesnesi Lighthouse'un Node API'sine verildi (kayıt→ölçüm→`DELETE /users/me` ile temizlik). **Sonuçlar (mobil, 360×800, önce→sonra):** Keşfet **85→96**, İçerik detayı (`/kitap/OL45804W`) **88→97**, Akış **87→96**.
  - **Bulunan ve düzeltilen 5 gerçek sorun:**
    1. Karanlık modda `text-brand-600` hem düz arka plan (3.58:1) hem rozet zemininde (3.1:1) 4.5:1'in altındaydı (elle hesapladığım `--muted` kontrastı doğruydu ama `brand-600`'ü kontrol etmemiştim) → tema-duyarlı `--link` token'ı eklendi (`main.css`, ışık: brand-600, karanlık: brand-400 = 5.83:1), **20 dosyadaki tüm `text-brand-600`** `text-link`'e taşındı.
    2. `BaseButton` birincil varyantı + header logosu: beyaz metin `bg-brand-500` üstünde 4.34:1 (gerekli 4.5:1) → `bg-brand-600`'e çekildi (5.31:1).
    3. Etiketsiz form kontrolleri: `FilterPanel` puan kaydırıcısı (`label for` eksik) ve `BaseSelect`'in `label`sız 2 kullanımı (`ReviewList`, `ProfilePage`) → `BaseSelect`'e `ariaLabel` prop'u eklendi.
    4. Avatarı olmayan kullanıcılarda avatar-yalnız profil bağlantıları (`ActivityCard`/`CommentThread`/`ReviewItem`/`UserCard`/`ReviewPage`) erişilebilir ada sahip değildi (baş harfler `aria-hidden`) → hepsine `:aria-label` eklendi.
    5. `LikeButton`'ın `aria-label`'ı görünür beğeni sayısını içermiyordu (WCAG 2.5.3) → sayaç etikete eklendi.
  - **Kalan 2 bulgu (bilinçli, düzeltilmedi):** (a) `aria-prohibited-attr` — Vue DevTools'un kendi `vue-devtools__anchor-btn` düğmesi, yalnızca dev modda var, üretimde yok, uygulama koduyla ilgisiz. (b) `label-content-name-mismatch` — header'daki kullanıcı menüsü düğmesinde avatarsız kullanıcının baş harfleri görsel olarak `aria-label="Kullanıcı menüsü"`yle birebir eşleşmiyor (yalnız sesli-komut yazılımlarını etkiler; ekran okuyucu/klavye/fare sorunsuz) — kullanıcıya özgü baş harflerin dinamik etikete eklenmesi bu adımın kapsamına göre orantısız görüldü.
- **Değişen dosyalar:** `frontend/src/pages/NotFoundPage.vue` (yeni), `frontend/src/components/layout/{ErrorBoundary,OfflineBanner,ShortcutsHelpModal}.vue` (yeni), `frontend/src/composables/{useSearchFocus,useKeyboardShortcuts}.ts` (+ `.spec.ts`, yeni), `frontend/src/components/ui/SafeImage.vue` (yeni), `frontend/src/styles/main.css` (`--link` token'ı), `frontend/src/components/ui/{BaseButton,BaseSelect}.vue`, `frontend/src/components/content/{ActivityCard,AddToListMenu,CastRow,CommentThread,ContentRow,FilterPanel,LibraryButtons,LikeButton,ReviewItem,ReviewList}.vue`, `frontend/src/components/layout/{AppShell,AppHeader,AppBottomNav}.vue`, `frontend/src/components/lists/ListCard.vue`, `frontend/src/components/users/{GenreChipPicker,ProfileForm,UserCard}.vue`, `frontend/src/pages/{ContentDetailPage,DiscoverPage,ListPage,ReviewPage,ProfilePage,SettingsPage,ForgotPasswordPage,LoginPage,RegisterPage,UiShowcasePage}.vue`, `frontend/src/router/index.ts`, `frontend/src/__tests__/ErrorBoundary.spec.ts` (yeni).
- **Doğrulama:** `npm run lint` → temiz ✓ · `npm run type-check` → temiz ✓ · `npm run test:unit -- run` → **73 passed** (9 yeni: `useSearchFocus` ×2, `ErrorBoundary` ×3, `useKeyboardShortcuts` ×4) ✓ · `npm run build` → başarılı ✓ · Vite dev sunucusunda tüm yeni modüller + `/rastgele-yok-sayfa` (404) tek tek istendi, hepsi 200 ✓ · **Lighthouse mobil erişilebilirlik (yukarıda ayrıntılı):** Keşfet 96, Detay 97, Akış 96 — plan kabul kriteri (≥90, üç sayfa) karşılandı ✓.
- **Kapanan maddeler:** BUG-07 (tamamen), DEBT-01 (kısmen — bkz. Notlar), REQ-1.2 (mobil uyum, kod düzeyinde denetim + Lighthouse; piksel-piksel 360/768/1280 görsel turu tarayıcı aracı olmadan yapılamadı)
- **Commit:** `65cedd0` (feat), `b204510` (fix BUG-07), `b762aa8` (fix a11y)
- **Notlar / sorunlar:** DEBT-01/DEBT-02'nin tam kapsamını görmek için `proje-plani.md`'nin §2 bölümüne bakılmadı (bu adımın odağı F3.9'un kendi kontrol listesiydi) — F3.10'da Ek A matrisini işaretlerken ayrıca gözden geçirilebilir. 360/768/1280 px'te piksel-piksel görsel tur hâlâ yapılamadı (tarayıcı aracı yok) ama kod düzeyinde hiçbir sabit taşma-riskli genişlik bulunamadı (`grep` ile doğrulandı) ve Lighthouse'un kendi mobil emülasyonu (360×800) üç sayfada da gerçek bir DOM/CSS render'ı üzerinden geçti — bu, salt statik kod incelemesinden daha güçlü bir kanıt.
- **Sonraki adım:** F3.10 — Faz 3 kapanışı: ilk kullanılabilir v2

### [2026-09-29] F3.8 — Ayarlar sayfası — ✅

- **Yapılanlar:**
  - **Gerçek hata düzeltmesi (F3.8'den önce de vardı, kod incelemesinde bulundu):** `EditProfileModal`'ın `useUpdateMe`/`useRemoveAvatar` çağrıları yalnız kullanılmayan bir TanStack `['user','me']` sorgusunu geçersiz kılıyordu, `auth` store'daki `me`'yi HİÇ güncellemiyordu. Sonuç: profil düzenlendikten sonra `AppHeader`/`AppBottomNav` bayat veri gösteriyordu; kullanıcı adı değişince alt gezinmenin "Profilim" bağlantısı bile eski/geçersiz kullanıcı adına gidiyordu (sayfa yenilenene kadar). F3.8'in Hesap/Güvenlik/Tercihler bölümleri aynı sorunu çoğaltacağı için kökten düzeltildi.
  - `EditProfileModal.vue`'nin içeriği paylaşılan `components/users/ProfileForm.vue`'ya çıkarıldı (avatar+kullanıcı adı+ad+biyografi+Kaydet, `@saved` olayı yayar, artık her başarılı kayıttan/avatar kaldırmadan sonra `auth.setMe(...)` çağırıyor). `EditProfileModal` artık yalnız `<BaseModal><ProfileForm @saved="open=false" /></BaseModal>` — `BaseModal`'ın zaten var olan ✕/Escape/dış tıklama ile kapanma davranışı yeterli olduğu için ayrı bir "Vazgeç" footer butonu kaldırıldı (işlev kaybı yok, yalnız gereksiz tekrar).
  - `components/users/GenreChipPicker.vue` (yeni, saf sunum — `genres`+`selected` props, `toggle` olayı): `OnboardingPage`'in İKİ AYRI yerde birebir kopyalanmış tür-çipi düğmesi artık bunu kullanıyor (davranış değişmedi, yalnız kod tekrarı gitti); `SettingsPage`'in Tercihler bölümü bileşeni üçüncü/dördüncü kullanım yeri olarak paylaşıyor.
  - `stores/auth.ts`: `setToken` dışa açıldı (öncesinde yalnız store'un kendi `login`/`register`/`logout` fonksiyonlarından erişilebiliyordu) — şifre değiştirmenin döndürdüğü yeni token'ı yazmak için gerekliydi.
  - `api/users.ts`: `useChangeEmail`, `useDeleteAccount` eklendi (ham `changeEmailRequest`/`deleteAccountRequest` zaten vardı, yalnız `use*` sarmalayıcıları eksikti). `api/auth.ts`'teki `useChangePassword`/`useLogoutAllDevices` bu oturumdan ÖNCE zaten yazılmıştı (muhtemelen backend'le birlikte ileriye dönük eklenmiş), bu adımda yalnız tüketildi — yeni bir şey yazmaya gerek kalmadı.
  - `SettingsPage.vue` (yeni, `/ayarlar`): **Profil** (paylaşılan `ProfileForm`), **Hesap** (e-posta değiştir — mevcut şifreyle; `INVALID_PASSWORD`/`EMAIL_TAKEN` alan hatası olarak gösteriliyor, `EditProfileModal`'daki `USERNAME_TAKEN` deseniyle aynı), **Güvenlik** (şifre değiştir — istemci tarafı güç/eşleşme doğrulaması `utils/validation.ts`'teki RegisterPage ile aynı fonksiyonlarla, başarıda `TokenOut`'tan gelen yeni token+kullanıcı `auth.setToken`+`auth.setMe` ile yazılıyor; "Tüm cihazlardan çıkış yap" — bunun KENDİ oturumunu da düşürdüğü `useConfirm` ile açıkça belirtiliyor, başarıda yerel `logout()`+`/kesfet`), **Görünüm** (`useTheme` — `AppHeader`'ın menüsündeki tema seçiciyle birebir aynı görsel desen), **Tercihler** (favori türler — Onboarding'deki AYNI iki grup, `GenreChipPicker` paylaşılıyor), **Tehlikeli bölge** (hesabı sil — şifre + tam "SİL" yazma onayı, ikisi de sağlanmadan buton `disabled`, `INVALID_PASSWORD` alan hatası, başarıda `logout()`+`/kesfet`).
  - **Bilinçli plan sapması:** Plan "Hesap" bölümünde e-posta VE kullanıcı adı değişikliğini birlikte listeliyordu, ama backend `PATCH /users/me` kullanıcı adını `display_name`/`bio` ile TEK bir uçta topluyor ve bu zaten `ProfileForm`'da (Profil bölümü) çalışıyor durumda. Kullanıcı adını Hesap bölümünde İKİNCİ kez düzenlenebilir yapmak aynı sayfada iki ayrı "kullanıcı adı" alanı göstererek kafa karıştırırdı; Hesap bölümü bu yüzden yalnız e-postaya odaklandı.
  - **Ödev kapsamı notu:** F3.8 Ek A'daki hiçbir REQ/BUG maddesini kapatmıyor — Ayarlar sayfası tamamen v2'nin kendi "ilk kullanılabilir sürüm" hedefinin bir parçası (plan §3.8), ödevin zorunlu gereksinimi değil.
- **Değişen dosyalar:** `frontend/src/stores/auth.ts`, `frontend/src/api/users.ts`, `frontend/src/components/users/{GenreChipPicker,ProfileForm}.vue` (yeni), `frontend/src/components/users/EditProfileModal.vue`, `frontend/src/pages/{OnboardingPage,SettingsPage}.vue` (SettingsPage yeni), `frontend/src/router/index.ts`.
- **Doğrulama:** `npm run lint` → temiz ✓ · `npm run type-check` → temiz ✓ · `npm run test:unit -- run` → 64 passed ✓ · `npm run build` → başarılı, `SettingsPage` (7.83 KB, gzip 2.75 KB) + `ProfileForm`/`GenreChipPicker` kendi paylaşılan chunk'larında; `OnboardingPage` 5.22→4.53 KB'a, `ProfilePage` 15.97→13.84 KB'a küçüldü (paylaşılan bileşenlere çıkarmanın doğrudan kanıtı) ✓ · Vite dev sunucusunda `/ayarlar` rotası + değişen modüller tek tek istendi, hepsi 200 ✓ · **gerçek backend'e karşı uçtan uca (httpx betiği, iki test kullanıcısıyla):** e-posta değiştir yanlış şifreyle → 400 `INVALID_PASSWORD` ✓; başka kullanıcının e-postasına değiştirmeye çalışınca → 409 `EMAIL_TAKEN` ✓; doğru şifreyle başarı ✓; `favorite_genres` güncelleme + kalıcılık ✓; şifre değiştir yanlış mevcut şifreyle → 400 ✓; doğru şifreyle başarı → **eski token artık 401, yeni token çalışıyor** ✓; eski şifre artık işe yaramıyor, yenisi çalışıyor ✓; `logout-all` çağıran oturumun KENDİ token'ını da, ayrı bir "B cihazı" token'ını da geçersiz kılıyor (ikisi de 401) ✓, sonra tekrar giriş yapılabiliyor ✓; hesabı sil yanlış şifreyle → 400 ✓; doğru şifreyle → 204, profil artık 404 ✓. 19/19 kontrol geçti, iki test kullanıcısı da temizlendi.
  - **Bilinçli kapsam sınırlaması:** `/_ui` vitrinine `SettingsPage`/`ProfileForm`/`GenreChipPicker` eklenmedi (gerçek `auth.me` durumuna bağlı, sahte veriyle yalnızca yarım bir görünüm olurdu) — doğrulama gerçek backend testiyle yapıldı.
  - **Kalıcı sınırlama:** Tarayıcı aracı bu oturumda da yok.
- **Kapanan maddeler:** Yok (ödev REQ/BUG'ı değil — bkz. "Ödev kapsamı notu")
- **Commit:** `08f3e8b`
- **Notlar / sorunlar:** F4.7'de "Verilerim" bölümünün bu sayfaya ekleneceğini plan zaten belirtiyor, o adıma bırakıldı.
- **Sonraki adım:** F3.9 — UX cilası

### [2026-09-29] F3.7 — Listeler — ✅

- **Yapılanlar:**
  - `api/lists.ts` genişletildi: `useListDetail(listId)` (`['lists','detail',id]`, 30 sn), `useUpdateList`, `useDeleteList`, `useUpdateListItemNote`, `useReorderListItems`. Hepsi başarıda geniş `['lists']` anahtarını geçersiz kılıyor (mevcut `useCreateList`/`useAddListItem`/`useRemoveListItem` zaten aynı deseni kullanıyordu) — bu, `['lists','detail',id]` alt-anahtarını da otomatik yakaladığı için ayrı bir invalidate yazmaya gerek bırakmadı.
  - `CreateListModal.vue` → `ListFormModal.vue` (yeniden adlandırıldı, `components/lists/`): plan tek bir "ListFormModal" adı verdiği için oluşturma VE düzenleme tek bileşende birleştirildi (`list?: Pick<ListOut,'id'|'title'|'description'|'is_public'>` prop'u verilirse düzenleme modu — başlık "Listeyi düzenle"/buton "Kaydet" olur, modal kapanır ama yönlendirme yapmaz; verilmezse oluşturma modu — eskisi gibi `/liste/:id`'ye yönlendirir). `ProfilePage.vue`'nin "Yeni Liste" akışı davranış değişmeden bu bileşene taşındı (import + etiket adı güncellendi).
  - `ListPage.vue` (yeni, `/liste/:id` — route-level `props` ile `id` enjekte ediliyor): 4'lü kapak kolajı (boşsa degrade), başlık, Herkese Açık/Gizli rozeti, sahip bağlantısı (`/u/:username`), öğe sayısı, açıklama; eylem çubuğu — Paylaş (clipboard), sahibiyse Düzenle (`ListFormModal`), Sil (`useConfirm`, danger, onay → kendi profiline döner), **sıralama modu** (sunucu sırasını `orderDraft` yerel taslağına kopyalar, her öğede ↑/↓ yalnız taslağı değiştirir, "Sırayı kaydet" ancak o an `PUT /lists/{id}/order`'ı tetikler, "Vazgeç" taslağı atar — bu adım [M] boyutlu olduğu için iyimser önbellek güncellemesi yerine bilinçli olarak sade invalidate+refetch tercih edildi). Öğe ızgarası `ContentGrid`'in `PosterCard` + `!w-full` + `xl:grid-cols-6` desenini birebir kullanıyor; her kartın altında sahibi için not ekle/düzenle (satır içi `<textarea>` + Kaydet/Vazgeç — tarayıcı `prompt()`/`alert()` kullanılmadı, F3.9'un kabul kriteriyle uyumlu) ve Kaldır bağlantıları.
  - Gizli listeye sahip olmayan/anonim erişim zaten backend'de (`lists/service.py::get_list_detail`) 404 döndürüyordu (F1.9'dan beri); frontend tarafında yalnız diğer sayfalarla birebir aynı `is404` (`ApiError.status===404`) + `EmptyState` deseni uygulandı — yeni bir backend değişikliği gerekmedi.
  - `router/index.ts`: `/liste/:id` artık `ComingSoonPage` değil, gerçek `ListPage.vue` (`props: (route) => ({ id: String(route.params.id) })`).
  - **Kusur düzeltmesi (commit'ten önce, kod incelemesinde yakalandı):** İlk taslakta liste öğeleri ızgarasında `PosterCard` sabit genişliğiyle (`w-36`) render ediliyordu; `ContentGrid.vue` referans alınınca `!w-full` sınıfı + `xl:grid-cols-6` kırılım noktasının eksik olduğu görüldü, düzeltildi — böylece liste sayfasındaki ızgara `ContentGrid` kullanan diğer tüm sayfalarla (Keşfet, Profil/Kütüphane) görsel olarak tutarlı.
- **Değişen dosyalar:** `frontend/src/api/lists.ts`, `frontend/src/components/lists/ListFormModal.vue` (yeni, `CreateListModal.vue`'nin yerine), `frontend/src/pages/ListPage.vue` (yeni), `frontend/src/pages/ProfilePage.vue`, `frontend/src/router/index.ts`.
- **Doğrulama:** `npm run lint` → temiz ✓ · `npm run type-check` → temiz ✓ · `npm run test:unit -- run` → 64 passed (yeni saf mantık eklenmedi, mevcut testler bozulmadı) ✓ · `npm run build` → başarılı, `ListPage` (6.86 KB, gzip 2.78 KB) ve `ListFormModal` (2.19 KB, gzip 1.12 KB) kendi lazy chunk'larında ✓ · Vite dev sunucusunda `/liste/:id` rotası + değişen modüller tek tek istendi, hepsi 200 ✓ · **gerçek backend'e karşı uçtan uca (httpx betiği, iki test kullanıcısıyla, kitap tarafı — TMDB U2'yi bekliyor):** liste oluştur → 2 öğe ekle (201; aynı öğeyi tekrar eklemek 200 idempotent) → detay sahip/başka kullanıcı/anonim'de herkese açıkken hepsi 200 ✓; öğe notu güncelle ✓; `PUT /order` ile sıra ters çevrilip detayda doğrulandı ✓; başkası başlığı değiştirmeye/öğe silmeye çalışınca 403 ✓; sahibi öğe kaldırır → `item_count` düşüyor ✓; sahibi başlığı değiştirip gizliye çevirir → artık başkası/anonim 404, sahibi hâlâ 200 ✓; `/users/{u}/lists` gizli listeyi başkasına göstermiyor, sahibine gösteriyor ✓; sahibi siler → 204, tekrar istek 404 ✓. 22/22 kontrol geçti, iki test kullanıcısı da script sonunda silindi.
  - **Bilinçli kapsam sınırlaması:** `/_ui` vitrinine liste bileşenleri eklenmedi (F3.6'da `CreateListModal` için de aynı karar alınmıştı — gerçek bir liste kimliği gerektiriyor); doğrulama `ProfilePage`'in Listeler sekmesi + yukarıdaki gerçek backend testiyle yapıldı.
  - **Kalıcı sınırlama:** Tarayıcı aracı bu oturumda da yok — görsel doğrulama kod incelemesi + lint/type-check/test/build + gerçek backend'e karşı uçtan uca istekle yapıldı.
- **Kapanan maddeler:** REQ-2.1.5e (özel listeler, artık tam)
- **Commit:** `813b5e9`
- **Notlar / sorunlar:** Önceki oturum kullanım limitine takıldığı için bu oturum önce yarım kalan F3.6 ilerleme-durumu commit'ini tamamladı (`d0fc66f`), sonra F3.7'ye devam etti — kod tarafı (`f61e341`) zaten önceki oturumda commit edilmişti, kayıp olmadı.
- **Sonraki adım:** F3.8 — Ayarlar sayfası

### [2026-09-27] F3.6 — Profil sayfası — ✅

- **Yapılanlar:**
  - `api/stats.ts`: `useProfileSummary` (`/users/{username}/summary`). `api/users.ts`: `useProfile`, `useFollowers`/`useFollowing` (`enabled` parametreli — modal açıkken VE doğru moddayken çalışıyor, gereksiz çift istek yok), `useUploadAvatar`/`useRemoveAvatar` (`POST`/`DELETE /users/me/avatar`, `FormData` — `client.ts`'in F2.3'ten beri var olan FormData desteği ilk kez gerçek kullanıcıya dönük bir akışta devreye girdi). `api/social.ts`: `useUserActivities` (cursor), `useUserReviews` (sayfalı).
  - `FollowButton.vue` (yeni, `components/users/`): "Takip Et" / "Takip Ediliyor" (üzerine gelince "Takipten Çık" — kırmızı vurgulu).
  - `ProfileHeader.vue` (yeni): avatar, ad, @kullanıcıadı, "Seni takip ediyor" rozeti, biyografi, katılım tarihi, sayaçlar (Takipçi/Takip tıklanabilir → `UserListModal`; Film/Dizi/Kitap/İnceleme `ProfileSummaryOut`'tan), kendi profilinde Profili Düzenle+Yeni Liste / başkasınınkinde `FollowButton`.
  - `UserListModal.vue` (yeni): takipçi/takip edilen listesi, `PublicUserWithFollowOut`'un gerçek `is_following` alanını kullanıyor (arama sonuçlarının aksine burada baştan doğru — F3.2/F3.5'teki "başlangıçta bilinmiyor" sınırlaması bu modalde yok).
  - `EditProfileModal.vue` (yeni): görünen ad, biyografi (300 karakter), kullanıcı adı (canlı ipucu + `USERNAME_TAKEN` 409'unu alan hatası olarak gösterme — `RegisterPage`'deki desenin aynısı), avatar yükleme (dosya seçince anında önizleme için `URL.createObjectURL`, kaydedince gerçek `POST`) ve kaldırma.
  - `ListCard.vue` + `CreateListModal.vue` (yeni, `components/lists/`): kolaj (ilk 4 kapak 2×2, boşsa degrade arka plan), yeni liste formu (başlık/açıklama/herkese açık) → oluşturunca `/liste/:id`'ye yönlendiriyor (sayfa henüz `ComingSoonPage`, F3.7'yi bekliyor).
  - `ProfilePage.vue` (`/u/:username`, route-level `props` ile `username` enjekte ediliyor): 6 sekme (`?sekme=` URL'de) — **Aktiviteler** (`ActivityCard` listesi + sayfalama), **Kütüphane** (7 alt filtre: İzlediklerim/İzlenecekler/İzliyorum/Okuduklarım/Okunacaklar/Okuyorum/Yarım Bıraktıklarım + 4 sıralama, `ContentGrid`), **Puanlar** (kütüphaneyi `sort=rating` çekip istemci tarafında `rating!==null` filtresi), **İncelemeler** (`ReviewItem` listesi), **Listeler** (`ListCard` ızgarası), **Favoriler** (`favorite=true` filtresi). 404/hata durumları, `document.title`.
  - **Bilinçli basitleştirme:** "İzlediklerim/İzlenecekler/İzliyorum" alt filtreleri şu an yalnız `type=movie` sorguluyor (dizi içeriği henüz sistemde yok — F4.1'i bekliyor); dizi desteği gelince bu üç filtrenin movie+tv'yi birleştirmesi gerekecek (backend `type` parametresi tek değer aldığı için iki ayrı sorgu birleştirilecek).
- **Değişen dosyalar:** `frontend/src/api/{stats,users,social}.ts`, `frontend/src/components/users/{FollowButton,ProfileHeader,EditProfileModal,UserListModal}.vue` (yeni), `frontend/src/components/lists/{ListCard,CreateListModal}.vue` (yeni), `frontend/src/pages/ProfilePage.vue` (yeni), `frontend/src/router/index.ts`.
- **Doğrulama:** `npm run lint` → temiz ✓ · `npm run type-check` → temiz ✓ · `npm run test:unit -- run` → 64 passed ✓ · `npm run build` → başarılı, `ProfilePage` kendi lazy chunk'ında (17.37 KB, gzip 5.76 KB) ✓ · Vite dev sunucusunda 10 yeni/değişen modül + `/u/demo1` rotası tek tek istendi, hepsi 200 ✓ · **gerçek backend'e karşı uçtan uca (curl):** `users/demo1` + `/summary` + `/followers` + `/library?type=book&status=completed&sort=rating` + `/reviews` + `/lists` (gerçek seed verisiyle) hepsi tipleriyle birebir eşleşti; yeni test kullanıcısıyla takip et → `followers_count` arttı ve `is_following:true` yansıdı ✓; `username=demo2`'ye değiştirmeye çalışınca 409 `USERNAME_TAKEN` ✓; 1×1 PNG ile avatar yükle → `{avatar_url}` döndü, kaldır → `{avatar_url:null}` ✓; test kullanıcısı silinince demo1'in takipçi sayısı otomatik 2'ye geri döndü (cascade doğrulandı) ✓.
- **Kapanan maddeler:** BUG-09, REQ-2.1.5a/b/c/d/f (REQ-2.1.5e kısmi — `/liste/:id` F3.7'yi bekliyor)
- **Commit:** `f61e341`
- **Notlar / sorunlar:** Tarayıcı aracı hâlâ yok. Bağlam özeti bu adımda F3.1–F3.6 için tek bir paragrafta kısaltıldı (Faz 1 kapanışında yapıldığı gibi) — ayrıntılar aşağıdaki tarihli günlük girdilerinde duruyor.
- **Sonraki adım:** F3.7 — Listeler

### [2026-09-27] F3.5 — Akış (feed) sayfası — ✅

- **Yapılanlar:**
  - `api/social.ts`: `useFeed(scope)` (`CursorPage<ActivityOut>`, 15'er). `useLike()` — bu oturumun İLK gerçek TanStack cache-seviyeli iyimser güncellemesi: `onMutate`'te `queryClient.setQueriesData({queryKey:['feed']}, ...)` ile `['feed','following']` VE `['feed','global']` sorgularının her ikisinde de (aynı aktivite ikisinde de görünebileceği için) eşleşen kartı doğrudan yamalıyor (`liked_by_me`+`likes_count`), hata olursa `onError`'da `previous` snapshot'ıyla geri alıyor. Diğer bileşenlerdeki yerel-overlay deseninden bilinçli bir sapma — plan burada açıkça "akış önbelleğindeki kartı günceller" diyor.
  - `utils/activity.ts` (yeni): `activityActionText(activity)` — planın 5 `card_type` için verdiği tam aksiyon metni eşlemesi (rating: "bir X puanladı"; review: "bir X hakkında inceleme yazdı"; status: film/dizi ve kitap için ayrı fiiller; list_add: "'{liste}' listesine ekledi"; list_create: "yeni bir liste oluşturdu"). 4 test.
  - `ActivityCard.vue` (yeni): ortak başlık (avatar+ad+aksiyon metni+göreli tarih, `title` özniteliğinde tam tarih) + `card_type`'a göre 5 gövde + ortak alt bilgi (`LikeButton`+"Yorum yap"+Paylaş).
  - **F3.4'te alınan bir kararın düzeltilmesi:** `CommentThread`'in `compact` modu girdi kutusunu gizliyordu; bu adımda planın "son 2 yorum + giriş + 'Tüm yorumlar'" ifadesiyle çeliştiği fark edildi — girdi kutusu artık `compact`'te de gösteriliyor, yalnızca gösterilen yorum sayısı ve "daha fazla" sayfalaması kısıtlanıyor. `CommentThread`'e yeni `expand` olayı eklendi ("Tüm yorumlar (N)" bağlantısı tıklanınca `compact→full`).
  - `FeedPage.vue` (`/`): Takip Ettiklerim/Herkes sekmeleri — ilk `following` sonucu boş gelirse otomatik `global`'e geçiyor (doğrudan bir "takip sayısı" alanı olmadığı için "kimseyi takip etmiyorsa" durumunu dolaylı ama pratik biçimde yakalıyor; kullanıcı sekmeyi elle değiştirirse bu otomatik geçiş bir daha tetiklenmiyor), "Arkadaşlarını bul" kartı, gerçek `IntersectionObserver` (rootMargin 400px) + görünür "Daha fazla yükle" butonu + son sayfada "Hepsi bu kadar 🎉", masaüstü kenar çubuğu ("Kimi takip etmeli?" + "Trend Kitaplar"), 3 iskelet kart/hata/sekmeye özel boş durumlar.
  - **Yeniden kullanım:** `composables/useFollowToggle.ts` (yeni) — F3.2'de `DiscoverPage`'e özel yazılmış takip et/bırak mantığı, `FeedPage`'in kenar çubuğu da aynı ihtiyacı duyunca paylaşılan composable'a çıkarıldı (ikinci gerçek ihtiyaç anı, erken soyutlama değil); `DiscoverPage` da kullanacak şekilde refactor edildi, davranış değişmedi.
  - **Bilinçli kapsam sınırlaması:** `/_ui` vitrinine `ActivityCard` sahte `ActivityOut` verisiyle eklendi (5 `card_type`'ın hepsi) — beğeni/yorum tıklamaları sahte aktivite kimliğine gittiği için hata toast'u gösterebilir, sayfada not olarak da belirtildi.
- **Değişen dosyalar:** `frontend/src/api/social.ts`, `frontend/src/utils/{activity,activity.spec}.ts` (yeni), `frontend/src/components/content/{ActivityCard,CommentThread}.vue` (ActivityCard yeni), `frontend/src/composables/useFollowToggle.ts` (yeni), `frontend/src/pages/{FeedPage,DiscoverPage,UiShowcasePage}.vue` (FeedPage yeni), `frontend/src/router/index.ts`.
- **Doğrulama:** `npm run lint` → temiz ✓ · `npm run type-check` → temiz ✓ · `npm run test:unit -- run` → **64 passed** (4 yeni) ✓ · `npm run build` → başarılı, `FeedPage` kendi lazy chunk'ında (11.14 KB, gzip 3.82 KB) ✓ · Vite dev sunucusunda 6 yeni/değişen modül + `/` rotası tek tek istendi, hepsi 200 ✓ · **gerçek backend'e karşı (curl):** `GET /feed?scope=global&limit=50` gerçek seed verisiyle **5 `card_type`'ın tamamını** döndürdü (12 rating, 5 review, 23 status, 8 list_add, 2 list_create) — hepsi `ActivityOut` tipiyle birebir eşleşti; bir "status" (kitap, planned→"okunacaklarına ekledi") ve bir "review" (puan+kesilmemiş alıntı) örneği elle incelenip `activityActionText`'in ürettiği metinle karşılaştırıldı, doğru.
- **Kapanan maddeler:** BUG-12 (tam), BUG-13 (tam), REQ-2.1.2 (tümü: a-g)
- **Commit:** `54750e5`
- **Notlar / sorunlar:** Tarayıcı aracı hâlâ yok — sekme geçişi/sonsuz kaydırma/iyimser beğeni animasyonunun görsel doğrulaması yalnızca kod incelemesi + yukarıdaki testlerle yapıldı.
- **Sonraki adım:** F3.6 — Profil sayfası

### [2026-09-27] F3.4 — İnceleme sayfası ve yorum dizisi — ✅

- **Yapılanlar:**
  - `api/social.ts`: `useComments` (`useInfiniteQuery`, `CursorPage` — backend'in `list_comments`'ı gerçekte **eskiden yeniye** ilerliyor, `cursor` "bu id'den büyük olanları getir" anlamına geliyor; planın "imleçli 'Önceki yorumları göster'" ifadesi bu yönle tam örtüşmediği için buton nötr "Daha fazla yorum göster" adlandırıldı — küçük ölçekli bir uygulamada bu ayrım pratikte önemli değil, çoğu aktivitenin 20'den az yorumu olacak), `useAddComment`/`useUpdateComment`/`useDeleteComment`.
  - `LikeButton.vue` (yeni, paylaşılan): kalp+sayı, `aria-pressed`, kısa CSS keyframe "pulse" (beğenince). `ReviewItem`'in F3.3'te yazılmış kendi iç kalp butonu bu bileşene geçirildi (mantık/optimistic state `ReviewItem`'de kaldı, yalnız görsel kısım paylaşıldı).
  - `CommentThread.vue` (yeni): yorum listesi + "Daha fazla yorum göster", ekleme (Enter gönderir/Shift+Enter yeni satır/1000 karakter sayacı), yerel `pendingComments` overlay'iyle iyimser ekleme (TanStack cache'i değil — `useContentActions`'daki aynı yerel-overlay deseni), satır içi düzenleme, silme — `can_edit`/`can_delete` bayrakları **backend tarafından zaten hesaplanıp gönderiliyor** (istemci tarafında ayrıca `author.id===me.id` hesabı gerekmedi), `compact` prop'u (son 2 yorum, F3.5'in akış kartlarında kullanılacak).
  - `ReviewPage.vue` (`/inceleme/:id`, route-level `props` ile `id` enjekte ediliyor): içerik mini başlığı (afiş+başlık+yıl→detay), yazar (avatar+ad→profil+göreli tarih+"düzenlendi"), `RatingDisplay`, tam metin+spoiler bulanıklığı, `LikeButton`, Paylaş, sahibiyse satır içi Düzenle+Sil, `CommentThread`. 404/hata/yükleniyor durumları, `document.title`.
  - **Tasarım kararı (ReviewEditor'ı burada yeniden kullanmadım):** `ReviewEditor` kendi `useReviewDetail` sorgusunu tekrar tetikleyip çift veri çekimine yol açardı ve yazar bilgisi/puan/beğeni gibi ReviewPage'e özel alanları göstermiyor; bu yüzden ReviewPage kendi küçük düzenleme formunu (textarea+spoiler onay kutusu+Kaydet/Vazgeç) doğrudan yazdı — küçük, göze görünür bir tekrar ama iki farklı görüntüleme bağlamını zorla birleştirmekten daha temiz.
  - **Bilinçli kapsam sınırlaması:** `/_ui` vitrinine `CommentThread` eklenmedi (gerçek bir `activityId` gerektiriyor, sahte biriyle yalnızca hata durumu gösterirdi); bunun yerine gerçek backend'e karşı curl ile kapsamlı doğrulandı. `LikeButton` yerel sahte durumla vitrine eklendi.
- **Değişen dosyalar:** `frontend/src/api/social.ts`, `frontend/src/components/content/{LikeButton,CommentThread}.vue` (yeni), `frontend/src/components/content/ReviewItem.vue` (LikeButton'a geçirildi), `frontend/src/pages/ReviewPage.vue` (yeni), `frontend/src/pages/UiShowcasePage.vue`, `frontend/src/router/index.ts`.
- **Doğrulama:** `npm run lint` → temiz ✓ · `npm run type-check` → temiz ✓ · `npm run test:unit -- run` → 60 passed ✓ · `npm run build` → başarılı, `ReviewPage` kendi lazy chunk'ında (11.37 KB, gzip 4.02 KB) ✓ · Vite dev sunucusunda 5 yeni/değişen modül + `/inceleme/:id` rotası tek tek istendi, hepsi 200 ✓ · **gerçek backend'e karşı uçtan uca (curl, iki test kullanıcısıyla):** yorum ekle → sahibi için `can_edit`/`can_delete:true` ✓; başkası görünce ikisi de `false` ✓; başkası düzenlemeye çalışınca 403 ✓; sahibi düzenliyor → `updated_at` değişiyor ✓; **aktivite sahibi (yorum sahibi değil) başkasının yorumunu siliyor → 204** (F1.8'in "sahip veya aktivite sahibi silebilir" kuralı canlı doğrulandı) ✓. Test kullanıcıları temizlendi.
- **Kapanan maddeler:** REQ-2.1.4h
- **Commit:** `6979589`
- **Notlar / sorunlar:** REQ-2.1.2f (akış kartında alıntı → tam metin) bu adımda kapatılmadı — o, F3.5'in `ActivityCard`'ının işi (bu adım yalnızca HEDEF sayfayı, yani `/inceleme/:id`'yi kurdu). Tarayıcı aracı hâlâ yok.
- **Sonraki adım:** F3.5 — Akış (feed) sayfası

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
