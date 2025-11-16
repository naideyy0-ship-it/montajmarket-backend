from fastapi import FastAPI
from pydantic import BaseModel
import psycopg2
import os

app = FastAPI()

# Veritabanı bağlantısı
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

# Model: İş Kalemi
class IsKalemi(BaseModel):
    ad: str
    birim: str
    fiyat: float

@app.get("/")
def root():
    return {"mesaj": "MontajMarket Backend Çalışıyor 🚀"}

@app.post("/is_kalemi_ekle")
def is_kalemi_ekle(kalem: IsKalemi):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS is_kalemleri (
            id SERIAL PRIMARY KEY,
            ad TEXT,
            birim TEXT,
            fiyat FLOAT
        )
    """)
    cur.execute("INSERT INTO is_kalemleri (ad, birim, fiyat) VALUES (%s, %s, %s)",
                (kalem.ad, kalem.birim, kalem.fiyat))
    conn.commit()
    cur.close()
    conn.close()
    return {"durum": "başarılı", "veri": kalem}

@app.get("/is_kalemleri")
def listele():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM is_kalemleri")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return {"is_kalemleri": rows}
