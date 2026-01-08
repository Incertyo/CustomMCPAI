"""
Database module for storing recommendations and logs
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

DB_PATH = "cloud_optimization.db"


class OptimizationDB:
    """Database manager for cloud optimization recommendations"""
    
    def __init__(self, db_path: str = DB_PATH):
        """Initialize database connection"""
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Recommendations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                resource_id TEXT,
                resource_type TEXT,
                issue TEXT,
                current_state TEXT,
                action TEXT,
                estimated_savings REAL,
                risk TEXT,
                priority TEXT,
                implementation_effort TEXT,
                status TEXT DEFAULT 'pending',
                approved BOOLEAN DEFAULT 0,
                approved_at DATETIME,
                metadata TEXT
            )
        """)
        
        # Analysis sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                total_savings REAL,
                recommendation_count INTEGER,
                summary TEXT,
                insights TEXT,
                status TEXT DEFAULT 'completed'
            )
        """)
        
        # Logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                level TEXT,
                component TEXT,
                message TEXT,
                metadata TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_recommendations(self, recommendations: Dict[str, Any], session_id: Optional[int] = None) -> int:
        """Save recommendations to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Save analysis session
        cursor.execute("""
            INSERT INTO analysis_sessions (total_savings, recommendation_count, summary, insights)
            VALUES (?, ?, ?, ?)
        """, (
            float(recommendations.get("total_potential_savings", "$0").replace("$", "").replace("/month", "")),
            len(recommendations.get("recommendations", [])),
            recommendations.get("summary", ""),
            json.dumps(recommendations.get("insights", []))
        ))
        
        session_id = cursor.lastrowid
        
        # Save individual recommendations
        for rec in recommendations.get("recommendations", []):
            savings_str = rec.get("estimated_savings", "$0/month")
            savings_value = float(savings_str.replace("$", "").replace("/month", "").strip())
            
            cursor.execute("""
                INSERT INTO recommendations (
                    resource_id, resource_type, issue, current_state, action,
                    estimated_savings, risk, priority, implementation_effort, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                rec.get("resource_id", ""),
                rec.get("resource_type", ""),
                rec.get("issue", ""),
                rec.get("current_state", ""),
                rec.get("action", ""),
                savings_value,
                rec.get("risk", "low"),
                rec.get("priority", "medium"),
                rec.get("implementation_effort", "low"),
                json.dumps(rec)
            ))
        
        conn.commit()
        conn.close()
        return session_id
    
    def get_recommendations(
        self,
        limit: int = 100,
        status: Optional[str] = None,
        resource_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get recommendations from database"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM recommendations WHERE 1=1"
        params = []
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        if resource_type:
            query += " AND resource_type = ?"
            params.append(resource_type)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        conn.close()
        return [dict(row) for row in rows]
    
    def get_analysis_sessions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get analysis sessions"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM analysis_sessions
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def approve_recommendation(self, recommendation_id: int):
        """Approve a recommendation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE recommendations
            SET approved = 1, approved_at = CURRENT_TIMESTAMP, status = 'approved'
            WHERE id = ?
        """, (recommendation_id,))
        
        conn.commit()
        conn.close()
    
    def reject_recommendation(self, recommendation_id: int):
        """Reject a recommendation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE recommendations
            SET status = 'rejected'
            WHERE id = ?
        """, (recommendation_id,))
        
        conn.commit()
        conn.close()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total recommendations
        cursor.execute("SELECT COUNT(*) FROM recommendations")
        total_recs = cursor.fetchone()[0]
        
        # Total savings
        cursor.execute("SELECT SUM(estimated_savings) FROM recommendations WHERE status != 'rejected'")
        total_savings = cursor.fetchone()[0] or 0
        
        # By status
        cursor.execute("""
            SELECT status, COUNT(*) FROM recommendations
            GROUP BY status
        """)
        by_status = dict(cursor.fetchall())
        
        # By resource type
        cursor.execute("""
            SELECT resource_type, COUNT(*) FROM recommendations
            GROUP BY resource_type
        """)
        by_type = dict(cursor.fetchall())
        
        # By risk
        cursor.execute("""
            SELECT risk, COUNT(*) FROM recommendations
            GROUP BY risk
        """)
        by_risk = dict(cursor.fetchall())
        
        # Recent sessions
        cursor.execute("SELECT COUNT(*) FROM analysis_sessions")
        total_sessions = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_recommendations": total_recs,
            "total_savings": total_savings,
            "by_status": by_status,
            "by_type": by_type,
            "by_risk": by_risk,
            "total_sessions": total_sessions
        }
    
    def log(self, level: str, component: str, message: str, metadata: Optional[Dict] = None):
        """Log an event"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO logs (level, component, message, metadata)
            VALUES (?, ?, ?, ?)
        """, (
            level,
            component,
            message,
            json.dumps(metadata) if metadata else None
        ))
        
        conn.commit()
        conn.close()
