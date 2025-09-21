import mysql.connector
from mysql.connector import Error
from config import Config
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Handles all database operations for the blog generator"""
    
    def __init__(self):
        self.config = Config.get_mysql_config()
    
    def get_connection(self):
        """Create and return a database connection"""
        try:
            connection = mysql.connector.connect(**self.config)
            return connection
        except Error as e:
            logger.error(f"Error connecting to MySQL: {e}")
            return None
    
    def create_database_if_not_exists(self):
        """Create the blog_generator database if it doesn't exist"""
        try:
            # Connect without specifying database
            config_without_db = self.config.copy()
            config_without_db.pop('database', None)
            
            connection = mysql.connector.connect(**config_without_db)
            cursor = connection.cursor()
            
            # Create database if it doesn't exist
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.config['database']}")
            logger.info(f"Database '{self.config['database']}' created or already exists")
            
            cursor.close()
            connection.close()
            return True
            
        except Error as e:
            logger.error(f"Error creating database: {e}")
            return False
    
    def create_tables(self):
        """Create necessary tables if they don't exist"""
        try:
            # First ensure database exists
            self.create_database_if_not_exists()
            
            connection = self.get_connection()
            if not connection:
                return False
            
            cursor = connection.cursor()
            
            # Create blogs table
            create_blogs_table = """
            CREATE TABLE IF NOT EXISTS blogs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                topic VARCHAR(500) NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_created_at (created_at),
                INDEX idx_topic (topic(100))
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            cursor.execute(create_blogs_table)
            logger.info("Blogs table created or already exists")
            
            cursor.close()
            connection.close()
            return True
            
        except Error as e:
            logger.error(f"Error creating tables: {e}")
            return False
    
    def save_blog(self, topic, content):
        """Save a blog post to the database"""
        try:
            connection = self.get_connection()
            if not connection:
                return None
            
            cursor = connection.cursor()
            
            insert_query = """
            INSERT INTO blogs (topic, content) 
            VALUES (%s, %s)
            """
            
            cursor.execute(insert_query, (topic, content))
            blog_id = cursor.lastrowid
            
            connection.commit()
            cursor.close()
            connection.close()
            
            logger.info(f"Blog saved successfully with ID: {blog_id}")
            return blog_id
            
        except Error as e:
            logger.error(f"Error saving blog: {e}")
            return None
    
    def get_all_blogs(self):
        """Retrieve all blog posts from the database"""
        try:
            connection = self.get_connection()
            if not connection:
                return []
            
            cursor = connection.cursor(dictionary=True)
            
            select_query = """
            SELECT id, topic, content, created_at, updated_at 
            FROM blogs 
            ORDER BY created_at DESC
            """
            
            cursor.execute(select_query)
            blogs = cursor.fetchall()
            
            cursor.close()
            connection.close()
            
            # Convert datetime objects to strings for JSON serialization
            for blog in blogs:
                if blog['created_at']:
                    blog['created_at'] = blog['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                if blog['updated_at']:
                    blog['updated_at'] = blog['updated_at'].strftime('%Y-%m-%d %H:%M:%S')
                
                # Truncate content for preview
                if len(blog['content']) > 200:
                    blog['preview'] = blog['content'][:200] + '...'
                else:
                    blog['preview'] = blog['content']
            
            return blogs
            
        except Error as e:
            logger.error(f"Error retrieving blogs: {e}")
            return []
    
    def get_blog_by_id(self, blog_id):
        """Retrieve a specific blog post by ID"""
        try:
            connection = self.get_connection()
            if not connection:
                return None
            
            cursor = connection.cursor(dictionary=True)
            
            select_query = """
            SELECT id, topic, content, created_at, updated_at 
            FROM blogs 
            WHERE id = %s
            """
            
            cursor.execute(select_query, (blog_id,))
            blog = cursor.fetchone()
            
            cursor.close()
            connection.close()
            
            if blog:
                # Convert datetime objects to strings
                if blog['created_at']:
                    blog['created_at'] = blog['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                if blog['updated_at']:
                    blog['updated_at'] = blog['updated_at'].strftime('%Y-%m-%d %H:%M:%S')
            
            return blog
            
        except Error as e:
            logger.error(f"Error retrieving blog by ID: {e}")
            return None
    
    def update_blog(self, blog_id, topic, content):
        """Update an existing blog post"""
        try:
            connection = self.get_connection()
            if not connection:
                return False
            
            cursor = connection.cursor()
            
            update_query = """
            UPDATE blogs 
            SET topic = %s, content = %s 
            WHERE id = %s
            """
            
            cursor.execute(update_query, (topic, content, blog_id))
            success = cursor.rowcount > 0
            
            connection.commit()
            cursor.close()
            connection.close()
            
            if success:
                logger.info(f"Blog updated successfully: ID {blog_id}")
            
            return success
            
        except Error as e:
            logger.error(f"Error updating blog: {e}")
            return False
    
    def delete_blog(self, blog_id):
        """Delete a blog post"""
        try:
            connection = self.get_connection()
            if not connection:
                return False
            
            cursor = connection.cursor()
            
            delete_query = "DELETE FROM blogs WHERE id = %s"
            cursor.execute(delete_query, (blog_id,))
            
            success = cursor.rowcount > 0
            connection.commit()
            cursor.close()
            connection.close()
            
            if success:
                logger.info(f"Blog deleted successfully: ID {blog_id}")
            
            return success
            
        except Error as e:
            logger.error(f"Error deleting blog: {e}")
            return False
    
    def get_blog_count(self):
        """Get total number of blogs in the database"""
        try:
            connection = self.get_connection()
            if not connection:
                return 0
            
            cursor = connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM blogs")
            count = cursor.fetchone()[0]
            
            cursor.close()
            connection.close()
            
            return count
            
        except Error as e:
            logger.error(f"Error getting blog count: {e}")
            return 0