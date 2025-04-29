from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
 
class Base(DeclarativeBase):
    pass

class Game(Base):
        __tablename__ = 'game'
        
        id : Mapped[int] = mapped_column(primary_key=True, autoincrement=True) 
        title : Mapped[str] = mapped_column(String(50), nullable=False)