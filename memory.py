import sqlite3
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from datetime import datetime

class Memory:
    """Memory store with semantic search."""
    
    def __init__(self, db_path="health_records.db"):
        self.db_path = db_path
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')  # Fast, lightweight
        self._init_db()
    
    def _init_db(self):
        """Initialize database tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # People table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS people (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            relationship TEXT,
            age INTEGER,
            conditions TEXT,  -- JSON list
            created_at TEXT
        )
        """)
        
        # Records table (structured health data)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            person_id INTEGER NOT NULL,
            record_type TEXT,  -- 'medication', 'lab', 'condition', 'appointment', 'note'
            content TEXT,
            date TEXT,
            metadata TEXT,  -- JSON
            embedding BLOB,  -- Numpy array serialized
            created_at TEXT,
            FOREIGN KEY (person_id) REFERENCES people (id)
        )
        """)
        
        # Feedback log (for learning)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT,
            agent_response TEXT,
            correction TEXT,
            created_at TEXT
        )
        """)
        
        conn.commit()
        conn.close()
    
    def add_person(self, name, relationship, age=None, conditions=None):
        """Add a family member."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO people (name, relationship, age, conditions, created_at) VALUES (?, ?, ?, ?, ?)",
                (name, relationship, age, json.dumps(conditions or []), datetime.now().isoformat())
            )
            conn.commit()
            person_id = cursor.lastrowid
            conn.close()
            return person_id
        except sqlite3.IntegrityError:
            conn.close()
            return None  # Person already exists
    
    def add_record(self, person_id, record_type, content, date=None, metadata=None):
        """Add a health record and embed it."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create embedding
        embedding = self.embedder.encode(content)
        embedding_blob = embedding.astype(np.float32).tobytes()
        
        cursor.execute("""
        INSERT INTO records (person_id, record_type, content, date, metadata, embedding, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            person_id,
            record_type,
            content,
            date or datetime.now().isoformat(),
            json.dumps(metadata or {}),
            embedding_blob,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def search_records(self, person_id, query, top_k=5):
        """Semantic search over a person's records."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all records for this person
        cursor.execute(
            "SELECT id, content, embedding FROM records WHERE person_id = ?",
            (person_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return []
        
        # Encode query
        query_embedding = self.embedder.encode(query)
        
        # Compute similarities
        scores = []
        for record_id, content, embedding_blob in rows:
            embedding = np.frombuffer(embedding_blob, dtype=np.float32)
            # Cosine similarity
            sim = np.dot(query_embedding, embedding) / (np.linalg.norm(query_embedding) * np.linalg.norm(embedding) + 1e-8)
            scores.append((record_id, content, sim))
        
        # Sort by similarity
        scores.sort(key=lambda x: x[2], reverse=True)
        
        return [{"id": s[0], "content": s[1], "similarity": float(s[2])} for s in scores[:top_k]]
    
    def get_person(self, name):
        """Get person by name."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, relationship, age, conditions FROM people WHERE name = ?", (name,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "id": row[0],
                "name": row[1],
                "relationship": row[2],
                "age": row[3],
                "conditions": json.loads(row[4]) if row[4] else []
            }
        return None
    
    def get_all_records(self, person_id, record_type=None):
        """Get all records for a person, optionally filtered by type."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if record_type:
            cursor.execute(
                "SELECT id, record_type, content, date FROM records WHERE person_id = ? AND record_type = ? ORDER BY date DESC",
                (person_id, record_type)
            )
        else:
            cursor.execute(
                "SELECT id, record_type, content, date FROM records WHERE person_id = ? ORDER BY date DESC",
                (person_id,)
            )
        
        rows = cursor.fetchall()
        conn.close()
        
        return [{"id": r[0], "type": r[1], "content": r[2], "date": r[3]} for r in rows]
    
    def add_feedback(self, query, agent_response, correction):
        """Log feedback for continuous learning."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO feedback (query, agent_response, correction, created_at) VALUES (?, ?, ?, ?)",
            (query, agent_response, correction, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
    
    def get_feedback(self, limit=10):
        """Get recent feedback for learning."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT query, agent_response, correction FROM feedback ORDER BY created_at DESC LIMIT ?",
            (limit,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {"query": r[0], "agent_response": r[1], "correction": r[2]}
            for r in rows
        ]
