import sys

try:
    from django.db import models
except Exception:
    print('Exception: Django Not Found, please install it with "pip install django".')
    sys.exit()
"""
class BackUpHandler(models.Model):
    what = models.ForeignKey("BackupObject", on_delete=models.CASCADE)
    where = models.ForeignKey("BackupObject", on_delete=models.CASCADE, related_name="where")
    what = models.CharField(max_length=50)
    where = models.CharField(max_length=50)
    when = models.CharField(max_length=50)

    def __str__(self):
        return f"what: {self.what}, where: {self.where}, when: {self.when}"
"""

class Backup(models.Model):
    path = models.CharField(max_length=250)
    gid = models.CharField(max_length=250)
    ver = models.IntegerField()

    def __str__(self):
        return f"path: {self.path}, gid: {self.gid}, ver: {self.ver}"

"""
# BackupObjectFamilies
LOCAL_DIR = 0
GDRIVE_ID = 1

class BackupObject(models.Model):
    family = models.IntegerField()
    content = models.CharField(max_length=4096)

    def __str__(self):
        return f"family: {self.family}, content: {self.content}"
"""