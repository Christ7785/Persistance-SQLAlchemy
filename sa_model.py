import logging
from typing import List, Tuple, Dict, Optional
from sqlalchemy import ForeignKey, String, Integer, Enum
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
import enum
import random

logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

class PlayerType(enum.Enum):
    WOLF = "wolf"
    VILLAGER = "villager"
    EMPTY = "empty"

class GameAction(Base):
    __tablename__ = 'game_action'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer, nullable=False)
    delta_x: Mapped[int] = mapped_column(Integer, nullable=False)
    delta_y: Mapped[int] = mapped_column(Integer, nullable=False)
    game_id: Mapped[int] = mapped_column(ForeignKey("game.id"))
    game: Mapped["Game"] = relationship(back_populates="action_records")
    
    def __init__(self, player_id: int, delta_x: int, delta_y: int, game_id: int = None, game: "Game" = None):
        self.player_id = player_id
        self.delta_x = delta_x
        self.delta_y = delta_y
        if game:
            self.game = game
            self.game_id = game.id
        elif game_id:
            self.game_id = game_id

class Game(Base):
    __tablename__ = 'game'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nb_max_turn: Mapped[int] = mapped_column(Integer, nullable=False)
    current_turn: Mapped[int] = mapped_column(Integer, default=0)
    width: Mapped[int] = mapped_column(Integer, nullable=False)
    height: Mapped[int] = mapped_column(Integer, nullable=False)
    started: Mapped[bool] = mapped_column(Integer, default=False, nullable=False)
    max_players: Mapped[int] = mapped_column(Integer, nullable=False, default=4)
    players: Mapped[List["Player"]] = relationship(back_populates="game", cascade="all, delete-orphan")
    action_records: Mapped[List["GameAction"]] = relationship(back_populates="game", cascade="all, delete-orphan")
    board: Mapped["GameBoard"] = relationship(back_populates="game", uselist=False, cascade="all, delete-orphan")

    def __init__(self, nb_max_turn: int, width: int, height: int, max_players: int = 4):
        self.nb_max_turn = nb_max_turn
        self.width = width
        self.height = height
        self.max_players = max_players
        self.current_turn = 0
        self.started = False
        self.board = GameBoard(width=width, height=height, game=self)
        self._temp_actions: Dict[int, Tuple[int, int]] = {} 

    def start_game(self):
        """Démarre la partie si tous les joueurs sont positionnés."""
        if not self.started:
            
            all_positioned = all(
                player.position_x is not None and player.position_y is not None
                for player in self.players
            )
            
            if all_positioned:
                self.started = True
                self.current_turn = 0
                return True
            else:
                logger.warning("Impossible de démarrer la partie : certains joueurs n'ont pas de position.")
                return False
        else:
            logger.info("La partie est déjà démarrée.")
            return False
    
    def stop_game(self):
        """Arrête la partie en cours."""
        if self.started:
            self.started = False
            return True
        else:
            logger.info("La partie n'est pas démarrée.")
            return False

    def register_action(self, player_id: int, action: Tuple[int, int]):
        """Enregistre une action pour un joueur si la partie est démarrée."""
        if not self.started:
            logger.warning("Impossible d'enregistrer une action : la partie n'est pas démarrée.")
            return False
        
        self._temp_actions[player_id] = action
        return True

    def process_actions(self):
        """Traite toutes les actions enregistrées si la partie est démarrée."""
        if not self.started:
            logger.warning("Impossible de traiter les actions : la partie n'est pas démarrée.")
            return False
        
        
        for cell in self.board.cells:
            if cell.is_next_state:
                cell.symbol = '.'
                
        
        for player in self.players:
            if player.position_x is not None and player.position_y is not None:
                next_cell = self.board.get_cell(player.position_x, player.position_y, is_next_state=True)
                if next_cell:
                    if player.player_type == PlayerType.WOLF:
                        next_cell.symbol = 'W'
                    elif player.player_type == PlayerType.VILLAGER:
                        next_cell.symbol = 'O'
        
      
        actions_to_process = []
        for player_id, action in self._temp_actions.items():
            player = next((p for p in self.players if p.id == player_id), None)
            if player:
                actions_to_process.append((player, action))
                logger.info(f"Action registered for player {player.pseudo} ({player.player_type.value}): movement ({action[0]}, {action[1]}) from position ({player.position_x}, {player.position_y})")
        
      
        for player, action in actions_to_process:
            success = self.board.move_player(player, action)
            if success:
                logger.info(f"Player {player.pseudo} successfully moved to position ({player.position_x}, {player.position_y})")
            else:
                logger.warning(f"Player {player.pseudo} failed to move from ({player.position_x}, {player.position_y}) using action ({action[0]}, {action[1]})")
        
       
        for player_id, action in self._temp_actions.items():
            action_record = GameAction(
                player_id=player_id,
                delta_x=action[0],
                delta_y=action[1],
                game_id=self.id
            )
            self.action_records.append(action_record)
        
       
        self._temp_actions = {}
        
  
        self.board.end_round()
        self.current_turn += 1
        
    
        if self.current_turn >= self.nb_max_turn:
            self.stop_game()
            logger.info(f"Partie terminée après {self.current_turn} tours.")
            
        return True

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
        """Getter pour la position du joueur"""
        return (self.position_x, self.position_y)

    @position.setter
    def position(self, value: Tuple[int, int]):
        """Setter pour la position du joueur"""
        if value is None:
            self.position_x = None
            self.position_y = None
        else:
            self.position_x, self.position_y = value

    def can_defeat(self, other_symbol: str) -> bool:
        """Détermine si ce joueur peut vaincre un autre joueur basé sur son symbole."""
       
        if self.player_type == PlayerType.WOLF and other_symbol == 'W':
            return False
        if self.player_type == PlayerType.VILLAGER and other_symbol == 'O':
            return False
            
      
        if self.player_type == PlayerType.WOLF and other_symbol == 'O':
            return True
            
       
        if self.player_type == PlayerType.VILLAGER and other_symbol == 'W':
            return False
            
     
        if other_symbol == '.':
            return True
            
        return False

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

