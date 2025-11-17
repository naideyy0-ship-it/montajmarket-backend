from sqlalchemy import Column, Integer, String, Float
from database import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)              # Proje adı (örn: Ford Otosan platform işi)
    location = Column(String, index=True)          # Proje yeri (örn: Eskişehir / Afyon / Ankara)
    description = Column(String)                   # İsteğe bağlı açıklama
    total_cost = Column(Float, default=0)          # Teklif toplamı
