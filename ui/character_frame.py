import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from database.models import Server
from database.operations.player_operations import (delete_player, get_player_by_id, get_player_skills, update_player, get_player_by_name, add_player)

class CharacterFrame(tk.Toplevel):
    def __init__(self, parent, session, data_store, main_frame):
        super().__init__(parent)
        self.session = session
        self.data_store = data_store
        
        self.title("Character Management")
        self.geometry('300x500')
        
        # Store entries for trade skills and their associated StringVars
        self.skill_vars = {}
        self.skill_entries = {}

        player_data = get_player_by_id(self.session, self.data_store.player_id)
        self.character_name = player_data['player_name'] if player_data else 'No Character Selected'


        # Label for "Selected Character:"
        ttk.Label(self, text="Selected Character:").grid(row=0, column=0, sticky='w', padx=10, pady=5)

        # Label for the actual character's name
        self.character_name_label = ttk.Label(self, text=self.character_name)
        self.character_name_label.grid(row=0, column=1, sticky='w', padx=10, pady=5)

        
        # Add a row for each skill in the given list
        self.skills_data = get_player_skills(self.session, self.data_store.player_id)
        for idx, skill_data in enumerate(self.skills_data):
            skill_name = skill_data["skill_name"]
            ttk.Label(self, text=skill_name).grid(row=idx+1, column=0, sticky='w', padx=10, pady=5)
            skill_var = tk.StringVar()
            skill_var.trace_add('write', lambda *args, sn=skill_name: self.save_skill_changes(sn))
            entry = ttk.Entry(self, textvariable=skill_var)
            entry.grid(row=idx+1, column=1, padx=10, pady=5)
            self.skill_entries[skill_name] = {"entry": entry, "var": skill_var}


        self.add_character_button = ttk.Button(self, text="Add Character", command=self.add_character)
        self.edit_character_button = ttk.Button(self, text="Edit Character", command=self.edit_character)        
        self.delete_character_button = ttk.Button(self, text="Delete Character", command=self.delete_character)
        self.close_button = ttk.Button(self, text="Close", command=self.destroy)

        self.add_character_button.grid(row=len(self.skills_data)+2, column=0, padx=10, pady=5)
        self.edit_character_button.grid(row=len(self.skills_data)+2, column=1, padx=10, pady=5)
        self.delete_character_button.grid(row=len(self.skills_data)+3, column=0, padx=10, pady=5)
        self.close_button.grid(row=len(self.skills_data)+3, column=1, padx=10, pady=5)

        
        self.display_character_info()

        if main_frame:
            self.main_frame = main_frame
            self.protocol("WM_DELETE_WINDOW", self.on_close)

    def delete_character(self):
        player_data = get_player_by_id(self.session, self.data_store.player_id)
        # Ask for confirmation before deletion
        confirmation = messagebox.askyesno("Confirmation", f"Are you sure you want to delete {player_data['player_name']}?")
        if confirmation:
            delete_player(self.session, self.data_store.player_id)  # Assuming you've imported the delete_player function
            messagebox.showinfo("Success", f"Character {player_data['player_name']} deleted!")
            self.on_close()


    def display_character_info(self):
        if self.skills_data:
            for skill in self.skills_data:
                skill_name = skill["skill_name"]
                skill_level = skill["skill_level"]
                entry_dict = self.skill_entries.get(skill_name)
                if entry_dict:
                    entry_widget = entry_dict["entry"]
                    entry_widget.delete(0, tk.END)
                    entry_widget.insert(0, skill_level)


    def save_skill_changes(self, skill_name):
        # Whenever an Entry's value is updated, this function will be triggered
        skill_value = self.skill_entries[skill_name]["var"].get()
        try:
            skill_level = int(skill_value)
            
            # Fetch current skills
            current_skills = get_player_skills(self.session, self.data_store.player_id)
            
            # Check if the skill exists in the current list and update its value
            for skill in current_skills:
                if skill["skill_name"] == skill_name:
                    skill["skill_level"] = skill_level
                    break
            else:  # This else block runs if the for loop didn't encounter a break, meaning the skill wasn't found
                current_skills.append({"skill_name": skill_name, "skill_level": skill_level})
            
            # Save the updated skills
            player_data = {"skills": current_skills}
            update_player(self.session, self.data_store.player_id, player_data)
            print(f"Updated {skill_name} to {skill_level}")
        except ValueError:
            # Handle cases where the input is not a valid integer
            print(f"Invalid value for {skill_name}: {skill_value}")



    def add_character(self):
        # Collect the data
        skills = [{"skill_name": skill_name, "skill_level": int(entry_dict["entry"].get() or 0)} 
                for skill_name, entry_dict in self.skill_entries.items()]
        player_name = simpledialog.askstring("Input", "What is the character's name?")
        if player_name:
            server = self.session.query(Server).filter(Server.server_id == self.data_store.server_id).first()
            if not server:
                raise ValueError(f"Server with ID '{self.data_store.server_id}' not found!")
            add_player(self.session, {"player_name": player_name, "server_name": server.server_name, "skills": skills})
            messagebox.showinfo("Success", f"Character {player_name} added!")
        self.display_character_info()

    def edit_character(self):
        skills = [{"skill_name": skill_name, "skill_level": int(entry_dict["entry"].get() or 0)} 
              for skill_name, entry_dict in self.skill_entries.items()]
        player_data = get_player_by_id(self.session, self.data_store.player_id)
        new_name = simpledialog.askstring("Input", "Edit the character's name:", initialvalue=player_data["player_name"])
        if new_name:
            update_player(self.session, self.data_store.player_id, {"player_name": new_name, "skills": skills})
            messagebox.showinfo("Success", f"Character name updated to {new_name}!")
        self.display_character_info()

    def on_close(self):
        # Call the main frame's method to update the character dropdown
        self.main_frame.populate_character_dropdown()
        # Close the window
        self.destroy()