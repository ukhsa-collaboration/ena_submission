import sys
data_file = '/home/ali/sophia_xml_files/ENA_submission_ST1s.csv'
meta_data_file = file(data_file, 'r')

# with open(data_file, 'U') as infile:
# 	text = infile.read()
data_file_heading = ['SAMPLE', 'TAXON_ID', 'SCIENTIFIC_NAME', 'DESCRIPTION']
for lineNum, line in enumerate(meta_data_file):
	print lineNum,line
	if lineNum == 0:
		headings_stripped = line.strip()
		headings = headings_stripped.split(',')
		# if the data_file_heading list has the heading in the data_file 
		if set(headings).issuperset(set(data_file_heading)):
			# Now compare the order...
			if headings[0] == data_file_heading[0] and headings[1] == data_file_heading[1] and headings[2] == data_file_heading[2] and headings[3] == data_file_heading[3]:
				print "Checking if data_file header order is correct....Yes"
			else:
				print "ERROR: The ORDER of the headers in the "+data_file+" file is incorrect.  You must have the following order: SAMPLE,TAXON_ID,SCIENTIFIC_NAME,DESCRIPTION."
				sys.exit()
		else:
			print "ERROR: The headers in the "+data_file+" file are incorrect.  You must have the following data headers: SAMPLE,TAXON_ID,SCIENTIFIC_NAME,DESCRIPTION."
			sys.exit()