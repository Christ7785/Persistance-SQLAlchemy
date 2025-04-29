from sa_model import Base, Game, Player, GameBoard, PlayerType
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

if __name__ == '__main__':
    # Utilisation de SQLite (stockage dans un fichier game.db)
    engine = create_engine('sqlite:///game.db', echo=True)

    # Création des tables
    Base.metadata.create_all(engine)
    
    # Création d'une partie de test
    with Session(engine) as session:
        # Créer une nouvelle partie
        game = Game(nb_max_turn=10)
        
        # Créer un plateau de jeu
        board = GameBoard(width=10, height=5, game=game)
        
        # Créer des joueurs
        wolf1 = Player(
            pseudo='A',
            player_type=PlayerType.WOLF,
            field_distance=2,
            position_x=0,
            position_y=0,
            game=game
        )
        
        wolf2 = Player(
            pseudo='B',
            player_type=PlayerType.WOLF,
            field_distance=2,
            position_x=1,
            position_y=1,
            game=game
        )
        
        villager = Player(
            pseudo='V',
            player_type=PlayerType.VILLAGER,
            field_distance=1,
            position_x=2,
            position_y=2,
            game=game
        )
        
        # Ajouter à la session et sauvegarder
        session.add(game)
        session.add(board)
        session.add_all([wolf1, wolf2, villager])
        session.commit()
        
        # Vérifier que tout a été sauvegardé
        games = session.scalars(select(Game)).all()
        for game in games:
            print(f"Game {game.id} - Turn {game.current_turn}/{game.nb_max_turn}")
            print(f"Board size: {board.width}x{board.height}")
            for player in game.players:
                print(f"Player {player.pseudo} ({player.player_type.value}) at position ({player.position_x}, {player.position_y})")