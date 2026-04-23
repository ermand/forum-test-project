from core.db_connection.database import engine, Base

def create_tables(engine):
    print("Creating tables")
    Base.metadata.create_all(engine)
    print("Tables created")


if __name__ == "__main__":
    create_tables(engine)