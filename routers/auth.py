from fastapi import APIRouter

router = APIRouter()

@router.post("/kayit")
def kayit():
    return {"durum": "ok", "mesaj": "Kayıt başarılı"}

@router.post("/giris")
def giris():
    return {"durum": "ok", "mesaj": "Giriş başarılı"}
