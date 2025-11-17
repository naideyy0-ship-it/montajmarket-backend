from routers import auth
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import os

# ----------------- VERİTABANI AYARI -----------------
DATABASE_URL = os.environ.get("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ----------------- MODEL -----------------
class IsKalemi(Base):
    __tablename__ = "is_kalemleri"

    id = Column(Integer, primary_key=True, index=True)
    ad = Column(String, nullable=False)
    birim_fiyat = Column(Float, nullable=False)
    birim = Column(String, nullable=False)

Base.metadata.create_all(bind=engine)

# ----------------- SCHEMA -----------------
class IsKalemiCreate(BaseModel):
    ad: str
    from routers import auth

    birim_fiyat: float
    birim: str

    class Config:
        orm_mode = True

# ----------------- HAZIR İŞ KALEMİ LİSTESİ -----------------
HAZIR_IS_KALEMLERI = [
    { "ad": "Çelik Konstrüksiyon İmalatı",         "birim_fiyat": 450.0, "birim": "kg" },
    { "ad": "Çelik Konstrüksiyon Montajı",        "birim_fiyat": 500.0, "birim": "kg" },
    { "ad": "Çelik Konstrüksiyon Demontajı",      "birim_fiyat": 180.0, "birim": "kg" },
    { "ad": "Sandviç Panel Çatı Montajı",         "birim_fiyat": 350.0, "birim": "m2" },
    { "ad": "Sandviç Panel Cephe Montajı",        "birim_fiyat": 320.0, "birim": "m2" },
    { "ad": "Eski Çatı / Panel Sökümü",           "birim_fiyat": 120.0, "birim": "m2" },
    { "ad": "Trapez Saç Kaplama",                 "birim_fiyat": 220.0, "birim": "m2" },
    { "ad": "Askı Detayı / Ankraj Montajı",       "birim_fiyat": 150.0, "birim": "adet" },
    { "ad": "Korkuluk / Platform Montajı",        "birim_fiyat": 400.0, "birim": "m" },
    { "ad": "Çelik İmalat Atölye İşçiliği",       "birim_fiyat": 90.0,  "birim": "kg" },
]

# ----------------- APP -----------------
app = FastAPI(title="Montaj Market API")
app.include_router(auth.router)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Sadece test için
@app.get("/test")
def test_endpoint():
    return {"status": "OK", "info": "API başarılı şekilde yayında!"}

# Tekli ekleme
@app.post("/is_kalemi_ekle")
def is_kalemi_ekle(kalem: IsKalemiCreate, db: Session = Depends(get_db)):
    db_kalem = IsKalemi(**kalem.dict())
    db.add(db_kalem)
    db.commit()
    db.refresh(db_kalem)
    return {
        "durum": "başarılı",
        "mesaj": f"{db_kalem.ad} iş kalemi eklendi 💪",
        "id": db_kalem.id,
    }

# Listeleme
@app.get("/is_kalemleri")
def is_kalemleri(db: Session = Depends(get_db)):
    return db.query(IsKalemi).all()

# ✅ TOPLU EKLEME (Swagger'dan JSON liste yollayabilirsin)
@app.post("/is_kalemi_toplu_ekle")
def is_kalemi_toplu_ekle(kalemler: List[IsKalemiCreate], db: Session = Depends(get_db)):
    db.add_all([IsKalemi(**k.dict()) for k in kalemler])
    db.commit()
    return {"durum": "başarılı", "adet": len(kalemler)}

# ✅ TEK TIKLA HAZIR İŞ KALEMLERİNİ EKLE
@app.post("/is_kalemleri_hazir_doldur")
def is_kalemleri_hazir_doldur(db: Session = Depends(get_db)):
    # Veritabanında zaten kayıt varsa tekrar doldurmasın
    mevcut = db.query(IsKalemi).count()
    if mevcut > 0:
        return {"durum": "zaten_var", "mevcut_adet": mevcut}

    nesneler = [IsKalemi(**k) for k in HAZIR_IS_KALEMLERI]
    db.add_all(nesneler)
    db.commit()
    return {"durum": "başarılı", "eklenen": len(nesneler)}
from pydantic import BaseModel
from typing import List, Optional
from fastapi import Depends
from sqlalchemy.orm import Session
# --- Teklif hesaplama için şemalar ---

class TeklifKalemi(BaseModel):
    is_kalemi_id: int   # İş kalemi tablosundaki id
    miktar: float       # Ne kadar yapılacak? (kg, m2, adet vs.)

class TeklifIstegi(BaseModel):
    kalemler: List[TeklifKalemi]
    kar_orani: Optional[float] = 0.0   # Örn: 20 girersen %20 kâr
@app.post("/teklif_hesapla")
def teklif_hesapla(istek: TeklifIstegi, db: Session = Depends(get_db)):
    kalem_detaylari = []
    ara_toplam = 0.0

    for satir in istek.kalemler:
        is_kalemi = db.query(IsKalemi).get(satir.is_kalemi_id)
        if not is_kalemi:
            # Hatalı id gelirse
            raise HTTPException(status_code=404, detail=f"İş kalemi bulunamadı: {satir.is_kalemi_id}")

        satir_tutar = is_kalemi.birim_fiyat * satir.miktar
        ara_toplam += satir_tutar

        kalem_detaylari.append({
            "id": is_kalemi.id,
            "ad": is_kalemi.ad,
            "birim": is_kalemi.birim,
            "birim_fiyat": is_kalemi.birim_fiyat,
            "miktar": satir.miktar,
            "tutar": satir_tutar,
        })

    kar_orani = istek.kar_orani or 0.0
    kar_tutar = ara_toplam * (kar_orani / 100)
    genel_toplam = ara_toplam + kar_tutar

    return {
        "durum": "başarılı",
        "ara_toplam": ara_toplam,
        "kar_orani": kar_orani,
        "kar_tutar": kar_tutar,
        "genel_toplam": genel_toplam,
        "kalemler": kalem_detaylari,
    }
app.include_router(auth.router)
from routers import auth
app.include_router(auth.router)
from routers import auth
app.include_router(auth.router)

