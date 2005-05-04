import sys

class CSV:
	def __init__(self, csvFileName, headerTypes):
		csvFile = open(csvFileName, 'r')
		self.read_headers(csvFile, headerTypes)
		self.read_main(csvFile)
		csvFile.close()

	def clean_up(self, itemName):
		'''
		Take in a string to remove whitespace, and if
		necessary quotes ie "Bob " -> Bob
		'''
		itemName = itemName.strip() #Remove whitespace
		
		return itemName
			
	def read_headers(self, csvFile, headerTypes):
		'''
		Read the headers in from "csvFile" file and create
		the "self.headers" list.
		'''
		line = csvFile.readline()
		headers = self._split_line(line)
		assert len(headerTypes) == len(headers), \
		       'Wrong number of header types (%d) to headers (%d)' % \
		       (len(headerTypes), len(headers))

		self.headers = []
		i = 0
		for headerName in headers:
			headerName = self.clean_up(headerName)
	                #afix type attribute to the header
			headerData = {'id': headerName,
				      'type': headerTypes[i]}	
			self.headers.append(headerData)
			i = i + 1
	
	def _split_line(self, line):
		import re
		fline = map(lambda x: x and x[0] or '',
			[filter(None, x)
				for x in
				re.findall('^\"(.*?)\"(?=,)|^(.*?)(?=,)|(?<=,)\"(.*?)\"(?=,)|(?<=,)\"(.*?)\"$|(?<=,)(.*?)(?=,)|(?<=,)(.*?)$',line.strip())])
		return fline

	def read_main(self, csvFile):
		self.mainData = []
		row = 0
		for line in csvFile.readlines():	
			data = self._split_line(line)
			assert len(data) == len(self.headers), \
				'csv data does not correspond to headers on row %s - %s' % (row, str(line))
			
			itemList = []
			column = 0
			for item in data:
				item = self.clean_up(item)
				try:
					#check the item type against header type.
					#Convert "blank" interger fields to "-1"
					if ((item == "") and (self.headers[column]['type'] == int)):
						itemList.append(-1)
					else:
						itemList.append(self.headers[column]['type'](item))
				except ValueError, e:
					msg = 'Could not convert "%s" to "%s"' %(str(item), str(self.headers[column]['type']))
					msg = '%s\n(%s: Row %d, Column %d)\n' %(msg, self.headers[column]['id'], row, column)
					sys.stderr.write(msg)
				column = column + 1

			#Check to see if the "cb_row" method exist, if it does then call it.,
			getattr(self, 'cb_row', lambda row: 1)(itemList) 
			
			self.mainData.append(itemList)
			row = row + 1
	
class CSVFile(CSV):
    def __init__(self, csvFile, headerTypes):
        self.read_headers(csvFile, headerTypes)
        self.read_main(csvFile)
