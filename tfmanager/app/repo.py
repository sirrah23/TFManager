from app.models import Folder, File, Content
from django.db import transaction
from django.contrib.auth.models import User

# TODO: Integrity check -- Not allowed to use a different user's folder as the parent to the current user's folder
# TODO: Use the User model's related_name to get the data instead of digging it up with a filter


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
        folders = Folder.objects.filter(owner_id=user_id, parent_id=parent_id)
        return [FolderRepo.to_json(folder) for folder in folders]

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
        folder.deleted = True
        folder.save()
        return True


class FileRepo:

    @staticmethod
    def to_json(file, content):
        res = {}
        res['name'] = file.name
        res['deleted'] = file.deleted
        res['creation_time'] = file.creation_time
        res['belong_id'] = file.belong.id
        res['content_text'] = content.text
        res['version'] = content.version
        return res

    @staticmethod
    def create_file(user_id, folder_id, name, text):
        user = User.objects.filter(id=user_id).first()
        folder = Folder.objects.filter(id=folder_id).first()
        if not user or not folder:
            return None
        with transaction.atomic():
            new_file = File(name=name, belong=folder)
            new_file.save()
            new_content = Content(text=text, version=0, file=new_file)
            new_content.save()
        return FileRepo.to_json(new_file, new_content)

    @staticmethod
    def get_file(user_id, file_id):
        pass

    @staticmethod
    def delete_file(user_id, file_id):
        pass
