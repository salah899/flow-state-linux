class FolderService:
    def __init__(self, db):
        self.db = db

    def list(self):
        return self.db.get_folders()

    def add(self, name):
        return self.db.add_folder(name)

    def delete(self, folder_id):
        self.db.delete_folder(folder_id)

    def name(self, folder_id, default="كل المهام"):
        return self.db.get_folder_name(folder_id) or default

    def default_id(self):
        folders = self.list()
        return folders[0]["id"] if folders else None
