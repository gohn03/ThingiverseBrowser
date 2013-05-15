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
        parent.categories = ["Thingiverse"]
        parent.dependencies = []
        parent.contributors = ["Nigel Goh (UWA)"]
        parent.helpText = """
        Module that allows users to browse and download designs from Thingiverse.com
        """
        parent.acknowledgementText = """
        This file was  developed by Nigel Goh, UWA, as part of a final year project.
        The assistance of Steve Pieper, Isomics, Inc., in the development process is greatly appreciated.
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

    def startButtonClicked(self):
        ThingViewer()
    
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
        global currentUrl
        currentUrl = 'http://www.thingiverse.com/'
        self.ThingView.page().setLinkDelegationPolicy(2)
        self.ThingView.setUrl(qt.QUrl(currentUrl))
        self.ThingView.resize(1050,800)
        self.ThingView.show()
        self.ThingView.linkClicked.connect(self.handleClick)
        
    def downloadFile(self, dlUrl):
        destination = slicer.mrmlScene.GetCacheManager().GetRemoteCacheDirectory()
        self.name = self.ThingView.title
        filePath = destination + "/" + self.name
        if "zip" in dlUrl:
            filePath = filePath + ".zip"
        elif "download" in dlUrl:
            filePath = filePath + "_" + dlUrl.rsplit(":")[2] + ".stl"
        if os.path.exists(filePath):
            checkOverwrite = self.overwriteCheck()
            if checkOverwrite is 0:
                self.ProgressBar.show()
                urllib.urlretrieve(dlUrl, filePath, self.reportProgress)
                self.ProgressBar.close()
            else:
                pass
        else:
            self.ProgressBar.show()
            urllib.urlretrieve(dlUrl, filePath, self.reportProgress)
            self.ProgressBar.close()            
        return filePath
    
    def overwriteCheck(self):
        checkBox = qt.QMessageBox()
        checkBox.setText("File already exists. Do you want to overwrite?")
        checkBox.addButton('Overwrite', 0)
        checkBox.addButton('Use existing file', 1)
        return checkBox.exec_()
    
    def extract(self, ZipSource):
        zip = zipfile.ZipFile(ZipSource)
        zipList = zip.namelist()
        folderName = zipList[0]
        extractDir = slicer.mrmlScene.GetCacheManager().GetRemoteCacheDirectory()
        zip.extractall(path = extractDir)
        finalDir = extractDir + '/' + folderName
        return finalDir
        
    def loadModel(self, loadDir):
        return slicer.util.loadModel(loadDir)
        
    def listFiles(self, fileSet):
        return dircache.listdir(fileSet)
        
    def loadFiles(self, folderToLoad):
        fileList = self.listFiles(folderToLoad)
        for ii in range(len(fileList)):
            toLoad = folderToLoad + "/" + fileList[ii]
            self.loadModel(toLoad)
        
    def reportProgress(self, blocks, blockSize, totalSize):
            percent = (blocks * blockSize * 100)/totalSize
            self.ProgressBar.setValue(percent)
        
    def handleClick(self, url):
        global nextUrl
        nextUrl = url.toString()
        global currentUrl
        if currentUrl is not nextUrl:
            if "download" in nextUrl:
                filePath = self.downloadFile(nextUrl)
                self.loadModel(filePath)
            elif "zip" in nextUrl:
                filePath = self.downloadFile(nextUrl)
                finalDir = self.extract(filePath)
                self.loadFiles(finalDir)
            else:
                currentUrl = nextUrl
                self.ThingView.setUrl(qt.QUrl(currentUrl))
