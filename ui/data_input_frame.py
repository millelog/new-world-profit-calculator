import tkinter as tk
from tkinter import ttk  # Themed Tkinter
from data_input.json_parse import process_json_data
from data_input.data_downloader import download_data, save_data_to_file, load_data_from_file
from database.models import Server

class DataInputFrame(tk.Frame):
    def __init__(self, parent, session):
        super().__init__(parent)
        self.session = session

        # Create a label for server selection
        self.server_label = tk.Label(self, text="Select Server:")
        self.server_label.grid(row=0, column=0, padx=5, pady=5)

        # Create a dropdown menu for server selection
        self.server_var = tk.StringVar()
        self.server_dropdown = ttk.Combobox(self, textvariable=self.server_var)
        self.server_dropdown.grid(row=0, column=1, padx=5, pady=5)
        self.populate_server_dropdown()

        # Create a button for updating prices
        self.update_button = tk.Button(self, text="Update Prices", command=self.update_prices)
        self.update_button.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

    def populate_server_dropdown(self):
        # Query the database for server names
        servers = self.session.query(Server.server_name).all()
        # Flatten the list of server names and set it as the values for the dropdown menu
        self.server_dropdown['values'] = [server[0] for server in servers]

    def update_prices(self):
        # Get the selected server ID from the dropdown menu
        selected_server_name = self.server_var.get()
        server = self.session.query(Server).filter_by(server_name=selected_server_name).first()
        if server:
            server_id = server.server_id
            # Download the data
            data = download_data(server_id)
            # Save the data to download.json
            save_data_to_file(data)
            # Now process the downloaded data
            process_json_data(self.session, data, server_id)
        else:
            print(f"No server found with name {selected_server_name}")

    def on_server_select(self, event):
        # This method can be used to trigger actions when a server is selected from the dropdown
        selected_server_name = self.server_var.get()
        print(f"Server selected: {selected_server_name}")
