import tkinter as tk
from ui.data_input_frame import DataInputFrame
from ui.analysis_frame import AnalysisFrame
from ui.recommendations_frame import RecommendationsFrame
from ui.data_store import DataStore

class MainWindow(tk.Tk):
    def __init__(self, session):
        super().__init__()
        self.data_store = DataStore()
        self.title("New World Profit Calculator")
        self.session = session

        self.data_input_frame = DataInputFrame(self, session, self.data_store)
        self.data_input_frame.pack(fill=tk.BOTH, expand=True)

        self.analysis_frame = AnalysisFrame(self, session, self.data_store)
        self.analysis_frame.pack(fill=tk.BOTH, expand=True)

        self.recommendations_frame = RecommendationsFrame(self, session, self.data_store)
        self.recommendations_frame.pack(fill=tk.BOTH, expand=True)
