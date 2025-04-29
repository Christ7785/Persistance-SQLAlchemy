from typing import List, Tuple
from sqlalchemy import ForeignKey, String, Integer, Enum, JSON
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
import enum
import random

class Base(DeclarativeBase):
    pass

class PlayerType(enum.Enum):
    WOLF = "wolf"
    VILLAGER = "villager"
    EMPTY = "empty"

class Game(Base):
    __tablename__ = 'game'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nb_max_turn: Mapped[int] = mapped_column(Integer, nullable=False)
    current_turn: Mapped[int] = mapped_column(Integer, default=0)
    width: Mapped[int] = mapped_column(Integer, nullable=False)
    height: Mapped[int] = mapped_column(Integer, nullable=False)
    actions: Mapped[dict] = mapped_column(JSON, default={})
    players: Mapped[List["Player"]] = relationship(back_populates="game", cascade="all, delete-orphan")
    board: Mapped["GameBoard"] = relationship(back_populates="game", uselist=False, cascade="all, delete-orphan")

    def __init__(self, nb_max_turn: int, width: int, height: int):
        self.nb_max_turn = nb_max_turn
        self.width = width
        self.height = height
        self.current_turn = 0
        self.actions = {}
        self.board = GameBoard(width=width, height=height, game=self)

    def register_action(self, player_id: int, action: Tuple[int, int]):
        self.actions[str(player_id)] = action

    def process_actions(self):
        for player_id, action in self.actions.items():
            player = next((p for p in self.players if str(p.id) == player_id), None)
            if player:
                self.board.move_player(player, action)
        self.actions = {}
        self.board.end_round()

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

    def __init__(self, pseudo: str, player_type: PlayerType, field_distance: int):
        if len(pseudo) != 1:
            raise ValueError('Max length of pseudo is 1')
        self.pseudo = pseudo
        self.player_type = player_type
        self.field_distance = field_distance
        self.position_x = None
        self.position_y = None

    @property
    def position(self) -> Tuple[int, int]:
        return (self.position_x, self.position_y)

    @position.setter
    def position(self, value: Tuple[int, int]):
        self.position_x, self.position_y = value

    def __str__(self):
        if self.player_type == PlayerType.WOLF:
            return 'W'
        elif self.player_type == PlayerType.VILLAGER:
            return 'O'
        return '.'

    def __gt__(self, other: "Player") -> bool:
        if self.player_type == PlayerType.WOLF:
            return other.player_type in [PlayerType.VILLAGER, PlayerType.EMPTY]
        elif self.player_type == PlayerType.VILLAGER:
            return other.player_type == PlayerType.EMPTY
        return False

class GameBoard(Base):
    __tablename__ = 'game_board'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    width: Mapped[int] = mapped_column(Integer, nullable=False)
    height: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[List[List[str]]] = mapped_column(JSON)
    next_content: Mapped[List[List[str]]] = mapped_column(JSON)
    available_positions: Mapped[List[Tuple[int, int]]] = mapped_column(JSON)
    game_id: Mapped[int] = mapped_column(ForeignKey("game.id"), unique=True)
    game: Mapped["Game"] = relationship(back_populates="board")

    def __init__(self, width: int, height: int, game: Game):
        self.width = width
        self.height = height
        self.game = game
        self.content = [['.'] * width for _ in range(height)]
        self.next_content = [['.'] * width for _ in range(height)]
        self.available_positions = [(w, h) for h in range(height) for w in range(width)]

    def subscribe_player(self, player: Player):
        if not self.available_positions:
            print('No more space to play')
            return False
            
        pos = random.choice(self.available_positions)
        player.position = pos
        self.available_positions.remove(pos)
        self.content[pos[1]][pos[0]] = str(player)
        return True

    def move_player(self, player: Player, action: Tuple[int, int]):
        width_delta, height_delta = action
        if not (-1 <= width_delta <= 1 and -1 <= height_delta <= 1):
            return

        current_x, current_y = player.position
        next_x = current_x + width_delta
        next_y = current_y + height_delta

        if 0 <= next_x < self.width and 0 <= next_y < self.height:
            if self.next_content[next_y][next_x] == '.':  # Only move if target cell is empty
                player.position = (next_x, next_y)
                self.next_content[next_y][next_x] = str(player)

    def end_round(self):
        self.content = [row[:] for row in self.next_content]
        self.next_content = [['.'] * self.width for _ in range(self.height)]

    def __str__(self):
        return '\n'.join(' '.join(row) for row in self.content)