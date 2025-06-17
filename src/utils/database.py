import sqlite3
import csv
import random
from typing import List, Optional
from pathlib import Path
from ..models import Quote, QuoteStatus

class QuoteDatabase:
    def __init__(self, db_path: str = "data/quotes/quotes.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        
    def _init_database(self):
        """Initialize database with quotes table."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS quotes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    quote TEXT NOT NULL,
                    author TEXT NOT NULL,
                    reflection TEXT NOT NULL,
                    social_media_post TEXT NOT NULL,
                    status TEXT DEFAULT 'unused'
                )
            """)
            conn.commit()
    
    def upload_csv(self, csv_file_path: str) -> int:
        """Upload quotes from CSV file. Returns number of added quotes."""
        added_count = 0
        
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            with sqlite3.connect(self.db_path) as conn:
                for row in reader:
                    # Map CSV columns to expected format
                    quote_data = {
                        'quote': row.get('QUOTE', '').strip(),
                        'author': row.get('AUTHOR', '').strip(),
                        'reflection': row.get('REFLECTION', '').strip(),
                        'social_media_post': row.get('SOCIAL_MEDIA_POST', '').strip(),
                        'status': 'unused'
                    }
                    
                    # Validate required fields
                    if not all([quote_data['quote'], quote_data['author'], 
                              quote_data['reflection'], quote_data['social_media_post']]):
                        continue
                        
                    # Check character limits
                    if len(quote_data['quote']) > 220 or len(quote_data['reflection']) > 220:
                        continue
                    
                    conn.execute("""
                        INSERT INTO quotes (quote, author, reflection, social_media_post, status)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        quote_data['quote'],
                        quote_data['author'],
                        quote_data['reflection'],
                        quote_data['social_media_post'],
                        quote_data['status']
                    ))
                    added_count += 1
                
                conn.commit()
        
        return added_count
    
    def get_random_unused_quote(self) -> Optional[Quote]:
        """Get a random unused quote. If no unused quotes, reset all and return one."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # First try to get unused quote
            cursor = conn.execute("""
                SELECT * FROM quotes WHERE status = 'unused'
            """)
            unused_quotes = cursor.fetchall()
            
            # If no unused quotes, reset all to unused
            if not unused_quotes:
                conn.execute("UPDATE quotes SET status = 'unused'")
                conn.commit()
                
                cursor = conn.execute("SELECT * FROM quotes WHERE status = 'unused'")
                unused_quotes = cursor.fetchall()
            
            if not unused_quotes:
                return None
                
            # Select random quote
            selected_row = random.choice(unused_quotes)
            return Quote(
                id=selected_row['id'],
                quote=selected_row['quote'],
                author=selected_row['author'],
                reflection=selected_row['reflection'],
                social_media_post=selected_row['social_media_post'],
                status=QuoteStatus.UNUSED
            )
    
    def mark_quote_used(self, quote_id: int):
        """Mark a quote as used."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE quotes SET status = 'used' WHERE id = ?", (quote_id,))
            conn.commit()
    
    def get_stats(self) -> dict:
        """Get database statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT status, COUNT(*) as count FROM quotes GROUP BY status")
            stats = dict(cursor.fetchall())
            
            cursor = conn.execute("SELECT COUNT(*) as total FROM quotes")
            total = cursor.fetchone()[0]
            
            return {
                'total': total,
                'unused': stats.get('unused', 0),
                'used': stats.get('used', 0)
            }