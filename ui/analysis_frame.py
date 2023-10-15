import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from analysis.crafting_profit import calculate_profitability, evaluate_all_recipes

class AnalysisFrame(tk.Frame):
    def __init__(self, parent, session):
        super().__init__(parent)
        self.session = session
        
        # Entry for item_id input
        self.item_id_entry = tk.Entry(self)
        self.item_id_entry.grid(row=0, column=1)
        self.item_id_label = tk.Label(self, text="Item ID:")
        self.item_id_label.grid(row=0, column=0)
        
        # Button to calculate profitability for a specific item
        self.calculate_button = tk.Button(self, text="Calculate Profitability", command=self.calculate_profitability)
        self.calculate_button.grid(row=1, columnspan=2)
        
        # Button to evaluate all recipes and find the most profitable
        self.evaluate_button = tk.Button(self, text="Evaluate All Recipes", command=self.evaluate_all_recipes)
        self.evaluate_button.grid(row=2, columnspan=2)
        
        # Text widget to display results
        self.result_text = tk.Text(self, width=40, height=10)
        self.result_text.grid(row=3, columnspan=2)

         # Treeview to display crafting tree
        self.tree = ttk.Treeview(self)
        self.tree.grid(row=4, columnspan=2)
    
    def calculate_profitability(self):
        item_id = self.item_id_entry.get()
        if not item_id:
            messagebox.showerror("Error", "Please enter an Item ID")
            return
        profit_margin, recommended_recipe, crafting_tree = calculate_profitability(self.session, item_id)
        result_text = f"Profit Margin: {profit_margin}\nRecommended Recipe ID: {recommended_recipe.recipe_id if recommended_recipe else 'N/A'}\nCrafting Tree: {crafting_tree}"
        self.result_text.delete('1.0', tk.END)
        self.result_text.insert(tk.END, result_text)
        self.populate_tree(crafting_tree)
    
    def evaluate_all_recipes(self):
        profitability_info = evaluate_all_recipes(self.session)
        top_5_profitable_items = sorted(profitability_info.items(), key=lambda x: x[1]["Profit Margin"], reverse=True)[:5]
        result_text = "Top 5 Profitable Items:\n"
        for item_id, info in top_5_profitable_items:
            result_text += f"Item ID: {item_id}, Profit Margin: {info['Profit Margin']}, Recommended Recipe ID: {info['Recommended Recipe ID']}\n"
        self.result_text.delete('1.0', tk.END)
        self.result_text.insert(tk.END, result_text)
    
    def populate_tree(self, crafting_tree):
        for item_id, node in crafting_tree.items():
            parent_id = self.tree.insert("", "end", text=item_id)
            self._add_tree_children(parent_id, node)
    
    def _add_tree_children(self, parent_id, node):
        for child_id, child_node in node.get("children", {}).items():
            child_parent_id = self.tree.insert(parent_id, "end", text=child_id)
            self._add_tree_children(child_parent_id, child_node)

# Usage:
if __name__ == '__main__':
    root = tk.Tk()
    session = None  # Assume you have a way to get your SQLAlchemy session
    analysis_frame = AnalysisFrame(root, session)
    analysis_frame.pack()
    root.mainloop()
