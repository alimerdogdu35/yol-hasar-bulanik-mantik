# Yol Hasar Müdahale Önceliği Sistemi

Bu proje, bulanık mantık tabanlı bir karar destek sistemi olarak yol hasarlarının onarım/müdahale önceliğini hesaplar. Sistem; hasar şiddeti, yol kullanım yoğunluğu ve kaza riski girişlerini kullanarak 0-100 aralığında müdahale önceliği üretir.

## Projeyi Raporu
--Proje raporu drive linkli:
https://docs.google.com/document/d/1kaQdULSHV8DZBVYOMEaAmhdsi8kzQ6qS/edit?usp=sharing&ouid=105522682853803228890&rtpof=true&sd=true
## Proje Özeti

- **Yöntem:** Mamdani bulanık çıkarım sistemi
- **Giriş değişkenleri:**
  - Hasar Şiddeti
  - Yol Kullanım Yoğunluğu
  - Kaza Riski
- **Çıkış değişkeni:**
  - Müdahale Önceliği
- **Durulaştırma:** Ağırlık merkezi / Centroid yöntemi
- **Kural sayısı:** 27 adet IF-THEN kuralı
- **Arayüz:** Streamlit

## Klasör Yapısı

```text
yol_hasar_fuzzy_project/
├── app.py
├── requirements.txt
├── README.md
├── src/
│   ├── __init__.py
│   └── fuzzy_engine.py
├── tests/
│   └── test_engine.py
├── docs/
│   ├── Yol_Hasar_Bulanik_Mantik_Raporu.docx
│   └── Yol_Hasar_Bulanik_Mantik_Raporu.pdf
└── assets/
    ├── uyelik_fonksiyonlari.png
    ├── cikti_durulastirma.png
    └── test_senaryolari.png
```

## Kurulum

### 1. Sanal ortam oluşturun

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 2. Gerekli paketleri yükleyin

```bash
pip install -r requirements.txt
```

### 3. Uygulamayı çalıştırın

```bash
streamlit run app.py
```

Tarayıcıda otomatik olarak Streamlit arayüzü açılır. Açılmazsa terminalde görünen yerel adresi kopyalayıp tarayıcıya yapıştırın.

## Testleri Çalıştırma

```bash
python -m pytest tests/test_engine.py
```

## Sistem Mantığı

Sistem üç giriş değerini 0-100 aralığında alır. Her giriş değişkeni için düşük, orta ve yüksek olmak üzere üç dilsel küme tanımlanmıştır. Çıkış değişkeni ise düşük, orta, yüksek ve kritik kümeleriyle modellenmiştir.

Kurallar Mamdani yaklaşımıyla değerlendirilir:

- AND işlemi: minimum operatörü
- Kural çıktılarının birleşimi: maksimum operatörü
- Durulaştırma: centroid yöntemi

## Örnek Kullanım

Örnek giriş değerleri:

- Hasar Şiddeti: 85
- Yol Kullanım Yoğunluğu: 90
- Kaza Riski: 80

Beklenen yorum: Bu değerler yüksek hasar, yoğun kullanım ve yüksek güvenlik riski gösterdiği için sistemin kritik müdahale önceliği üretmesi beklenir.


