import requests
import time
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DataFetcher:
    
    @staticmethod
    def fetch_world_bank_data():
        logger.info("Fetching World Bank debt statistics")
        
        base_url = "http://api.worldbank.org/v2/country/all/indicator/"
        
        indicators = {
            'DT.DOD.DECT.CD': 'external_debt_stocks',
            'DT.INT.DECT.CD': 'interest_payments',
            'NY.GDP.MKTP.CD': 'gdp',
            'GC.DOD.TOTL.GD.ZS': 'government_debt_gdp',
            'DT.TDS.DECT.EX.ZS': 'debt_service_exports'
        }
        
        all_data = []
        
        for indicator_code, indicator_name in indicators.items():
            try:
                url = f"{base_url}{indicator_code}?format=json&per_page=500&date=2015:2023"
                response = requests.get(url, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    if len(data) > 1:
                        for record in data[1]:
                            if record['value'] is not None:
                                all_data.append({
                                    'country': record['country']['value'],
                                    'country_code': record['countryiso3code'],
                                    'year': int(record['date']),
                                    'indicator': indicator_name,
                                    'value': float(record['value'])
                                })
                
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error fetching {indicator_name}: {str(e)}")
        
        logger.info(f"Fetched {len(all_data)} World Bank records")
        return all_data
    
    @staticmethod
    def fetch_emissions_data():
        logger.info("Fetching global emissions data")
        
        base_url = "http://api.worldbank.org/v2/country/all/indicator/"
        
        emissions_indicators = {
            'EN.ATM.CO2E.KT': 'co2_emissions_kt',
            'EN.ATM.CO2E.PC': 'co2_emissions_per_capita',
            'EG.USE.COMM.FO.ZS': 'fossil_fuel_energy_consumption',
            'EG.FEC.RNEW.ZS': 'renewable_energy_consumption',
            'EN.ATM.GHGT.KT.CE': 'ghg_emissions'
        }
        
        emissions_data = []
        
        for indicator_code, indicator_name in emissions_indicators.items():
            try:
                url = f"{base_url}{indicator_code}?format=json&per_page=500&date=2015:2023"
                response = requests.get(url, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    if len(data) > 1:
                        for record in data[1]:
                            if record['value'] is not None:
                                emissions_data.append({
                                    'country': record['country']['value'],
                                    'country_code': record['countryiso3code'],
                                    'year': int(record['date']),
                                    'indicator': indicator_name,
                                    'value': float(record['value'])
                                })
                
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error fetching {indicator_name}: {str(e)}")
        
        logger.info(f"Fetched {len(emissions_data)} emissions records")
        return emissions_data
    
    @staticmethod
    def fetch_energy_data():
        logger.info("Fetching energy and sustainability metrics")
        
        base_url = "http://api.worldbank.org/v2/country/all/indicator/"
        
        energy_indicators = {
            'EG.USE.ELEC.KH.PC': 'electricity_consumption_per_capita',
            'EG.ELC.RNEW.ZS': 'renewable_electricity_output',
            'EN.ATM.PM25.MC.M3': 'pm25_air_pollution',
            'AG.LND.FRST.ZS': 'forest_area_percent',
            'ER.H2O.FWST.ZS': 'freshwater_stress'
        }
        
        energy_data = []
        
        for indicator_code, indicator_name in energy_indicators.items():
            try:
                url = f"{base_url}{indicator_code}?format=json&per_page=500&date=2015:2023"
                response = requests.get(url, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    if len(data) > 1:
                        for record in data[1]:
                            if record['value'] is not None:
                                energy_data.append({
                                    'country': record['country']['value'],
                                    'country_code': record['countryiso3code'],
                                    'year': int(record['date']),
                                    'indicator': indicator_name,
                                    'value': float(record['value'])
                                })
                
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error fetching {indicator_name}: {str(e)}")
        
        logger.info(f"Fetched {len(energy_data)} energy records")
        return energy_data
