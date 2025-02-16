from typing import Dict, List
import asyncio
from datetime import datetime
import json
from google.cloud import storage
from oci.object_storage import ObjectStorageClient
from oci.config import from_file as oci_config_from_file

class FailoverManager:
    def __init__(self):
        # Initialize cloud clients
        self.oci_client = ObjectStorageClient(oci_config_from_file())
        self.gcp_client = storage.Client()
        
        # Configuration
        self.primary_cloud = "oracle"  # Oracle Cloud as primary
        self.backup_cloud = "gcp"      # Google Cloud as backup
        self.check_interval = 60       # Check every 60 seconds
        
        # Monitoring state
        self.last_check = None
        self.primary_healthy = True
        self.failover_active = False
        
    async def start_monitoring(self):
        """Start continuous monitoring of cloud services"""
        print("Starting cloud failover monitoring...")
        while True:
            try:
                await self.check_health()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                print(f"Error in monitoring: {str(e)}")
                await asyncio.sleep(self.check_interval)
    
    async def check_health(self):
        """Check health of both cloud services"""
        self.last_check = datetime.now()
        
        # Check primary (Oracle Cloud)
        primary_health = await self.check_oracle_health()
        
        # If primary is unhealthy and failover not active
        if not primary_health and not self.failover_active:
            await self.activate_failover()
        
        # If primary is healthy and failover is active
        elif primary_health and self.failover_active:
            await self.deactivate_failover()
        
        self.primary_healthy = primary_health
    
    async def check_oracle_health(self) -> bool:
        """Check Oracle Cloud health"""
        try:
            # Check compute instance status
            compute_healthy = await self.check_oracle_compute()
            
            # Check storage access
            storage_healthy = await self.check_oracle_storage()
            
            # Check network latency
            network_healthy = await self.check_oracle_network()
            
            return all([compute_healthy, storage_healthy, network_healthy])
            
        except Exception as e:
            print(f"Oracle health check failed: {str(e)}")
            return False
    
    async def activate_failover(self):
        """Activate failover to Google Cloud"""
        try:
            print("Activating failover to Google Cloud...")
            
            # 1. Stop non-critical services
            await self.stop_non_critical_services()
            
            # 2. Sync latest data to Google Cloud
            await self.sync_to_google_cloud()
            
            # 3. Update DNS/routing
            await self.update_routing_to_backup()
            
            # 4. Start services on Google Cloud
            await self.start_backup_services()
            
            self.failover_active = True
            print("Failover activated successfully")
            
        except Exception as e:
            print(f"Failover activation failed: {str(e)}")
    
    async def deactivate_failover(self):
        """Deactivate failover and return to Oracle Cloud"""
        try:
            print("Deactivating failover, returning to Oracle Cloud...")
            
            # 1. Sync latest data back to Oracle
            await self.sync_to_oracle_cloud()
            
            # 2. Update DNS/routing
            await self.update_routing_to_primary()
            
            # 3. Stop backup services
            await self.stop_backup_services()
            
            self.failover_active = False
            print("Failover deactivated successfully")
            
        except Exception as e:
            print(f"Failover deactivation failed: {str(e)}")
    
    async def sync_to_google_cloud(self):
        """Sync critical data to Google Cloud"""
        try:
            # 1. Get list of critical data
            critical_data = await self.get_critical_data_list()
            
            # 2. Upload to Google Cloud Storage
            bucket = self.gcp_client.bucket('ai-trading-backup')
            
            for data in critical_data:
                blob = bucket.blob(data['path'])
                blob.upload_from_string(
                    json.dumps(data['content']),
                    content_type='application/json'
                )
            
            print(f"Synced {len(critical_data)} items to Google Cloud")
            
        except Exception as e:
            print(f"Google Cloud sync failed: {str(e)}")
            raise
    
    async def sync_to_oracle_cloud(self):
        """Sync data back to Oracle Cloud"""
        try:
            # 1. Get list of updated data from Google Cloud
            updated_data = await self.get_updated_data_from_gcp()
            
            # 2. Upload to Oracle Cloud Storage
            for data in updated_data:
                self.oci_client.put_object(
                    namespace_name="ai-trading",
                    bucket_name="primary-storage",
                    object_name=data['path'],
                    put_object_body=json.dumps(data['content'])
                )
            
            print(f"Synced {len(updated_data)} items back to Oracle Cloud")
            
        except Exception as e:
            print(f"Oracle Cloud sync failed: {str(e)}")
            raise
    
    async def update_routing_to_backup(self):
        """Update routing to point to Google Cloud"""
        # Implement DNS/routing update logic
        pass
    
    async def update_routing_to_primary(self):
        """Update routing to point back to Oracle Cloud"""
        # Implement DNS/routing update logic
        pass
    
    async def get_failover_status(self) -> Dict:
        """Get current failover status"""
        return {
            'primary_cloud': self.primary_cloud,
            'backup_cloud': self.backup_cloud,
            'primary_healthy': self.primary_healthy,
            'failover_active': self.failover_active,
            'last_check': self.last_check.isoformat() if self.last_check else None
        }
    
    async def get_health_metrics(self) -> Dict:
        """Get detailed health metrics"""
        return {
            'oracle_cloud': {
                'compute': await self.check_oracle_compute(),
                'storage': await self.check_oracle_storage(),
                'network': await self.check_oracle_network()
            },
            'google_cloud': {
                'compute': await self.check_gcp_compute(),
                'storage': await self.check_gcp_storage(),
                'network': await self.check_gcp_network()
            }
        }
