from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Catalog, Base, CatalogItem, User

engine = create_engine('sqlite:///catalogproject.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create dummy user
User1 = User(
    name="Gustavo Nobrega",
    email="gustavo@g.com",
    picture='https://t2.ftcdn.net/jpg/02/26/55/01/400_F_226550110_yfI6YiSgx35Xd49x6WY76v0Y2h0U6jgu.jpg')
session.add(User1)
session.commit()

# Menu for UrbanBurger
catalog1 = Catalog(user_id=1, name="Esporte")

session.add(catalog1)
session.commit()

catalogItem2 = CatalogItem(
    user_id=1,
    name="Futebol",
    description="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
    catalog=catalog1)

session.add(catalogItem2)
session.commit()


catalogItem1 = CatalogItem(
    user_id=1,
    name="Voleybol",
    description="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. ",
    catalog=catalog1)

session.add(catalogItem1)
session.commit()


# Menu for Super Stir Fry
catalog2 = Catalog(user_id=1, name="Carros")

session.add(catalog2)
session.commit()


catalogItem3 = CatalogItem(
    user_id=1,
    name="Ferrari",
    description="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. ",
    catalog=catalog2)

session.add(catalogItem3)
session.commit()

catalogItem4 = CatalogItem(
    user_id=1,
    name="Porsche",
    description="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. ",
    catalog=catalog2)

session.add(catalogItem4)
session.commit()

print "added items!"
