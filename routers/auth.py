from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from pydantic import BaseModel
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta

router = APIRouter()

# Şifreleme
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "montajmarketsecret"
ALGORITHM = "HS256"

# --- Pydantic modelleri ---
class UserRegister(BaseModel):
    isim: str
    email: str
    sifre: str

class UserLogin(BaseModel):
    email: str
    sifre: str

# --- Yardımcı fonksiyonlar ---
def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def create_token(data: dict):
    expire = datetime.utcnow() + timedelta(hours=12)
    data.update({"exp": expire})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

# --- Kayıt ol ---
@router.post("/register")
def register_user(request: UserRegister, db: Session = Depends(get_db)):
    is_exist = db.query(User).filter(User.email == request.email).first()
    if is_exist:
        raise HTTPException(status_code=400, detail="Bu email zaten kayıtlı!")

    yeni = User(
        isim=request.isim,
        email=request.email,
        sifre=hash_password(request.sifre)
    )

    db.add(yeni)
    db.commit()
    db.refresh(yeni)

    return {"durum": "başarılı", "mesaj": "Kullanıcı oluşturuldu"}

# --- Giriş yap ---
@router.post("/login")
def login_user(request: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı!")

    if not verify_password(request.sifre, user.sifre):
        raise HTTPException(status_code=400, detail="Şifre yanlış!")

    token = create_token({"user_id": user.id})

    return {
        "durum": "başarılı",
        "token": token
    }
