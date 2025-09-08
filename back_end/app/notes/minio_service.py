from minio import Minio
from minio.error import S3Error
import os
import io
from typing import Optional
from datetime import timedelta
# from Config.config import minio_url, minio_username, minio_pwd

minio_url = os.getenv("MINIO_INTERNAL_URL")
minio_username = os.getenv("MINIO_USERNAME")
minio_pwd = os.getenv("MINIO_PWD")
server_ip = os.getenv("SERVER_IP")

class MinioService:
    def __init__(self):
        self.client = Minio(
            server_ip + ":9000",
            access_key=minio_username,
            secret_key=minio_pwd,
            secure=False
        )
        self.bucket_name = "notes"
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """确保存储桶存在"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                print(f"Created bucket: {self.bucket_name}")
        except S3Error as e:
            print(f"Error creating bucket: {e}")
            raise
    
    def create_user_directory(self, user_id: int):
        """创建用户目录"""
        user_dir = f"user_{user_id}/"
        try:
            # 在MinIO中创建目录（实际上是通过上传空对象实现的）
            self.client.put_object(
                self.bucket_name,
                user_dir,
                io.BytesIO(b""),
                0
            )
            print(f"Created user directory: {user_dir}")
        except S3Error as e:
            print(f"Error creating user directory: {e}")
            raise

    def create_organization_directory(self, organization_id: int):
        """创建组织目录"""
        org_dir = f"org_{organization_id}/"
        try:
            # 在MinIO中创建目录（实际上是通过上传空对象实现的）
            self.client.put_object(
                self.bucket_name,
                org_dir,
                io.BytesIO(b""),
                0
            )
            print(f"Created organization directory: {org_dir}")
        except S3Error as e:
            print(f"Error creating organization directory: {e}")
            raise
    
    def create_folder_directory(self, user_id: Optional[int], organization_id: Optional[int], folder_id: int):
        """创建文件夹目录"""
        if user_id:
            folder_dir = f"user_{user_id}/folder_{folder_id}/"
        else:
            folder_dir = f"org_{organization_id}/folder_{folder_id}/"
        try:
            self.client.put_object(
                self.bucket_name,
                folder_dir,
                io.BytesIO(b""),
                0
            )
            print(f"Created folder directory: {folder_dir}")
        except S3Error as e:
            print(f"Error creating folder directory: {e}")
            raise
    
    def create_note_directory(self, user_id: Optional[int], organization_id: Optional[int], folder_id: int, note_id: int):
        """创建笔记目录"""
        if user_id:
            note_dir = f"user_{user_id}/folder_{folder_id}/note_{note_id}/"
        else:
            note_dir = f"org_{organization_id}/folder_{folder_id}/note_{note_id}/"
        try:
            self.client.put_object(
                self.bucket_name,
                note_dir,
                io.BytesIO(b""),
                0
            )
            print(f"Created note directory: {note_dir}")
        except S3Error as e:
            print(f"Error creating note目录: {e}")
            raise
    
    def upload_file(self, user_id: Optional[int], organization_id: Optional[int], folder_id: int, note_id: int, 
                   file_name: str, file_data, file_size: int, content_type: str) -> str:
        """上传文件到MinIO"""
        if user_id:
            object_name = f"user_{user_id}/folder_{folder_id}/note_{note_id}/{file_name}"
        else:
            object_name = f"org_{organization_id}/folder_{folder_id}/note_{note_id}/{file_name}"
        data = io.BytesIO(file_data)
        
        try:
            self.client.put_object(
                self.bucket_name,
                object_name,
                data,
                file_size,
                content_type=content_type
            )
            
            # 生成预签名URL用于下载（7天有效期）
            download_url = self.client.presigned_get_object(
                self.bucket_name,
                object_name,
                expires=timedelta(days=7)
            )
            
            return download_url
        except S3Error as e:
            print(f"Error uploading file: {e}")
            raise
    
    def delete_file(self, user_id: Optional[int], organization_id: Optional[int], folder_id: int, note_id: int, file_name: str):
        """删除文件"""
        if user_id:
            object_name = f"user_{user_id}/folder_{folder_id}/note_{note_id}/{file_name}"
        else:
            object_name = f"org_{organization_id}/folder_{folder_id}/note_{note_id}/{file_name}"
        
        try:
            self.client.remove_object(self.bucket_name, object_name)
            print(f"Deleted file: {object_name}")
        except S3Error as e:
            print(f"Error deleting file: {e}")
            raise
    
    def delete_note_directory(self, user_id: Optional[int], organization_id: Optional[int], folder_id: int, note_id: int):
        """删除笔记目录及其所有文件"""
        if user_id:
            note_prefix = f"user_{user_id}/folder_{folder_id}/note_{note_id}/"
        else:
            note_prefix = f"org_{organization_id}/folder_{folder_id}/note_{note_id}/"
        
        try:
            # 列出并删除所有文件
            objects = self.client.list_objects(self.bucket_name, prefix=note_prefix, recursive=True)
            for obj in objects:
                self.client.remove_object(self.bucket_name, obj.object_name)
            
            print(f"Deleted note directory: {note_prefix}")
        except S3Error as e:
            print(f"Error deleting note directory: {e}")
            raise
    
    def delete_folder_directory(self, user_id: Optional[int], organization_id: Optional[int], folder_id: int):
        """删除文件夹目录及其所有内容"""
        if user_id:
            folder_prefix = f"user_{user_id}/folder_{folder_id}/"
        else:
            folder_prefix = f"org_{organization_id}/folder_{folder_id}/"
        
        try:
            # 列出并删除所有文件
            objects = self.client.list_objects(self.bucket_name, prefix=folder_prefix, recursive=True)
            for obj in objects:
                self.client.remove_object(self.bucket_name, obj.object_name)
            
            print(f"Deleted folder directory: {folder_prefix}")
        except S3Error as e:
            print(f"Error deleting folder directory: {e}")
            raise
    
    def delete_user_directory(self, user_id: int):
        """删除用户目录及其所有内容"""
        user_prefix = f"user_{user_id}/"
        
        try:
            # 列出并删除所有文件
            objects = self.client.list_objects(self.bucket_name, prefix=user_prefix, recursive=True)
            for obj in objects:
                self.client.remove_object(self.bucket_name, obj.object_name)
            
            print(f"Deleted user directory: {user_prefix}")
        except S3Error as e:
            print(f"Error deleting user directory: {e}")
            raise

    def delete_organization_directory(self, organization_id: int):
        """删除组织目录及其所有内容"""
        org_prefix = f"org_{organization_id}/"
        
        try:
            # 列出并删除所有文件
            objects = self.client.list_objects(self.bucket_name, prefix=org_prefix, recursive=True)
            for obj in objects:
                self.client.remove_object(self.bucket_name, obj.object_name)
            
            print(f"Deleted organization directory: {org_prefix}")
        except S3Error as e:
            print(f"Error deleting organization directory: {e}")
            raise

# 全局MinIO服务实例
minio_service = MinioService()
