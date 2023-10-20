import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from analysis.crafting_profit import CraftingProfitAnalyzer
from database.operations.item_operations import get_item_by_id
from ui.graph_frame import ItemGraphFrame

class AnalysisFrame(tk.Frame):
    def __init__(self, parent, session, data_store):
        super().__init__(parent)
        self.session = session
        self.data_store = data_store
        self.crafting_profit_analyzer = CraftingProfitAnalyzer(self.session, self.data_store.server_id, self.data_store.player_id)
        
        self.progress = ttk.Progressbar(self, orient="horizontal", length=200, mode="determinate")
        self.progress.grid(row=0, column=1, pady=(5,5))

        # Button to evaluate all recipes and find the most profitable
        self.evaluate_button = tk.Button(self, text="Evaluate All Recipes", command=self.evaluate_all_recipes_ui)
        self.evaluate_button.grid(row=0, column=0)

        
        # Text widget to display results
        self.result_text = tk.Text(self, width=40, height=10)
        self.result_text.grid(row=1, columnspan=2)

         # Create Panedwindow to hold the listbox and treeview
        self.panedwindow = ttk.Panedwindow(self, orient=tk.HORIZONTAL)
        self.panedwindow.grid(row=2, column=0, columnspan=2, sticky='nsew')
        
         # Create the ItemPriceGraphFrame and place it in the AnalysisFrame
        self.price_graph_frame = ItemGraphFrame(self, self.session, self.data_store)
        self.price_graph_frame.grid(row=3, column=0, columnspan=2, sticky='nsew')

        # Frame for Listbox
        self.listbox_frame = tk.Frame(self.panedwindow)
        self.panedwindow.add(self.listbox_frame, weight=1)
        
        # Listbox to display item IDs of the top 50 profitable items
        self.listbox = tk.Listbox(self.listbox_frame)
        self.listbox.pack(fill=tk.BOTH, expand=True)
        
        # Frame for Treeview
        self.tree_frame = tk.Frame(self.panedwindow)
        self.panedwindow.add(self.tree_frame, weight=3)
        
        # Update Treeview to include new columns
        self.tree = ttk.Treeview(self.tree_frame, columns=("Item ID", "Item Name", "Quantity", "Cost", "Source"), show="headings")
        self.tree.heading("Item ID", text="Item ID")
        self.tree.heading("Item Name", text="Item Name")
        self.tree.heading("Quantity", text="Quantity")
        self.tree.heading("Cost", text="Cost")
        self.tree.heading("Source", text="Source")
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind listbox selection event to update the treeview
        self.listbox.bind('<<ListboxSelect>>', self.on_listbox_select)
    
    def calculate_profitability(self):
        item_id = self.item_id_entry.get()
        if not item_id:
            messagebox.showerror("Error", "Please enter an Item ID")
            return
        info = self.profitability_info.get(item_id, {})
        result_text = f"Name: {get_item_by_id(self.session, item_id).item_name}\nProfit: {info.get('Profit', 'N/A')}\nCrafting Tree: {info.get('Crafting Tree', {})}"
        self.result_text.delete('1.0', tk.END)
        self.result_text.insert(tk.END, result_text)
        self.populate_tree(info.get("Crafting Tree", {}))
    
    def evaluate_all_recipes_ui(self):
        profitability_info_list = self.crafting_profit_analyzer.evaluate_all_recipes(callback=self.update_progress)
        # Convert list of tuples to a dictionary
        self.profitability_info = {item_id: info for item_id, info in profitability_info_list}
        self.listbox.delete(0, tk.END)  # Clear existing listbox items
        for item_id in self.profitability_info:
            self.listbox.insert(tk.END, item_id)

    def update_progress(self, current, total):
        progress = (current / total) * 100
        self.progress["value"] = progress
        self.update_idletasks()


    def on_listbox_select(self, event):
        selected_item_index = self.listbox.curselection()
        
        if not selected_item_index:
            return  # No item selected
        item_id = self.listbox.get(selected_item_index[0])
        # Update the graph based on the selected item
        self.price_graph_frame.plot_prices_for_item(item_id)
        self.display_item_info(item_id)

    def display_item_info(self, item_id):
        # Lookup the item info from the stored profitability_info
        info = self.profitability_info.get(item_id, {})
        item_name = get_item_by_id(self.session, item_id).item_name
        profit = "{:.2f}".format(info.get("Profit", "N/A"))
        profit_margin = "{:.2f}".format(info.get("Profit Margin", 0.00))
        score = "{:.2f}".format(info.get("Score", 0.00))
        availability = info.get("Availability", "N/A")
        recommended_recipe_id = info.get("Recommended Recipe ID", "N/A")
        crafting_cost = "{:.2f}".format(info.get("Crafting Cost", "N/A"))
        market_price = "{:.2f}".format(info.get("Market Price", "N/A"))
        crafting_tree = info.get("Crafting Tree", {})

        result_text = (f"Item Name: {item_name}\n"
                          f"Market Price: {market_price}\n"
                       f"Crafting Cost: {crafting_cost}\n"                       
                       f"Profit: {profit}\n"
                       f"Profit Margin: {profit_margin}%\n"
                       f"Score: {score}\n"
                       f"Availability: {availability}\n"
                       f"Recommended Recipe ID: {recommended_recipe_id}\n")

        self.result_text.delete('1.0', tk.END)
        self.result_text.insert(tk.END, result_text)
        self.populate_tree(crafting_tree, item_id)


    def populate_tree(self, crafting_tree, root_item_id):
        self.tree.delete(*self.tree.get_children())  # Clear existing tree items
        self._add_tree_children("", crafting_tree)  # Start with the root node of the crafting_tree

    def _add_tree_children(self, parent_id, node):
        for item_id, info in node.items():
            # Now values only include item_id, cost, and source
            values = (item_id, get_item_by_id(self.session, item_id).item_name, info.get('quantity', 'N/A'), info.get('cost', 'N/A'), info.get('source', 'N/A'))
            child_id = self.tree.insert(parent_id, "end", text=item_id, values=values)
            self._add_tree_children(child_id, info.get('children', {}))




# Usage:
if __name__ == '__main__':
    root = tk.Tk()
    session = None  # Assume you have a way to get your SQLAlchemy session
    analysis_frame = AnalysisFrame(root, session)
    analysis_frame.pack()
    root.mainloop()
