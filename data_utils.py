#!/usr/bin/env python3
"""
Utility functions for microgrid data collection
"""

import requests
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional
import csv
import json

logger = logging.getLogger(__name__)

class DataCollectionUtils:
    """Utility functions for data collection"""
    
    @staticmethod
    def safe_request(url: str, params: Optional[Dict] = None, headers: Optional[Dict] = None, 
                     timeout: int = 30, max_retries: int = 3) -> Optional[requests.Response]:
        """Make a safe HTTP request with retries"""
        for attempt in range(max_retries):
            try:
                response = requests.get(url, params=params, headers=headers, timeout=timeout)
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"All retry attempts failed for {url}")
                    return None
        return None
    
    @staticmethod
    def save_csv(data: List[Dict], filepath: str, fieldnames: Optional[List[str]] = None):
        """Save data to CSV file"""
        if not data:
            logger.warning(f"No data to save to {filepath}")
            return
        
        if fieldnames is None:
            fieldnames = list(data[0].keys())
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        
        logger.info(f"Saved {len(data)} rows to {filepath}")
    
    @staticmethod
    def save_json(data: Dict, filepath: str):
        """Save data to JSON file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved data to {filepath}")
    
    @staticmethod
    def load_csv(filepath: str) -> List[Dict]:
        """Load data from CSV file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            return list(csv.DictReader(f))
    
    @staticmethod
    def add_metadata(data: Dict, source: str, collection_date: Optional[str] = None) -> Dict:
        """Add metadata to collected data"""
        if collection_date is None:
            collection_date = datetime.now().isoformat()
        
        data['_metadata'] = {
            'source': source,
            'collection_date': collection_date,
            'collector_version': '1.0'
        }
        return data
    
    @staticmethod
    def validate_coordinates(lat: float, lon: float) -> bool:
        """Validate GPS coordinates"""
        return -90 <= lat <= 90 and -180 <= lon <= 180
    
    @staticmethod
    def format_currency(value: float, decimals: int = 2) -> str:
        """Format value as currency"""
        return f"${value:,.{decimals}f}"
    
    @staticmethod
    def calculate_weighted_average(values: List[float], weights: List[float]) -> float:
        """Calculate weighted average"""
        if len(values) != len(weights) or not values:
            raise ValueError("Values and weights must have same length and be non-empty")
        return sum(v * w for v, w in zip(values, weights)) / sum(weights)
