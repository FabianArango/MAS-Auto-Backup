import os, json
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
gauth = GoogleAuth()
gauth.LocalWebserverAuth()
gdrive = GoogleDrive(gauth)

def backup(path, gid, ref, ver, lastref, forced):
    for filename in os.listdir(path):
        print(filename)
        if os.path.isdir(path+"\\"+filename):
            """
            If the filename it's a folder, we create the folder and then check if the filename exists in the previous bakup,
            if it exixst then we compare if both (The actual file and the previous) are folders, if this situation it's true
            then we use recursion using the previous folder in 'lastref', else, we pass an empty dict.
            """
            gfolder = gdrive.CreateFile({'title': filename, "parents":  [{"id": gid}], "mimeType": "application/vnd.google-apps.folder"})
            gfolder.Upload()

            ref[filename] = {"gid": gfolder["id"], "subFiles": {}}
            if filename in lastref and "subFiles" in lastref[filename]: # The folder it's in the prev bak and not present changes
                backup(path+"\\"+filename, gfolder["id"], ref[filename]["subFiles"], ver, lastref[filename]["subFiles"], forced)

            else:
                backup(path+"\\"+filename, gfolder["id"], ref[filename]["subFiles"], ver, {}, forced)

        else:
            """
            if the local filename is a file, then whe check the filename exists in the previous backup,
            if the filename exists then whe check if is a file or a folder, if it's a file whe reuse his 
            ref info, else, whe upload the file and create a new ref info.
            """

            # |-------------NOT IN FORCED---------AND------------------------IN LAST BACKUP---------------------|
            if not path+"\\"+filename in forced and filename in lastref and not "subFiles" in lastref[filename]:
                ref[filename] = lastref[filename]

            else:
                gfile = gdrive.CreateFile({"title": filename, "parents": [{"id": gid}]})
                gfile.SetContentFile(path+"\\"+filename)
                gfile.Upload()

                ref[filename] = {"gid": gfile["id"], "ver": ver}

if __name__ == "__main__":
    ver = 2
    gid = "1oEmPfLgLL9y3Rn3PFnkPEkU4NwkkCnD2"

    # given a google drive id, the version folder is cretated
    verFol = gdrive.CreateFile({'title': str(ver), "parents":  [{"id": gid}], "mimeType": "application/vnd.google-apps.folder"})
    verFol.Upload()

    # given the version folder id, the content folder
    contentFol = gdrive.CreateFile({'title': "content", "parents":  [{"id": verFol["id"]}], "mimeType": "application/vnd.google-apps.folder"})
    contentFol.Upload()

    ref = dict()
    lastref = {
        '1': {'gid': '1g6oOfuObtfk-jmGFZhYGbJBQ-ykzDHeR', 'ver': 1, 'subFiles': {
            '2222.txt': {'gid': '1tHOI0yGN5Pf0FpNFbqAMKhEazFOfYvLJ', 'ver': 1}, 
            '27272': {'gid': '15iqbV9KMuJ-mSJBt2yeteuToqwvIt95J', 'ver': 1, 'subFiles': {
                '3232': {'gid': '1s-x5_9oBkEYbztBm9M33tRQ-89lgz7NA', 'ver': 1, 'subFiles': {}}, 
                'asdfghjk.js': {'gid': '1EQ7tjz1zZO-UPAMikMclYzUVaLFLgBfo', 'ver': 1}, 
                'sksksks.py': {'gid': '139kYJQ2KiNhBO7P1i-djCUTS8_FFhfdW', 'ver': 1}, 
                'ssssssss1': {'gid': '1J7W9TznbJrYsctyhEPMZF867NyxeScvv', 'ver': 1, 'subFiles': {
                    '2.c': {'gid': '1Mm6ebKLbBnBQWRgCN36DBY1PkRN5Ne0O', 'ver': 1}, 
                    '3.c': {'gid': '1ABPPV835SJnaxIAbhXlfvJG6Fmj4RanP', 'ver': 1}}}}}, 
            'jsjsjsk.txt': {'gid': '1c8au_5oLZP7OObijv4fx54Fk1YrTHo8Q', 'ver': 1}, 
            'new.java': {'gid': '1KltCjw4qsBFgGNGIwDzfLqwoTbecw01V', 'ver': 1}}}, 
        'a.txt': {'gid': '15fKSoCJ9tKFLlGAlD14ftQKhGrGcGI0R', 'ver': 1}, 
        'b.txt': {'gid': '1peD9Z8T8BP80V8XfgqU9Gu6NixdiX3JF', 'ver': 1}, 
        'c.txt': {'gid': '1KQS19PqozfIrQCuWkI1xmOUplNVQq8I0', 'ver': 1}, 
        'd111.txt': {'gid': '1BAXFrsmOq02aPQvrNoZIp7r1vIixt3i3', 'ver': 1},
        'no2': {'gid': '1as9wQLeKnFc8YvLJ9nG7QdPm3MoNEDP-', 'ver': 1}
        }

    forced = [r"C:\Users\Lenovo-PC\Desktop\scripts\AutoBackup\wathF\a.txt", r"C:\Users\Lenovo-PC\Desktop\scripts\AutoBackup\wathF\1\27272\asdfghjk.js"]
    
    backup(r"C:\Users\Lenovo-PC\Desktop\scripts\AutoBackup\wathF", contentFol["id"], ref, ver, lastref, forced)
    print(ref)
    
