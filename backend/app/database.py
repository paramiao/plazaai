from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from .config import settings
import logging
from .models import Base

logger = logging.getLogger(__name__)

# 创建数据库引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True
)

# 创建异步会话工厂
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def init_db():
    """
    初始化数据库，创建所有表
    """
    async with engine.begin() as conn:
        logger.info("Creating database tables...")
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")

async def get_db():
    """
    获取数据库会话的依赖函数
    """
    async with AsyncSessionLocal() as session:
        logger.info("Creating database session")
        try:
            yield session
            await session.commit()
            logger.info("Database session committed")
        except Exception as e:
            await session.rollback()
            logger.error(f"Database error: {str(e)}")
            raise
        finally:
            await session.close()
            logger.info("Database session closed") 