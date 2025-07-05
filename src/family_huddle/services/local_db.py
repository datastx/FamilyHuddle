"""Local database service that mimics Supabase functionality."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

import pandas as pd


class LocalDatabase:
    """Mock Supabase client using local JSON storage."""
    
    def __init__(self, data_dir: str = "data/db"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._initialize_tables()
    
    def _initialize_tables(self):
        """Initialize empty tables if they don't exist."""
        tables = [
            "users", "profiles", "pools", "pool_participants",
            "nfl_teams", "team_selections", "nfl_seasons", 
            "nfl_weeks", "nfl_games", "team_performance", "pool_scores"
        ]
        
        for table in tables:
            table_path = self.data_dir / f"{table}.json"
            if not table_path.exists():
                with open(table_path, "w") as f:
                    json.dump([], f)
    
    def table(self, name: str):
        """Return a table query builder."""
        return TableQuery(self.data_dir, name)


class TableQuery:
    """Query builder for local table operations."""
    
    def __init__(self, data_dir: Path, table_name: str):
        self.data_dir = data_dir
        self.table_name = table_name
        self.table_path = data_dir / f"{table_name}.json"
        self.filters = []
        self.select_columns = None
        
    def _load_data(self) -> List[Dict[str, Any]]:
        """Load table data from JSON file."""
        try:
            with open(self.table_path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_data(self, data: List[Dict[str, Any]]):
        """Save table data to JSON file."""
        with open(self.table_path, "w") as f:
            json.dump(data, f, indent=2, default=str)
    
    def select(self, columns: str = "*"):
        """Select columns from table."""
        self.select_columns = columns
        return self
    
    def eq(self, column: str, value: Any):
        """Filter by equality."""
        self.filters.append(("eq", column, value))
        return self
    
    def insert(self, data: Dict[str, Any] | List[Dict[str, Any]]):
        """Insert data into table."""
        table_data = self._load_data()
        
        if isinstance(data, dict):
            data = [data]
        
        for record in data:
            # Add UUID if not present - handle special cases
            id_field = self._get_id_field()
            if id_field not in record:
                record[id_field] = str(uuid4())
            # Add timestamp if not present
            if "created_at" not in record:
                record["created_at"] = datetime.now().isoformat()
            
            table_data.append(record)
        
        self._save_data(table_data)
        return MockResult(data)
    
    def update(self, data: Dict[str, Any]):
        """Update records in table."""
        table_data = self._load_data()
        updated = []
        
        for record in table_data:
            if self._matches_filters(record):
                record.update(data)
                record["updated_at"] = datetime.now().isoformat()
                updated.append(record)
        
        self._save_data(table_data)
        return MockResult(updated)
    
    def delete(self):
        """Delete records from table."""
        table_data = self._load_data()
        remaining = []
        deleted = []
        
        for record in table_data:
            if self._matches_filters(record):
                deleted.append(record)
            else:
                remaining.append(record)
        
        self._save_data(remaining)
        return MockResult(deleted)
    
    def execute(self):
        """Execute the query and return results."""
        table_data = self._load_data()
        results = []
        
        for record in table_data:
            if self._matches_filters(record):
                if self.select_columns and self.select_columns != "*":
                    # Filter columns
                    selected = {}
                    columns = [col.strip() for col in self.select_columns.split(",")]
                    for col in columns:
                        if col in record:
                            selected[col] = record[col]
                    results.append(selected)
                else:
                    results.append(record)
        
        return MockResult(results)
    
    def _matches_filters(self, record: Dict[str, Any]) -> bool:
        """Check if record matches all filters."""
        for filter_type, column, value in self.filters:
            if filter_type == "eq":
                if record.get(column) != value:
                    return False
        return True
    
    def _get_id_field(self) -> str:
        """Get the ID field name for the table."""
        # Handle special cases
        if self.table_name == "nfl_teams":
            return "team_id"
        elif self.table_name == "nfl_seasons":
            return "season_id"
        elif self.table_name == "nfl_weeks":
            return "week_id"
        elif self.table_name == "nfl_games":
            return "game_id"
        # Default pattern: remove 's' and add '_id'
        return f"{self.table_name[:-1]}_id"


class MockResult:
    """Mock Supabase result object."""
    
    def __init__(self, data: List[Dict[str, Any]]):
        self.data = data
        self.error = None
        
    def single(self):
        """Return single result."""
        if self.data:
            return self.data[0]
        return None


def create_client(url: str, key: str) -> LocalDatabase:
    """Create a local database client (mock Supabase interface)."""
    return LocalDatabase()