from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from databases import Database

DATABASE_URL = "mysql+aiomysql://username:password@localhost/dbname"

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# For queries using `databases` library
database = Database(DATABASE_URL)
