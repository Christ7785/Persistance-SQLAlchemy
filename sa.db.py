from sa_model import Base, Game, Player, GameBoard, PlayerType
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

if __name__ == '__main__':
    # Utilisation de SQLite
    engine = create_engine('sqlite:///game.db', echo=True)

    # Création des tables
    Base.metadata.create_all(engine)
    
    # Test du jeu
    with Session(engine) as session:
        # Créer une nouvelle partie 10x5
        game = Game(nb_max_turn=10, width=10, height=5)
        
        # Créer des joueurs
        wolf1 = Player(
            pseudo='A',
            player_type=PlayerType.WOLF,
            field_distance=2
        )
        
        wolf2 = Player(
            pseudo='B',
            player_type=PlayerType.WOLF,
            field_distance=2
        )
        
        villager1 = Player(
            pseudo='V',
            player_type=PlayerType.VILLAGER,
            field_distance=1
        )
        
        villager2 = Player(
            pseudo='X',
            player_type=PlayerType.VILLAGER,
            field_distance=1
        )
        
        # Ajouter les joueurs à la partie
        game.players.extend([wolf1, wolf2, villager1, villager2])
        
        # Ajouter à la session et sauvegarder
        session.add(game)
        session.commit()
        
        # Afficher le plateau initial
        print("Initial board:")
        print(game.board)
        
        # Placer les joueurs sur le plateau
        game.board.subscribe_player(wolf1)
        game.board.subscribe_player(wolf2)
        game.board.subscribe_player(villager1)
        game.board.subscribe_player(villager2)
        
        print("\nBoard after placing players:")
        print(game.board)
        
        # Test de déplacement
        print("\nTesting movements:")
        game.register_action(wolf1.id, (0, 1))  # Déplacement vers le bas
        game.register_action(villager1.id, (1, 0))  # Déplacement vers la droite
        
        game.process_actions()
        
        print("\nBoard after movements:")
        print(game.board)
        
        # Sauvegarder les changements
        session.commit()