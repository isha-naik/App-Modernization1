"""RAG Infrastructure - Bedrock + FAISS for semantic search"""
from typing import List, Dict, Optional, Any
from pathlib import Path
import json
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from src.knowledge_graph.graph import KnowledgeGraph


class GraphToDocuments:
    """Convert Knowledge Graph to LangChain Documents"""
    
    def __init__(self, knowledge_graph: KnowledgeGraph):
        self.kg = knowledge_graph
    
    def convert(self) -> List[Document]:
        """Convert all nodes to documents"""
        documents = []
        documents.extend(self._convert_classes())
        documents.extend(self._convert_methods())
        documents.extend(self._convert_endpoints())
        documents.extend(self._convert_fields())
        return documents
    
    def _convert_classes(self) -> List[Document]:
        """Convert class nodes to documents"""
        docs = []
        for class_id, class_node in self.kg.classes.items():
            content = f"""
Class: {class_node.name}
Package: {class_node.package}
Type: {class_node.java_type}
File: {class_node.file_path}
Modifiers: {', '.join(class_node.modifiers)}
Annotations: {', '.join(class_node.annotations)}
Interfaces: {', '.join(class_node.interfaces)}
Superclass: {class_node.superclass or 'None'}
Abstract: {class_node.is_abstract}
            """
            docs.append(Document(
                page_content=content,
                metadata={
                    'type': 'class',
                    'name': class_node.name,
                    'package': class_node.package,
                    'node_id': class_id
                }
            ))
        return docs
    
    def _convert_methods(self) -> List[Document]:
        """Convert method nodes to documents"""
        docs = []
        for method_id, method_node in self.kg.methods.items():
            params_str = ', '.join(
                [f"{p['type']} {p['name']}" for p in method_node.parameters]
            )
            content = f"""
Method: {method_node.name}
Class: {method_node.class_name}
Signature: {method_node.signature}
Return Type: {method_node.return_type}
Parameters: {params_str}
Modifiers: {', '.join(method_node.modifiers)}
Annotations: {', '.join(method_node.annotations)}
Lines: {method_node.line_start}-{method_node.line_end}
            """
            docs.append(Document(
                page_content=content,
                metadata={
                    'type': 'method',
                    'name': method_node.name,
                    'class': method_node.class_name,
                    'node_id': method_id
                }
            ))
        return docs
    
    def _convert_endpoints(self) -> List[Document]:
        """Convert endpoint nodes to documents"""
        docs = []
        for endpoint_id, endpoint_node in self.kg.endpoints.items():
            params_str = ', '.join(
                [f"{p.get('name', 'param')}: {p.get('type', 'unknown')}" 
                 for p in endpoint_node.params]
            )
            content = f"""
REST Endpoint
HTTP Method: {endpoint_node.http_method}
Path: {endpoint_node.path}
Handler: {endpoint_node.handler_class}.{endpoint_node.handler_method}
Parameters: {params_str}
Consumes: {', '.join(endpoint_node.consumes)}
Produces: {', '.join(endpoint_node.produces)}
            """
            docs.append(Document(
                page_content=content,
                metadata={
                    'type': 'endpoint',
                    'method': endpoint_node.http_method,
                    'path': endpoint_node.path,
                    'node_id': endpoint_id
                }
            ))
        return docs
    
    def _convert_fields(self) -> List[Document]:
        """Convert field nodes to documents"""
        docs = []
        for field_id, field_node in self.kg.fields.items():
            content = f"""
Field: {field_node.name}
Class: {field_node.class_name}
Type: {field_node.field_type}
Modifiers: {', '.join(field_node.modifiers)}
Annotations: {', '.join(field_node.annotations)}
Initial Value: {field_node.initial_value or 'None'}
            """
            docs.append(Document(
                page_content=content,
                metadata={
                    'type': 'field',
                    'name': field_node.name,
                    'class': field_node.class_name,
                    'node_id': field_id
                }
            ))
        return docs


class BedrockEmbeddingsLocal:
    """Local embeddings using sentence-transformers as fallback"""
    
    def __init__(self):
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
        except ImportError:
            print("Installing sentence-transformers...")
            import subprocess
            subprocess.check_call(['pip', 'install', 'sentence-transformers'])
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed documents"""
        return self.model.encode(texts, convert_to_numpy=True).tolist()
    
    def embed_query(self, text: str) -> List[float]:
        """Embed a single query"""
        return self.model.encode(text, convert_to_numpy=True).tolist()


class VectorStoreManager:
    """Manage FAISS vector store with embeddings"""
    
    def __init__(self, output_dimensionality: int = 384, use_bedrock: bool = False):
        self.output_dimensionality = output_dimensionality
        self.use_bedrock = use_bedrock
        self.vectorstore = None
        self.embeddings = BedrockEmbeddingsLocal()
        
        # Define index path
        self.index_path = Path("rag_indices")
        self.index_path.mkdir(exist_ok=True)
    
    def create_vectorstore(self, documents: List[Document], 
                          repo_name: str = "default") -> FAISS:
        """Create FAISS vectorstore from documents"""
        try:
            self.vectorstore = FAISS.from_documents(
                documents,
                self.embeddings
            )
            self.save_vectorstore(repo_name)
            return self.vectorstore
        except Exception as e:
            print(f"Error creating vectorstore: {e}")
            return None
    
    def save_vectorstore(self, repo_name: str = "default"):
        """Save vectorstore to disk"""
        try:
            save_path = self.index_path / repo_name
            save_path.mkdir(exist_ok=True)
            self.vectorstore.save_local(str(save_path))
            print(f"Vectorstore saved to {save_path}")
        except Exception as e:
            print(f"Error saving vectorstore: {e}")
    
    def load_vectorstore(self, repo_name: str = "default") -> Optional[FAISS]:
        """Load vectorstore from disk"""
        try:
            load_path = self.index_path / repo_name
            if load_path.exists():
                self.vectorstore = FAISS.load_local(
                    str(load_path),
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                return self.vectorstore
            return None
        except Exception as e:
            print(f"Error loading vectorstore: {e}")
            return None
    
    def search(self, query: str, k: int = 5) -> List[Document]:
        """Search vectorstore"""
        if not self.vectorstore:
            return []
        return self.vectorstore.similarity_search(query, k=k)
    
    def search_with_scores(self, query: str, k: int = 5) -> List[tuple]:
        """Search with similarity scores"""
        if not self.vectorstore:
            return []
        return self.vectorstore.similarity_search_with_score(query, k=k)


def convert_graph_to_documents(knowledge_graph: KnowledgeGraph) -> List[Document]:
    """Convenience function to convert graph to documents"""
    converter = GraphToDocuments(knowledge_graph)
    return converter.convert()
