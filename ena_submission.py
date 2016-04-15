#!/usr/bin/env python

import os, os.path, sys, subprocess, glob, inspect

module_folder_paths = ["modules"]

for module_folder_path in module_folder_paths:
	module_folder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],module_folder_path)))
	if module_folder not in sys.path:
		sys.path.insert(1, module_folder)

import populate_data_to_ENA
import argparse
from argparse import RawTextHelpFormatter
import textwrap

class MultilineFormatter(argparse.HelpFormatter):
	# class to provide new lines when comments below are displayed in git.
    def _fill_text(self, text, width, indent):
		text = self._whitespace_matcher.sub(' ', text).strip()
		paragraphs = text.split('|n ')
		multiline_text = ''
		for paragraph in paragraphs:
		    formatted_paragraph = textwrap.fill(paragraph, width=500, initial_indent=indent, subsequent_indent=indent) + '\n\n'
		    multiline_text = multiline_text + formatted_paragraph
		return multiline_text


def set_up_argparse():
	parser = argparse.ArgumentParser(description="""

	**This tool in a single step will create the necessary xml files and uploads all your files to the ENA repository.**|n
	Description of the Process|n
	--------------------------|n
	In order to submit your files as a batch to ENA, you need to create some files that have information about your samples which then you can use to upload to ENA.  It can be a tedious task.  This script would make this possible in one step.  This is how it works (provided that you have provided the necessary files, see 'Required files' below):|n

	1- Creates a checksum file of all your files needed for submission.|n
	2- Uploads the files to the ENA server using FTP.  It will use the authentications you have provided it.|n
	3- Provided the data that you have provided is correct, the script will create five xml files: sample.xml, experiment.xml, run.xml, study.xml and submission.xml.|n
	4- If all the .xml files have been successfully created, the script will run a test curl command that will upload all the .xml files to the ENA server and returns a receipt.xml file.  If this process failes, you will be notified and you must correct the error and re-submit using the -curl option.  The script will run a test command to test if its sucessful. You must then run the production curl command to upload your data to production.|n


	Dependencies|n
	------------|n
	

	None.|n


	Required files|n
	--------------|n
Merge the remote changes before pushing again
	To upload your files to ENA, you will need the following:|n

	1- A directory which contains all your files (fwd and rev).  If you are uploading fastq files, the files must be in the following format:|n

	SAMPLE_NAME.R1.fastq.gz|n
	SAMPLE_NAME.R2.fastq.gz|n

	E.g. |n

	MN127.R1.fastq.gz|n
	MN127.R2.fastq.gz|n

	Otherwise, if you are uploading a different type of file, like bam files or fasta files, you can name them whatever you like but they should have the suffix at the end, e.g. .bam or .fasta|n

	2- A csv (comma separated values) file that contains all the information for each of your samples.  The text file should contain four required columns.  You may add as many coloumns of data as you wish after the fourth required coloumn.  The columns are separated by commas.  e.g. (note the headings are required and the order must be respected):|n

	SAMPLE,TAXON_ID,SCIENTIFIC_NAME,DESCRIPTION|n

	data....|n

	See a template file in the examples dir.|n

	3- A text file that contains the title for your project and an abstract explaining the project.  The two coloumns must be separated by TABS. There are no headings needed here. e.g.|n

	Bioinformatics for biologists \t Bioinformatics is great for biologists.....etc|n

	4- An ENA ftp username and password.  If you do not have one, you need to contact ENA at: datasubs@ebi.ac.uk.|n

	NOTE!! If you are uploading files other than fastq files, you must use the -F flag and add the suffix, e.g. -F bam.|n

	Before you run the script....|n

	-------------------|n

	Before you run the script, make sure you have the following ready as you cannot proceed without it:|n

	      -i : dir to your files|n
	      -r : a reference name for your project|n
	      -f : the path to the data file (see point 2 above)|n
	      -a : the path to the title and abstract text file|n
	      -o : the path to the output directory|n
	      -user : ENA username|n
	      -pass : ENA password|n

	You may like to familarise yourself with the other options you can use before running the script.|n


	Examples of commands|n
	--------------------|n

	So, what do you like to do? |n

	If you like to run a single command that does EVERYTHING, i.e. creates checksums, uploads your files to ftp, creates the xml files, uploads the xml files and run the curl command, then use the -d option, e.g. |n


	E.g. for fastq submission (otherwise use -F suffix)|n

	    python ena_submission.py -d -i /PATH/TO/SAMPLES_FILES_DIR -r phe_mycoplasma -f /PATH/TO/DATA_FILE.txt -o /PATH/TO/OUTPUT_DIR -a /PATH/TO/TITLE_ABSTRACT_FILE.txt -c CENTRE_NAME -user Webin-YYYYY -pass XXXXX|n

	
	Or you may wish to run each step individually. The following are examples of how to run each step individually:|n
	----|n

	To just create the checksums file:|n

	--create_checksums_file : only create the checksums file for my fastqs. e.g.|n
	    python ena_submission.py -cs -i /SOME/PATH/fastqs -r test3|n

	----|n

	To just upload your data to the ENA server:|n

	--upload_data_to_ena_ftp_server : only upload the data to ENA. e.g.|n
	    python ena_submission.py -ftp -i /SOME/PATH/fastqs -r phe_mycoplasma -user Webin-40432 -pass XXXXX|n

	----|n

	To just create sample.xml file:|n

	  -x sample : use the word 'sample' (same goes for the rest) to create sample.xml only. e.g.|n

	    python ena_submission.py -x sample -i /SOME/PATH/fastqs -r phe_mycoplasma -f /SOME/PATH/data_file_for_ena_submission.txt -c CENTRE_NAME -o /SOME/PATH/ena_submission|n

	----|n
	To just create experiment.xml file:|n

	  -x experiment : to create experiment.xml only. e.g.|n

	    python ena_submission.py -x experiment -i /SOME/PATH/fastqs -r phe_mycoplasma -f /SOME/PATH/data_file_for_ena_submission.txt -c CENTRE_NAME -o /SOME/PATH/ena_submission  |n
	----|n

	To just create run.xml file:|n

	  -x run : to create run.xml only. e.g.|n

	    python ena_submission.py -x run -i /SOME/PATH/fastqs -r phe_mycoplasma -c CENTRE_NAME -o /SOME/PATH/ena_submission|n
	----|n

	To just create study.xml file:|n
	  -x study : to create study.xml only. e.g.|n

	    python ena_submission.py -x study -a /SOME/PATH/title_and_abstract_for_ena.txt -r phe_mycoplasma -i /SOME/PATH/fastqs -c CENTRE_NAME -o /SOME/PATH/ena_submission|n

	----|n

	To just create submission.xml file:|n

	  -x submission : to create submission.xml only. e.g.|n

	    python ena_submission.py -x submission -i /SOME/PATH/fastqs -o /SOME/PATH/ena_submission -r phe_mycoplasma -c CENTRE_NAME |n

	  NOTE: Here you may hold your data from release publicly if you use -ho option and specify the date.|n

	----|n

	To just run the curl command:|n

	  -curl : just run curl command.  Note: you must have uploaded the data and created all the xml files to run the curl command. e.g.|n

	    python ena_submission.py -curl -user Webin-40432 -pass XXXX -o /SOME/PATH/ena_submission|n

	--------|n

	Contact|n
	-------|n

	Ali Al-Shahib|n
	ali.al-shahib@phe.gov.uk|n""", formatter_class=MultilineFormatter)

	# parser = argparse.ArgumentParser(epilog="Good luck! If your jobs breaks, don't blame me :-)", add_help=True)
	parser.add_argument('--do_everything', '-d', help='This option would run everything in one step, i.e: 1) Create checkums, 2) Uploads files to ENA ftp server, 3) Creats all the XML files, 4) Submits XML files to ENA (test only)',action='store_true')
	parser.add_argument('--generate_xml_file_for', '-x', help='please provide the name for the xml you like to generate, one of the following:experiment,run,sample,study,submission')
	parser.add_argument('--dir_of_input_data', '-i', help='please provide the path for the files you like to upload to ENA. NOTE: the fastq files must be in the following format: *.R1.fastq.gz and *.R2.fastq.gz.')
	parser.add_argument('--data_file', '-f', help='data_file, file : this text file must have at least four columns seperated by TABS in the following order and with the following headings:  Column 1: SAMPLE, Column 2: TAXON_ID, Column 3: SCIENTIFIC_NAME, Column 4: DESCRIPTION.  If you like to add further data then add it after the DESCRIPTION column.')
	parser.add_argument('--ftp_user_name', '-user', help='please provide the ftp user name')
	parser.add_argument('--ftp_password', '-pass', help='please provide the ftp password')
	parser.add_argument('--title_and_abstract_file', '-a', help='please provide the title and abstract text file.  This is needed to generate the study.xml file.  The file should be in the following format: full title of the project\tabstract')
	parser.add_argument('--center_name', '-c', help='Please provide the center name')
	parser.add_argument('--refname', '-r', help='Please provide the unique name for the whole submission. This name must not have been used before in any other submission to ENA.')
	parser.add_argument('--library_strategy', '-s', help='please provide the library strategy used. default = WGS', default='WGS')#
	parser.add_argument('--library_source', '-u', help='please provide the library source used. default = GENOMIC', default='GENOMIC')
	parser.add_argument('--library_selection', '-e', help='please provide the library selection used. default = RANDOM', default='RANDOM')
	parser.add_argument('--read_length', '-l', help='Please provide the read length. default = 100', default='100')
	parser.add_argument('--read_sdev', '-sdev', help='Please provide the read stdv. default = 0.0', default='0.0')
	parser.add_argument('--instrument_model', '-m', help='please provide the name of the instrument model used. default = Illumina HiSeq 2500', default='Illumina HiSeq 2500')
	parser.add_argument('--filetype', '-F', help='Please provide the file type, default=fastq', default='fastq')
	parser.add_argument('--hold_date', '-ho', help='This option will hold the data privately until a specified date.  Please provide the specified date using the following format: YYYY-MM-DD')
	parser.add_argument('--release', '-R', help='This option will release the data immediatley to the public domain. Cannot be used with --hold_date. default = False', default=False, action='store_true')
	parser.add_argument('--curl_command', '-curl', help='Run curl command to upload everything to ENA',action='store_true')
	parser.add_argument('--create_checksums_file', '-cs', help='Create a checksum file',action='store_true')
	parser.add_argument('--upload_data_to_ena_ftp_server', '-ftp', help='Upload data into the ftp server',action='store_true')
	parser.add_argument('--out_dir', '-o', help='please provide the path to the output directory which will include all the xml files.')
	opts = parser.parse_args()
	
	return opts

