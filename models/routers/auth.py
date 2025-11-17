from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from Model.user import Kullanıcı
from passlib.context import CryptContext

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Şifre hashle
def sifrele(password: str):
    return pwd_context.hash(password)

# Şifre doğrula
def dogrula(password: str, hashed: str):
    return pwd_context.verify(password, hashed)

# Kullanıcı kayıt (signup)
@router.post("/kayit")
def kayit(isim: str, email: str, sifre: str, db: Session = Depends(get_db)):
    mevcut = db.query(Kullanıcı).filter(Kullanıcı.email == email).first()

    if mevcut:
        raise HTTPException(status_code=400, detail="Bu email zaten kayıtlı!")

    yeni = Kullanıcı(
        isim=isim,
        email=email,
        sifre=sifrele(sifre)
    )

    db.add(yeni)
    db.commit()
    db.refresh(yeni)

    return {"durum": "başarılı", "mesaj": "Kullanıcı kaydedildi", "kullanıcı": yeni.email}


# Kullanıcı giriş (login)
@router.post("/giris")
def giris(email: str, sifre: str, db: Session = Depends(get_db)):
    kullanıcı = db.query(Kullanıcı).filter(Kullanıcı.email == email).first()

    if not kullanıcı:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı!")

    if not dogrula(sifre, kullanıcı.sifre):
        raise HTTPException(status_code=400, detail="Şifre yanlış!")

    return {"durum": "başarılı", "mesaj": "Giriş başarılı", "kullanıcı": kullanıcı.email}
