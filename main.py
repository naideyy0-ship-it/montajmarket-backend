from fastapi import FastAPI
import psycopg2
from psycopg2.extras import RealDictCursor
import os

app = FastAPI(title="Montaj Market API", version="1.0")

# --- Veritabanı bağlantısı ---
DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

# --- Test endpoint ---
@app.get("/test")
def test():
    return {"durum": "OK", "bilgi": "API çalışıyor 🔥"}

# --- İş kalemi ekleme ---
@app.post("/is_kalemi_ekle")
def is_kalemi_ekle(ad: str, birim_fiyat: float, birim: str):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "CREATE TABLE IF NOT EXISTS is_kalemi (id SERIAL PRIMARY KEY, ad TEXT, birim_fiyat FLOAT, birim TEXT)"
        )
        cur.execute(
            "INSERT INTO is_kalemi (ad, birim_fiyat, birim) VALUES (%s, %s, %s)",
            (ad, birim_fiyat, birim),
        )
        conn.commit()
        cur.close()
        conn.close()
        return {"durum": "başarılı", "mesaj": f"{ad} iş kalemi eklendi 💪"}
    except Exception as e:
        return {"durum": "hata", "mesaj": str(e)}

# --- Tüm iş kalemlerini listeleme ---
@app.get("/is_kalemleri")
def is_kalemleri():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM is_kalemi")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return {"is_kalemleri": rows}
