import os
import gamelist.gamelibrary
import gamelist.igdb
import gamelist.platforms

from PyQt5.QtCore import QStringListModel
from PyQt5.QtWidgets import QMainWindow, QCompleter, QTableWidgetItem, QDialog, QFileDialog, QMessageBox

from gamelist.mainwindow_ui import Ui_MainWindow
from gamelist.aboutdialog_ui import Ui_AboutDialog


class GameListGUI(QMainWindow):

    def __init__(self):
        super(GameListGUI, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Widgets
        self.platformComboBox = self.ui.platformComboBox
        self.searchLineEdit = self.ui.searchLineEdit
        self.table = self.ui.tableWidget
        self.platformLineEdit = self.ui.platformLineEdit
        self.titleLineEdit = self.ui.titleLineEdit
        self.addButton = self.ui.addButton
        self.statusbar = self.ui.statusbar

        # Class members
        self.filename = 'untitled.db'
        self.igdb = gamelist.igdb.igdb('API-KEY-GOES-HERE')
        self.gamelib = gamelist.gamelibrary.GameLibrary(self.filename)
        self.platforms = gamelist.platforms.Platforms('platforms.dat')

        self.setupUi()
        self.refreshUi()

        # Menu bar signals and slots
        self.ui.actionNew.triggered.connect(self.new)
        self.ui.actionOpen.triggered.connect(self.open_)
        self.ui.actionSave.triggered.connect(self.save)
        self.ui.actionImport.triggered.connect(self.import_)
        self.ui.actionExport.triggered.connect(self.export)
        self.ui.actionRemove.triggered.connect(self.removeRecord)
        self.ui.actionUpdate_platform_database.triggered.connect(self.updatePlatforms)
        self.ui.actionAbout.triggered.connect(self.showAboutDialog)

        # Other signals and slots
        self.ui.platformComboBox.activated.connect(self.displayTableWrapper)
        self.ui.searchLineEdit.textChanged.connect(self.displayTableWrapper)
        self.ui.addButton.clicked.connect(self.addRecord)
        self.ui.titleLineEdit.returnPressed.connect(self.addRecord)
        self.ui.platformLineEdit.editingFinished.connect(self.setupTitleCompleter)

    def setupUi(self):
        self.setupPlatformCompleter()

    def showAboutDialog(self):
        'Displays About dialog box'
        dialog = QDialog()
        ui = Ui_AboutDialog()
        ui.setupUi(dialog)
        dialog.exec_()

    def updatePlatforms(self):
        'Updates the platform database'
        try:
            self.statusbar.showMessage('Updating... downloading platforms.')
            plats = self.igdb.get_platforms('&fields=name')

            self.statusbar.showMessage('Updating... updating local database.')
            self.platforms.removeAll()
            for item in plats:
                self.platforms.add(item['id'], item['name'])

            self.statusbar.showMessage('Update successful.')
            self.setupPlatformCompleter()
        except:
            self.statusbar.showMessage('Update failed.')

    def setupPlatformCompleter(self):
        'Sets up platformLineEdit completer with all platforms'
        completer = QCompleter(self)
        self.ui.platformLineEdit.setCompleter(completer)
        model = QStringListModel()
        completer.setModel(model)

        try:
            platformNames = [item[1] for item in self.platforms.getPlatforms()]
            model.setStringList(platformNames)
        except:
            # couldn't get the list of platforms
            pass

    def setupTitleCompleter(self):
        'Sets up titleLineEdit completer with all games for a platform'
        completer = QCompleter(self)
        self.ui.titleLineEdit.setCompleter(completer)
        model = QStringListModel()
        completer.setModel(model)

        try:
            # get the platform name and id
            platformName = self.platformLineEdit.text()
            platformId = self.platforms.getPlatformId(platformName)

            # get every game for that platform id
            games = self.igdb.get_games(platformId)

            # set the model
            model.setStringList(games)

        except:
            pass

    def refreshUi(self):
        'Renders the dynamic parts of the UI'
        self.displayTitle()
        self.displayComboBox()
        self.displayTableWrapper()

    def displayTitle(self):
        'Displays the file name in the window title'

        head, tail = os.path.split(self.filename)
        tail = os.path.splitext(tail)[0]

        if self.gamelib.saved:
            title = '{}'.format(tail)
        else:
            title = '{}*'.format(tail)
        
        self.setWindowTitle(title)

    def displayComboBox(self):
        'Displays a combobox with a list of platforms'
        # Get the user's previous selection
        selectedPlatform = self.ui.platformComboBox.currentText()

        # Clear the comboxbox and rebuild it
        self.ui.platformComboBox.clear()
        self.ui.platformComboBox.addItem("All Platforms")
        
        for item in self.gamelib.getPlatforms():
            self.ui.platformComboBox.addItem(item)

        # After rebuild, current index is already set to 0
        # If the previous selection is still there, find it and change the index to that
        for i in range(self.ui.platformComboBox.count()):
            if self.ui.platformComboBox.itemText(i) == selectedPlatform:
                self.ui.platformComboBox.setCurrentIndex(i)

    def displayTableWrapper(self):
        'Wraps displayTable() to pass information from the ui'
        
        # Get text from the comboBox and search box
        platform = self.ui.platformComboBox.currentText()
        searchbox = self.ui.searchLineEdit.text()

        # Set platform and searchbox to variables that work with GameLibrary.getGamesBySearch()
        if platform == 'All Platforms':
            platform = ''

        # Create header and body
        headers = ['Platform', 'Title', 'Release Date', 'Genres']
        games = self.gamelib.getGamesByQuery(searchbox, platform)
        body = [(record[1], record[3], record[7], record[8]) for record in games]
            
        self.displayTable(headers, body)

    def displayTable(self, headers, body):
        'Displays the table'
        
        # Get currently selected row and column
        oldrow = self.ui.tableWidget.currentRow()
        oldcolumn = self.ui.tableWidget.currentColumn()

        # Clear the table
        self.ui.tableWidget.setColumnCount(0)
        self.ui.tableWidget.setRowCount(0)
        self.ui.tableWidget.clear()

        # Display table headings
        self.ui.tableWidget.setColumnCount(len(headers))
        self.ui.tableWidget.setHorizontalHeaderLabels(headers)

        # Populate the table
        row, column = 0, 0
        for record in body:

            self.ui.tableWidget.insertRow(row)
            
            for item in record:
                newcell = QTableWidgetItem(item)
                self.ui.tableWidget.setItem(row, column, newcell)
                column += 1

            column = 0
            row += 1

        # Select the row/column that was selected before
        if oldrow > self.ui.tableWidget.rowCount()-1:
            oldrow -= 1
        self.ui.tableWidget.setCurrentCell(oldrow, oldcolumn)
        

    def new(self):
        'Starts a new file'
        # See if current file is saved first
        self.savecheck()

        # Close the file and make a new temp file
        self.gamelib.close()
        self.filename = 'untitled.db'
        self.gamelib = gamelist.gamelibrary.GameLibrary('untitled.db')
        self.refreshUi()
        
    def open_(self):
        'Opens a file'

        # See if current file is saved first
        self.savecheck()

        # Ask for the filename
        file, _ = QFileDialog.getOpenFileName(self, 'Open file', '', 'Gamelist Files (*.db)')

        # Return if the user hit cancel
        if file == '':
                return

        # Open the file and refreshe the ui
        self.filename = file
        self.gamelib.close()
        self.gamelib = gamelist.gamelibrary.GameLibrary(self.filename)
        self.refreshUi()

    def save(self):
        'Saves the file'

        # Ask for filename if using default
        if self.filename == 'untitled.db':

            self.filename, _ = QFileDialog.getSaveFileName(self, 'Save file', '', 'Gamelist Files (*.db)')

            # Return if the user hit cancel
            if self.filename == '':
                self.filename = 'untitled.db'
                return

            # Make sure the file ends with .db
            if not self.filename.endswith('.db'):
                self.filename += '.db'

            # If file already exists, delete it
            if os.path.isfile(self.filename):
                os.remove(self.filename)

            # Close the default file, move it to where user wants, reopen it
            self.gamelib.save()
            self.gamelib.close()
            os.rename('untitled.db', self.filename)
            self.gamelib = gamelist.gamelibrary.GameLibrary(self.filename)
            self.refreshUi()

        else:
            self.gamelib.save()
            self.refreshUi()

    def savecheck(self):
        'Asks the user to save if there are unsaved changes'

        # Return if no unsaved changes
        if self.gamelib.saved:
          return

        # See if user wants to save changes
        result = QMessageBox.question(self, 'Save', "There are unsaved changes. Save them?",
                                                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        # If user selects yes, save the file
        if result == QMessageBox.Yes:
            self.save()

    def import_(self):
        'Imports from .csv file'
        
        self.savecheck()
        file = QFileDialog.getOpenFileName(self, 'Import file', '', 'CSV (Comma delimited) (*.csv)')

        if file != '':
            self.gamelib.import_(file)

        self.refreshUi()

    def export(self):
        'Exports to .csv file'
        
        self.savecheck()
        file = QFileDialog.getSaveFileName(self, 'Export file', '', 'CSV (Comma delimited) (*.csv)')

        if file != '':
            self.gamelib.export(file)

        self.refreshUi()

    def addRecord(self):
        'Adds a record to the database and updates the ui'
        platform = self.platformLineEdit.text()
        title = self.titleLineEdit.text()

        if platform == '' or title == '':
            return

        try:
            # search igdb for the game
            game = self.igdb.games('?filter[name][eq]={}&fields=name,genres,release_dates,cover&expand=genres'.format(title))
            game = game[0]

            # get the game info
            titleid = game['id']
            platformid = self.platforms.getPlatformId(platform)

            genres = ''
            for item in game['genres']:
                genres += item['name'] + ' '

            release_date = ''
            for item in game['release_dates']:
                if item['platform'] == platformid:
                    release_date += item['human'] + ' '

            coverid = game['cover']['cloudinary_id']
            coverUrl = game['cover']['url']

            # Finally, insert everything
            self.gamelib.add(platform, title, titleid=titleid, platformid=platformid, cover=coverUrl, coverid=coverid,
                             release_date=release_date, genres=genres)

            self.refreshUi()
            self.ui.titleLineEdit.setText('')
            self.ui.titleLineEdit.setFocus()

        except:
            # If all else fails, just insert what the user entered.
            self.gamelib.add(platform, title)

            self.refreshUi()
            self.ui.titleLineEdit.setText('')
            self.ui.titleLineEdit.setFocus()

    def removeRecord(self):
        'Removes the highlighted row from the database'
        row = self.ui.tableWidget.currentRow()

        if row == -1:
            return

        platform = self.ui.tableWidget.item(row, 0).text()
        title = self.ui.tableWidget.item(row, 1).text()

        self.gamelib.remove(platform, title)
        self.refreshUi()

    def closeEvent(self, event):
        'Cleanup when the window closes'
        
        self.savecheck()
        self.gamelib.close()

        if os.path.isfile('untitled.db'):
            os.remove('untitled.db')
        
        event.accept()
