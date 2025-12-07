"""
Universal data loader for all modules
"""
import sqlite3
import pandas as pd
from pathlib import Path
import json
from typing import Dict, List, Optional

class DataLoader:
    """Load and prepare data for all analysis modules"""
    
    def __init__(self, db_path: str = "data/db.sqlite"):
        self.db_path = Path(db_path)
        self.conn = None
        self.df = None
        self.metadata = {}
        
    def connect(self):
        """Connect to SQLite database"""
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found at {self.db_path}")
        
        self.conn = sqlite3.connect(self.db_path)
        return self.conn
    
    def load_raw_data(self) -> pd.DataFrame:
        """Load all raw data from database"""
        self.connect()
        query = "SELECT * FROM csat_extract"
        self.df = pd.read_sql_query(query, self.conn)
        
        # Basic cleaning
        if 'date_contact' in self.df.columns:
            self.df['date_contact'] = pd.to_datetime(
                self.df['date_contact'], errors='coerce'
            )
        
        # Generate unique customer IDs if not present
        if 'contact_id' not in self.df.columns:
            self.df['contact_id'] = range(1, len(self.df) + 1)
        
        return self.df
    
    def get_data_stats(self) -> Dict:
        """Get comprehensive data statistics"""
        if self.df is None:
            self.load_raw_data()
        
        stats = {
            "total_records": len(self.df),
            "columns": self.df.columns.tolist(),
            "date_range": {
                "min": str(self.df['date_contact'].min()),
                "max": str(self.df['date_contact'].max())
            } if 'date_contact' in self.df.columns else None,
            "csat_stats": {
                "mean": float(self.df['csat'].mean()),
                "std": float(self.df['csat'].std()),
                "distribution": self.df['csat'].value_counts().sort_index().to_dict()
            },
            "missing_values": self.df.isnull().sum().to_dict()
        }
        
        return stats
    
    def save_processed_data(self, df: pd.DataFrame, filename: str):
        """Save processed data for other modules"""
        output_path = Path("results") / filename
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        return output_path
    
    def load_processed_data(self, filename: str) -> pd.DataFrame:
        """Load previously processed data"""
        file_path = Path("results") / filename
        if file_path.exists():
            return pd.read_csv(file_path)
        else:
            raise FileNotFoundError(f"Processed data not found: {file_path}")
