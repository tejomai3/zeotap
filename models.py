from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Rule(Base):
    __tablename__ = 'rules'
    id = Column(Integer, primary_key=True)
    rule_string = Column(String, nullable=False)
    ast = Column(Text, nullable=False)

# Setup SQLite database
engine = create_engine('sqlite:///rules.db')
Base.metadata.create_all(engine)
