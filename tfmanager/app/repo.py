from app.models import Folder, File, Content
from django.db import transaction
from django.contrib.auth.models import User

# TODO: Integrity check -- Not allowed to use a different user's folder as the parent to the current user's folder
# TODO: Use the User model's related_name to get the data instead of digging it up with a filter
# TODO: Don't allow same folder to be created twice
# TODO: Folder deleted -> All files deleted as well
# TODO: Test the get_folder method


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
    def get_folder(user_id, folder_id):
        folder = Folder.objects.filter(owner_id=user_id, id=folder_id).first()
        if not folder:
            return
        return FolderRepo.to_json(folder)

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
        existing_folder = Folder.objects.filter(
            name=name, owner=user, parent=parent).first()
        if existing_folder:
            return None
        new_folder = Folder(name=name, owner=user, parent=parent)
        new_folder.save()
        return FolderRepo.to_json(new_folder)

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
        res['id'] = file.id
        res['name'] = file.name
        res['deleted'] = file.deleted
        res['creation_time'] = file.creation_time
        res['belong_id'] = file.belong.id
        res['owner'] = file.belong.owner.id  # TODO: Add test for this
        res['content_text'] = content.text
        res['version'] = content.version
        return res

    @staticmethod
    def create_file(user_id, folder_id, name, text):

        # Make sure user and folder exist
        user = User.objects.filter(id=user_id).first()
        folder = Folder.objects.filter(id=folder_id).first()
        if not user or not folder:
            return None

        # Ensure that the input folder is owned by the input user
        if folder.owner.id != user.id:
            return None

        # Validate that a file with this name does not already exist
        owned_file_names = [folder.name for folder in folder.owned_files.all()]
        if name in owned_file_names:
            return None

        # Create the new file
        with transaction.atomic():
            new_file = File(name=name, belong=folder)
            new_file.save()
            new_content = Content(text=text, version=0, file=new_file)
            new_content.save()

        # Serialize new file and content to JSON
        return FileRepo.to_json(new_file, new_content)

    @staticmethod
    def get_file(user_id, file_id):
        user = User.objects.filter(id=user_id).first()
        file = File.objects.filter(id=file_id).first()

        # Ensure that input user and file exist
        if not user or not file:
            return None

        # Ensure that input file is owned by the input user
        if file.belong.owner.id != user.id:
            return None

        # Get the latest version of the file content
        content = file.file_content.latest('version')
        if not content:  # Should never happen...
            return None

        return FileRepo.to_json(file, content)

    @staticmethod
    def publish_new_version(user_id, file_id, text):
        fo = File.objects.filter(id=file_id, belong__owner__id=user_id).first()
        if not fo:
            return None

        # Grab the latest version of the file content currently stored in database
        co = fo.file_content.latest('version')
        if not co:  # Should never happen...
            return None

        # Create a new content object with the input text and file as foreign key
        new_co = Content(text=text, version=co.version + 1, file=fo)

        # Save the new version of the file content to the datbase
        new_co.save()

        # Return the updated file
        return FileRepo.to_json(fo, new_co)

    @staticmethod
    def delete_file(user_id, file_id):
        user = User.objects.filter(id=user_id).first()
        file = File.objects.filter(id=file_id).first()

        # Ensure that input user and file exist
        if not user or not file:
            return False

        # Ensure that input file is owned by the input user
        if file.belong.owner.id != user.id:
            return False

        file.deleted = True
        file.save()
        return True

    @staticmethod
    def get_files_within_folder(user_id, folder_id):
        # Get the folder and check it
        # TODO: Should I use the Folder model directly?
        folder = FolderRepo.get_folder(user_id, folder_id)
        if not folder:
            return None

        # Get the files and return the JSON format for each one
        file_ids = list(
            map(lambda f: f['id'], File.objects.filter(belong=folder_id).values('id')))
        return list(map(lambda f: FileRepo.get_file(user_id, f), file_ids))

    @staticmethod
    def get_file_by_version(user_id, file_id, version_num):
        fo = File.objects.filter(id=file_id, belong__owner__id=user_id).first()
        if not fo:
            return None

        co = Content.objects.filter(file=file_id, version=version_num).first()
        if not co:
            return None

        return FileRepo.to_json(fo, co)


class FileHistoryRepo:
    
    @staticmethod
    def to_json(fo, cos):
        res = {}
        res['id'] = fo.id
        res['name'] = fo.name
        res['histories'] = [ {k: v for k, v in zip(('creation_time', 'version'),(co.creation_time.strftime("%I:%M%p on %B %d, %Y"), co.version))} for co in cos]
        return res
    
    @staticmethod
    def get_history(user_id, file_id):
        fo = File.objects.filter(id=file_id, belong__owner__id=user_id).first()

        # Ensure that input user and file exist
        if not fo:
            return None

        # Get the latest version of the file content
        content = list(Content.objects.filter(file_id=fo.id).order_by('-version'))
        if not content:  # Should never happen...
            return None

        return FileHistoryRepo.to_json(fo, content)
