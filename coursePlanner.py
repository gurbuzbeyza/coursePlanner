#!/usr/bin/env python
import requests, bs4, re, sys, os.path
from PyQt4.QtCore import *
from PyQt4.QtGui import * 
from urllib2 import urlopen
class MyTable(QDialog):
	def __init__(self, parent = None):
		super(MyTable, self).__init__(parent)
		self.mainlayout = QVBoxLayout()
		self.layout = QGridLayout()
		self.table = QTableWidget()
		self.table.setRowCount(5)
		self.table.setColumnCount(9)
		horHeaders = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
		verHeaders = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
		self.table.setHorizontalHeaderLabels(horHeaders)
		self.table.setVerticalHeaderLabels(verHeaders)
		self.addLine = QLineEdit('Add Course')
		self.removeLine = QLineEdit('Remove Course')
		self.addButton = QPushButton('Add Course')
		self.removeButton = QPushButton('Remove Course')
		self.upload = QPushButton('Upload')
		self.mainlayout.addWidget(self.table)
		self.layout.addWidget(self.addButton, 0, 0)
		self.layout.addWidget(self.addLine, 0, 1)
		self.layout.addWidget(self.removeButton, 1, 0)
		self.layout.addWidget(self.removeLine, 1, 1)
		self.mainlayout.addLayout(self.layout)  
		self.mainlayout.addWidget(self.upload)  
		self.setLayout(self.mainlayout) 
		self.connect(self.addButton, SIGNAL("clicked()"), self.addClick)
		self.connect(self.removeButton, SIGNAL("clicked()"), self.removeClick)
		self.connect(self.upload, SIGNAL("clicked()"), uploadClick)
		self.table.resizeColumnsToContents()
		self.table.resizeRowsToContents()
		self.table.setFixedSize(self.table.horizontalHeader().length()+100, self.table.verticalHeader().length()+30)
		self.setWindowTitle('Course Planner for BOUN Students')
	def addClick(self):
		course = self.addLine.text()
		for i in allLessons:
			if course == i.name:
				self.parse(i)
				break
	def removeClick(self):
		course = self.removeLine.text()
		for x in xrange(0,5):
			for y in xrange(0,9):
				if self.table.item(x,y) != None:
					if self.table.item(x,y).text() == course:
						newitem = QTableWidgetItem('')		
					elif course + '/' in self.table.item(x,y).text():
						newitem = QTableWidgetItem(self.table.item(x,y).text().replace(course + '/',''))		
					elif '/' + course in self.table.item(x,y).text():
						newitem = QTableWidgetItem(self.table.item(x,y).text().replace('/' + course,''))
					else:
						newitem = QTableWidgetItem(self.table.item(x,y).text())
					self.table.setItem(x, y, newitem)
		self.table.resizeColumnsToContents()
		self.table.resizeRowsToContents()  
		self.table.setFixedSize(self.table.horizontalHeader().length()+100, self.table.verticalHeader().length()+30)
		return

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
				newitem = QTableWidgetItem(self.table.item(x-1, y-1).text() + '/' + less.name)
				self.table.setItem(x-1, y-1, newitem)
			else:	
				newitem = QTableWidgetItem(less.name)			
				self.table.setItem(x-1, y-1, newitem)
			self.table.resizeColumnsToContents()
			self.table.resizeRowsToContents()
			self.table.setFixedSize(self.table.horizontalHeader().length()+100, self.table.verticalHeader().length()+30)   
		
class Lesson:
	def __init__ (self, name, days, slots):
		self.name = name
		self.days = days
		self.slots = slots

def uploadClick():
	global allLessons
	allLessons = []
	openFile = open('courses.html', 'w')
	soup = bs4.BeautifulSoup(urlopen("http://registration.boun.edu.tr/scripts/schdepsel.asp"), "html.parser")
	selected = soup.select('a[class="menu2"]')

	for i in selected:
		matchobj = re.match(r'(.*?)&(.*)',str(i.get('href')))
		if matchobj:
			newSoup = bs4.BeautifulSoup(urlopen('http://registration.boun.edu.tr' + matchobj.group(1) + '2016/2017-2&' + matchobj.group(2)), "html.parser")
			lesson = newSoup.select('td')
			lesson = lesson[37:]
			for x in xrange(0,len(lesson),14):
				name = lesson[x].getText().replace(" ","").strip()
				days = lesson[x+7].getText().strip()
				slots = lesson[x+8].getText().strip()
				openFile.write(str(lesson[x]))
				openFile.write(str(lesson[x+7]))
				openFile.write(str(lesson[x+8]))
				allLessons.append(Lesson(name, days, slots))

	openFile.close()
	return

allLessons = []

if not os.path.isfile('courses.html'):
	uploadClick()
	
else:
	soup = bs4.BeautifulSoup(open("courses.html"), "html.parser")
	selected = soup.select('td')
	for x in xrange(0,len(selected),3):
		allLessons.append(Lesson(selected[x].getText().replace(" ","").strip(), selected[x+1].getText().strip(), selected[x+2].getText().strip()))
		


app = QApplication(sys.argv)
dialog = MyTable()
dialog.show()
sys.exit(app.exec_())