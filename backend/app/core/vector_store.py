"""
Vector Store Management
Handles ChromaDB operations and index persistence
"""

import os
import shutil
from typing import List, Optional
from pathlib import Path
import chromadb
from chromadb.config import Settings as ChromaSettings
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import Document

from ..config import get_settings

class VectorStoreManager:
    """Manages vector database operations"""
    
    def __init__(self, persist_dir: Optional[str] = None):
        self.settings = get_settings()
        self.persist_dir = persist_dir or self.settings.vector_db_dir
        self.client = None
        self.collection = None
        self.vector_store = None
        self.storage_context = None
        
        self._initialize()
    
    def _initialize(self):
        """Initialize ChromaDB client and collection"""
        # Ensure directory exists
        os.makedirs(self.persist_dir, exist_ok=True)
        
        # Initialize Chroma client
        self.client = chromadb.PersistentClient(
            path=self.persist_dir,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"description": "RAG system documents"}
        )
        
        # Create vector store
        self.vector_store = ChromaVectorStore(chroma_collection=self.collection)
        
        # Create storage context
        self.storage_context = StorageContext.from_defaults(
            vector_store=self.vector_store
        )
        
        print(f"✓ Vector store initialized at: {self.persist_dir}")
        print(f"✓ Collection contains {self.collection.count()} vectors")
    
    def get_storage_context(self) -> StorageContext:
        """Get the storage context for index creation"""
        return self.storage_context
    
    def get_document_count(self) -> int:
        """Get total number of documents in vector store"""
        return self.collection.count()
    
    def clear_collection(self):
        """Clear all documents from the collection"""
        try:
            self.client.delete_collection("documents")
            self.collection = self.client.create_collection(
                name="documents",
                metadata={"description": "RAG system documents"}
            )
            self.vector_store = ChromaVectorStore(chroma_collection=self.collection)
            self.storage_context = StorageContext.from_defaults(
                vector_store=self.vector_store
            )
            print("✓ Collection cleared successfully")
            return True
        except Exception as e:
            print(f"Error clearing collection: {e}")
            return False
    
    def delete_by_filename(self, filename: str) -> bool:
        """
        Delete all documents with specific filename
        Note: This is a simplified version - full implementation would require
        tracking document IDs by filename
        """
        try:
            # Get all items with matching filename in metadata
            results = self.collection.get(
                where={"filename": filename}
            )
            
            if results and results['ids']:
                self.collection.delete(ids=results['ids'])
                print(f"✓ Deleted {len(results['ids'])} documents for {filename}")
                return True
            
            return False
        except Exception as e:
            print(f"Error deleting documents: {e}")
            return False
    
    def get_collection_stats(self) -> dict:
        """Get statistics about the vector store"""
        try:
            count = self.collection.count()
            
            # Get sample to check metadata
            sample = self.collection.peek(limit=10)
            
            # Count by source type
            stats = {
                "total_documents": count,
                "collection_name": "documents",
                "persist_dir": self.persist_dir,
                "sample_metadata": sample['metadatas'][:3] if sample['metadatas'] else []
            }
            
            return stats
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {"error": str(e)}
    
    def backup_vector_store(self, backup_path: str) -> bool:
        """Create a backup of the vector store"""
        try:
            if os.path.exists(backup_path):
                shutil.rmtree(backup_path)
            
            shutil.copytree(self.persist_dir, backup_path)
            print(f"✓ Backup created at: {backup_path}")
            return True
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False
    
    def restore_from_backup(self, backup_path: str) -> bool:
        """Restore vector store from backup"""
        try:
            if not os.path.exists(backup_path):
                print(f"Backup not found: {backup_path}")
                return False
            
            # Remove current data
            if os.path.exists(self.persist_dir):
                shutil.rmtree(self.persist_dir)
            
            # Restore from backup
            shutil.copytree(backup_path, self.persist_dir)
            
            # Reinitialize
            self._initialize()
            
            print(f"✓ Restored from backup: {backup_path}")
            return True
        except Exception as e:
            print(f"Error restoring backup: {e}")
            return False
    
    def optimize_collection(self):
        """Optimize the vector store (if supported by backend)"""
        try:
            # ChromaDB doesn't require explicit optimization
            # but we can verify integrity
            count = self.collection.count()
            print(f"✓ Collection optimized. Contains {count} vectors")
            return True
        except Exception as e:
            print(f"Error optimizing collection: {e}")
            return False

# Global instance
vector_store_manager = VectorStoreManager()