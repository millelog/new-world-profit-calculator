from sqlalchemy import Table, create_engine, Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from config.database_config import DATABASE_URI

Base = declarative_base()
# Define the association table for the many-to-many relationship between Item and ItemType
item_itemtype_association = Table('item_itemtype_association', Base.metadata,
    Column('item_id', String, ForeignKey('items.item_id')),
    Column('item_type_id', Integer, ForeignKey('item_types.item_type_id'))
)

class ItemType(Base):
    __tablename__ = 'item_types'

    item_type_id = Column(Integer, primary_key=True, autoincrement=True)
    item_type_name = Column(String, nullable=False)
    
    # Define the relationship to items
    items = relationship("Item", secondary=item_itemtype_association, back_populates="item_types")


class RecipeReagent(Base):
    __tablename__ = 'recipe_reagents'
    
    recipe_id = Column(Integer, ForeignKey('crafting_recipes.recipe_id'), primary_key=True, autoincrement=True)
    reagent_item_id = Column(String, ForeignKey('items.item_id'), nullable=True)
    reagent_item_type_id = Column(Integer, ForeignKey('item_types.item_type_id'), nullable=True)
    quantity_required = Column(Integer, nullable=False)

    reagent = relationship("Item", backref="recipe_reagents_as_specific_item")
    recipe = relationship("CraftingRecipe", backref="recipe_reagents")

class Item(Base):
    __tablename__ = 'items'
    
    item_id = Column(String, primary_key=True)
    item_name = Column(String, nullable=False)

    current_price = relationship("CurrentPrice", back_populates="item", uselist=False)
    price_logs = relationship("PriceLog", back_populates="item")
    crafting_recipes = relationship("CraftingRecipe", back_populates="result_item")
    recipe_reagents = relationship("RecipeReagent", back_populates="reagent")
    item_types = relationship("ItemType", secondary=item_itemtype_association, back_populates="items")


class PriceLog(Base):
    __tablename__ = 'price_logs'
    
    log_id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(String, ForeignKey('items.item_id'))
    price = Column(Float, nullable=False)
    availability = Column(Integer, nullable=False)
    last_updated = Column(DateTime, nullable=False)
    highest_buy_order = Column(Float)
    qty = Column(Integer)
    server_id = Column(Integer, ForeignKey('servers.server_id'))

    server = relationship("Server", back_populates="price_logs")
    item = relationship("Item", back_populates="price_logs")


class CurrentPrice(Base):
    __tablename__ = 'current_prices'
    
    item_id = Column(String, ForeignKey('items.item_id'), primary_key=True)
    price = Column(Float, nullable=False)
    availability = Column(Integer, nullable=False)
    last_updated = Column(DateTime, nullable=False)
    highest_buy_order = Column(Float)
    qty = Column(Integer)

    server_id = Column(Integer, ForeignKey('servers.server_id'))
    server = relationship("Server", back_populates="current_prices")
    item = relationship("Item", back_populates="current_price")


class TradeSkill(Base):
    __tablename__ = 'trade_skills'
    
    skill_id = Column(Integer, primary_key=True, autoincrement=True)
    skill_name = Column(String, nullable=False)

    players = relationship("Player", back_populates="trade_skill")


class RecipeSkillRequirement(Base):
    __tablename__ = 'recipe_skill_requirements'
    
    recipe_id = Column(Integer, ForeignKey('crafting_recipes.recipe_id'), primary_key=True)
    skill_id = Column(Integer, ForeignKey('trade_skills.skill_id'), primary_key=True)
    level_required = Column(Integer, nullable=False)

    skill = relationship("TradeSkill")
    recipe = relationship("CraftingRecipe", back_populates="skill_requirements")


class CraftingRecipe(Base):
    __tablename__ = 'crafting_recipes'
    
    recipe_id = Column(Integer, primary_key=True, autoincrement=True)
    result_item_id = Column(String, ForeignKey('items.item_id'))
    quantity_produced = Column(Integer, nullable=False)

    result_item = relationship("Item", back_populates="crafting_recipes")
    recipe_reagents = relationship("RecipeReagent", back_populates="recipe")
    skill_requirements = relationship("RecipeSkillRequirement", back_populates="recipe")


class Player(Base):
    __tablename__ = 'players'
    
    player_id = Column(Integer, primary_key=True, autoincrement=True)
    player_name = Column(String, nullable=False)
    server_id = Column(Integer, ForeignKey('servers.server_id'))
    
    server = relationship("Server", back_populates="players")
    skills = relationship("PlayerSkill", back_populates="player")
    transactions = relationship("Transaction", back_populates="player")


class PlayerSkill(Base):
    __tablename__ = 'player_skills'
    
    player_id = Column(Integer, ForeignKey('players.player_id'), primary_key=True)
    skill_id = Column(Integer, ForeignKey('trade_skills.skill_id'), primary_key=True)
    skill_level = Column(Integer, nullable=False)
    
    player = relationship("Player", back_populates="skills")
    trade_skill = relationship("TradeSkill")


class Transaction(Base):
    __tablename__ = 'transactions'
    
    transaction_id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(String, ForeignKey('items.item_id'))
    player_id = Column(Integer, ForeignKey('players.player_id'))
    transaction_type = Column(String, nullable=False)  # Can be 'buy' or 'sell'
    quantity = Column(Integer, nullable=False)
    total_price = Column(Float, nullable=False)
    transaction_date = Column(DateTime, nullable=False)

    server_id = Column(Integer, ForeignKey('servers.server_id'))
    server = relationship("Server", back_populates="transactions")

    item = relationship("Item")
    player = relationship("Player", back_populates="transactions")


class Server(Base):
    __tablename__ = 'servers'
    
    server_id = Column(Integer, primary_key=True, autoincrement=True)
    server_name = Column(String, unique=True, nullable=False)

    price_logs = relationship("PriceLog", back_populates="server")
    current_prices = relationship("CurrentPrice", back_populates="server")
    players = relationship("Player", back_populates="server")
    transactions = relationship("Transaction", back_populates="server")


# Create an engine and bind it to the Base
engine = create_engine(DATABASE_URI)
Base.metadata.create_all(engine)
