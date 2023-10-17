import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.database_config import DATABASE_URI, DATABASE_PATH
from ui.main_window import MainWindow

def main():
    try:      
        # Create an engine and session to interact with the database
        engine = create_engine(DATABASE_URI)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Launch the UI
        app = MainWindow(session)
        app.mainloop()
        
    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the session
        session.close()


if __name__ == '__main__':
    main()

