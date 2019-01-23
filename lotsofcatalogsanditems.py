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
User1 = User(name="gustavo", email="gustavo@g.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()

User2 = User(name="thiago", email="thiago@g.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User2)
session.commit()

# Catalog for Sports
catalog1 = Catalog(user_id=1, name="Sports")

session.add(catalog1)
session.commit()

catalogItem1 = CatalogItem(user_id=1, name="Football", description="Football bla-bla and etc etc...",
                     catalog=catalog1)

session.add(catalogItem1)
session.commit()


catalogItem2 = CatalogItem(user_id=1, name="Basquet Ball", description="Jordan is the best player...",
                     catalog=catalog1)

session.add(catalogItem2)
session.commit()


# Catalog for Cars
catalog2 = Catalog(user_id=1, name="Cars")

session.add(catalog2)
session.commit()


catalogItem3 = CatalogItem(user_id=2, name="Ferrari", description="Manufactory process is in Italy",
                     catalog=catalog2)

session.add(catalogItem3)
session.commit()

print "added menu items!"