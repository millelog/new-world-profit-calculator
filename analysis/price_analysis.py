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
    
    return True

def calculate_profit_potential(item_data):
    """Calculate the raw money-making potential of an item."""
    profit_per_unit = item_data["Profit"]
    average_available = item_data["avg_available"]

    profit_potential = average_available * profit_per_unit

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
            x[1]["profit_potential"]
        ),
        reverse=True
    )

    # Convert back to dictionary
    ranked_dict = {item[0]: item[1] for item in ranked_items}
    
    return ranked_dict

def get_mean_avg_availability(price_data):
    mean_value = np.mean([data_point["avg_avail"] for data_point in price_data["price_graph_data"]])

    if mean_value > 10:
        rounded_value = round(mean_value, -1)
    else:
        rounded_value = round(mean_value) 

    return rounded_value

def get_upward_price_signals(price_data, activity_derivatives):
    # Extract the necessary data
    avg_avails = [data_point["avg_avail"] for data_point in price_data["price_graph_data"]]
    avg_avail_derivative = activity_derivatives["avg_avail"]
    lowest_price_derivative = activity_derivatives["lowest_price"]
    
    # Ensure there are enough data points to analyze
    if len(avg_avails) < 2 or len(avg_avail_derivative) < 1 or len(lowest_price_derivative) < 1:
        return 0

    # Initialize the score to 0
    score = 0
    
    # Check for decreasing availability
    if avg_avail_derivative[-1] < 0:
        score += 1

    # Check for decreasing price with low availability
    if lowest_price_derivative[-1] < 0 and avg_avails[-1] < np.mean(avg_avails):
        score += 1

    # Check for inflection point in price
    # If the second last derivative is negative and the last one is positive
    if len(lowest_price_derivative) > 1 and lowest_price_derivative[-2] < 0 and lowest_price_derivative[-1] > 0:
        score += 1

    # Check for inflection point in availability
    if avg_avails[-1] < np.mean(avg_avails):
        score += 1

    return score


def analyze_market_health(session, server_id, items_dict):
    """Main function to analyze and rank items based on market health."""
    
    for item_id, item_data in items_dict.items():
        # Extract data from cache
        price_data = get_price_data(session, item_id, server_id)

        item_data["avg_available"] = get_mean_avg_availability(price_data)

        # Check market activity
        activity_derivatives = {
            "avg_avail": calculate_derivative([data_point["avg_avail"] for data_point in price_data["price_graph_data"]]),
            "lowest_price": calculate_derivative([data_point["lowest_price"] for data_point in price_data["price_graph_data"]]),
            "avg_price": calculate_derivative([data_point["avg_price"] for data_point in price_data["price_graph_data"]])
        }
        item_data["active"] = 1 if is_market_active(activity_derivatives) else 0

        # Check price trend
        item_data["upward_price"] = get_upward_price_signals(price_data, activity_derivatives)

        # Calculate raw profit-making potential
        item_data["profit_potential"] = calculate_profit_potential(item_data)

    # Rank the items
    ranked_items_dict = rank_items(items_dict)

    return ranked_items_dict