def check_if_flag_is_provided(flag,name,option):
	if flag is None:
		print "Checking if", name, "is provided...No!"
		print "You have not provided the", name,"!", "use the",option,"option to provide the", name
		sys.exit(1)
	else:
		print "Checking if", name, "is provided...Yes"

def main(opts):

	if opts.create_checksums_file:
		check_if_flag_is_provided(opts.refname,"refname","-r")
		check_if_flag_is_provided(opts.dir_of_input_data,"dir_of_input_data","-i")
		populate_data_to_ENA.create_checksums_file(opts.dir_of_input_data,opts.refname,opts.filetype)
		sys.exit()

	elif opts.upload_data_to_ena_ftp_server:
		check_if_flag_is_provided(opts.dir_of_input_data,"dir_of_input_data","-i")
		check_if_flag_is_provided(opts.refname,"refname","-r")
		check_if_flag_is_provided(opts.ftp_user_name, "ftp_user_name", "-user")
		check_if_flag_is_provided(opts.ftp_password, "ftp_password", "pass")
		populate_data_to_ENA.upload_data_to_ena_ftp_server(opts.dir_of_input_data,opts.refname,opts.ftp_user_name,opts.ftp_password,opts.filetype)
		sys.exit()

	elif opts.curl_command:
		check_if_flag_is_provided(opts.ftp_user_name, "ftp_user_name", "-user")
		check_if_flag_is_provided(opts.ftp_password, "ftp_password", "pass")
		check_if_flag_is_provided(opts.out_dir,"out_dir","-o")
		populate_data_to_ENA.run_curl_command(opts.ftp_user_name,opts.ftp_password,opts.out_dir)
		sys.exit()

	elif opts.do_everything:
		print "\nYou would like me to upload your files, generate all the xml files needed to submit your data to ENA, and upload the xml files to ENA.\nLet me check if you have provided all the necessary information....\n"
		# check if output file exists, otherwise create it...
		if not os.path.exists(opts.out_dir):
		    os.makedirs(opts.out_dir)
		check_if_flag_is_provided(opts.ftp_user_name, "ftp_user_name", "-user")
		check_if_flag_is_provided(opts.ftp_password, "ftp_password", "pass")
		check_if_flag_is_provided(opts.dir_of_input_data,"dir_of_input_data","-i")
		check_if_flag_is_provided(opts.center_name,"center_name","-c")
		check_if_flag_is_provided(opts.refname,"refname","-r")
		check_if_flag_is_provided(opts.data_file,"data_file","-f")
		check_if_flag_is_provided(opts.title_and_abstract_file,"title_and_abstract_file","-a")
		check_if_flag_is_provided(opts.out_dir,"out_dir","-o")

		populate_data_to_ENA.check_data_file(opts.data_file)
		populate_data_to_ENA.check_abstract_file(opts.title_and_abstract_file)
		populate_data_to_ENA.create_checksums_file(opts.dir_of_input_data,opts.refname,opts.filetype)
		populate_data_to_ENA.upload_data_to_ena_ftp_server(opts.dir_of_input_data,opts.refname,opts.ftp_user_name,opts.ftp_password,opts.filetype)
		populate_data_to_ENA.sample_xml(opts.dir_of_input_data,opts.refname,opts.data_file,opts.center_name,opts.out_dir)
		populate_data_to_ENA.experiment_xml(opts.dir_of_input_data,opts.data_file,opts.refname,opts.center_name,opts.library_strategy,opts.library_source,opts.library_selection,opts.read_length,opts.read_sdev,opts.instrument_model,opts.out_dir)
		populate_data_to_ENA.run_xml(opts.dir_of_input_data,opts.refname,opts.center_name,opts.filetype,opts.out_dir)
		populate_data_to_ENA.study_xml(opts.title_and_abstract_file,opts.center_name,opts.refname,opts.out_dir)
		populate_data_to_ENA.submission_xml(opts.refname,opts.center_name,opts.out_dir,opts.hold_date)

		print "\nAll your xml files have been generated successfully in", opts.out_dir, "\n"

		print "\nNow running curl command..."

		populate_data_to_ENA.run_curl_command(opts.ftp_user_name,opts.ftp_password,opts.out_dir)

		print "All done...Your files have been submitted to the ENA test server. please check if all the files have been uploaded to ENA."
		# print "All done...please check if all the files have been uploaded to ENA."

	elif opts.generate_xml_file_for == "sample":

		print "\nYou would like me to generate the", opts.generate_xml_file_for,".xml file needed to submit your data to ENA....\nLet me check if you have provided all the necessary information....\n"

		check_if_flag_is_provided(opts.dir_of_input_data,"dir_of_input_data","-i")
		check_if_flag_is_provided(opts.refname,"refname","-r")
		check_if_flag_is_provided(opts.center_name,"center_name","-c")
		check_if_flag_is_provided(opts.data_file,"data_file","-f")
		check_if_flag_is_provided(opts.out_dir,"out_dir","-o")	

		populate_data_to_ENA.check_data_file(opts.data_file)
		populate_data_to_ENA.sample_xml(opts.dir_of_input_data,opts.refname,opts.data_file,opts.center_name,opts.out_dir)

		print "\nYour", opts.generate_xml_file_for,".xml file have been generated successfully in", opts.out_dir

	elif opts.generate_xml_file_for == "experiment":

		print "\nYou would like me to generate the", opts.generate_xml_file_for, ".xml file needed to submit your data to ENA....\nLet me check if you have provided all the necessary information....\n"

		check_if_flag_is_provided(opts.dir_of_input_data,"dir_of_input_data","-i")
		check_if_flag_is_provided(opts.refname,"refname","-r")
		check_if_flag_is_provided(opts.center_name,"center_name","-c")
		check_if_flag_is_provided(opts.data_file,"data_file","-f")
		check_if_flag_is_provided(opts.out_dir,"out_dir","-o")

		populate_data_to_ENA.check_data_file(opts.data_file)
		populate_data_to_ENA.experiment_xml(opts.dir_of_input_data,opts.data_file,opts.refname,opts.center_name,opts.library_strategy,opts.library_source,opts.library_selection,opts.read_length,opts.read_sdev,opts.instrument_model,opts.out_dir)

		print "\nYour", opts.generate_xml_file_for,".xml file have been generated successfully in", opts.out_dir

	elif opts.generate_xml_file_for == "run":

		print "\nYou would like me to generate the", opts.generate_xml_file_for, ".xml file needed to submit your data to ENA....\nLet me check if you have provided all the necessary information....\n"

		check_if_flag_is_provided(opts.dir_of_input_data,"dir_of_input_data","-i")
		check_if_flag_is_provided(opts.refname,"refname","-r")
		check_if_flag_is_provided(opts.center_name,"center_name","-c")
		check_if_flag_is_provided(opts.out_dir,"out_dir","-o")

		populate_data_to_ENA.run_xml(opts.dir_of_input_data,opts.refname,opts.center_name,opts.filetype,opts.out_dir)

		print "\nYour", opts.generate_xml_file_for,".xml file have been generated successfully in", opts.out_dir

	elif opts.generate_xml_file_for == "study":
		
		print "\nYou would like me to generate the", opts.generate_xml_file_for, ".xml file needed to submit your data to ENA....\nLet me check if you have provided all the necessary information....\n"

		check_if_flag_is_provided(opts.refname,"refname","-r")
		check_if_flag_is_provided(opts.center_name,"center_name","-c")
		check_if_flag_is_provided(opts.title_and_abstract_file,"title_and_abstract_file","-a")
		check_if_flag_is_provided(opts.out_dir,"out_dir","-o")

		populate_data_to_ENA.study_xml(opts.title_and_abstract_file,opts.center_name,opts.refname,opts.out_dir)

		print "\nYour", opts.generate_xml_file_for,".xml file have been generated successfully in", opts.out_dir

	elif opts.generate_xml_file_for == "submission":
		
		print "\nYou would like me to generate the", opts.generate_xml_file_for, ".xml file needed to submit your data to ENA....\nLet me check if you have provided all the necessary information....\n"

		check_if_flag_is_provided(opts.refname,"refname","-r")
		check_if_flag_is_provided(opts.center_name,"center_name","-c")
		check_if_flag_is_provided(opts.out_dir,"out_dir","-o")

		populate_data_to_ENA.submission_xml(opts.refname,opts.center_name,opts.out_dir,opts.release,opts.hold_date)

		print "\nYour", opts.generate_xml_file_for,".xml file have been generated successfully in", opts.out_dir
	else:
		print "You need any help?  Use the -h option."


if __name__ == '__main__':
    opts = set_up_argparse()
    main(opts)