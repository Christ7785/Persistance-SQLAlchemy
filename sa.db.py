from sa_model import Base, Game
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

if __name__ == '__main__':
   
    engine = create_engine('postgresql+psycopg2://postgres:password@172.17.0.2:5432/game', echo=True)

    Base.metadata.create_all(engine)
    
    with Session(engine) as session:
        statement = select(Game)
        for game in session.scalars(statement):
            print(game.title)