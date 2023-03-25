from mainUI import MainUI
from searchFiles import SearchFiles
from uploadFiles import UploadFiles

def MainToSF(master):
    searchFilesPage = SearchFiles(master)
    searchFilesPage.pack()

def SFToMain(master):
    mainUIPage = MainUI(master)
    mainUIPage.pack()

def MainToUF(master):
    uploadFilesPage = UploadFiles(master)
    uploadFilesPage.pack()

def UFToMain(master):
    mainUIPage = MainUI(master)
    mainUIPage.pack()


