from distutils.command.upload import upload
from typing import Counter
import aria2p
import os
from aria2p.api import API
import psycopg2
import psycopg2.extras
from pyasn1.type.univ import Null
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import json
from os import path, remove, stat
import logging
from pydrive.files import GoogleDriveFile

aria2 = aria2p.API(
    aria2p.Client(
        host="http://localhost",
        secret=""
    )
)

class File:
    def __init__(self, email, link, downloadObj):
        self.emailAdd = email
        self.linkAdd = link
        self.downloadObject = downloadObj
        self.failed = False
        self.gDriveFile = None
        self.folderID = None
        self.counter = 1

downloads = []

def downloadURL(link, email, folderID = "root"):
        download = aria2.add_uris([link], options={"dir": "./Downloads", "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36"})
        if folderID == "root":
            downloadObj = File(email, link, download)
        else:
            downloadObj = File(email, link, download)
            downloadObj.folderID = folderID
        downloads.append(downloadObj)
        print("Sending File object now")
        return downloadObj

def dbFetch(email, title, folderID, downObj):
    dbURL = os.environ.get('DATABASE_URL')
    conn = psycopg2.connect(dbURL)
    cur = conn.cursor()
    select = "SELECT * FROM token WHERE email = %s"
    print(email)
    cur.execute(select, (email,))
    fetch = cur.fetchone()
    if(fetch != None):
        token = fetch[1]
        gauth = GoogleAuth()
        with open("credentials.json", "r") as jsonFile:
            data = json.load(jsonFile)
            data["refresh_token"] = token
        with open("credentials.json", "w") as jsonFile:
            json.dump(data, jsonFile)
        gauth.LoadCredentialsFile('credentials.json')
        gauth.Refresh()
        drive = GoogleDrive(gauth)
        folderFile = None
        rootPath = "./Downloads/" + title
        if os.path.isdir(rootPath):
            if folderID == None:
                folder = drive.CreateFile({'title': title, "mimeType": "application/vnd.google-apps.folder"})
            else:
                folder = drive.CreateFile({'title': title, "parents": [{"kind": "drive#fileLink", "id": folderID}], "mimeType": "application/vnd.google-apps.folder"})
            folder.Upload(param={'supportsTeamDrives': True})
            folderNew = folder.get('id')
            for file in os.listdir("./Downloads/" + title):
                filePath = os.path.join("./Downloads/" + title, file)
                if os.path.isfile(filePath):
                    file = drive.CreateFile({'title': file, "parents": [{"kind": "drive#fileLink", "id": folderNew}]})
                    file.SetContentFile(filePath)
                    file.Upload(param={'supportsTeamDrives': True})
                elif os.path.isdir(filePath):
                    logging.warning("Moving to UploadDir function")
                    logging.warning("dBFetch "+filePath)
                    uploadDirectory(drive, file, filePath, rootPath, folderNew)
            return folder
        else:
            if folderID == None:
                file = drive.CreateFile({'title': title})
            else:
                file = drive.CreateFile({'title': title,"parents": [{"kind": "drive#fileLink", "id": folderID}]})
            file.SetContentFile('./Downloads/'+title)
            try:
                file.Upload(param={'supportsTeamDrives': True})
                print("File uploading")
            except Exception as e:
                print(e)
                downObj.failed = True
                return file
            return file

def uploadDirectory(drive, file, parentPath, rootPath, parentFolderID):
    logging.warning("Uploading directory function entered")
    parentFolder = drive.CreateFile({'title': file,  "parents": [{"kind": "drive#fileLink", "id": parentFolderID}],"mimeType": "application/vnd.google-apps.folder"})
    parentFolder.Upload(param={'supportsTeamDrives': True})
    rootID = parentFolder.get('id')
    for file in os.listdir(parentPath):
        filePath = os.path.join(parentPath, file)
        logging.warning(filePath)
        print(filePath)
        if os.path.isdir(filePath):
            logging.warning("Directory found in subfolder, RECURSION")
            uploadDirectory(drive, file, filePath, rootID)
        else:
            logging.warning("File found in subfolder")
            file = drive.CreateFile({'title': file, "parents": [{"kind": "drive#fileLink", "id": rootID}]})
            file.SetContentFile(filePath)
            file.Upload(param={'supportsTeamDrives': True})
    return True
    
