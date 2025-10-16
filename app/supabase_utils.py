"""
Supabase integration utilities for Paper-CMS
"""
import os
from supabase import create_client, Client
from flask import current_app
import tempfile
from werkzeug.utils import secure_filename

class SupabaseClient:
    """Supabase client wrapper for Paper-CMS"""
    
    def __init__(self):
        self.client: Client = None
        self.storage_bucket = None
    
    def init_app(self, app):
        """Initialize Supabase client with Flask app"""
        supabase_url = app.config.get('SUPABASE_URL')
        supabase_key = app.config.get('SUPABASE_KEY') or app.config.get('SUPABASE_ANON_KEY')
        
        if supabase_url and supabase_key:
            try:
                self.client = create_client(supabase_url, supabase_key)
                self.storage_bucket = app.config.get('SUPABASE_STORAGE_BUCKET', 'papers')
                app.logger.info('Supabase client initialized successfully')
            except Exception as e:
                app.logger.warning(f'Failed to initialize Supabase client: {e}. Using local storage.')
                self.client = None
        else:
            app.logger.warning('Supabase credentials not found, using local storage')
    
    def upload_file(self, file, folder_path='papers'):
        """Upload file to Supabase Storage"""
        if not self.client:
            return self._save_local_file(file, folder_path)
        
        try:
            filename = secure_filename(file.filename)
            file_path = f"{folder_path}/{filename}"
            
            # Read file content
            file_content = file.read()
            file.seek(0)  # Reset file pointer
            
            # Upload to Supabase Storage
            result = self.client.storage.from_(self.storage_bucket).upload(
                path=file_path,
                file=file_content,
                file_options={
                    "content-type": file.content_type,
                    "cache-control": "3600"
                }
            )
            
            if result.status_code == 200:
                # Get public URL
                public_url = self.client.storage.from_(self.storage_bucket).get_public_url(file_path)
                return public_url
            else:
                current_app.logger.error(f"Failed to upload file: {result}")
                return self._save_local_file(file, folder_path)
                
        except Exception as e:
            current_app.logger.error(f"Supabase upload error: {e}")
            return self._save_local_file(file, folder_path)
    
    def _save_local_file(self, file, folder_path):
        """Fallback to local file storage"""
        try:
            # Create temp directory if it doesn't exist
            temp_dir = os.path.join('/tmp', 'uploads', folder_path)
            os.makedirs(temp_dir, exist_ok=True)
            
            filename = secure_filename(file.filename)
            file_path = os.path.join(temp_dir, filename)
            file.save(file_path)
            
            return file_path
        except Exception as e:
            current_app.logger.error(f"Local file save error: {e}")
            return None
    
    def delete_file(self, file_path):
        """Delete file from Supabase Storage"""
        if not self.client:
            return self._delete_local_file(file_path)
        
        try:
            result = self.client.storage.from_(self.storage_bucket).remove([file_path])
            return result.status_code == 200
        except Exception as e:
            current_app.logger.error(f"Supabase delete error: {e}")
            return False
    
    def _delete_local_file(self, file_path):
        """Delete local file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            current_app.logger.error(f"Local file delete error: {e}")
            return False
    
    def get_file_url(self, file_path):
        """Get public URL for file"""
        if not self.client:
            return file_path  # Return local path
        
        try:
            public_url = self.client.storage.from_(self.storage_bucket).get_public_url(file_path)
            return public_url
        except Exception as e:
            current_app.logger.error(f"Error getting file URL: {e}")
            return file_path

# Global Supabase client instance
supabase_client = SupabaseClient()