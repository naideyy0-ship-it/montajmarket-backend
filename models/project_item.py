from sqlalchemy import Column, Integer, Float
from database import Base

class ProjectItem(Base):
    __tablename__ = "project_items"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, index=True)        # Hangi projeye ait
    job_item_id = Column(Integer, index=True)       # Hangi iş kalemi
    quantity = Column(Float)                        # Miktar (kg, m2, adet)
    total = Column(Float)                           # Hesaplanan toplam fiyat