def genStatusJSON(email):
    print("Generating status JSON")
    task = []
    for download in downloads:
        if(download.emailAdd == email):
            if(download.downloadObject.is_complete == False):
                download.downloadObject.update()
            size = human_size(download.downloadObject.total_length)
            percentageFloat = float(download.downloadObject.progress).__round__(2)
            percentage = str(percentageFloat) + "%"
            completed = download.downloadObject.is_complete
            link = download.linkAdd
            failed = download.failed
            uploaded = False
            gDriveLink = ""
            speed = human_size(download.downloadObject.download_speed)
            time = download.downloadObject.eta
            if download.downloadObject.is_torrent:
                torrent = True
                seeders = download.downloadObject.num_seeders
            else:
                torrent = False
                seeders = 0
            if(download.gDriveFile != None):
                download.gDriveFile.update()
                if(download.gDriveFile.uploaded == True):
                    uploaded = True
                    download.counter += 1
                    gDriveLink = download.gDriveFile.get('alternateLink')
                    if download.counter == 5:
                        download.downloadObject.remove(files=True)
                        downloads.remove(download)
            task.append({
            "title": download.downloadObject.name,
            "size": size,
            "percentage": "{}".format(percentage),
            "completed" : "{}".format(completed),
            "uploaded": "{}".format(uploaded),
            "gDriveLink" : "{}".format(gDriveLink),
            "failed" : "{}".format(failed),
            "link" : link,
            "speed" : "{}".format(speed),
            "time" : "{}".format(time),
            "torrent": "{}".format(torrent),
            "seeders": "{}".format(seeders)
            })
            if(failed == True):
                print("Removing from list")
                downloads.remove(download)
    print(task)
    JSONStr = json.dumps(task)
    return JSONStr

def genStatusShortcutJSON(email):
    print("Generating status JSON")
    item = "{"
    for download in downloads:
        if(download.emailAdd == email):
            if(download.downloadObject.is_complete == False):
                download.downloadObject.update()
            size = human_size(download.downloadObject.total_length)
            percentageFloat = float(download.downloadObject.progress).__round__(2)
            percentage = str(percentageFloat) + "%"
            completed = download.downloadObject.is_complete
            link = download.linkAdd
            failed = download.failed
            uploaded = False
            gDriveLink = ""
            speed = human_size(download.downloadObject.download_speed)
            time = download.downloadObject.eta
            if download.downloadObject.is_torrent:
                torrent = True
                seeders = download.downloadObject.num_seeders
            else:
                torrent = False
                seeders = 0
            if(download.gDriveFile != None):
                download.gDriveFile.update()
                if(download.gDriveFile.uploaded == True):
                    uploaded = True
                    download.counter += 1
                    gDriveLink = download.gDriveFile.get('alternateLink')
                    if download.counter == 5:
                        download.downloadObject.remove(files=True)
                        downloads.remove(download)
            if failed == True:
                status = '"' + "{} Failed".format(download.downloadObject.name) + '",'
            elif completed == True and uploaded == True:
                status = '"' +  "{} Completed & Uploaded".format(download.downloadObject.name)+ '",'
            elif completed == True and uploaded == False:
                status = '"' +  "{} Completed & Uploading".format(download.downloadObject.name)+ '",'
            elif completed == False and uploaded == False:
                status = '"' + "{} {} {}".format(download.downloadObject.name, percentage, speed)+ '",'
            item = item + status
            if(failed == True):
                print("Removing from list")
                downloads.remove(download)
    item = item[:-1] + "}"
    print(item)
    return item


def getUploadStatus(email, link):
    for download in downloads:
        if(download.emailAdd == email and download.linkAdd == link):
            uploaded = False
            gDriveLink = ""
            if(download.gDriveFile != None):
                download.gDriveFile.update()
                if(download.gDriveFile.uploaded == True):
                    uploaded = True
                    gDriveLink = download.gDriveFile.get('alternateLink')
                    download.downloadObject.remove(files=True)
                    downloads.remove(download)
    return uploaded, gDriveLink

def deleteDownload(email):
    for download in downloads:
        if(download.emailAdd == email):
            download.downloadObject.remove(files=True)
            downloads.remove(download)
            return True
    return False

def completedDownload(api: API, gid):
    print("DOWNLOAD COMPLETE EVENT")
    for download in downloads:
        if(download.downloadObject.gid == gid):
            download.downloadObject.update()
            if(download.downloadObject.followed_by_ids is not None and download.downloadObject.is_metadata):
                new_gid = download.downloadObject.followed_by_ids[0]
                new_download = api.get_download(new_gid)
                download.downloadObject = new_download
            else:
                if(download.downloadObject.is_complete == True):
                    print("Download complete")
                    emailStr = download.emailAdd
                    title = str(download.downloadObject.name)
                    if title.find("?") != -1:
                        title = title[:title.find("?")]
                    else:
                        title = str(download.downloadObject.name)
                    folder = download.folderID
                    print("Uploading to GDrive")
                    download.gDriveFile = dbFetch(emailStr, title, folder, download.downloadObject)
                    if(download.gDriveFile.uploaded):
                        print("Uploaded to GDrive")
                    return True

def errorDownload(api: API, gid):
    for download in downloads:
        if(download.downloadObject.gid == gid):
            download.failed = True
            return False

def human_size(bytes, units=[' bytes','KB','MB','GB','TB', 'PB', 'EB']):
    """ Returns a human readable string representation of bytes """
    return str(bytes) + units[0] if bytes < 1024 else human_size(bytes>>10, units[1:])


aria2.listen_to_notifications(threaded=True, on_download_complete=completedDownload, on_download_error=errorDownload, timeout=3)