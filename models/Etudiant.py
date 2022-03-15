from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
engine = create_engine('sqlite:///:memory:', echo=True)

class Etudiant(Base):
  __tablename__ = 'etudiants'
  cin = Column(Integer, primary_key=True)
  nom = Column(Text)
  prenom  = Column(Text)
  password = Column(Text)
