from dotenv import load_dotenv
import os


load_dotenv()

class Settings:
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "Flight_tracker")
    PORT: int = int(os.getenv("PORT", "8000"))

settings = Settings()