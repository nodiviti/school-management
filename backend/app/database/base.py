"""Database adapter pattern to support multiple databases"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()


class DatabaseAdapter(ABC):
    """Abstract base class for database operations"""
    
    @abstractmethod
    async def connect(self):
        """Connect to database"""
        pass
    
    @abstractmethod
    async def disconnect(self):
        """Disconnect from database"""
        pass
    
    @abstractmethod
    async def insert_one(self, collection: str, document: Dict[str, Any]) -> str:
        """Insert a single document"""
        pass
    
    @abstractmethod
    async def find_one(self, collection: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find a single document"""
        pass
    
    @abstractmethod
    async def find_many(self, collection: str, query: Dict[str, Any], limit: int = 100) -> List[Dict[str, Any]]:
        """Find multiple documents"""
        pass
    
    @abstractmethod
    async def update_one(self, collection: str, query: Dict[str, Any], update: Dict[str, Any]) -> bool:
        """Update a single document"""
        pass
    
    @abstractmethod
    async def delete_one(self, collection: str, query: Dict[str, Any]) -> bool:
        """Delete a single document"""
        pass


class MongoDBAdapter(DatabaseAdapter):
    """MongoDB database adapter"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None
    
    async def connect(self):
        """Connect to MongoDB"""
        self.client = AsyncIOMotorClient(settings.MONGO_URL)
        self.db = self.client[settings.DB_NAME]
        logger.info(f"Connected to MongoDB: {settings.DB_NAME}")
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    async def insert_one(self, collection: str, document: Dict[str, Any]) -> str:
        """Insert a single document"""
        result = await self.db[collection].insert_one(document)
        return str(result.inserted_id)
    
    async def find_one(self, collection: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find a single document"""
        result = await self.db[collection].find_one(query, {"_id": 0})
        return result
    
    async def find_many(self, collection: str, query: Dict[str, Any], limit: int = 100) -> List[Dict[str, Any]]:
        """Find multiple documents"""
        cursor = self.db[collection].find(query, {"_id": 0}).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def update_one(self, collection: str, query: Dict[str, Any], update: Dict[str, Any]) -> bool:
        """Update a single document"""
        result = await self.db[collection].update_one(query, {"$set": update})
        return result.modified_count > 0
    
    async def delete_one(self, collection: str, query: Dict[str, Any]) -> bool:
        """Delete a single document"""
        result = await self.db[collection].delete_one(query)
        return result.deleted_count > 0


class PostgreSQLAdapter(DatabaseAdapter):
    """PostgreSQL database adapter using SQLAlchemy"""
    
    def __init__(self):
        self.engine = None
        self.session_factory = None
    
    async def connect(self):
        """Connect to PostgreSQL"""
        # Convert postgresql:// to postgresql+asyncpg://
        db_url = settings.POSTGRES_URL
        if db_url and not db_url.startswith("postgresql+asyncpg"):
            db_url = db_url.replace("postgresql://", "postgresql+asyncpg://")
        
        self.engine = create_async_engine(
            db_url,
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_MAX_OVERFLOW,
            echo=settings.DEBUG
        )
        
        self.session_factory = sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        # Create tables
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Connected to PostgreSQL")
    
    async def disconnect(self):
        """Disconnect from PostgreSQL"""
        if self.engine:
            await self.engine.dispose()
            logger.info("Disconnected from PostgreSQL")
    
    async def get_session(self) -> AsyncSession:
        """Get database session"""
        async with self.session_factory() as session:
            return session
    
    # Note: PostgreSQL adapter would use SQLAlchemy ORM
    # The generic methods below are simplified
    
    async def insert_one(self, collection: str, document: Dict[str, Any]) -> str:
        """Insert one record (simplified)"""
        # In real implementation, use SQLAlchemy models
        return "postgres_id"
    
    async def find_one(self, collection: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find one record (simplified)"""
        return None
    
    async def find_many(self, collection: str, query: Dict[str, Any], limit: int = 100) -> List[Dict[str, Any]]:
        """Find many records (simplified)"""
        return []
    
    async def update_one(self, collection: str, query: Dict[str, Any], update: Dict[str, Any]) -> bool:
        """Update one record (simplified)"""
        return False
    
    async def delete_one(self, collection: str, query: Dict[str, Any]) -> bool:
        """Delete one record (simplified)"""
        return False


def get_database() -> DatabaseAdapter:
    """Factory function to get appropriate database adapter"""
    if settings.DATABASE_TYPE == "mongodb":
        return MongoDBAdapter()
    elif settings.DATABASE_TYPE == "postgresql":
        return PostgreSQLAdapter()
    else:
        raise ValueError(f"Unsupported database type: {settings.DATABASE_TYPE}")


# Global database instance
db_adapter = get_database()