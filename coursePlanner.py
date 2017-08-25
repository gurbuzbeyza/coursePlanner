#!/usr/bin/env python
import requests, bs4, re, sys, os.path, time
from PyQt5.QtCore import *
from PyQt5.QtGui import * 
from PyQt5.QtWidgets import *
from urllib2 import urlopen
class MyTable(QDialog):
	#static variables
	addCourseText = "Add Course"
	removeCourseText = "Remove Course"
	updateButtonText = "Update"
	updateProgressText = "Update in progress ..."

	def __init__(self, parent = None):
		super(MyTable, self).__init__(parent)
		self.mainlayout = QVBoxLayout()
		self.layout = QGridLayout()
		self.addlo = QHBoxLayout()
		self.table = QTableWidget()
		self.table.setRowCount(5)
		self.table.setColumnCount(9)
		horHeaders = ['09.00-10.00', '10.00-11.00', '11.00-12.00', '12.00-13.00', '13.00-14.00', '14.00-15.00', '15.00-16.00', '16.00-17.00', '17.00-18.00']
		verHeaders = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
		self.table.setHorizontalHeaderLabels(horHeaders)
		self.table.setVerticalHeaderLabels(verHeaders)
		self.addLine = QLineEdit()
		self.addLine.setPlaceholderText(self.addCourseText)
		self.deps = QComboBox()
		self.conums = QComboBox()
		self.secs = QComboBox()
		self.deps.addItems(sorted(departments))
		self.addlo.addWidget(self.addLine)
		self.addlo.addWidget(self.deps)
		self.addlo.addWidget(self.conums)
		self.addlo.addWidget(self.secs)
		self.removeLine = QLineEdit()
		self.removeLine.setPlaceholderText(self.removeCourseText)
		self.addButton = QPushButton(self.addCourseText)
		self.removeButton = QPushButton(self.removeCourseText)
		self.update = QPushButton(self.updateButtonText)
		self.label = QLabel()
		self.mainlayout.addWidget(self.table)
		self.layout.addWidget(self.addButton, 0, 0)
		self.layout.addLayout(self.addlo, 0, 1)
		self.layout.addWidget(self.removeButton, 1, 0)
		self.layout.addWidget(self.removeLine, 1, 1)
		self.mainlayout.addLayout(self.layout)  
		self.mainlayout.addWidget(self.update)  
		self.setLayout(self.mainlayout) 
		self.addButton.clicked.connect(self.addClick)
		self.removeButton.clicked.connect(self.removeClick)
		self.update.clicked.connect(self.updateClick)
		self.deps.currentIndexChanged.connect(self.depsChanged)
		self.conums.currentIndexChanged.connect(self.conumsChanged)
		self.secs.currentIndexChanged.connect(self.secsChanged)
		self.table.resizeColumnsToContents()
		self.table.resizeRowsToContents()
		self.table.setFixedSize(self.table.horizontalHeader().length()+100, self.table.verticalHeader().length()+30)
		self.setWindowTitle('Course Planner for BOUN Students')
	def addClick(self):
		course = str(self.addLine.text()).strip()
		for i in allLessons:
			if course == i.name:
				self.parse(i)
				break
		self.addLine.clear()
	def removeClick(self):
		course = str(self.removeLine.text()).strip()
		for x in xrange(0,5):
			for y in xrange(0,9):
				if self.table.item(x,y) != None:
					if self.table.item(x,y).text() == course:
						newitem = QTableWidgetItem('')
						newitem.setFlags(Qt.ItemIsEditable | Qt.ItemIsEnabled)		
					elif course + '\n' in self.table.item(x,y).text():
						newitem = QTableWidgetItem(self.table.item(x,y).text().replace(course + '\n',''))		
					elif '\n' + course in self.table.item(x,y).text():
						newitem = QTableWidgetItem(self.table.item(x,y).text().replace('\n' + course,''))
					else:
						newitem = QTableWidgetItem(self.table.item(x,y).text())
					self.table.setItem(x, y, newitem)
		self.table.resizeColumnsToContents()
		self.table.resizeRowsToContents()  
		self.table.setFixedSize(self.table.horizontalHeader().length()+100, self.table.verticalHeader().length()+30)
		self.removeLine.clear()

	def parse(self, less):
		days = []
		slots = []
		if less.days != 'TBA' and less.days != '':
			if 'Th' in less.days:
				str=less.days.replace("Th","H")
			else:
				str=less.days
			i=0
			for x in str:
				if x == 'M':
					days.append(1)
				elif x == 'T':
					days.append(2)
				elif x == 'W':
					days.append(3)
				elif x == 'H':
					days.append(4)
				elif x == 'F':
					days.append(5)
				slots.append(int(less.slots[i]))
				i+=1
			self.createTable(less, days, slots)
		return

	def createTable(self, less, days, slots):
		for x, y in zip(days, slots):
			if self.table.item(x-1, y-1) != None and self.table.item(x-1, y-1).text() != '': 
				if less.name in self.table.item(x-1, y-1).text():
					continue
				newitem = QTableWidgetItem(self.table.item(x-1, y-1).text() + '\n' + less.name)
				newitem.setFlags(Qt.ItemIsEnabled)
				self.table.setItem(x-1, y-1, newitem)
			else:	
				newitem = QTableWidgetItem(less.name)			
				newitem.setFlags(Qt.ItemIsEnabled)
				self.table.setItem(x-1, y-1, newitem)
			self.table.resizeColumnsToContents()
			self.table.resizeRowsToContents()
			self.table.setFixedSize(self.table.horizontalHeader().length()+100, self.table.verticalHeader().length()+30)   
	
	def updateClick(self):
		global departments
		self.label.setText(self.updateProgressText)
		self.mainlayout.addWidget(self.label)
		self.repaint()
		qApp.processEvents()
		update()
		self.label.setText('Updated!')
		departments = []
		
		for x in allLessons:
			matchobj = re.match(r'([a-zA-Z]+)(.+)\.(.+)', x.name)
			if matchobj:
				x.department = matchobj.group(1)
				x.course = matchobj.group(2)
				x.section = matchobj.group(3)
				if matchobj.group(1) not in departments:
					departments.append(matchobj.group(1))


	def depsChanged(self):
		courses = []
		self.conums.clear()
		for x in allLessons:
				if self.deps.currentText() == x.department and x.course not in courses:
					courses.append(x.course)
		self.conums.addItems(courses)
	def conumsChanged(self):
		sections = []
		self.secs.clear()
		for x in allLessons:
				if self.deps.currentText() == x.department and self.conums.currentText() == x.course and x.section not in sections:
					sections.append(x.section)
		self.secs.addItems(sections)
	def secsChanged(self):
		self.addLine.setText(self.deps.currentText() + self.conums.currentText() + '.' + self.secs.currentText())
