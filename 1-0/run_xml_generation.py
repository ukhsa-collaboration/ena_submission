import os, os.path, sys, subprocess, argparse, glob, inspect

module_folder_paths = ["modules"]

for module_folder_path in module_folder_paths:
	module_folder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],module_folder_path)))
	if module_folder not in sys.path:
		sys.path.insert(1, module_folder)

import populate_data_to_ENA

"""
We have set parser = argparse.ArgumentParser() and added all arguments by adding parser.add_argument.

"""

parser = argparse.ArgumentParser()

parser.add_argument('--xml_file', '-x', help='please provide the name for the xml you like to generate, one of the following:all,experiment,run,sample,study,submission')
parser.add_argument('--dir_of_input_data', '-i', help='please provide the path for the files you like to upload to ENA. NOTE: the fastq files must be in the following format: *.R1.fastq.gz and *.R2.fastq.gz.')
parser.add_argument('-data_file', '-f', help='data_file, file : this text file must have at least three columns seperated by tabs in the following order and with the following headings:  Column 1: SAMPLE, Column 2: TAXON_ID, Column 3: SCIENTIFIC_NAME, Column 4: DESCRIPTION.  If you like to add further data then add it after the DESCRIPTION column.')
parser.add_argument('--ftp_user_name', '-user', help='please provide the ftp user name')
parser.add_argument('--ftp_password', '-pass', help='please provide the ftp password')
parser.add_argument('--title_and_abstract_file', '-a', help='please provide the title and abstract text file.  This is needed to generate the study.xml file.  The file should be in the following format: full title of the project\tabstract')
parser.add_argument('--center_name', '-c', help='Please provide the center name', default="PHE")
parser.add_argument('--refname', '-r', help='Please provide the unique name for the whole submission. This name must not have been used before in any other submission to ENA.')
parser.add_argument('--library_strategy', '-s', help='please provide the library strategy used', default='WGS')#
parser.add_argument('--library_source', '-u', help='please provide the library source used', default='GENOMIC')
parser.add_argument('--library_selection', '-e', help='please provide the library selection used', default='RANDOM')
parser.add_argument('--read_length', '-l', help='Please provide the read length', default='100')
parser.add_argument('--read_sdev', '-sdev', help='Please provide the read stdv', default='0.0')
parser.add_argument('--instrument_model', '-m', help='please provide the name of the instrument model used', default='Illumina HiSeq 2500')
parser.add_argument('--filetype', '-F', help='Please provide the file type', default='fastq')
# parser.add_argument('--center_project_name', '-p', help='Give the study a project name.  This is needed for the study.xml file', default='PHE_SCIENTIFIC_PROJECT')
# parser.add_argument('--suffix', '-suffix', help='Please provide the suffix of your files. Note: your suffix must contain R1 in it, e.g. prefix.R1.fastq.gz', default='R1.fastq.gz')
parser.add_argument('--hold_date', '-ho', help='This option will hold the data privately until a specified date.  Please provide the specified date using the following format: YYYY-MM-DD')
parser.add_argument('--release', '-R', help='This option will release the data immediatley to the public domain. Cannot be used with --hold_date', default=False, action='store_true')
parser.add_argument('--curl_command', '-curl', help='Run curl command to upload everything to ENA',action='store_true')
parser.add_argument('--create_checksums_file', '-cs', help='Create a checksum file',action='store_true')
parser.add_argument('--upload_data_to_ena_ftp_server', '-ftp', help='Upload data into the ftp server',action='store_true')
parser.add_argument('--out_dir', '-o', help='please provide the path to the output directory which will include all the xml files.')
opts = parser.parse_args()


def check_if_flag_is_provided(flag,name,option):
	if flag is None:
		print "Checking if", name, "is provided...No!"
		print "You have not provided the", name,"!", "use the",option,"option to provide the", name
		sys.exit(1)
	else:
		print "Checking if", name, "is provided...Yes"

