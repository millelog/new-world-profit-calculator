import numpy as np
from database.operations.cache_operations import get_price_data



def extract_data_points(item_data):
    """Extract average availability, average price, and lowest price data points from item_data."""
    avg_avails = [entry["avg_avail"] for entry in item_data["price_graph_data"]]
    avg_prices = [entry["avg_price"] for entry in item_data["price_graph_data"]]
    lowest_prices = [entry["lowest_price"] for entry in item_data["price_graph_data"]]
    
    return avg_avails, avg_prices, lowest_prices

def calculate_derivative(data_points):
    """Calculate the derivative (rate of change) of a list of data points."""
    return [data_points[i+1] - data_points[i] for i in range(len(data_points)-1)]

def is_market_active(derivatives):
    """Check if the market activity is healthy."""
    
    # If more than half the derivatives in any list are zero, market is possibly stagnant
    for key, values in derivatives.items():
        if len([val for val in values if val == 0]) > len(values) / 2:
            return False

    #for key, values in derivatives.items():
    #    mean_derivative = np.mean(values)
    #    std_deviation = np.std(values)

        # Check for extreme values
    #    for val in values:
    #        if val < mean_derivative - 4*std_deviation or val > mean_derivative + 4*std_deviation:
    #            return False
    
    return True

def calculate_profit_potential(item_data, average_availabilities):
    """Calculate the raw money-making potential of an item."""
    
    # Extract the relevant data from item_data
    avg_availability = np.mean(average_availabilities)
    profit_per_unit = item_data["Profit"]

    # Calculate the profit potential
    profit_potential = avg_availability * profit_per_unit

    return profit_potential

def is_price_trending_upwards(price_data):
    """Check if the price of an item is trending upwards."""
    
    # Extract the list of lowest prices from price_data
    lowest_prices = [data_point["lowest_price"] for data_point in price_data["price_graph_data"]]

    # Calculate the derivative of the lowest prices
    price_derivatives = calculate_derivative(lowest_prices)

    # If the last derivative is positive, the price is trending upwards
    if price_derivatives:
        return price_derivatives[-1] > 0
    return False

def rank_items(items_dict):
    """Rank items based on their scores."""
    
    # Convert dictionary to list of tuples [(key, value), ...]
    items_list = list(items_dict.items())
    
    # Sort the items based on the given criteria
    ranked_items = sorted(
        items_list,
        key=lambda x: (
            x[1]["active"], 
            x[1]["upward_price"], 
            -x[1]["profit_potential"]
        ),
        reverse=True
    )

    # Convert back to dictionary
    ranked_dict = {item[0]: item[1] for item in ranked_items}
    
    return ranked_dict

def analyze_market_health(session, server_id, items_dict):
    """Main function to analyze and rank items based on market health."""
    
    for item_id, item_data in items_dict.items():
        # Extract data from cache
        price_data = get_price_data(session, item_id, server_id)

        # Check market activity
        activity_derivatives = {
            "avg_avail": calculate_derivative([data_point["avg_avail"] for data_point in price_data["price_graph_data"]]),
            "lowest_price": calculate_derivative([data_point["lowest_price"] for data_point in price_data["price_graph_data"]])
        }
        item_data["active"] = 1 if is_market_active(activity_derivatives) else 0

        # Check price trend
        item_data["upward_price"] = 1 if is_price_trending_upwards(price_data) else 0

        # Calculate raw profit-making potential
        item_data["profit_potential"] = calculate_profit_potential(item_data, [data_point["avg_avail"] for data_point in price_data["price_graph_data"]])

    # Rank the items
    ranked_items_dict = rank_items(items_dict)

    return ranked_items_dict