from sqlalchemy import Column, Integer, String, Float
from database import Base

class JobItem(Base):
    __tablename__ = "job_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)          # Örn: Çelik Konstrüksiyon İmalatı
    unit = Column(String)                      # Birim: kg, m2, adet
    unit_price = Column(Float)                 # Birim fiyatı
