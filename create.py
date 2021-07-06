import sys, os, django
sys.dont_write_bytecode = True 
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings") 
django.setup()

from db import models

def dall():
    for bak in models.Backup.objects.all():
        bak.delete()

if __name__ == "__main__":
    from pydrive.auth import GoogleAuth
    from pydrive.drive import GoogleDrive
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    gdrive = GoogleDrive(gauth)

    initbak = input("Enter a google drive id: ")
    data = input("Enter the locations to backup: ")
    data = data.split("|")
    nb = 0

    while True:
        lastnb = gdrive.ListFile({'q': f"'{initbak}' in parents and trashed=false and title='{nb}'"}).GetList()
        if not lastnb:
            break
        nb += 1

    for path in data:
        gfolder = gdrive.CreateFile({'title': str(nb), "parents":  [{"id": initbak}], "mimeType": "application/vnd.google-apps.folder"})
        gfolder.Upload()

        namef = gdrive.CreateFile({'title': "name", "parents":  [{"id": gfolder["id"]}]})
        namef.SetContentString(path.split("\\")[-1])
        namef.Upload()

        backup = models.Backup(path=path, gid=gfolder["id"], ver=0)
        backup.save()

        nb += 1

    for bak in models.Backup.objects.all():
        print(bak)