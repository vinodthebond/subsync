import subsync.gui.layout.settingswin
from subsync.gui.components.filedlg import showSaveFileDlg
from subsync.settings import settings, Settings
from subsync.data import descriptions
from subsync import config
import multiprocessing
import wx


class SettingsWin(subsync.gui.layout.settingswin.SettingsWin):
    def __init__(self, parent):
        super().__init__(parent)
        self.m_outputCharEnc.SetString(0, _('same as input subtitles'))

        self.m_buttonMaxPointDistInfo.message = descriptions.maxPointDistInfo
        self.m_buttonMinPointsNoInfo.message = descriptions.minPointsNoInfo
        self.m_buttonMinWordLenInfo.message = descriptions.minWordLenInfo
        self.m_buttonMinWordSimInfo.message = descriptions.minWordSimInfo
        self.m_buttonMinCorrelationInfo.message = descriptions.minCorrelationInfo
        self.m_buttonMinWordProbInfo.message = descriptions.minWordProbInfo
        self.m_buttonJobsNoInfo.message = descriptions.jobsNoInfo

        if not config.assetupd:
            self.m_textUpdates.Hide()
            self.m_autoUpdate.Hide()
            self.m_askForUpdate.Hide()

        self.setSettings(settings())

    def setSettings(self, settings):
        self.settings = Settings(settings)

        self.m_jobsNo.SetValue(max(multiprocessing.cpu_count(), 2))

        for field, key, val in self.settingsFieldsGen():
            if val != None:
                field.SetValue(val)

        jobsNo = self.settings.jobsNo
        self.m_checkAutoJobsNo.SetValue(jobsNo == None)
        self.m_jobsNo.Enable(jobsNo != None)

        logLevel = self.settings.logLevel / 10
        if logLevel >= 0 and logLevel < self.m_choiceLogLevel.GetCount():
            self.m_choiceLogLevel.SetSelection(logLevel)

        logFile = self.settings.logFile
        self.m_checkLogToFile.SetValue(logFile != None)
        self.m_textLogFilePath.Enable(logFile != None)
        self.m_buttonLogFileSelect.Enable(logFile != None)
        self.m_textLogFilePath.SetValue(logFile if logFile else '')

        logBlacklist = self.settings.logBlacklist
        if logBlacklist == None:
            logBlacklist = []
        self.m_textLogBlacklist.SetValue('\n'.join(logBlacklist))

    def getSettings(self):
        for field, key, val in self.settingsFieldsGen():
            setattr(self.settings, key, field.GetValue())

        if self.m_checkAutoJobsNo.IsChecked():
            self.settings.jobsNo = None

        logLevel = self.m_choiceLogLevel.GetSelection()
        if logLevel != wx.NOT_FOUND:
            self.settings.logLevel = logLevel * 10

        if self.m_checkLogToFile.IsChecked():
            self.settings.logFile = self.m_textLogFilePath.GetValue()
        else:
            self.settings.logFile = None

        logBlacklist = self.m_textLogBlacklist.GetValue().split()
        if len(logBlacklist) > 0:
            self.settings.logBlacklist = logBlacklist
        else:
            self.settings.logBlacklist = None

        return self.settings

    def settingsFieldsGen(self):
        for key in self.settings.keys():
            field = 'm_' + key
            if hasattr(self, field):
                yield getattr(self, field), key, self.settings.get(key)

    def onCheckAutoJobsNoCheck(self, event):
        auto = self.m_checkAutoJobsNo.IsChecked()
        self.m_jobsNo.Enable(not auto)

    def onCheckLogToFileCheck(self, event):
        enabled = self.m_checkLogToFile.IsChecked()
        self.m_textLogFilePath.Enable(enabled)
        self.m_buttonLogFileSelect.Enable(enabled)
        if not self.m_textLogFilePath.GetValue():
            if not self.selectLogFile():
                self.m_checkLogToFile.SetValue(False)

    def onButtonLogFileSelectClick(self, event):
        self.selectLogFile()

    def selectLogFile(self):
        path = showSaveFileDlg(self)
        if path:
            self.m_textLogFilePath.SetValue(path)
        return path

    def onButtonRestoreDefaultsClick(self, event):
        dlg = wx.MessageDialog(
                self,
                _('Are you sure you want to reset settings to defaults?'),
                _('Restore defaults'),
                wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)

        if dlg.ShowModal() == wx.ID_YES:
            self.setSettings(Settings())
