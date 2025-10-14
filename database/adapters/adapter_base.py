from abc import ABC, abstractmethod

class AdapterBase(ABC):
    @abstractmethod
    def insert(self, table, data):
        pass

    @abstractmethod
    def get_all(self, table):
        pass

    @abstractmethod
    def get_by_id(self, table, id):
        pass

    @abstractmethod
    def update(self, table, id, data):
        pass

    @abstractmethod
    def delete(self, table, id):
        pass