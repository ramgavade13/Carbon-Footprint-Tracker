import os
import requests

def calculate_co2(activity_type, value, unit):
    """
    Mock implementation of a Carbon Calculation API (e.g. Climatiq or ADEME).
    If an API key is present, we could do a real requests.post to Climatiq here.
    For now, we use standard estimated emission factors.
    """
    api_key = os.getenv('CLIMATIQ_API_KEY')
    
    # NOTE: To use real climatiq integration, we would typically do:
    # url = "https://beta4.api.climatiq.io/estimate"
    # headers = {"Authorization": f"Bearer {api_key}"}
    # payload = {...}
    # response = requests.post(url, headers=headers, json=payload)
    # return response.json().get('co2e')
    
    # Fake API logic using standard factors for accurate offline functioning
    # electricity: ~0.45 kg CO2e per kWh (Global Average roughly)
    # transport: ~0.192 kg CO2e per km for avg petrol car
    # cloud: ~0.003 kg CO2e per GB
    # office_flight: ~90.0 kg CO2e per hour of flight
    
    if activity_type == 'electricity':
        # value in kWh
        return value * 0.45
    elif activity_type == 'transport':
        # value in km
        return value * 0.192
    elif activity_type == 'cloud':
        return value * 0.003
    elif activity_type == 'office_flight':
        return value * 90.0
    
    return 0.0

def get_suggestions(activity_type, co2_amount):
    # A typical tree absorbs ~21.7 kg of CO2 per year
    trees = int(co2_amount / 21.7) + 1
    
    tips = {
        'electricity': "Consider switching to LED bulbs or unplugging idle devices to lower this.",
        'transport': "Try carpooling, cycling, or ensuring your tires are properly inflated.",
        'cloud': "Optimize data storage and run workloads during off-peak hours.",
        'office_flight': "Replace short-haul business flights with virtual meetings where possible."
    }
    
    suggestion = tips.get(activity_type, "Small daily changes can significantly reduce your impact.")
    
    return {
        "trees": trees,
        "tip": suggestion
    }
