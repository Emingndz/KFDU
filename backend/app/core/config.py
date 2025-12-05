from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Yazlab Proje 2"
    API_V1_STR: str = "/api/v1"
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///./sql_app.db"
    TMDB_API_KEY: str = "224eeadad3cc958c58809c8e71247a44"
    
    # SMTP Email Settings
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "m.eminsocail27@gmail.com"  # Gmail adresin
    SMTP_PASSWORD: str = "qidywplezojijihb"  # Buraya App Password yaz (16 karakter)
    EMAILS_FROM_EMAIL: str = "noreply@kfdu.com"
    EMAILS_FROM_NAME: str = "KFDU Platform"

    class Config:
        case_sensitive = True

settings = Settings()