class Lesson:
	def __init__ (self, name, days, slots):
		self.name = name
		self.days = days
		self.slots = slots
		self.department = ''
		self.course = ''
		self.section = ''

def update():
	global allLessons
	allLessons = []
	openFile = open('courses.html', 'w')
	soup = bs4.BeautifulSoup(urlopen("http://registration.boun.edu.tr/schedule.htm"), "html.parser")
	selected = soup.select('option')
	term = selected[0].get('value')
	soup = bs4.BeautifulSoup(urlopen("http://registration.boun.edu.tr/scripts/schdepsel.asp"), "html.parser")
	selected = soup.select('a[class="menu2"]')

	for i in selected:
		matchobj = re.match(r'(.*?)&(.*)',str(i.get('href')))
		if matchobj:
			newSoup = bs4.BeautifulSoup(urlopen('http://registration.boun.edu.tr' + matchobj.group(1) + term + '&' + matchobj.group(2)), "html.parser")
			lesson = newSoup.select('td')
			lesson = lesson[36:]
			for x in xrange(0,len(lesson),13):
				name = lesson[x].getText().replace(" ","").strip()
				days = lesson[x+6].getText().strip()
				slots = lesson[x+7].getText().strip()
				openFile.write(str(lesson[x]))
				openFile.write(str(lesson[x+6]))
				openFile.write(str(lesson[x+7]))
				allLessons.append(Lesson(name, days, slots))

	openFile.close()
	
	
	return

app = QApplication(sys.argv)
allLessons = []

if not os.path.isfile('courses.html'):
	#start splash
	splash_pix = QPixmap('./img/downloading.png')
	splash = QSplashScreen(splash_pix)
	splash.show()
	app.processEvents()

	update()

	#end splash
	splash.close()
	
else:
	splash_pix = QPixmap('./img/loading.png')
	splash = QSplashScreen(splash_pix)
	splash.show()
	app.processEvents()

	soup = bs4.BeautifulSoup(open("courses.html"), "html.parser")
	selected = soup.select('td')
	for x in xrange(0,len(selected),3):
		allLessons.append(Lesson(selected[x].getText().replace(" ","").strip(), selected[x+1].getText().strip(), selected[x+2].getText().strip()))

	time.sleep(3)
	splash.close()

departments = []
		
for x in allLessons:
	matchobj = re.match(r'([a-zA-Z]+)(.+)\.(.+)', x.name)
	if matchobj:
		x.department = matchobj.group(1)
		x.course = matchobj.group(2)
		x.section = matchobj.group(3)
		if matchobj.group(1) not in departments:
			departments.append(matchobj.group(1))



dialog = MyTable()
dialog.show()
sys.exit(app.exec_())