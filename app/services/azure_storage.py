import os
import uuid
from datetime import datetime
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.core.exceptions import AzureError, ResourceNotFoundError
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class AzureBlobStorageService:
    """Service class for Azure Blob Storage operations."""
    
    def __init__(self):
        self.connection_string = None
        self.container_name = None
        self.blob_service_client = None
        self._initialize()
    
    def _initialize(self):
        """Initialize Azure Blob Storage client."""
        try:
            self.connection_string = current_app.config.get('AZURE_STORAGE_CONNECTION_STRING')
            self.container_name = current_app.config.get('AZURE_CONTAINER_NAME', 'compliance-documents')
            
            if not self.connection_string:
                logger.warning("Azure Storage connection string not configured")
                return
            
            self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
            
            # Ensure container exists
            self._ensure_container_exists()
            
        except Exception as e:
            logger.error(f"Failed to initialize Azure Blob Storage: {e}")
            raise
    
    def _ensure_container_exists(self):
        """Ensure the container exists, create if it doesn't."""
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            container_client.get_container_properties()
        except ResourceNotFoundError:
            try:
                container_client = self.blob_service_client.create_container(self.container_name)
                logger.info(f"Created container: {self.container_name}")
            except Exception as e:
                logger.error(f"Failed to create container {self.container_name}: {e}")
                raise
        except Exception as e:
            logger.error(f"Error checking container {self.container_name}: {e}")
            raise
    
    def is_configured(self):
        """Check if Azure Storage is properly configured."""
        return self.connection_string is not None and self.blob_service_client is not None
    
    def generate_blob_name(self, original_filename, user_id):
        """Generate a unique blob name for the file."""
        # Get file extension
        file_ext = os.path.splitext(original_filename)[1].lower()
        
        # Generate unique identifier
        unique_id = str(uuid.uuid4())
        
        # Create timestamp
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        
        # Combine to create unique blob name
        blob_name = f"user_{user_id}/{timestamp}_{unique_id}{file_ext}"
        
        return blob_name
    
    def upload_file(self, file_stream, blob_name, content_type=None, metadata=None):
        """
        Upload a file to Azure Blob Storage.
        
        Args:
            file_stream: File stream to upload
            blob_name: Name for the blob in storage
            content_type: MIME type of the file
            metadata: Dictionary of metadata to store with the blob
        
        Returns:
            dict: Upload result with success status and blob info
        """
        if not self.is_configured():
            return {
                'success': False,
                'error': 'Azure Storage not configured',
                'error_code': 'STORAGE_NOT_CONFIGURED'
            }
        
        try:
            # Get blob client
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            # Prepare upload parameters
            upload_params = {
                'data': file_stream,
                'overwrite': True
            }
            
            if content_type:
                upload_params['content_settings'] = {
                    'content_type': content_type
                }
            
            if metadata:
                upload_params['metadata'] = metadata
            
            # Upload the file
            blob_client.upload_blob(**upload_params)
            
            # Get blob properties to confirm upload
            blob_properties = blob_client.get_blob_properties()
            
            return {
                'success': True,
                'blob_name': blob_name,
                'size': blob_properties.size,
                'last_modified': blob_properties.last_modified,
                'etag': blob_properties.etag,
                'url': blob_client.url
            }
            
        except AzureError as e:
            logger.error(f"Azure error uploading file {blob_name}: {e}")
            return {
                'success': False,
                'error': f'Azure storage error: {str(e)}',
                'error_code': 'AZURE_ERROR'
            }
        except Exception as e:
            logger.error(f"Unexpected error uploading file {blob_name}: {e}")
            return {
                'success': False,
                'error': f'Upload failed: {str(e)}',
                'error_code': 'UPLOAD_ERROR'
            }
    
    def download_file(self, blob_name):
        """
        Download a file from Azure Blob Storage.
        
        Args:
            blob_name: Name of the blob to download
        
        Returns:
            dict: Download result with success status and file data
        """
        if not self.is_configured():
            return {
                'success': False,
                'error': 'Azure Storage not configured',
                'error_code': 'STORAGE_NOT_CONFIGURED'
            }
        
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            # Download the blob
            blob_data = blob_client.download_blob()
            
            # Get blob properties
            blob_properties = blob_client.get_blob_properties()
            
            return {
                'success': True,
                'data': blob_data.readall(),
                'content_type': blob_properties.content_settings.content_type,
                'size': blob_properties.size,
                'last_modified': blob_properties.last_modified
            }
            
        except ResourceNotFoundError:
            logger.error(f"Blob not found: {blob_name}")
            return {
                'success': False,
                'error': 'File not found',
                'error_code': 'FILE_NOT_FOUND'
            }
        except AzureError as e:
            logger.error(f"Azure error downloading file {blob_name}: {e}")
            return {
                'success': False,
                'error': f'Azure storage error: {str(e)}',
                'error_code': 'AZURE_ERROR'
            }
        except Exception as e:
            logger.error(f"Unexpected error downloading file {blob_name}: {e}")
            return {
                'success': False,
                'error': f'Download failed: {str(e)}',
                'error_code': 'DOWNLOAD_ERROR'
            }
    
    def delete_file(self, blob_name):
        """
        Delete a file from Azure Blob Storage.
        
        Args:
            blob_name: Name of the blob to delete
        
        Returns:
            dict: Delete result with success status
        """
        if not self.is_configured():
            return {
                'success': False,
                'error': 'Azure Storage not configured',
                'error_code': 'STORAGE_NOT_CONFIGURED'
            }
        
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            # Delete the blob
            blob_client.delete_blob()
            
            return {
                'success': True,
                'message': f'File {blob_name} deleted successfully'
            }
            
        except ResourceNotFoundError:
            logger.warning(f"Attempted to delete non-existent blob: {blob_name}")
            return {
                'success': True,  # Consider it successful if file doesn't exist
                'message': 'File already deleted or does not exist'
            }
        except AzureError as e:
            logger.error(f"Azure error deleting file {blob_name}: {e}")
            return {
                'success': False,
                'error': f'Azure storage error: {str(e)}',
                'error_code': 'AZURE_ERROR'
            }
        except Exception as e:
            logger.error(f"Unexpected error deleting file {blob_name}: {e}")
            return {
                'success': False,
                'error': f'Delete failed: {str(e)}',
                'error_code': 'DELETE_ERROR'
            }
    
    def get_file_url(self, blob_name, expiry_hours=1):
        """
        Generate a signed URL for accessing a blob.
        
        Args:
            blob_name: Name of the blob
            expiry_hours: Hours until the URL expires
        
        Returns:
            dict: Result with success status and URL
        """
        if not self.is_configured():
            return {
                'success': False,
                'error': 'Azure Storage not configured',
                'error_code': 'STORAGE_NOT_CONFIGURED'
            }
        
        try:
            from azure.storage.blob import generate_blob_sas, BlobSasPermissions
            from datetime import timedelta
            
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            # Generate SAS token
            sas_token = generate_blob_sas(
                account_name=blob_client.account_name,
                container_name=self.container_name,
                blob_name=blob_name,
                account_key=blob_client.credential.account_key,
                permission=BlobSasPermissions(read=True),
                expiry=datetime.utcnow() + timedelta(hours=expiry_hours)
            )
            
            # Construct the full URL
            url = f"{blob_client.url}?{sas_token}"
            
            return {
                'success': True,
                'url': url,
                'expires_in_hours': expiry_hours
            }
            
        except Exception as e:
            logger.error(f"Error generating URL for {blob_name}: {e}")
            return {
                'success': False,
                'error': f'URL generation failed: {str(e)}',
                'error_code': 'URL_ERROR'
            }
    
    def list_files(self, prefix=None):
        """
        List files in the container.
        
        Args:
            prefix: Optional prefix to filter blobs
        
        Returns:
            dict: Result with success status and list of files
        """
        if not self.is_configured():
            return {
                'success': False,
                'error': 'Azure Storage not configured',
                'error_code': 'STORAGE_NOT_CONFIGURED'
            }
        
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            
            blobs = container_client.list_blobs(name_starts_with=prefix)
            
            file_list = []
            for blob in blobs:
                file_list.append({
                    'name': blob.name,
                    'size': blob.size,
                    'last_modified': blob.last_modified,
                    'content_type': blob.content_settings.content_type if blob.content_settings else None
                })
            
            return {
                'success': True,
                'files': file_list,
                'count': len(file_list)
            }
            
        except AzureError as e:
            logger.error(f"Azure error listing files: {e}")
            return {
                'success': False,
                'error': f'Azure storage error: {str(e)}',
                'error_code': 'AZURE_ERROR'
            }
        except Exception as e:
            logger.error(f"Unexpected error listing files: {e}")
            return {
                'success': False,
                'error': f'List operation failed: {str(e)}',
                'error_code': 'LIST_ERROR'
            }