import pandas as pd
from datetime import datetime

def calculate_current_value(amount, start_date, end_date, inflation_data, ppi_data=None):
    """
    Calculate the current value of money considering monthly inflation rates and PPI
    
    Parameters:
    amount (float): Initial amount in PLN
    start_date (str): Start date in format 'YYYY-MM'
    end_date (str): End date in format 'YYYY-MM'
    inflation_data (dict): Dictionary with inflation data by year and month
    ppi_data (dict): Dictionary with PPI quarterly data
    
    Returns:
    float: Current value after inflation
    """
    start = datetime.strptime(start_date, '%Y-%m')
    end = datetime.strptime(end_date, '%Y-%m')
    
    current_value = amount
    
    df = pd.DataFrame(inflation_data)
    
    # Zaktualizowane dane kwartalne na podstawie raportu GUS z 04.12.2024
    quarterly_ppi = {
        '2024Q1': 1.042,  # wzrost o 4.2% w porównaniu z Q4 2023
        '2024Q2': 1.007,  # wzrost o 0.7% kw/kw
        '2024Q3': 1.007,  # wzrost o 0.7% kw/kw
        '2024Q4': 1.007   # estymacja na podstawie trendu z Q3
    }
    
    current_date = start
    while current_date <= end:
        year = str(current_date.year)
        month_idx = current_date.month - 1
        
        if year in df.columns and not pd.isna(df.iloc[month_idx][year]):
            yearly_rate = df.iloc[month_idx][year]
            # Konwersja rocznej stopy na miesięczną
            monthly_rate = (1 + yearly_rate/100)**(1/12) - 1
            current_value *= (1 + monthly_rate)
        
        # Dodanie korekty kwartalnej PPI
        quarter = f"{year}Q{(current_date.month-1)//3 + 1}"
        if quarter in quarterly_ppi:
            # Aplikujemy 1/3 efektu kwartalnego na każdy miesiąc
            monthly_ppi = quarterly_ppi[quarter]**(1/3)
            current_value *= monthly_ppi
            
        current_date = datetime(current_date.year + (current_date.month)//12,
                              (current_date.month % 12) + 1, 1)
    
    return round(current_value, 2)


def compare_rice_purchasing_power(price_2024, start_date, end_date, inflation_data):
    """
    Compare how much rice you could buy before and after inflation
    """
    # Obliczamy wartość 1 PLN z początku 2023 w 2024
    value_change = calculate_current_value(1, start_date, end_date, inflation_data)
    
    # Za 1 kg ryżu w 2024 trzeba zapłacić:
    kg_min_2024 = 3.68
    kg_max_2024 = 10.11
    
    # Ile kosztował 1 kg ryżu w 2023 (przeliczenie wstecz)
    kg_min_2023 = kg_min_2024 / value_change
    kg_max_2023 = kg_max_2024 / value_change
    
    return {
        '2023_min': kg_min_2023,
        '2023_max': kg_max_2023,
        '2024_min': kg_min_2024,
        '2024_max': kg_max_2024,
        'value_change': value_change
    }

# 2024-12-10 https://www.selinawamucii.com/insights/prices/poland/rice/
rice_prices = {
    'kg_min': 3.68,
    'kg_max': 10.11,
    'lb_min': 1.67,
    'lb_max': 4.59
}

inflation_data = {
    '2021': [2.6, 2.4, 3.2, 4.3, 4.7, 4.4, 5.0, 5.5, 5.9, 6.8, 7.8, 8.6],
    '2022': [9.4, 8.5, 11.0, 12.4, 13.9, 15.5, 15.6, 16.1, 17.2, 17.9, 17.5, 16.6],
    '2023': [16.6, 18.4, 16.1, 14.7, 13.0, 11.5, 10.8, 10.1, 8.2, 6.6, 6.6, 6.2],
    '2024': [3.7, 2.8, 2.0, 2.4, 2.5, 2.6, 4.2, 4.3, 4.9, 5.0, 4.6, 4.6]
}

initial_amount = 65
start_date = '2023-01'
end_date = '2024-12'

result = calculate_current_value(initial_amount, start_date, end_date, inflation_data)
comparison = compare_rice_purchasing_power(rice_prices, start_date, end_date, inflation_data)

print(f"{initial_amount} PLN z {start_date} jest warte {result} PLN w {end_date}")

print(f"\nPorównanie siły nabywczej (ryż):")
print(f"W styczniu 2023 1 kg ryżu kosztował: {comparison['2023_min']:.2f} - {comparison['2023_max']:.2f} PLN")
print(f"W grudniu 2024 1 kg ryżu kosztuje: {comparison['2024_min']:.2f} - {comparison['2024_max']:.2f} PLN")

print("\nInaczej mówiąc:")
print(f"Jeśli w styczniu 2023 kupiłeś 1 kg ryżu za {comparison['2023_max']:.2f} PLN (najdroższy),")
print(f"to dziś za tę samą kwotę (po inflacji) kupisz tylko {(comparison['value_change']/comparison['2024_max']*1000):.0f} gramów ryżu")

print("\nLub odwrotnie:")
print(f"Żeby kupić 1 kg tego samego ryżu w grudniu 2024,")
print(f"musisz zapłacić o {((comparison['2024_max']/comparison['2023_max'] - 1)*100):.1f}% więcej niż w styczniu 2023")
