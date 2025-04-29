from typing import List
from sqlalchemy import ForeignKey, String, Integer, Enum
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
import enum

class Base(DeclarativeBase):
    pass

class PlayerType(enum.Enum):
    WOLF = "wolf"
    VILLAGER = "villager"

class Game(Base):
    __tablename__ = 'game'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nb_max_turn: Mapped[int] = mapped_column(Integer, nullable=False)
    current_turn: Mapped[int] = mapped_column(Integer, default=0)
    players: Mapped[List["Player"]] = relationship(back_populates="game", cascade="all, delete-orphan")

class Player(Base):
    __tablename__ = 'player'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    pseudo: Mapped[str] = mapped_column(String(1), nullable=False)
    player_type: Mapped[PlayerType] = mapped_column(Enum(PlayerType), nullable=False)
    field_distance: Mapped[int] = mapped_column(Integer, nullable=False)
    position_x: Mapped[int] = mapped_column(Integer, nullable=True)
    position_y: Mapped[int] = mapped_column(Integer, nullable=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("game.id"))
    game: Mapped["Game"] = relationship(back_populates="players")

class GameBoard(Base):
    __tablename__ = 'game_board'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    width: Mapped[int] = mapped_column(Integer, nullable=False)
    height: Mapped[int] = mapped_column(Integer, nullable=False)
    game_id: Mapped[int] = mapped_column(ForeignKey("game.id"), unique=True)
    game: Mapped["Game"] = relationship()