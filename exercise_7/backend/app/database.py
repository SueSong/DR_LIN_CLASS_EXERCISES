"""
Database configuration and connection management for Exercise 6 RAG Chatbot
Handles PostgreSQL with pgvector extension
"""

import logging
from datetime import datetime
from typing import AsyncGenerator, Dict, Any, Optional
from contextlib import asynccontextmanager

import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text

from app.config import settings

logger = logging.getLogger(__name__)

# SQLAlchemy setup
Base = declarative_base()
engine = None
async_session_maker = None
connection_pool = None

# =============================================================================
# DATABASE INITIALIZATION
# =============================================================================

async def init_database():
    """Initialize database connections and setup"""
    global engine, async_session_maker, connection_pool
    
    try:
        logger.info("🔗 Connecting to PostgreSQL database...")
        
        # Create SQLAlchemy async engine
        engine = create_async_engine(
            settings.database_url,
            pool_size=settings.db_pool_size,
            max_overflow=settings.db_max_overflow,
            pool_timeout=settings.db_pool_timeout,
            echo=settings.is_development,
            future=True,
        )
        
        # Create session maker
        async_session_maker = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        # Create asyncpg connection pool for direct queries
        connection_pool = await asyncpg.create_pool(
            settings.database_url,
            min_size=5,
            max_size=settings.db_pool_size,
            command_timeout=settings.db_pool_timeout,
        )
        
        # Test connection
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            logger.info("✅ Database connection established successfully")
        
        # Check pgvector extension
        await check_pgvector_extension()
        
        logger.info("✅ Database initialization completed")
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise


async def close_database():
    """Close database connections"""
    global engine, connection_pool
    
    try:
        if connection_pool:
            await connection_pool.close()
            logger.info("🔌 AsyncPG connection pool closed")
        
        if engine:
            await engine.dispose()
            logger.info("🔌 SQLAlchemy engine disposed")
            
    except Exception as e:
        logger.error(f"❌ Error closing database connections: {e}")


async def check_pgvector_extension():
    """Check if pgvector extension is available"""
    try:
        async with connection_pool.acquire() as conn:
            result = await conn.fetchval(
                "SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'vector')"
            )
            
            if result:
                logger.info("✅ pgvector extension is available")
            else:
                logger.warning("⚠️ pgvector extension not found - vector operations may not work")
                
    except Exception as e:
        logger.error(f"❌ Error checking pgvector extension: {e}")


