from abc import ABC, abstractmethod

class Sequence(ABC):

    @abstractmethod
    def add_sequence(self, step_number, animation_sequence):
        pass

    @abstractmethod
    def get_latest_sequence(self):
        pass

    @abstractmethod
    def get_all_sequences(self):
        pass

    @abstractmethod
    def load_sequences(self, sequences):
        pass

    # Removed methods
    # def get_sequence(self):
    #     pass

    # def list_sequences(self):
    #     pass

    # def play_sequence(self):
    #     pass

    # def remove_sequence(self):
    #     pass

    # def stop_sequence(self):
    #     pass