import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration settings for the Flask application"""
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')
    DEBUG = True
    
    # OpenAI API settings
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # MySQL Database settings
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'shreyash7710')
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'blog_generator')
    
    # Blog generation settings
    MAX_BLOG_LENGTH = 2000
    DEFAULT_MODEL = "gpt-4o-mini"
    
    @staticmethod
    def get_mysql_config():
        """Get MySQL connection configuration as dictionary"""
        return {
            'host': Config.MYSQL_HOST,
            'port': Config.MYSQL_PORT,
            'user': Config.MYSQL_USER,
            'password': Config.MYSQL_PASSWORD,
            'database': Config.MYSQL_DATABASE,
            'charset': 'utf8mb4',
            'autocommit': True
        }
    
    @staticmethod
    def validate_config():
        """Validate that all required configuration is present"""
        required_vars = ['OPENAI_API_KEY', 'MYSQL_PASSWORD']
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True