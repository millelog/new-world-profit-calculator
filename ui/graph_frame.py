import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from database.operations.cache_operations import get_price_data
class ItemGraphFrame(ttk.Frame):
    def __init__(self, parent, session, data_store):
        super().__init__(parent)
        self.session = session
        self.data_store = data_store

        self.plot_button = ttk.Button(self, text="Fetch & Plot", command=self.plot_prices)
        self.plot_button.pack(pady=20)


    def plot_prices(self):
        plt.close()

        data =  get_price_data(self.session, self.data_store.item_id, self.data_store.server_id)

        if not data:
            return

        # Extract data for plotting
        dates = [entry['date_only'] for entry in data['price_graph_data']]
        rolling_avg = [entry['rolling_average'] for entry in data['price_graph_data']]
        avg_price = [entry['avg_price'] for entry in data['price_graph_data']]
        lowest_price = [entry['lowest_price'] for entry in data['price_graph_data']]
        avg_avail = [entry['avg_avail'] for entry in data['price_graph_data']]
        
        fig, ax1 = plt.subplots(figsize=(10, 5))

        # Plot rolling average, avg_price, and lowest_price on the primary y-axis (left)
        ax1.plot(dates, rolling_avg, marker='o', linestyle='-', color='b', label='Rolling Average')
        ax1.plot(dates, avg_price, marker='o', linestyle='-', color='r', label='Average Price')
        ax1.plot(dates, lowest_price, marker='o', linestyle='-', color='c', label='Lowest Price')
        
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Price')
        ax1.grid(True)
        ax1.legend(loc='upper left')
        if len(dates) > 10:
            ax1.set_xticks(dates[::len(dates)//10])
        else:
            ax1.set_xticks(dates)
        ax1.tick_params(axis='y')

        # Create a second y-axis for avg_avail bar graph
        ax2 = ax1.twinx() 
        ax2.bar(dates, avg_avail, color='g', alpha=0.6, label='Average Availability')
        ax2.set_ylabel('Average Availability', color='g')
        ax2.tick_params(axis='y', labelcolor='g')
        ax2.legend(loc='upper right')

        fig.autofmt_xdate()
        fig.suptitle(data['item_name'])

        # Clear previous canvas before adding a new one
        if hasattr(self, 'canvas'):
            self.canvas.get_tk_widget().pack_forget()
            del self.canvas  # Ensure it's removed

        self.canvas = FigureCanvasTkAgg(fig, self)
        self.canvas.draw()
        canvas_widget = self.canvas.get_tk_widget()
        canvas_widget.pack(fill=tk.BOTH, expand=True)




    def plot_prices_for_item(self, item_id):
        self.data_store.item_id = item_id 
        self.plot_prices()