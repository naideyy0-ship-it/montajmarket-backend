[
  { "ad": "Çelik Konstrüksiyon İmalatı",      "birim_fiyat": 450.0, "birim": "kg" },
  { "ad": "Çelik Konstrüksiyon Montajı",     "birim_fiyat": 500.0, "birim": "kg" },
  { "ad": "Çelik Konstrüksiyon Demontaj",    "birim_fiyat": 180.0, "birim": "kg" },
  { "ad": "Sandviç Panel Çatı Montajı",      "birim_fiyat": 350.0, "birim": "m2" },
  { "ad": "Sandviç Panel Cephe Montajı",     "birim_fiyat": 320.0, "birim": "m2" },
  { "ad": "Eski Çatı / Panel Sökümü",        "birim_fiyat": 120.0, "birim": "m2" },
  { "ad": "Trapez Saç Kaplama",              "birim_fiyat": 220.0, "birim": "m2" },
  { "ad": "Askı Detayı / Ankraj Montajı",    "birim_fiyat": 150.0, "birim": "adet" },
  { "ad": "Korkuluk / Platform Montajı",     "birim_fiyat": 400.0, "birim": "m" },
  { "ad": "Çelik İmalat Atölye İşçiliği",    "birim_fiyat": 90.0,  "birim": "kg" }
]
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


class IsKalemi(Base):
    __tablename__ = "is_kalemleri"

    id = Column(Integer, primary_key=True, index=True)
    ad = Column(String, nullable=False)
    birim_fiyat = Column(Float, nullable=False)
    birim = Column(String, nullable=False)


Base.metadata.create_all(bind=engine)


class IsKalemiCreate(BaseModel):
    ad: str
    birim_fiyat: float
    birim: str

    class Config:
        orm_mode = True


app = FastAPI(title="Montaj Market API")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/test")
def test_endpoint():
    return {"status": "OK", "info": "API başarılı şekilde yayında!"}


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


@app.get("/is_kalemleri")
def is_kalemleri(db: Session = Depends(get_db)):
    return db.query(IsKalemi).all()


# ✅ TOPLU EKLEME ENDPOINT
@app.post("/is_kalemi_toplu_ekle")
def is_kalemi_toplu_ekle(kalemler: List[IsKalemiCreate], db: Session = Depends(get_db)):
    db.add_all([IsKalemi(**k.dict()) for k in kalemler])
    db.commit()
    return {"durum": "başarılı", "adet": len(kalemler)}

