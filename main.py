from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import os

# Router import (SADECE 1 TANE!)
from routers import auth

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
    birim_fiyat: float
    birim: str

    class Config:
        orm_mode = True

# ----------------- HAZIR İŞ KALEMİ LİSTESİ -----------------
HAZIR_IS_KALEMLERI = [
    { "ad": "Çelik Konstrüksiyon İmalatı", "birim_fiyat": 450.0, "birim": "kg" },
    { "ad": "Çelik Konstrüksiyon Montajı", "birim_fiyat": 500.0, "birim": "kg" },
    { "ad": "Çelik Konstrüksiyon Demontajı", "birim_fiyat": 180.0, "birim": "kg" },
    { "ad": "Sandviç Panel Çatı Montajı", "birim_fiyat": 350.0, "birim": "m2" },
    { "ad": "Sandviç Panel Cephe Montajı", "birim_fiyat": 320.0, "birim": "m2" },
    { "ad": "Eski Çatı / Panel Sökümü", "birim_fiyat": 120.0, "birim": "m2" },
    { "ad": "Trapez Saç Kaplama", "birim_fiyat": 220.0, "birim": "m2" },
    { "ad": "Askı Detayı / Ankraj Montajı", "birim_fiyat": 150.0, "birim": "adet" },
    { "ad": "Korkuluk / Platform Montajı", "birim_fiyat": 400.0, "birim": "m" },
    { "ad": "Çelik İmalat Atölye İşçiliği", "birim_fiyat": 90.0, "birim": "kg" },
]

# ----------------- APP -----------------
app = FastAPI(title="Montaj Market API")
app.include_router(auth.router)   # SADECE BİR KEZ!

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ----------------- ENDPOINTLER -----------------

@app.get("/test")
def test_endpoint():
    return {"status": "OK", "info": "API çalışıyor!"}

@app.post("/is_kalemi_ekle")
def is_kalemi_ekle(kalem: IsKalemiCreate, db: Session = Depends(get_db)):
    db_kalem = IsKalemi(**kalem.dict())
    db.add(db_kalem)
    db.commit()
    db.refresh(db_kalem)
    return {"durum": "başarılı", "id": db_kalem.id}

@app.get("/is_kalemleri")
def is_kalemleri(db: Session = Depends(get_db)):
    return db.query(IsKalemi).all()

@app.post("/is_kalemi_toplu_ekle")
def is_kalemi_toplu_ekle(kalemler: List[IsKalemiCreate], db: Session = Depends(get_db)):
    db.add_all([IsKalemi(**k.dict()) for k in kalemler])
    db.commit()
    return {"durum": "başarılı", "adet": len(kalemler)}

@app.post("/is_kalemleri_hazir_doldur")
def is_kalemleri_hazir_doldur(db: Session = Depends(get_db)):
    mevcut = db.query(IsKalemi).count()
    if mevcut > 0:
        return {"durum": "zaten_var"}

    nesneler = [IsKalemi(**k) for k in HAZIR_IS_KALEMLERI]
    db.add_all(nesneler)
    db.commit()
    return {"durum": "başarılı", "eklenen": len(nesneler)}

# --- Teklif ---
class TeklifKalemi(BaseModel):
    is_kalemi_id: int
    miktar: float

class TeklifIstegi(BaseModel):
    kalemler: List[TeklifKalemi]
    kar_orani: Optional[float] = 0.0

@app.post("/teklif_hesapla")
def teklif_hesapla(istek: TeklifIstegi, db: Session = Depends(get_db)):
    ara = 0.0
    detay = []

    for satir in istek.kalemler:
        kalem = db.query(IsKalemi).get(satir.is_kalemi_id)
        if not kalem:
            raise HTTPException(404, f"İş kalemi yok: {satir.is_kalemi_id}")

        tutar = kalem.birim_fiyat * satir.miktar
        ara += tutar

        detay.append({
            "ad": kalem.ad,
            "birim_fiyat": kalem.birim_fiyat,
            "miktar": satir.miktar,
            "tutar": tutar
        })

    kar = ara * (istek.kar_orani / 100)
    genel = ara + kar

    return {
        "ara_toplam": ara,
        "kar": kar,
        "genel_toplam": genel,
        "kalemler": detay
    }
