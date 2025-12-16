"""
RAG Engine - Core retrieval and generation logic
"""

import os
from pathlib import Path
import time
from typing import List, Tuple, Optional
from llama_index.core import VectorStoreIndex, Settings, load_index_from_storage
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import PromptTemplate

from ..config import get_settings
from .document_processor import DocumentProcessor
from .vector_store import VectorStoreManager


class RAGEngine:
    """Core RAG system engine with improved vector store integration"""
    
    def __init__(self):
        self.settings = get_settings()
        self.vector_store_manager = VectorStoreManager()
        self._setup_models()
        self.index = None
        self.query_engine = None
        
    def _setup_models(self):
        """Initialize embeddings and LLM"""
        os.environ["GROQ_API_KEY"] = self.settings.groq_api_key
        
        Settings.embed_model = HuggingFaceEmbedding(self.settings.embedding_model)
        Settings.llm = Groq(model=self.settings.llm_model)
        Settings.text_splitter = SentenceSplitter(
            chunk_size=self.settings.chunk_size,
            chunk_overlap=self.settings.chunk_overlap
        )
        
        self.qa_prompt = PromptTemplate(
            "Context from your documents (may contain tables):\n"
            "---------------------\n"
            "{context_str}\n"
            "---------------------\n"
            "Using ONLY the context above, answer the question below.\n"
            "If calculation is needed, show every step.\n"
            "You MUST provide a final numerical answer or clear statement.\n"
            "Question: {query_str}\n"
            "Answer:"
        )
        
        self.refine_prompt = PromptTemplate(
            "We already have this answer: {existing_answer}\n"
            "New context (may contain tables):\n"
            "---------------------\n"
            "{context_str}\n"
            "---------------------\n"
            "If the new context adds useful data, refine or correct the answer.\n"
            "Always end with a clear final answer.\n"
            "Question: {query_str}\n"
            "Refined Answer:"
        )
    
    def load_or_create_index(self):
        """Load existing index or create new one"""
        persist_dir = self.settings.vector_db_dir
        
        # Create directories if they don't exist
        os.makedirs(persist_dir, exist_ok=True)
        os.makedirs(self.settings.upload_dir, exist_ok=True)
        
        # Check if index exists
        doc_count = self.vector_store_manager.get_document_count()
        
        if doc_count > 0:
            print(f"Loading existing index with {doc_count} documents...")
            try:
                # Load from existing vector store
                storage_context = self.vector_store_manager.get_storage_context()
                
                # Try to load existing index
                if os.path.exists(os.path.join(persist_dir, "docstore.json")):
                    self.index = load_index_from_storage(storage_context)
                else:
                    # Create new index with existing vectors
                    self.index = VectorStoreIndex(
                        [],
                        storage_context=storage_context
                    )
                
                print(f"✓ Loaded existing index with {doc_count} vectors")
            except Exception as e:
                print(f"Error loading index: {e}")
                print("Creating new index...")
                self._create_new_index()
        else:
            print("No existing documents found. Creating new index...")
            self._create_new_index()
        
        # Create query engine
        self._create_query_engine()
    
    def _create_new_index(self):
        """Create a new empty index"""
        storage_context = self.vector_store_manager.get_storage_context()
        self.index = VectorStoreIndex([], storage_context=storage_context)
        self.index.storage_context.persist(persist_dir=self.settings.vector_db_dir)
        print("✓ Created new empty index")
    
    def _create_query_engine(self):
        """Create or recreate the query engine"""
        self.query_engine = self.index.as_query_engine(
            similarity_top_k=self.settings.top_k,
            text_qa_template=self.qa_prompt,
            refine_template=self.refine_prompt,
            response_mode="compact",
            verbose=True
        )
    
    def add_document(self, file_path: str) -> bool:
        """Add a new document to the index"""
        try:
            print(f"Processing document: {file_path}")
            
            # Process document
            documents = DocumentProcessor.process_document(file_path)
            
            if not documents:
                print("No documents extracted")
                return False
            
            print(f"Extracted {len(documents)} chunks from document")
            
            # Add to index
            for doc in documents:
                self.index.insert(doc)
            
            # Persist changes
            self.index.storage_context.persist(persist_dir=self.settings.vector_db_dir)
            
            # Recreate query engine to include new documents
            self._create_query_engine()
            
            print(f"✓ Successfully added {len(documents)} chunks to index")
            return True
        
        except Exception as e:
            print(f"Error adding document: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def rebuild_index_from_uploads(self) -> bool:
        """Rebuild entire index from all files in upload directory"""
        try:
            print("Starting index rebuild...")
            
            # Clear existing collection
            self.vector_store_manager.clear_collection()
            
            # Create new index
            self._create_new_index()
            
            # Get all files from upload directory
            upload_dir = self.settings.upload_dir
            files = []
            
            for ext in ['.pdf', '.docx', '.doc', '.xlsx', '.xls']:
                files.extend(list(Path(upload_dir).glob(f'*{ext}')))
            
            if not files:
                print("No files found in upload directory")
                return True
            
            print(f"Found {len(files)} files to process")
            
            # Process each file
            for file_path in files:
                print(f"Processing: {file_path.name}")
                self.add_document(str(file_path))
            
            print("✓ Index rebuild completed")
            return True
            
        except Exception as e:
            print(f"Error rebuilding index: {e}")
            return False
    
    def delete_document(self, filename: str) -> bool:
        """Delete a document from the index"""
        try:
            success = self.vector_store_manager.delete_by_filename(filename)
            
            if success:
                # Recreate query engine
                self._create_query_engine()
            
            return success
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False
    
    def get_index_stats(self) -> dict:
        """Get statistics about the current index"""
        stats = self.vector_store_manager.get_collection_stats()
        
        if self.index:
            stats['index_loaded'] = True
            stats['query_engine_ready'] = self.query_engine is not None
        else:
            stats['index_loaded'] = False
            stats['query_engine_ready'] = False
        
        return stats
    
    def query(self, question: str) -> Tuple[str, List[dict], float]:
        """Query the RAG system"""
        if not self.query_engine:
            raise RuntimeError("Query engine not initialized. Call load_or_create_index() first.")
        
        start_time = time.time()
        
        try:
            response = self.query_engine.query(question)
            
            # Extract sources
            sources = []
            if hasattr(response, 'source_nodes'):
                for node in response.source_nodes[:5]:
                    metadata = node.metadata
                    
                    if metadata.get('source_type') == 'excel' or 'product' in metadata:
                        sources.append({
                            "type": "excel",
                            "filename": metadata.get('filename', 'Unknown'),
                            "content": f"{metadata.get('product', 'N/A')} - {metadata.get('type', 'N/A')} - {metadata.get('month', 'N/A')} {metadata.get('year', 'N/A')}"
                        })
                    elif metadata.get('source_type') == 'word':
                        sources.append({
                            "type": "word",
                            "filename": metadata.get('filename', 'Unknown'),
                            "content": node.text[:200] + "..." if len(node.text) > 200 else node.text
                        })
                    else:
                        sources.append({
                            "type": "pdf",
                            "filename": metadata.get('filename', metadata.get('file_name', 'Unknown')),
                            "content": node.text[:200] + "..." if len(node.text) > 200 else node.text
                        })
            
            processing_time = time.time() - start_time
            
            return str(response), sources, processing_time
        
        except Exception as e:
            print(f"Error during query: {e}")
            raise

# Global instance
rag_engine = RAGEngine()