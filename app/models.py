import sqlite3
import hashlib
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask import current_app
import os

class User(UserMixin):
    """User model for authentication and user management."""
    
    def __init__(self, id=None, email=None, password_hash=None, created_at=None, is_active=True):
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at or datetime.utcnow()
        self.is_active = is_active
    
    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if the provided password matches the user's password."""
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        """Return the user ID as a string (required by Flask-Login)."""
        return str(self.id)
    
    @staticmethod
    def get_db_connection():
        """Get database connection."""
        db_path = current_app.config.get('DATABASE_URL', 'sqlite:///compliance.db').replace('sqlite:///', '')
        return sqlite3.connect(db_path)
    
    @classmethod
    def create_user(cls, email, password):
        """Create a new user in the database."""
        conn = cls.get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Check if user already exists
            cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
            if cursor.fetchone():
                return None  # User already exists
            
            # Create new user
            user = cls(email=email)
            user.set_password(password)
            
            cursor.execute('''
                INSERT INTO users (email, password_hash, created_at, is_active)
                VALUES (?, ?, ?, ?)
            ''', (user.email, user.password_hash, user.created_at, user.is_active))
            
            user.id = cursor.lastrowid
            conn.commit()
            return user
            
        except sqlite3.Error as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    @classmethod
    def get_by_id(cls, user_id):
        """Get user by ID."""
        conn = cls.get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, email, password_hash, created_at, is_active
                FROM users WHERE id = ?
            ''', (user_id,))
            
            row = cursor.fetchone()
            if row:
                return cls(
                    id=row[0],
                    email=row[1],
                    password_hash=row[2],
                    created_at=row[3],
                    is_active=bool(row[4])
                )
            return None
            
        except sqlite3.Error:
            return None
        finally:
            conn.close()
    
    @classmethod
    def get_by_email(cls, email):
        """Get user by email."""
        conn = cls.get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, email, password_hash, created_at, is_active
                FROM users WHERE email = ?
            ''', (email,))
            
            row = cursor.fetchone()
            if row:
                return cls(
                    id=row[0],
                    email=row[1],
                    password_hash=row[2],
                    created_at=row[3],
                    is_active=bool(row[4])
                )
            return None
            
        except sqlite3.Error:
            return None
        finally:
            conn.close()
    
    def save(self):
        """Save user changes to database."""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        try:
            if self.id:
                # Update existing user
                cursor.execute('''
                    UPDATE users 
                    SET email = ?, password_hash = ?, is_active = ?
                    WHERE id = ?
                ''', (self.email, self.password_hash, self.is_active, self.id))
            else:
                # Insert new user
                cursor.execute('''
                    INSERT INTO users (email, password_hash, created_at, is_active)
                    VALUES (?, ?, ?, ?)
                ''', (self.email, self.password_hash, self.created_at, self.is_active))
                self.id = cursor.lastrowid
            
            conn.commit()
            return True
            
        except sqlite3.Error:
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def __repr__(self):
        return f'<User {self.email}>'