# =============================================================================
# SESSION MANAGEMENT
# =============================================================================

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session"""
    if not async_session_maker:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    
    async with async_session_maker() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_db_session():
    """Context manager for database sessions"""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database transaction error: {e}")
            raise
        finally:
            await session.close()


async def get_connection() -> asyncpg.Connection:
    """Get direct asyncpg connection from pool or create new connection"""
    if connection_pool:
        return await connection_pool.acquire()
    else:
        # Fallback: create direct connection if pool not available
        logger.warning("Connection pool not available, creating direct connection")
        # Convert SQLAlchemy URL to asyncpg format
        asyncpg_url = settings.database_url.replace("postgresql+asyncpg://", "postgresql://")
        return await asyncpg.connect(asyncpg_url)


@asynccontextmanager
async def get_db_connection():
    """Context manager for direct database connections"""
    conn = await connection_pool.acquire()
    try:
        yield conn
    finally:
        await connection_pool.release(conn)


# =============================================================================
# HEALTH CHECK
# =============================================================================

async def get_database_health() -> Dict[str, Any]:
    """Check database health status"""
    health_info = {
        "status": "unhealthy",
        "details": {},
        "timestamp": None
    }
    
    try:
        # Test SQLAlchemy connection
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            health_info["details"]["postgresql_version"] = version
        
        # Test connection pool
        async with connection_pool.acquire() as conn:
            pool_size = connection_pool.get_size()
            health_info["details"]["pool_size"] = pool_size
            health_info["details"]["pool_available"] = connection_pool.get_idle_size()
        
        # Check pgvector extension
        async with connection_pool.acquire() as conn:
            pgvector_available = await conn.fetchval(
                "SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'vector')"
            )
            health_info["details"]["pgvector_available"] = pgvector_available
        
        health_info["status"] = "healthy"
        health_info["timestamp"] = datetime.utcnow().isoformat()
        
    except Exception as e:
        health_info["details"]["error"] = str(e)
        logger.error(f"Database health check failed: {e}")
    
    return health_info


# =============================================================================
# VECTOR OPERATIONS
# =============================================================================

async def create_vector_index(table_name: str, column_name: str, dimension: int):
    """Create vector index for similarity search"""
    try:
        async with connection_pool.acquire() as conn:
            # Create IVFFlat index for vector similarity search
            index_name = f"idx_{table_name}_{column_name}_vector"
            
            await conn.execute(f"""
                CREATE INDEX IF NOT EXISTS {index_name}
                ON {table_name} 
                USING ivfflat ({column_name} vector_cosine_ops)
                WITH (lists = 100)
            """)
            
            logger.info(f"✅ Vector index created: {index_name}")
            
    except Exception as e:
        logger.error(f"❌ Error creating vector index: {e}")
        raise


async def similarity_search(
    table_name: str,
    column_name: str,
    query_vector: list,
    limit: int = 10,
    threshold: float = 0.7
) -> list:
    """Perform vector similarity search"""
    try:
        async with connection_pool.acquire() as conn:
            query = f"""
                SELECT *, 1 - ({column_name} <=> $1) as similarity
                FROM {table_name}
                WHERE 1 - ({column_name} <=> $1) > $2
                ORDER BY {column_name} <=> $1
                LIMIT $3
            """
            
            results = await conn.fetch(query, query_vector, threshold, limit)
            return [dict(row) for row in results]
            
    except Exception as e:
        logger.error(f"❌ Vector similarity search failed: {e}")
        raise


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

async def execute_raw_query(query: str, *args) -> list:
    """Execute raw SQL query"""
    try:
        async with connection_pool.acquire() as conn:
            results = await conn.fetch(query, *args)
            return [dict(row) for row in results]
            
    except Exception as e:
        logger.error(f"❌ Raw query execution failed: {e}")
        raise


async def execute_raw_command(query: str, *args) -> str:
    """Execute raw SQL command (INSERT, UPDATE, DELETE)"""
    try:
        async with connection_pool.acquire() as conn:
            result = await conn.execute(query, *args)
            return result
            
    except Exception as e:
        logger.error(f"❌ Raw command execution failed: {e}")
        raise


async def get_table_info(table_name: str) -> Dict[str, Any]:
    """Get information about a table"""
    try:
        async with connection_pool.acquire() as conn:
            # Get column information
            columns = await conn.fetch("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = $1
                ORDER BY ordinal_position
            """, table_name)
            
            # Get row count
            row_count = await conn.fetchval(f"SELECT COUNT(*) FROM {table_name}")
            
            return {
                "table_name": table_name,
                "columns": [dict(col) for col in columns],
                "row_count": row_count,
            }
            
    except Exception as e:
        logger.error(f"❌ Error getting table info: {e}")
        raise


# =============================================================================
# MIGRATION HELPERS
# =============================================================================

async def run_migration(migration_sql: str):
    """Run database migration"""
    try:
        async with connection_pool.acquire() as conn:
            await conn.execute(migration_sql)
            logger.info("✅ Migration executed successfully")
            
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        raise


async def check_table_exists(table_name: str) -> bool:
    """Check if table exists"""
    try:
        async with connection_pool.acquire() as conn:
            result = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = $1
                )
            """, table_name)
            return result
            
    except Exception as e:
        logger.error(f"❌ Error checking table existence: {e}")
        return False
