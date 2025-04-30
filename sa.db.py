from sa_model import Base, Game, Player, GameBoard, PlayerType
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
import os
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("game.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    
    if os.path.exists('game.db'):
        os.remove('game.db')
        
    engine = create_engine('sqlite:///game.db', echo=True)

    # Création des tables
    Base.metadata.create_all(engine)
    
    # Test du jeu
    with Session(engine) as session:
        # Créer une nouvelle partie 10x5
        game = Game(nb_max_turn=10, width=10, height=5, max_players=4)
        
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
        
        logger.info(f"État de la partie avant démarrage: {'démarrée' if game.started else 'non démarrée'}")
        
        # Essayer de démarrer la partie avant de positionner les joueurs
        if game.start_game():
            logger.info("La partie a démarré avec succès.")
        else:
            logger.warning("La partie n'a pas pu démarrer (attendu, car joueurs non positionnés).")
        
        # Afficher le plateau initial
        logger.info("\nInitial board:")
        logger.info(game.board)
        
        # Placer les joueurs sur le plateau
        logger.info("\nPlacement des joueurs...")
        logger.info("Placement de Wolf1 (A)...")
        game.board.subscribe_player(wolf1)
        session.flush()  
        logger.info("Board après placement de Wolf1:")
        logger.info(game.board)
        
        logger.info("\nPlacement de Wolf2 (B)...")
        game.board.subscribe_player(wolf2)
        session.flush()
        logger.info("Board après placement de Wolf2:")
        logger.info(game.board)
        
        logger.info("\nPlacement de Villager1 (V)...")
        game.board.subscribe_player(villager1)
        session.flush()
        logger.info("Board après placement de Villager1:")
        logger.info(game.board)
        
        logger.info("\nPlacement de Villager2 (X)...")
        game.board.subscribe_player(villager2)
        session.commit()  # Commit final après tous les placements
        
        logger.info("\nBoard after placing all players:")
        logger.info(game.board)
        
        # Vérifier que les joueurs sont correctement positionnés
        logger.info("\nJoueurs positionnés:")
        for player in game.players:
            symbol = "W" if player.player_type == PlayerType.WOLF else "O"
            logger.info(f"Joueur {player.pseudo} ({symbol}) à la position ({player.position_x}, {player.position_y})")
        
        # Maintenant, essayer de démarrer la partie
        logger.info("\nDémarrage de la partie...")
        if game.start_game():
            logger.info("La partie a démarré avec succès!")
            logger.info(f"État de la partie: {'démarrée' if game.started else 'non démarrée'}")
        else:
            logger.warning("La partie n'a pas pu démarrer.")
        
        # Test de mouvements:
        logger.info("\nTest de mouvements:")
        logger.info("Enregistrement d'une action pour Wolf1 (A) - déplacement vers la gauche...")
        if game.register_action(wolf1.id, (-1, 0)):
            logger.info(f"Action pour joueur {wolf1.pseudo} enregistrée.")
        
        logger.info("Enregistrement d'une action pour Villager1 (V) - déplacement vers la droite...")
        if game.register_action(villager1.id, (1, 0)):
            logger.info(f"Action pour joueur {villager1.pseudo} enregistrée.")
        
        logger.info("\nTraitement des actions...")
        if game.process_actions():
            logger.info("Actions traitées avec succès.")
        
        session.commit()
        
        logger.info("\nPositions des joueurs avant affichage du plateau:")
        for player in game.players:
            symbol = "W" if player.player_type == PlayerType.WOLF else "O"
            logger.info(f"Joueur {player.pseudo} ({symbol}) à la position ({player.position_x}, {player.position_y})")
        
        logger.info("\nBoard after movements:")
        logger.info(game.board)
        
        logger.info("\nÉtat suivant du plateau (debug):")
        logger.info(game.board.debug_next_state())
        
        # Test d'un second tour
        logger.info("\n===============================")
        logger.info("TEST D'UN SECOND TOUR")
        logger.info("===============================")
        
        logger.info("Enregistrement d'une action pour Wolf2 (B) - déplacement vers le bas...")
        if game.register_action(wolf2.id, (0, 1)):
            logger.info(f"Action pour joueur {wolf2.pseudo} enregistrée.")
        
        logger.info("Enregistrement d'une action pour Villager2 (X) - déplacement vers la droite...")
        if game.register_action(villager2.id, (1, 0)):
            logger.info(f"Action pour joueur {villager2.pseudo} enregistrée.")
            
        logger.info("\nTraitement des actions du second tour...")
        if game.process_actions():
            logger.info("Actions du second tour traitées avec succès.")
            
        session.commit()
        
        logger.info("\nPositions des joueurs après le second tour:")
        for player in game.players:
            symbol = "W" if player.player_type == PlayerType.WOLF else "O"
            logger.info(f"Joueur {player.pseudo} ({symbol}) à la position ({player.position_x}, {player.position_y})")
            
        logger.info("\nBoard after second round:")
        logger.info(game.board)
        
        # Vérifier les nouvelles positions
        logger.info("\nRécapitulatif des positions finales:")
        for player in game.players:
            symbol = "W" if player.player_type == PlayerType.WOLF else "O"
            logger.info(f"Joueur {player.pseudo} ({symbol}) à la position ({player.position_x}, {player.position_y})")
        
        # Arrêter la partie manuellement
        logger.info("\nArrêt de la partie...")
        if game.stop_game():
            logger.info("La partie a été arrêtée avec succès.")
            logger.info(f"État de la partie: {'démarrée' if game.started else 'non démarrée'}")
        else:
            logger.warning("La partie n'a pas pu être arrêtée.")
        
        # Essayer d'enregistrer une action après l'arrêt de la partie
        logger.info("\nTest d'enregistrement d'action après arrêt:")
        if game.register_action(wolf2.id, (1, 1)):
            logger.info("Action enregistrée (inattendu).")
        else:
            logger.info("Action non enregistrée comme prévu.")
        
        # Vérifier que les données sont bien enregistrées
        logger.info("\nVérification des actions enregistrées:")
        logger.info(f"Nombre d'actions: {len(game.action_records)}")
        for action in game.action_records:
            player = next((p for p in game.players if p.id == action.player_id), None)
            player_name = player.pseudo if player else "Inconnu"
            symbol = "W" if player and player.player_type == PlayerType.WOLF else "O"
            logger.info(f"Joueur {player_name} ({symbol}) a effectué mouvement ({action.delta_x}, {action.delta_y})")