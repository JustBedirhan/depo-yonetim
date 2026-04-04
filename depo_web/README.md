# Depo Yönetimi — Web Uygulaması

## Deploy Adımları (Render.com — Ücretsiz)

### 1. GitHub'a Yükle
1. github.com adresinde hesap aç (yoksa)
2. Yeni repository oluştur: "depo-yonetim" 
3. Bu klasördeki tüm dosyaları yükle

### 2. Render.com'a Deploy Et
1. render.com adresine git, GitHub ile giriş yap
2. "New +" → "Web Service" tıkla
3. GitHub reposunu seç
4. Şu ayarları gir:
   - Build Command: `pip install -r requirements.txt`
   - Start Command:  `gunicorn app:app`
5. "New +" → "PostgreSQL" ile ücretsiz veritabanı oluştur
6. Web Service'in Environment Variables kısmına ekle:
   - DATABASE_URL = (PostgreSQL bağlantı adresi — Render otomatik verir)
   - SECRET_KEY   = (istediğin rastgele bir metin, örn: "gizli123abc")
7. "Deploy" tıkla — 2-3 dakika bekle

### 3. Giriş
- URL: https://depo-yonetim.onrender.com (Render'ın verdiği link)
- Kullanıcı adı: admin
- Şifre: admin123  ← İLK GİRİŞTE DEĞİŞTİR!

## Yerel Test (isteğe bağlı)
```
pip install flask psycopg2-binary
python app.py
```
Localhost için DATABASE_URL yerine SQLite kullanmak istersen app.py'deki
get_db() fonksiyonunu düzenleyebilirsin.