def main():

	if opts.create_checksums_file:
		populate_data_to_ENA.create_checksums_file(opts.dir_of_input_data,opts.refname)
		sys.exit()

	elif opts.upload_data_to_ena_ftp_server:
		populate_data_to_ENA.upload_data_to_ena_ftp_server(opts.dir_of_input_data,opts.refname,opts.ftp_user_name,opts.ftp_password)
		sys.exit()

	elif opts.curl_command:
		populate_data_to_ENA.run_curl_command(opts.ftp_user_name,opts.ftp_password,opts.out_dir)
		sys.exit()

	elif not opts.xml_file:
		print("\n-x flag not provided! You must supply which xml file(s) you like to generate. options are all,sample,experiment,run,study,submission.\n\n")
		print parser.print_help()
		sys.exit()

	elif not opts.dir_of_input_data:
		print("\nYou must supply a path to the data you like to upload to ENA. Use -i flag\n\n")
		print parser.print_help()
		sys.exit(1)

	else:

		if opts.xml_file == "all":
			print "\nYou would like me to generate all the xml files needed to submit your data to ENA....\nLet me check if you have provided all the necessary information....\n"

			check_if_flag_is_provided(opts.ftp_user_name, "ftp_user_name", "-user")
			check_if_flag_is_provided(opts.ftp_password, "ftp_password", "pass")
			check_if_flag_is_provided(opts.dir_of_input_data,"dir_of_input_data","-i")
			check_if_flag_is_provided(opts.refname,"refname","-r")
			check_if_flag_is_provided(opts.data_file,"data_file","-f")
			check_if_flag_is_provided(opts.title_and_abstract_file,"title_and_abstract_file","-a")
			# check_if_flag_is_provided(opts.center_project_name,"center_project_name","-p")
			check_if_flag_is_provided(opts.out_dir,"out_dir","-o")

			populate_data_to_ENA.create_checksums_file(opts.dir_of_input_data,opts.refname)
			populate_data_to_ENA.upload_data_to_ena_ftp_server(opts.dir_of_input_data,opts.refname,opts.ftp_user_name,opts.ftp_password)
			populate_data_to_ENA.sample_xml(opts.dir_of_input_data,opts.refname,opts.data_file,opts.center_name,opts.out_dir)
			populate_data_to_ENA.experiment_xml(opts.dir_of_input_data,opts.data_file,opts.refname,opts.center_name,opts.library_strategy,opts.library_source,opts.library_selection,opts.read_length,opts.read_sdev,opts.instrument_model,opts.out_dir)
			populate_data_to_ENA.run_xml(opts.dir_of_input_data,opts.refname,opts.center_name,opts.filetype,opts.out_dir)
			populate_data_to_ENA.study_xml(opts.title_and_abstract_file,opts.center_name,opts.refname,opts.out_dir)
			populate_data_to_ENA.submission_xml(opts.refname,opts.center_name,opts.out_dir,opts.hold_date)

			print "\nAll your xml files have been generated successfully in", opts.out_dir, "\n"

			print "\nNow running curl command..."

			populate_data_to_ENA.run_curl_command(opts.ftp_user_name,opts.ftp_password,opts.out_dir)

			print "All done...please check if all the files have been uploaded to ENA."

		elif opts.xml_file == "sample":

			print "\nYou would like me to generate the", opts.xml_file,".xml file needed to submit your data to ENA....\nLet me check if you have provided all the necessary information....\n"

			check_if_flag_is_provided(opts.dir_of_input_data,"dir_of_input_data","-i")
			check_if_flag_is_provided(opts.refname,"refname","-r")
			check_if_flag_is_provided(opts.data_file,"data_file","-f")
			check_if_flag_is_provided(opts.out_dir,"out_dir","-o")	

			populate_data_to_ENA.sample_xml(opts.dir_of_input_data,opts.refname,opts.data_file,opts.center_name,opts.out_dir)

			print "\nYour", opts.xml_file,".xml file have been generated successfully in", opts.out_dir

		elif opts.xml_file == "experiment":

			print "\nYou would like me to generate the", opts.xml_file, ".xml file needed to submit your data to ENA....\nLet me check if you have provided all the necessary information....\n"

			check_if_flag_is_provided(opts.dir_of_input_data,"dir_of_input_data","-i")
			check_if_flag_is_provided(opts.refname,"refname","-r")
			check_if_flag_is_provided(opts.data_file,"data_file","-f")
			check_if_flag_is_provided(opts.out_dir,"out_dir","-o")

			populate_data_to_ENA.experiment_xml(opts.dir_of_input_data,opts.data_file,opts.refname,opts.center_name,opts.library_strategy,opts.library_source,opts.library_selection,opts.read_length,opts.read_sdev,opts.instrument_model,opts.out_dir)

			print "\nYour", opts.xml_file,".xml file have been generated successfully in", opts.out_dir

		elif opts.xml_file == "run":

			print "\nYou would like me to generate the", opts.xml_file, ".xml file needed to submit your data to ENA....\nLet me check if you have provided all the necessary information....\n"

			check_if_flag_is_provided(opts.dir_of_input_data,"dir_of_input_data","-i")
			check_if_flag_is_provided(opts.refname,"refname","-r")
			check_if_flag_is_provided(opts.out_dir,"out_dir","-o")

			populate_data_to_ENA.run_xml(opts.dir_of_input_data,opts.refname,opts.center_name,opts.filetype,opts.out_dir)

			print "\nYour", opts.xml_file,".xml file have been generated successfully in", opts.out_dir

		elif opts.xml_file == "study":
			
			print "\nYou would like me to generate the", opts.xml_file, ".xml file needed to submit your data to ENA....\nLet me check if you have provided all the necessary information....\n"

			check_if_flag_is_provided(opts.refname,"refname","-r")
			check_if_flag_is_provided(opts.title_and_abstract_file,"title_and_abstract_file","-a")
			# check_if_flag_is_provided(opts.center_project_name,"center_project_name","-p")
			check_if_flag_is_provided(opts.out_dir,"out_dir","-o")

			populate_data_to_ENA.study_xml(opts.title_and_abstract_file,opts.center_name,opts.refname,opts.out_dir)

			print "\nYour", opts.xml_file,".xml file have been generated successfully in", opts.out_dir

		elif opts.xml_file == "submission":
			
			print "\nYou would like me to generate the", opts.xml_file, ".xml file needed to submit your data to ENA....\nLet me check if you have provided all the necessary information....\n"

			check_if_flag_is_provided(opts.refname,"refname","-r")
			check_if_flag_is_provided(opts.out_dir,"out_dir","-o")

			populate_data_to_ENA.submission_xml(opts.refname,opts.center_name,opts.out_dir,opts.release,opts.hold_date)

			print "\nYour", opts.xml_file,".xml file have been generated successfully in", opts.out_dir

main()