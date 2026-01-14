import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.data_fetcher import DataFetcher
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def collect_all_data():
    """Collect data from all external sources"""
    logger.info("Starting data collection...")
    
    fetcher = DataFetcher()
    
    # Fetch World Bank data
    logger.info("\nFetching World Bank debt statistics...")
    wb_data = fetcher.fetch_world_bank_data()
    wb_df = pd.DataFrame(wb_data)
    logger.info(f"Collected {len(wb_df)} World Bank records")
    
    # Fetch emissions data
    logger.info("\nFetching global emissions data...")
    emissions_data = fetcher.fetch_emissions_data()
    emissions_df = pd.DataFrame(emissions_data)
    logger.info(f"Collected {len(emissions_df)} emissions records")
    
    # Fetch energy data
    logger.info("\nFetching energy and sustainability data...")
    energy_data = fetcher.fetch_energy_data()
    energy_df = pd.DataFrame(energy_data)
    logger.info(f"Collected {len(energy_df)} energy records")
    
    # Save to CSV files
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    wb_df.to_csv(os.path.join(data_dir, 'world_bank_data.csv'), index=False)
    emissions_df.to_csv(os.path.join(data_dir, 'emissions_data.csv'), index=False)
    energy_df.to_csv(os.path.join(data_dir, 'energy_data.csv'), index=False)
    
    logger.info(f"\nData saved to {data_dir}")
    logger.info("Data collection completed successfully")

if __name__ == '__main__':
    collect_all_data()