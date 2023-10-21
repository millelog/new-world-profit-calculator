class DataStore:
    def __init__(self):
        self._observers = []
        self.server_id = None
        self.player_id = None
        self.item_id = None
        self._selected_item_info = {}

    def add_observer(self, observer_callback):
        self._observers.append(observer_callback)

    def notify_observers(self):
        for callback in self._observers:
            callback()

    @property
    def selected_item_info(self):
        return self._selected_item_info

    @selected_item_info.setter
    def selected_item_info(self, value):
        self._selected_item_info = value
        self.notify_observers()
