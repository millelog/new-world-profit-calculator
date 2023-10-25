import tkinter as tk
from tkinter import ttk
from database.operations.item_operations import get_item_by_id

class ShoppingListFrame(ttk.Frame):
    def __init__(self, parent, data_store, session):
        super().__init__(parent)
        self.data_store = data_store
        self.session = session
        
        # Shopping list dictionary
        self.shopping_list = {}
        
        # Label and Entry for Quantity
        self.quantity_label = ttk.Label(self, text="Quantity:")
        self.quantity_label.grid(row=0, column=0, padx=(2, 0), pady=5)
        
        # Define StringVar for quantity_entry
        self.quantity_var = tk.StringVar()
        
        # Bind StringVar to quantity_entry
        self.quantity_entry = ttk.Entry(self, width=10, textvariable=self.quantity_var)
        self.quantity_entry.grid(row=0, column=1, padx=(0, 5), pady=5)


        # Cost Preview Label
        self.cost_preview_label = ttk.Label(self, text="Cost Preview:")
        self.cost_preview_label.grid(row=0, column=4, padx=(5, 2), pady=5)
        
        self.cost_preview_value = ttk.Label(self, text="0.0")
        self.cost_preview_value.grid(row=0, column=5, padx=(2, 5), pady=5)
        
        # Update the cost preview whenever the quantity changes
        self.quantity_entry.bind('<KeyRelease>', self.update_cost_preview)

        # Total cost label
        self.total_cost_label = ttk.Label(self, text="Total Cost: ")
        self.total_cost_label.grid(row=2, column=3, padx=2, pady=5)
        
        self.total_cost_value = ttk.Label(self, text="0.0")
        self.total_cost_value.grid(row=2, column=4, padx=2, pady=5)

        # Buy Reagents button
        self.auto_fill_button = ttk.Button(self, text="Autofill", command=self.auto_populate_quantity_entry)
        self.auto_fill_button.grid(row=0, column=2, padx=5, pady=5)
        
        # Buy Reagents button
        self.buy_button = ttk.Button(self, text="Buy Reagents", command=self.add_to_shopping_list)
        self.buy_button.grid(row=0, column=3, padx=5, pady=5)
        
        # Create Treeview for displaying the shopping list
        self.tree = ttk.Treeview(self, columns=("Item ID", "Item Name", "Market Price", "Quantity", "Cost"), show="headings", height=25)

        self.tree.column("Item ID", width=100)
        self.tree.column("Item Name", width=200)
        self.tree.column("Market Price", width=100)
        self.tree.column("Quantity", width=100)


        self.tree.heading("Item ID", text="Item ID")
        self.tree.heading("Item Name", text="Item Name")
        self.tree.heading("Market Price", text="Market Price")
        self.tree.heading("Quantity", text="Quantity")
        self.tree.grid(row=1, column=0, columnspan=3, padx=2, pady=5, sticky='nsew')

                # Update the Treeview columns
        self.tree.heading("Cost", text="Cost")
        self.tree.column("Cost", width=100)

        # Create Treeview for displaying crafting recipes
        self.crafting_tree_label = ttk.Label(self, text="Crafting Recipes")
        self.crafting_tree_label.grid(row=3, column=0, columnspan=3, padx=2, pady=5, sticky='w')
        
        self.crafting_tree = ttk.Treeview(self, columns=("Item ID", "Item Name", "Quantity to Craft"), show="headings", height=15)

        self.crafting_tree.column("Item ID", width=200)
        self.crafting_tree.column("Item Name", width=200)
        self.crafting_tree.column("Quantity to Craft", width=200)

        self.crafting_tree.heading("Item ID", text="Item ID")
        self.crafting_tree.heading("Item Name", text="Item Name")
        self.crafting_tree.heading("Quantity to Craft", text="Quantity to Craft")
        self.crafting_tree.grid(row=4, column=0, columnspan=3, padx=2, pady=5, sticky='nsew')
        
        # Clear Shopping List Button
        self.clear_button = ttk.Button(self, text="Clear Shopping List", command=self.clear_shopping_list)
        self.clear_button.grid(row=2, column=0, columnspan=3, padx=2, pady=5)


    def auto_populate_quantity_entry(self):
        quantity = self.data_store.selected_item_info.get("avg_available")
        self.quantity_var.set(int(quantity))
        self.update_cost_preview()
        

    def _populate_crafting_tree(self, node, multiplier=1):
        for item_id, info in node.items():
            # Check if the item is already in the tree
            existing_item = [child for child in self.crafting_tree.get_children() if self.crafting_tree.item(child, "values")[0] == item_id]
            
            if info.get('source') == 'crafted':
                item_name = get_item_by_id(self.session, item_id).item_name
                quantity_to_craft = info.get('quantity', 0) * multiplier
                
                if existing_item:
                    # If the item already exists, update its quantity
                    existing_values = self.crafting_tree.item(existing_item[0], "values")
                    updated_quantity = int(existing_values[2]) + quantity_to_craft
                    self.crafting_tree.item(existing_item[0], values=(item_id, item_name, updated_quantity))
                else:
                    # If the item doesn't exist, insert it into the tree
                    values = (item_id, item_name, quantity_to_craft)
                    self.crafting_tree.insert("", "end", values=values)

            # For nested crafting, multiply the current quantity with the parent multiplier
            nested_multiplier = info.get('quantity', 1) * multiplier
            self._populate_crafting_tree(info.get('children', {}), nested_multiplier)


    def add_to_shopping_list(self):
        item_info = self.data_store.selected_item_info
        if not item_info:
            return

        # Add the selected item itself to the crafting tree
        selected_item_id = item_info.get("Item ID")
        selected_item_name = get_item_by_id(self.session, selected_item_id).item_name
        try:
            selected_item_quantity = int(self.quantity_entry.get())
        except ValueError:
            selected_item_quantity = 1

        # Check if the selected item is already in the tree
        existing_selected_item = [child for child in self.crafting_tree.get_children() if self.crafting_tree.item(child, "values")[0] == selected_item_id]
        if existing_selected_item:
            # Update its quantity if it exists
            existing_values = self.crafting_tree.item(existing_selected_item[0], "values")
            updated_quantity = int(existing_values[2]) + selected_item_quantity
            self.crafting_tree.item(existing_selected_item[0], values=(selected_item_id, selected_item_name, updated_quantity))
        else:
            # Insert the selected item into the tree if it doesn't exist
            self.crafting_tree.insert("", "end", values=(selected_item_id, selected_item_name, selected_item_quantity))

        # Continue with the rest of the crafting tree
        crafting_tree = item_info.get("Crafting Tree", {})
        self._parse_crafting_tree(crafting_tree, selected_item_quantity)
        self._populate_tree()
        self._populate_crafting_tree(crafting_tree, selected_item_quantity)


    def _parse_crafting_tree(self, node, selected_item_quantity, multiplier=1):
        for item_id, info in node.items():
            if info.get('source') == 'market':
                item_name = get_item_by_id(self.session, item_id).item_name
                market_price = info.get('cost', 'N/A')
                
                # Multiply the recipe quantity with the selected_item_quantity and the multiplier
                quantity = info.get('quantity', 0) * multiplier * selected_item_quantity

                # Check if the item is already in the shopping list
                if item_id in self.shopping_list:
                    self.shopping_list[item_id]['Quantity'] += quantity
                else:
                    self.shopping_list[item_id] = {
                        "Item Name": item_name,
                        "Market Price": market_price,
                        "Quantity": quantity
                    }

            # For nested crafting, multiply the current quantity with the parent multiplier
            nested_multiplier = info.get('quantity', 1) * multiplier
            self._parse_crafting_tree(info.get('children', {}), selected_item_quantity, nested_multiplier)


    def clear_shopping_list(self):
        # Clear shopping list dictionary
        self.shopping_list = {}

        # Clear treeview items in both the shopping list and the crafting tree
        self.tree.delete(*self.tree.get_children())  
        self.crafting_tree.delete(*self.crafting_tree.get_children())  
        
        # Reset the total cost value
        self.total_cost_value["text"] = "0.0"


    def update_cost_preview(self, event=None):  # added default value for event
        try:
            # Convert the string value from the StringVar back to an integer
            quantity = int(self.quantity_var.get())
            craft_cost = self.data_store.selected_item_info.get("Crafting Cost", 0)
            total_cost = craft_cost * quantity
            self.cost_preview_value["text"] = "{:.2f}".format(total_cost)
        except ValueError:
            self.cost_preview_value["text"] = "Invalid Quantity"
        

    def _populate_tree(self):
        self.tree.delete(*self.tree.get_children())  # Clear existing tree items
        total_cost = 0
        for item_id, info in self.shopping_list.items():
            cost = info["Market Price"] * info["Quantity"]
            values = (item_id, info["Item Name"], info["Market Price"], info["Quantity"], "{:.2f}".format(cost))
            total_cost += cost
            self.tree.insert("", "end", values=values)
        self.total_cost_value["text"] = "{:.2f}".format(total_cost)
        

