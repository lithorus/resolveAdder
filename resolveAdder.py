#!/usr/bin/python3.6
'''
Created on 2 Jul 2018

@author: jimmy
'''

import os
import sys
import re
from PySide2 import QtWidgets, QtUiTools, QtCore

import DaVinciResolveScript

resolve = DaVinciResolveScript.scriptapp("Resolve")  # @UndefinedVariable
projectManager = resolve.GetProjectManager()
mediaStorage = resolve.GetMediaStorage()

sequenceProg = re.compile('(.*)\.(\d+)\.(\w+)$')


def pathWalker(dirpath, prog):
    sequences = {}
    for direntry in os.scandir(dirpath):
        if direntry.is_dir() is True:
            sequences.update(pathWalker(direntry.path, prog))
        else:
            if prog.match(direntry.path) is not None:
                sequenceMatch = sequenceProg.match(direntry.path)
                if sequenceMatch:
                    if sequenceMatch.group(1) not in sequences:
                        sequences[sequenceMatch.group(1)] = {'extension': sequenceMatch.group(3), 'padding': len(sequenceMatch.group(2)), 'startFrame': 999999999999999, 'endFrame': 0}
                    if int(sequenceMatch.group(2)) < sequences[sequenceMatch.group(1)].get('startFrame'):
                        sequences[sequenceMatch.group(1)]['startFrame'] = int(sequenceMatch.group(2))
                    if int(sequenceMatch.group(2)) > sequences[sequenceMatch.group(1)].get('endFrame'):
                        sequences[sequenceMatch.group(1)]['endFrame'] = int(sequenceMatch.group(2))
                pass
                # paths.append(direntry.path)
    return sequences


class resolveAdder():
    def __init__(self, startPath):
        self.app = QtWidgets.QApplication(sys.argv)

        loader = QtUiTools.QUiLoader()

        self.ui = loader.load("resolveAdderGUI.ui")
        if os.path.isdir(startPath):
            self.ui.inputPathInput.setText(startPath)
        self.ui.browseButton.clicked.connect(self.browsePath)
        self.ui.searchButton.clicked.connect(self.searchPath)
        self.ui.regexInput.editingFinished.connect(self.validateRegex)

        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.show()

        self.app.exec_()

    def browsePath(self):
        fileDialog = QtWidgets.QFileDialog(self.ui)
        fileDialog.setFileMode(fileDialog.Directory)
        path = fileDialog.getExistingDirectory()
        self.ui.inputPathInput.setText(path)

    def validateRegex(self):
        regex = self.ui.regexInput.text()
        try:
            re.compile(regex)
            self.ui.regexInput.setProperty('fail', False)
        except re.error:
            self.ui.regexInput.setProperty('fail', True)
        self.ui.regexInput.style().unpolish(self.ui.regexInput)
        self.ui.regexInput.style().polish(self.ui.regexInput)

    def searchPath(self):
        path = self.ui.inputPathInput.text()
        prog = re.compile(self.ui.regexInput.text())

        sequences = pathWalker(path, prog)
        for sequenceKey, sequenceData in sequences.items():
            extension = sequenceData.get('extension')
            sequenceName = "%s.%s%d-%d.%s" % (sequenceKey, '#' * sequenceData.get('padding'), sequenceData.get('startFrame'), sequenceData.get('endFrame'), extension)
            firstFrame = "%s.%s.%s" % (sequenceKey, '%%0%dd' % sequenceData.get('padding') % sequenceData.get('startFrame'), extension)
            fileItem = QtWidgets.QTreeWidgetItem(self.ui.fileTreeWidget, [sequenceName, extension])
            fileItem.setCheckState(2, QtCore.Qt.Checked)
            fileItem.setData(0, QtCore.Qt.UserRole, firstFrame)
        self.ui.fileTreeWidget.resizeColumnToContents(0)
        self.ui.fileTreeWidget.resizeColumnToContents(1)
        self.ui.fileTreeWidget.resizeColumnToContents(2)

    def accept(self):
        for index in range(0, self.ui.fileTreeWidget.topLevelItemCount()):
            fileEntry = self.ui.fileTreeWidget.topLevelItem(index)
            if fileEntry.checkState(2) == QtCore.Qt.Checked:
                filePath = fileEntry.data(0, QtCore.Qt.UserRole)
                print(filePath)
                print(mediaStorage.AddItemsToMediaPool(filePath))
        self.ui.accept()


if __name__ == "__main__":
    resolveAdder(sys.argv[1])
