from django.contrib.auth.models import Group

class GroupService:
    @staticmethod
    def create_group(name):
        group, created = Group.objects.get_or_create(name=name)
        return group