class Document:
    """Document model for file metadata management."""
    
    def __init__(self, id=None, filename=None, original_filename=None, blob_name=None, 
                 file_size=None, content_type=None, uploaded_by=None, uploaded_at=None, is_active=True):
        self.id = id
        self.filename = filename
        self.original_filename = original_filename
        self.blob_name = blob_name
        self.file_size = file_size
        self.content_type = content_type
        self.uploaded_by = uploaded_by
        self.uploaded_at = uploaded_at or datetime.utcnow()
        self.is_active = is_active
    
    @staticmethod
    def get_db_connection():
        """Get database connection."""
        db_path = current_app.config.get('DATABASE_URL', 'sqlite:///compliance.db').replace('sqlite:///', '')
        return sqlite3.connect(db_path)
    
    @classmethod
    def create_document(cls, filename, original_filename, blob_name, file_size, content_type, uploaded_by):
        """Create a new document record in the database."""
        conn = cls.get_db_connection()
        cursor = conn.cursor()
        
        try:
            document = cls(
                filename=filename,
                original_filename=original_filename,
                blob_name=blob_name,
                file_size=file_size,
                content_type=content_type,
                uploaded_by=uploaded_by
            )
            
            cursor.execute('''
                INSERT INTO documents (filename, original_filename, blob_name, file_size, 
                                     content_type, uploaded_by, uploaded_at, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (document.filename, document.original_filename, document.blob_name,
                  document.file_size, document.content_type, document.uploaded_by,
                  document.uploaded_at, document.is_active))
            
            document.id = cursor.lastrowid
            conn.commit()
            return document
            
        except sqlite3.Error as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    @classmethod
    def get_by_id(cls, document_id):
        """Get document by ID."""
        conn = cls.get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, filename, original_filename, blob_name, file_size,
                       content_type, uploaded_by, uploaded_at, is_active
                FROM documents WHERE id = ?
            ''', (document_id,))
            
            row = cursor.fetchone()
            if row:
                return cls(
                    id=row[0],
                    filename=row[1],
                    original_filename=row[2],
                    blob_name=row[3],
                    file_size=row[4],
                    content_type=row[5],
                    uploaded_by=row[6],
                    uploaded_at=row[7],
                    is_active=bool(row[8])
                )
            return None
            
        except sqlite3.Error:
            return None
        finally:
            conn.close()
    
    @classmethod
    def get_by_user(cls, user_id, limit=None):
        """Get all documents uploaded by a specific user."""
        conn = cls.get_db_connection()
        cursor = conn.cursor()
        
        try:
            query = '''
                SELECT id, filename, original_filename, blob_name, file_size,
                       content_type, uploaded_by, uploaded_at, is_active
                FROM documents 
                WHERE uploaded_by = ? AND is_active = 1
                ORDER BY uploaded_at DESC
            '''
            
            if limit:
                query += f' LIMIT {limit}'
            
            cursor.execute(query, (user_id,))
            
            documents = []
            for row in cursor.fetchall():
                documents.append(cls(
                    id=row[0],
                    filename=row[1],
                    original_filename=row[2],
                    blob_name=row[3],
                    file_size=row[4],
                    content_type=row[5],
                    uploaded_by=row[6],
                    uploaded_at=row[7],
                    is_active=bool(row[8])
                ))
            
            return documents
            
        except sqlite3.Error:
            return []
        finally:
            conn.close()
    
    @classmethod
    def get_all_active(cls, limit=None):
        """Get all active documents."""
        conn = cls.get_db_connection()
        cursor = conn.cursor()
        
        try:
            query = '''
                SELECT d.id, d.filename, d.original_filename, d.blob_name, d.file_size,
                       d.content_type, d.uploaded_by, d.uploaded_at, d.is_active,
                       u.email as uploader_email
                FROM documents d
                JOIN users u ON d.uploaded_by = u.id
                WHERE d.is_active = 1
                ORDER BY d.uploaded_at DESC
            '''
            
            if limit:
                query += f' LIMIT {limit}'
            
            cursor.execute(query)
            
            documents = []
            for row in cursor.fetchall():
                doc = cls(
                    id=row[0],
                    filename=row[1],
                    original_filename=row[2],
                    blob_name=row[3],
                    file_size=row[4],
                    content_type=row[5],
                    uploaded_by=row[6],
                    uploaded_at=row[7],
                    is_active=bool(row[8])
                )
                doc.uploader_email = row[9]  # Add uploader email for display
                documents.append(doc)
            
            return documents
            
        except sqlite3.Error:
            return []
        finally:
            conn.close()
    
    def save(self):
        """Save document changes to database."""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        try:
            if self.id:
                # Update existing document
                cursor.execute('''
                    UPDATE documents 
                    SET filename = ?, original_filename = ?, blob_name = ?,
                        file_size = ?, content_type = ?, is_active = ?
                    WHERE id = ?
                ''', (self.filename, self.original_filename, self.blob_name,
                      self.file_size, self.content_type, self.is_active, self.id))
            else:
                # Insert new document
                cursor.execute('''
                    INSERT INTO documents (filename, original_filename, blob_name, file_size,
                                         content_type, uploaded_by, uploaded_at, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (self.filename, self.original_filename, self.blob_name,
                      self.file_size, self.content_type, self.uploaded_by,
                      self.uploaded_at, self.is_active))
                self.id = cursor.lastrowid
            
            conn.commit()
            return True
            
        except sqlite3.Error:
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def delete(self):
        """Soft delete document (set is_active to False)."""
        self.is_active = False
        return self.save()
    
    def get_file_size_formatted(self):
        """Return formatted file size."""
        if not self.file_size:
            return "Unknown"
        
        # Convert bytes to human readable format
        for unit in ['B', 'KB', 'MB', 'GB']:
            if self.file_size < 1024.0:
                return f"{self.file_size:.1f} {unit}"
            self.file_size /= 1024.0
        return f"{self.file_size:.1f} TB"
    
    def __repr__(self):
        return f'<Document {self.filename}>'