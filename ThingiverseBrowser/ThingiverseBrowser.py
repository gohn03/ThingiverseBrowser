from __main__ import slicer
import zipfile
import urllib
import os
import dircache

#
# Thingiverse
#

class ThingiverseBrowser:
    def __init__(self, parent):
        parent.title = "Thingiverse Browser"
        parent.categories = ["Utilities"]
        parent.dependencies = []
        parent.contributors = ["Nigel Goh (UWA)"]
        parent.helpText = """
        Module that allows users to browse and download designs from Thingiverse.com
        """
        parent.acknowledgementText = """
        This file was  developed by Nigel Goh, UWA, as part of a final year project.
        The assistance of Steve Pieper, Isomics, Inc., and Jean-Christophe, KitWare, in the development process is greatly appreciated.
        """
        self.parent = parent

#
# ThingiverseWidget
#

class ThingiverseBrowserWidget:
    def __init__(self, parent = None):
        if not parent:
            self.parent = slicer.qMRMLWidget()
            self.parent.setLayout(qt.QVBoxLayout())
            self.parent.setMRMLScene(slicer.mrmlScene)
        else:
            self.parent = parent
        self.layout = self.parent.layout()
        if not parent:
            self.setup()
            self.parent.show()

    #Add Slicer Interface Buttons
    def setup(self):
        startButton = qt.QPushButton("Start Browser")
        startButton.toolTip = "Start QWebView to begin browsing Thingiverse"
        clearButton = qt.QPushButton("Clear All")
        clearButton.toolTip = "Clears all loaded models"
        self.layout.addWidget(startButton)
        self.layout.addWidget(clearButton)
        startButton.connect('clicked(bool)',self.startButtonClicked)
        clearButton.connect('clicked(bool)',self.clearButtonClicked)

        # Add vertical spacer
        self.layout.addStretch(1)

        # Set local var as instance attribute
        self.startButton = startButton
        self.clearButton = clearButton

    #Run ThingViewer if Start is clicked
    def startButtonClicked(self):
        ThingViewer()
    
    #Clear all models from Slicer screen if Clear All is clicked
    def clearButtonClicked(self):
        slicer.mrmlScene.Clear(0)

#
# ThingViewer
#
        
class ThingViewer:
    def __init__(self):
        self.ThingView = qt.QWebView()
        self.ProgressBar = qt.QProgressDialog()
        self.ProgressBar.setLabelText('Downloading File')
        
        #Initialize and assign the global variable currentUrl to starting webpage
        global currentUrl
        currentUrl = 'http://www.thingiverse.com/'
        self.ThingView.setUrl(qt.QUrl(currentUrl))
        self.ThingView.resize(1050,800)
        
        #Activate and show QWebView using show()
        self.ThingView.show()
        
        #Change QWebView such that link clicks are not automatically acted on
        #When links are clicked, run the handleClick() function
        self.ThingView.page().setLinkDelegationPolicy(2)        
        self.ThingView.linkClicked.connect(self.handleClick)
    
    #Function used to download files
    def downloadFile(self, dlUrl):
        #Set download directory to a folder in Slicer cache
        #Folder name is based on title of current webpage (Name of design)
        destination = slicer.mrmlScene.GetCacheManager().GetRemoteCacheDirectory()
        self.name = self.ThingView.title
        filePath = destination + "/" + self.name
        
        #If download URL has 'zip', save file as .zip
        if "zip" in dlUrl:
            filePath = filePath + ".zip"
        #Otherwise, file is an .stl file. Save file as .stl
        elif "download" in dlUrl:
            filePath = filePath + "_" + dlUrl.rsplit(":")[2] + ".stl"
        
        #Check if file already exists in directory.
        #If exists, check if user wants to overwrite or redownload using overwriteCheck()
        if os.path.exists(filePath):
            checkOverwrite = self.overwriteCheck()
            #If user chooses to overwrite (overwriteCheck returns 0), redownload
            #Display progress bar and use urlretrieve() to download
            if checkOverwrite is 0:
                self.ProgressBar.show()
                urllib.urlretrieve(dlUrl, filePath, self.reportProgress)
                self.ProgressBar.close()
            #If user chooses to reuse existing file, do nothing
            else:
                pass
        #If file doesn't exist, begin download
        #Display progress bar and use urlretrieve() to download
        else:
            self.ProgressBar.show()
            urllib.urlretrieve(dlUrl, filePath, self.reportProgress)
            self.ProgressBar.close()            
        return filePath
    
    #Displays a box that asks users to Overwrite or Use existing file
    #Returns 0 to Overwrite, 1 to use existing file
    #Executes at the end using exec_()
    def overwriteCheck(self):
        checkBox = qt.QMessageBox()
        checkBox.setText("File already exists. Do you want to overwrite?")
        checkBox.addButton('Overwrite', 0)
        checkBox.addButton('Use existing file', 1)
        return checkBox.exec_()
    
    #Function used to extract all files from a zip
    def extract(self, ZipSource):
        zip = zipfile.ZipFile(ZipSource)
        
        #Thingiverse stores designs in a folder in the zip
        #This extracts the name of the folder inside the zip
        zipList = zip.namelist()
        folderName = zipList[0]
        
        #Returns final directory including the folder that was in the zip
        extractDir = slicer.mrmlScene.GetCacheManager().GetRemoteCacheDirectory()
        zip.extractall(path = extractDir)
        finalDir = extractDir + '/' + folderName
        return finalDir
    
    #Loads model into Slicer
    def loadModel(self, loadDir):
        return slicer.util.loadModel(loadDir)
    
    #Supporting function for loadFiles() that lists all the files inside a folder
    def listFiles(self, fileSet):
        return dircache.listdir(fileSet)
    
    #Loads all the models inside a folder into Slicer
    def loadFiles(self, folderToLoad):
        fileList = self.listFiles(folderToLoad)
        for ii in range(len(fileList)):
            toLoad = folderToLoad + "/" + fileList[ii]
            self.loadModel(toLoad)
    
    #Changes value of ProgressBar based on download progress
    #ProgressBar is hidden by default and only shown when downloads occur
    def reportProgress(self, blocks, blockSize, totalSize):
            percent = (blocks * blockSize * 100)/totalSize
            self.ProgressBar.setValue(percent)
        
    #Main function that runs whenever a link is clicked    
    def handleClick(self, url):
        #Define new global variable nextUrl
        global nextUrl
        #Store the link clicked as the global variable nextUrl
        nextUrl = url.toString()
        #Define function's currentUrl as the global currentUrl
        global currentUrl
        
        #Logic for clicks. 
        #Only execute if the link clicked is different to current page
        if currentUrl is not nextUrl:
            #Thingiverse has 'download' in the title of all .stl downloads
            #When downloads for STL files are clicked, run this 
            if "download" in nextUrl:
                filePath = self.downloadFile(nextUrl)
                self.loadModel(filePath)
            #Thingiverse has 'zip' in the title of all .zip downloads
            #When downloads for ZIP files are clicked, run this
            elif "zip" in nextUrl:
                filePath = self.downloadFile(nextUrl)
                finalDir = self.extract(filePath)
                self.loadFiles(finalDir)
            #If link clicked is not a download but is different, navigate to new link
            else:
                currentUrl = nextUrl
                self.ThingView.setUrl(qt.QUrl(currentUrl))