class Cell(Base):
    __tablename__ = 'cell'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    x: Mapped[int] = mapped_column(Integer, nullable=False)
    y: Mapped[int] = mapped_column(Integer, nullable=False)
    symbol: Mapped[str] = mapped_column(String(1), default='.')
    is_next_state: Mapped[bool] = mapped_column(Integer, default=False)
    board_id: Mapped[int] = mapped_column(ForeignKey("game_board.id"))
    board: Mapped["GameBoard"] = relationship(back_populates="cells")
    
    def __init__(self, x: int, y: int, symbol: str = '.', is_next_state: bool = False, board: "GameBoard" = None):
        self.x = x
        self.y = y
        self.symbol = symbol
        self.is_next_state = is_next_state
        self.board = board

class GameBoard(Base):
    __tablename__ = 'game_board'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    width: Mapped[int] = mapped_column(Integer, nullable=False)
    height: Mapped[int] = mapped_column(Integer, nullable=False)
    game_id: Mapped[int] = mapped_column(ForeignKey("game.id"), unique=True)
    game: Mapped["Game"] = relationship(back_populates="board")
    cells: Mapped[List["Cell"]] = relationship(back_populates="board", cascade="all, delete-orphan")

    def __init__(self, width: int, height: int, game: Game):
        self.width = width
        self.height = height
        self.game = game
        
      
        for y in range(height):
            for x in range(width):
                self.cells.append(Cell(x=x, y=y, board=self))
                
        
        for y in range(height):
            for x in range(width):
                self.cells.append(Cell(x=x, y=y, is_next_state=True, board=self))
    
    @property
    def available_positions(self) -> List[Tuple[int, int]]:
        return [(cell.x, cell.y) for cell in self.cells 
                if not cell.is_next_state and cell.symbol == '.']
    
    def get_cell(self, x: int, y: int, is_next_state: bool = False) -> Optional[Cell]:
        return next((cell for cell in self.cells 
                    if cell.x == x and cell.y == y and cell.is_next_state == is_next_state), None)

    def subscribe_player(self, player: Player):
        available = self.available_positions
        if not available:
            logger.warning('No more space to play')
            return False
            
        pos_x, pos_y = random.choice(available)
       
        player.position_x = pos_x
        player.position_y = pos_y
      
        current_cell = self.get_cell(pos_x, pos_y)
        next_cell = self.get_cell(pos_x, pos_y, is_next_state=True)
        
        if current_cell:
            if player.player_type == PlayerType.WOLF:
                current_cell.symbol = 'W'
            elif player.player_type == PlayerType.VILLAGER:
                current_cell.symbol = 'O'
            else:
                current_cell.symbol = '.'
                
        if next_cell:
            if player.player_type == PlayerType.WOLF:
                next_cell.symbol = 'W'
            elif player.player_type == PlayerType.VILLAGER:
                next_cell.symbol = 'O'
            else:
                next_cell.symbol = '.'
        
        return True

    def move_player(self, player: Player, action: Tuple[int, int]):
        width_delta, height_delta = action
        if not (-1 <= width_delta <= 1 and -1 <= height_delta <= 1):
            logger.warning(f"Invalid movement delta: ({width_delta}, {height_delta}). Must be between -1 and 1.")
            return False
            
        
        current_x, current_y = player.position_x, player.position_y
        next_x = current_x + width_delta
        next_y = current_y + height_delta

        
        if not (0 <= next_x < self.width and 0 <= next_y < self.height):
            logger.warning(f"Movement out of bounds: ({next_x}, {next_y}) is outside board size ({self.width}x{self.height})")
           
            if width_delta != 0 and 0 <= current_x + width_delta < self.width:
                next_y = current_y  
                next_x = current_x + width_delta
                logger.info(f"Adjusting to horizontal movement to ({next_x}, {next_y})")
            
            elif height_delta != 0 and 0 <= current_y + height_delta < self.height:
                next_x = current_x  
                next_y = current_y + height_delta
                logger.info(f"Adjusting to vertical movement to ({next_x}, {next_y})")
            else:
               
                return False
              
        
        current_next_cell = self.get_cell(current_x, current_y, is_next_state=True)
        if current_next_cell:
            
            other_players_at_current = [p for p in self.game.players 
                                        if p.id != player.id and p.position_x == current_x and p.position_y == current_y]
                                        
            if not other_players_at_current:
                current_next_cell.symbol = '.'
            else:
                
                other_player = other_players_at_current[0]
                if other_player.player_type == PlayerType.WOLF:
                    current_next_cell.symbol = 'W'
                elif other_player.player_type == PlayerType.VILLAGER:
                    current_next_cell.symbol = 'O'
            
        
        target_next_cell = self.get_cell(next_x, next_y, is_next_state=True)
        if target_next_cell:
            
            if not player.can_defeat(target_next_cell.symbol):
                
                for alt_dx, alt_dy in [(1,0), (-1,0), (0,1), (0,-1)]:
                
                    if (alt_dx == width_delta and alt_dy == height_delta) or \
                       (alt_dx == -width_delta and alt_dy == -height_delta):
                        continue
                        
                    alt_x = current_x + alt_dx
                    alt_y = current_y + alt_dy
                    
                   
                    if not (0 <= alt_x < self.width and 0 <= alt_y < self.height):
                        continue
                        
                    alt_cell = self.get_cell(alt_x, alt_y, is_next_state=True)
                    if alt_cell and player.can_defeat(alt_cell.symbol):
                        logger.info(f"Player {player.pseudo} ({player.player_type.value}) redirected to ({alt_x}, {alt_y})")
                        next_x, next_y = alt_x, alt_y
                        target_next_cell = alt_cell
                        break
                else:
                
                    logger.warning(f"Player {player.pseudo} ({player.player_type.value}) cannot move to cell ({next_x}, {next_y}) containing '{target_next_cell.symbol}' and no alternative found")
                
                    next_x, next_y = current_x, current_y
                    target_next_cell = current_next_cell
              
 
            player.position_x = next_x
            player.position_y = next_y
              
          
            if player.player_type == PlayerType.WOLF:
                target_next_cell.symbol = 'W'
            elif player.player_type == PlayerType.VILLAGER:
                target_next_cell.symbol = 'O'
                
            return True
                
        logger.error(f"Could not find target cell at ({next_x}, {next_y})")
        return False

    def end_round(self):
        """
        Termine un tour de jeu en copiant l'état suivant dans l'état actuel.
        """
        
        current_cells = {(cell.x, cell.y): cell for cell in self.cells if not cell.is_next_state}
        next_cells = {(cell.x, cell.y): cell for cell in self.cells if cell.is_next_state}
        
       
        for cell in current_cells.values():
            cell.symbol = '.'
        
       
        for pos, next_cell in next_cells.items():
            if pos in current_cells:
                current_cells[pos].symbol = next_cell.symbol
        
      
        for player in self.game.players:
            if player.position_x is not None and player.position_y is not None:
                pos = (player.position_x, player.position_y)
                if pos in current_cells:
                    cell = current_cells[pos]
                    if player.player_type == PlayerType.WOLF:
                        cell.symbol = 'W'
                    elif player.player_type == PlayerType.VILLAGER:
                        cell.symbol = 'O'
                    
               
                if pos in next_cells:
                    cell = next_cells[pos]
                    if player.player_type == PlayerType.WOLF:
                        cell.symbol = 'W'
                    elif player.player_type == PlayerType.VILLAGER:
                        cell.symbol = 'O'
    
    def __str__(self):
        result = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                cell = self.get_cell(x, y, is_next_state=False)
                if cell:
                    row.append(cell.symbol)
                else:
                    row.append('.')
            result.append(' '.join(row))
        return '\n'.join(result)
        
    def debug_next_state(self):
        """Affiche l'état suivant du plateau (utile pour le débogage)"""
        result = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                cell = self.get_cell(x, y, is_next_state=True)
                if cell:
                    row.append(cell.symbol)
                else:
                    row.append('.')
            result.append(' '.join(row))
        return '\n'.join(result)