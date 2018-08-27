from app.models import Folder
from django.contrib.auth.models import User

# TODO: Integrity check -- Not allowed to use a different user's folder as the parent to the current user's folder


class FolderRepo:

    @staticmethod
    def to_json(folder_obj):
        res = {}
        res['id'] = folder_obj.id
        res['name'] = folder_obj.name
        res['deleted'] = folder_obj.deleted
        res['owner_id'] = folder_obj.owner.id
        res['creation_time'] = folder_obj.creation_time
        res['parent_id'] = folder_obj.parent.id if folder_obj.parent else None
        return res

    @staticmethod
    def get_all_folder_for_user(user_id):
        folders = Folder.objects.filter(owner_id=user_id)
        return [FolderRepo.to_json(folder) for folder in folders]

    @staticmethod
    def get_all_folder_for_user_with_parent(user_id, parent_id):
        pass

    @staticmethod
    def create_folder(user_id, name, parent_id=None):
        user = User.objects.filter(id=user_id).first()
        parent = None
        if not user:
            return None
        if parent_id:
            parent = Folder.objects.filter(id=parent_id).first()
            if not parent:
                return None
        folder = Folder(name=name, owner=user, parent=parent)
        folder.save()
        return FolderRepo.to_json(folder)

    @staticmethod
    def delete_folder(user_id, folder_id):
        folder = Folder.objects.filter(id=folder_id, owner_id=user_id).first()
        if not folder:
            return False
        folder.delete()
        return True
