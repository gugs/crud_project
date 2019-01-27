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
User1 = User(name="Robo Barista", email="tinnyTim@udacity.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()

# Menu for UrbanBurger
restaurant1 = Catalog(user_id=1, name="Sport")

session.add(restaurant1)
session.commit()

menuItem2 = CatalogItem(user_id=1, name="Footbal", description="Juicy grilled veggie patty with tomato mayo and lettuce",
                     catalog=restaurant1)

session.add(menuItem2)
session.commit()


menuItem1 = CatalogItem(user_id=1, name="Voleyball", description="with garlic and parmesan",
                     catalog=restaurant1)

session.add(menuItem1)
session.commit()


# Menu for Super Stir Fry
restaurant2 = Catalog(user_id=1, name="Cars")

session.add(restaurant2)
session.commit()


menuItem1 = CatalogItem(user_id=1, name="Ferrari", description="With your choice of noodles vegetables and sauces",
                     catalog=restaurant2)

session.add(menuItem1)
session.commit()

menuItem2 = CatalogItem(user_id=1, name="Porsche", description=" A famous duck dish asdfasdf ...", 
                     catalog=restaurant2)

session.add(menuItem2)
session.commit()

print "added menu items!"