from sqlalchemy import Column, Integer, String, JSON, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from ..config.database import Base

class APIProvider(Base):
    __tablename__ = "api_providers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    category = Column(String)  # trading, storage, news, etc.
    website = Column(String)
    documentation_url = Column(String)
    logo_url = Column(String)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    api_configs = relationship("APIConfiguration", back_populates="provider")
    endpoints = relationship("APIEndpoint", back_populates="provider")

class APIConfiguration(Base):
    __tablename__ = "api_configurations"

    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("api_providers.id"))
    name = Column(String)  # e.g., "Production", "Testing"
    config_type = Column(String)  # api_key, oauth, custom
    credentials = Column(JSON)  # Encrypted credentials
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Additional fields for OAuth
    oauth_client_id = Column(String, nullable=True)
    oauth_client_secret = Column(String, nullable=True)
    oauth_redirect_uri = Column(String, nullable=True)
    
    # Relationships
    provider = relationship("APIProvider", back_populates="api_configs")
    usage_logs = relationship("APIUsageLog", back_populates="config")

class APIEndpoint(Base):
    __tablename__ = "api_endpoints"

    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("api_providers.id"))
    name = Column(String)
    endpoint_url = Column(String)
    method = Column(String)  # GET, POST, etc.
    parameters = Column(JSON)  # Required and optional parameters
    headers = Column(JSON)  # Required headers
    rate_limit = Column(JSON)  # Rate limit details
    response_format = Column(JSON)  # Expected response format
    sample_response = Column(JSON)  # Sample response
    is_active = Column(Boolean, default=True)
    
    # Relationships
    provider = relationship("APIProvider", back_populates="endpoints")

class APIUsageLog(Base):
    __tablename__ = "api_usage_logs"

    id = Column(Integer, primary_key=True, index=True)
    config_id = Column(Integer, ForeignKey("api_configurations.id"))
    endpoint = Column(String)
    method = Column(String)
    status_code = Column(Integer)
    response_time = Column(Integer)  # in milliseconds
    error_message = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    config = relationship("APIConfiguration", back_populates="usage_logs")

class CustomCode(Base):
    __tablename__ = "custom_codes"

    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("api_providers.id"))
    name = Column(String)
    code_type = Column(String)  # python, javascript, etc.
    code_content = Column(String)
    description = Column(String)
    version = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CloudProvider(Base):
    __tablename__ = "cloud_providers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)  # aws, gcp, oracle
    config_type = Column(String)  # storage, compute, database
    credentials = Column(JSON)
    region = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # AWS Specific
    aws_access_key = Column(String, nullable=True)
    aws_secret_key = Column(String, nullable=True)
    aws_region = Column(String, nullable=True)
    aws_bucket = Column(String, nullable=True)

    # Google Cloud Specific
    gcp_project_id = Column(String, nullable=True)
    gcp_private_key = Column(String, nullable=True)
    gcp_client_email = Column(String, nullable=True)
    gcp_bucket = Column(String, nullable=True)

    # Oracle Cloud Specific
    oci_user_ocid = Column(String, nullable=True)
    oci_tenancy_ocid = Column(String, nullable=True)
    oci_fingerprint = Column(String, nullable=True)
    oci_private_key = Column(String, nullable=True)
    oci_region = Column(String, nullable=True)
    oci_namespace = Column(String, nullable=True)
    oci_bucket = Column(String, nullable=True)

    # Relationships
    storage_configs = relationship("CloudStorageConfig", back_populates="provider")
    usage_logs = relationship("CloudUsageLog", back_populates="provider")

class CloudStorageConfig(Base):
    __tablename__ = "cloud_storage_configs"

    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("cloud_providers.id"))
    name = Column(String)
    storage_type = Column(String)  # blob, file, object
    path_prefix = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    provider = relationship("CloudProvider", back_populates="storage_configs")

class CloudUsageLog(Base):
    __tablename__ = "cloud_usage_logs"

    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("cloud_providers.id"))
    operation = Column(String)  # upload, download, delete
    file_size = Column(Integer)  # in bytes
    status = Column(String)
    error_message = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    provider = relationship("CloudProvider", back_populates="usage_logs")
