#!/usr/bin/env python

'''
populate_data_to_ENA.py


AAlShahib_Aug_2015

'''
import xml.etree.cElementTree as ET
from xml.dom import minidom
import csv
import sys
import hashlib
import glob
import os
import ftplib
import subprocess


def check_file_exists(filepath, file_description):
    """
	A function to check if a file exists.
	It will print out an error message and exit if the file is not found

	Params
	----------
	filepath : String
	    the path to the file to be checked
	file_description : String
	    a description of the file to be checked e.g "config file"
	"""
    if not os.path.exists(filepath):
        print("The " + file_description + " (" + filepath + ") does not exist")
        sys.exit(1)


def check_data_file(data_file):
    """
	A function to check whether the data input file is in the right format or not.

	Params
    ------
    data_file, str: file (as a path) containing the meta data for the project.

    return
    ------
    None


	"""
    meta_data_file = file(data_file, 'U')
    # the data file should have this heading...
    data_file_heading = ['SAMPLE', 'TAXON_ID', 'SCIENTIFIC_NAME', 'DESCRIPTION']
    for lineNum, line in enumerate(meta_data_file):
        if lineNum == 0:
            headings_stripped = line.strip()
            headings = headings_stripped.split('\t')
            # if the data_file_heading list has the heading in the data_file
            if set(headings).issuperset(set(data_file_heading)):
                # Now compare the order...
                if headings[0] == data_file_heading[0] and headings[1] == data_file_heading[1] and headings[2] == \
                        data_file_heading[2] and headings[3] == data_file_heading[3]:
                    print "Checking if data_file header order is correct....Yes"
                else:
                    print "ERROR: The ORDER of the headers in the " + data_file + " file is incorrect.  You must have the following order: SAMPLE,TAXON_ID,SCIENTIFIC_NAME,DESCRIPTION."
                    sys.exit()
            else:
                print "ERROR: The headers in the " + data_file + " file are incorrect.  You must have the following data headers: SAMPLE,TAXON_ID,SCIENTIFIC_NAME,DESCRIPTION."
                sys.exit()


def check_abstract_file(title_and_abstract_file):
    '''
	check_abstract_file(title_and_abstract_file)

	A function to check whether the title and abstract function is in the correct format.


	Params
    ------
    title_and_abstract_file, str: file (as a path) containing title and abstract of the project.

    return
    ------
    None

	'''
    try:
        with open(title_and_abstract_file, 'U') as f:
            lines = f.readlines()
            for line in lines:
                cols = line.decode('utf-8').strip().split('\t')
                title = cols[0]
                abstract = cols[1]
        print "Checking if title and abstract file is in the correct format....Yes"
    except:
        print "Something is wrong with the title and abstract file " + title_and_abstract_file + ". It should have a title with a tab separator and abstract.  The file should only have one line. Please check and re-submit."
        sys.exit()


def rchop(string, ending):
    """
    This function removes the ending of a string

    Parameters
    ----------
    string : str
        String from which the ending part will be removed, e.g. 'sample_1.fastq.gz'
    ending : str
        Ending part of the string to be removed, e.g. '_1.fastq.gz'

    Returns
    -------
    string : str
        The original string without the ending part, e.g. 'sample'
    """
    if string.endswith(ending):
        string = string[:-len(ending)]
    return string


def create_checksums_file(dir_of_input_data, refname, filetype, fastq_ends):
    '''
	create_checksums_file(dir_of_input_data,refname)

	This function creates the checksum file of all the files to be submitted to ENA.  The fastq files MUST begin with the sample name and end with R1.fastq.gz or R2.fastq.gz and must be seperated by dots, e.g. my_sample.whatever.R1.fastq.gz

	Params
    ------
    dir_of_input_data, dir: This is the directory that contains all the files to be uploaded to ENA.  NOTE: the fastq files must be in the following format: *.R1.fastq.gz and *.R2.fastq.gz.
    refname, str: You must provide a reference name for your study, e.g. phe_ecoli
    filetype, str: Type of files to submit, e.g. 'fastq'
    fastq_ends, tuple: Tuple of strings of size 2 with fastq files end, e.g. ('.R1.fastq.gz', '.R2.fastq.gz')

    return
    ------

    checksums_file, file : a checksum file will be created in the dir_of_input_data directory.  It would be called: refname_"checksums.md5".

	'''
    try:
        if filetype == "fastq":
            files = glob.glob(dir_of_input_data + "/*" + fastq_ends[0])
            num_files = len(files) * 2
        else:
            files = glob.glob(dir_of_input_data + "/" + "*." + filetype)
            num_files = len(files)

        if not files:
            print "The files in " + dir_of_input_data + " do not match the prefix.  Please check and try again. Note: if you are uploading other than fastq files please use the -F option to specify the prefix of your files, e.g. -F bam."
            sys.exit()

        # find out if checksums has already been done first
        if not os.path.exists(dir_of_input_data + '/' + refname + '_checksums.md5'):
            checksums_file = open(dir_of_input_data + '/' + refname + '_checksums.md5', "w")

            print "creating checksums....."
            for file in files:
                (SeqDir, seqFileName_R1) = os.path.split(file)
                # get the sample name
                if filetype == "fastq":
                    sample_name = rchop(seqFileName_R1, fastq_ends[0])
                else:
                    sample_name = seqFileName_R1.split('.')[0]
                checksum_main = hashlib.md5(open(file, 'rb').read()).hexdigest()
                checksums_file.write(checksum_main + " " + seqFileName_R1 + "\n")
                if filetype == "fastq":
                    read_2_file = ''.join(glob.glob(SeqDir + "/" + sample_name + fastq_ends[1]))
                    checksum_read2 = hashlib.md5(open(read_2_file, 'rb').read()).hexdigest()
                    (SeqDir, seqFileName_R2) = os.path.split(read_2_file)
                    checksums_file.write(checksum_read2 + " " + seqFileName_R2 + "\n")
            print "created checksums file.  It's located in " + dir_of_input_data + '/' + refname + '_checksums.md5'
        else:
            num_lines_in_checksums_file = sum(1 for line in open(dir_of_input_data + '/' + refname + '_checksums.md5'))

            if num_lines_in_checksums_file == num_files:
                print "\nChecksums file has already been generated and fully populated!"
    except IOError:
        print "ERROR: Something has gone wrong with creating the checksums file.  Please check and re-submit."
        sys.exit()


def upload_data_to_ena_ftp_server(dir_of_input_data, refname, ftp_user_name, ftp_password, filetype, fastq_ends):
    '''
	upload_data_to_ena_ftp_server(dir_of_input_data,refname,ftp_user_name,ftp_password)

	This function uploads the data to the ena ftp server.

	Params
    ------
    dir_of_input_data, dir: This is the directory that contains all the files to be uploaded to ENA.  NOTE: the fastq files must be in the following format: *.R1.fastq.gz and *.R2.fastq.gz.
    refname, str: You must provide a reference name for your study, e.g. phe_ecoli
    ftp_user_name, str: You must provide your ENA ftp username, e.g. Webin-40432
    ftp_password, str: You must provide your ENA ftp password
    fastq_ends, tuple: Tuple of strings of size 2 with fastq files end, e.g. ('.R1.fastq.gz', '.R2.fastq.gz')

    return
    ------
	
	None

	'''

    try:
        print "\nconnecting to ftp.webin.ebi.ac.uk...."
        ftp = ftplib.FTP("webin.ebi.ac.uk", ftp_user_name, ftp_password)
    except IOError:
        print(ftp.lastErrorText())
        print "ERROR: could not connect to the ftp server.  Please check your login details."
        sys.exit()

    # print ftp.sendcmd('SITE CHMOD 644 ' + ftp.cwd())
    print "\nSuccess!\n"

    try:
        if refname in ftp.nlst():
            print refname, "directory in ftp already exists....OK no problem..."
            ftp.cwd(str(refname))
        else:
            print "\nmaking new directory in ftp called", refname
            ftp.mkd(str(refname))
            ftp.cwd(str(refname))

        check_file_exists(dir_of_input_data + '/' + refname + '_checksums.md5', 'checksum_file')
        checksum_file = open(dir_of_input_data + '/' + refname + '_checksums.md5', 'rb')  # file to send

        print "\nuploading checksum file to ENA ftp server in the", refname, "directory\n"

        ftp.storbinary('STOR ' + refname + '_checksums.md5', checksum_file)  # send the file
        checksum_file.close()
    except IOError:
        print "ERROR: could not find the checksum file.  I'm looking for", dir_of_input_data + '/' + refname + '_checksums.md5'
        sys.exit()

    print "Now uploading all the data to ENA ftp server in the", refname, "directory\n"

    # added a while loop so if ftp fails it can try again.
    # print ftplib.FTP.dir(ftp)
    # ftp.cwd(str(refname))

    for i in range(0, 3):
        try:
            if filetype == "fastq":
                files = [os.path.join(dir_of_input_data, f) for f in os.listdir(dir_of_input_data)
                         if not f.startswith('.')
                         and os.path.isfile(os.path.join(dir_of_input_data, f))
                         and f.endswith(fastq_ends)]
            else:
                files = glob.glob(dir_of_input_data + "/" + "*." + filetype)

            for file in files:

                (SeqDir, seqFileName) = os.path.split(file)
                # if the sample has already been uploaded, check the file size number. If its the same as the dir file size then move on otherwise upload it again.
                if seqFileName in ftp.nlst():
                    fileSize_in_ftp = ftp.size(seqFileName)
                    fileSize_in_dir = os.path.getsize(str(file))
                    if fileSize_in_dir != fileSize_in_ftp:
                        print seqFileName + " is uploaded but not all of it so uploading it again now to ENA ftp server.\n"
                        ftp.storbinary('STOR ' + seqFileName, open(file, 'rb'))
                    else:
                        print seqFileName + " has already been uploaded.\n"
                else:
                    print "uploading", file, "to ENA ftp server.\n"
                    ftp.storbinary('STOR ' + seqFileName, open(file, 'rb'))
            break
        except Exception as e:
            print(e)
            print "Something went wrong with ftp, lets try again...."
    else:
        print "Oops! something has gone wrong while uploading data to the ENA ftp server!"
        sys.exit()

    ftp.quit()


def indent(elem, level=0):
    '''
	indent(elem, level=0)

	This function indents the xml files to the appropriate indentations.

	Params
    ------
    elem, ET.Element object.

    return
    ------
	
	ET.Element object: indented ET.Element object.

	'''

    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def create_dict_with_data(dir_of_input_data, refname, data_file, fastq_ends, header=True):
    '''
	create_dict_with_data(dir_of_input_data,refname,data_file)

	This function uses the data file provided and creates a dictionary to be used to create some xml files. The order of the rows is respected.

	Params
	------
	dir_of_input_data, dir: This is the directory that contains all the files to be uploaded to ENA.  NOTE: the fastq files must be in the following format: *.R1.fastq.gz and *.R2.fastq.gz.
	refname, str: You must provide a reference name for your study, e.g. phe_ecoli
	data_file, file : this csv file must have at least three columns seperated by commas in the following order and with the following headings:  Column 1: SAMPLE, Column 2: TAXON_ID, Column 3: SCIENTIFIC_NAME, Column 4: DESCRIPTION.  If you like to add further data then add it after the DESCRIPTION column.
	header, True or False :  if True the first line will be considered a header line
    fastq_ends, tuple: Tuple of strings of size 2 with fastq files end, e.g. ('.R1.fastq.gz', '.R2.fastq.gz')


	return
	------

	sample_id_and_data, dict : a dictionary that has the headings as keys and the data as values.

	'''

    meta_data_file = file(data_file, 'U')
    cols = {}
    indexToName = {}

    with open(dir_of_input_data + '/' + refname + '_checksums.md5', 'rb') as f:
        sample_id_and_data = []
        for line in f:
            line = line.split()[1]
            for fastq_end in fastq_ends:
                sample_name = rchop(line, fastq_end)
                if len(sample_name) < len(line):
                    sample_id_and_data.append(sample_name)
                    break
        # values are nil at the moment as we will populate them only if there is a data_file provided.
        # sample_id_and_data[str(sample_name_split[0])] = ""

    strain_names = set(sample_id_and_data)

    for lineNum, line in enumerate(meta_data_file):
        if lineNum == 0:
            headings = line.split('\t')
            i = 0
            for heading in headings:
                heading = heading.strip()
                if header:
                    cols[heading] = []
                    indexToName[i] = heading
                else:
                    # in this case the heading is actually just a cell
                    cols[i] = [heading]
                    indexToName[i] = i
                i += 1
        else:
            strip_line = line.strip()
            # cells is a list of each of the lines in the data file, e.g. ['ST38_21', '562', 'Escherichia coli', 'OXA-48 producer', 'North West_3', '28_2014']
            cells = strip_line.split('\t')
            x = 0
            # if the sample name (cells[0]) is in the strain names obtained from the checksums file then add to dict cols
            if cells[0] in strain_names:
                try:
                    for cell in cells:
                        cell = cell.rstrip()
                        # indexToName[i] is the header name index
                        cols[indexToName[x]] += [cell]
                        x += 1
                except EOFError:
                    print "ERROR: something is wrong with the " + data_file + " file."
            else:
                msg = 'ERROR: {sample} from the {data_file} is not equivalent to samples name you have labelled your' \
                      ' sequecing files in:\n' \
                      '{samples_files}'.format(sample=cells[0], data_file=data_file,
                                               samples_files='\n'.join(strain_names))
                sys.exit(msg)
    return cols


def sample_xml(dir_of_input_data, refname, data_file, center_name, out_dir, fastq_ends):
    '''
	create_checksums_file(dir_of_input_data,refname)

	This function creates the checksum file of all the files to be submitted to ENA.

	Params
    ------
    dir_of_input_data, dir: This is the directory that contains all the files to be uploaded to ENA.
    data_file, file : this text file must have at least three columns seperated by commas in the following order and with the following headings:  Column 1: SAMPLE, Column 2: TAXON_ID, Column 3: SCIENTIFIC_NAME, Column 4: DESCRIPTION.  If you like to add further data then add it after the DESCRIPTION column.
    refname, str: You must provide a reference name for your study, e.g. phe_ecoli
    center_name, str : name of the center, e.g. PHE
    taxon_id, str : the taxon id of the organism from NCBI
    out_dir, str : path to the output directory where all the xml files will be added.
    fastq_ends, tuple: Tuple of strings of size 2 with fastq files end, e.g. ('.R1.fastq.gz', '.R2.fastq.gz')

    return
    ------

    outfile, file : a sample xml file needed for ENA submission.

 	'''

    sample_id_and_data = create_dict_with_data(dir_of_input_data, refname, data_file, fastq_ends)
    if set(('SAMPLE', 'TAXON_ID', 'SCIENTIFIC_NAME', 'DESCRIPTION')) <= set(sample_id_and_data):
        sample_set = ET.Element('SAMPLE_SET')
        sample_scientific_name_description = set(['SAMPLE', 'TAXON_ID', 'SCIENTIFIC_NAME', 'DESCRIPTION'])
        all_keys_in_a_lits = set(sample_id_and_data.keys())
        remaining_keys = all_keys_in_a_lits - sample_scientific_name_description

        for index, sample_name in enumerate(sample_id_and_data["SAMPLE"]):
            for key in sample_scientific_name_description:
                field = []
                field.append(sample_id_and_data[key][index])
                # begin with indentation of the xml file.  start with sample...
                if key == "SAMPLE":
                    sample = ET.SubElement(sample_set, 'SAMPLE', alias=''.join(field), center_name=center_name)
                    # and then title
                    title = ET.SubElement(sample, "TITLE").text = ''.join(field)
                    sample_name = ET.SubElement(sample, "SAMPLE_NAME")
                # for below only use if you want to update and have isolate ena number
                # scientific and description are optional.  If they included in the data_file then they will be populated, otherwise they will be left empty.
                elif key == "TAXON_ID":
                    taxon = ET.SubElement(sample_name, "TAXON_ID").text = ''.join(field)

                elif key == "SCIENTIFIC_NAME":
                    scientific = ET.SubElement(sample_name, "SCIENTIFIC_NAME").text = ''.join(field)

                elif key == "DESCRIPTION":
                    desc = ET.SubElement(sample, "DESCRIPTION").text = ''.join(field)

            # only add sample attributes if required
            if len(remaining_keys) > 0:
                sample_attributes = ET.SubElement(sample, "SAMPLE_ATTRIBUTES")

                for key in remaining_keys:
                    field = []
                    field.append(sample_id_and_data[key][index])
                    # for below only use if you want to update and have isolate ena number
                    sample_attribute = ET.SubElement(sample_attributes, "SAMPLE_ATTRIBUTE")
                    # tag = ET.SubElement(sample_attribute, "TAG").text = "SAMPLE"
                    # value = ET.SubElement(sample_attribute, "VALUE").text = str(sample_name)
                    tag = ET.SubElement(sample_attribute, "TAG").text = str(key)
                    value = ET.SubElement(sample_attribute, "VALUE").text = ''.join(field)
                # use the indent function to indent the xml file
    else:
        print "ERROR: The " + data_file + " file does not contain one of the following fields: SAMPLE, TAXON_ID, SCIENTIFIC_NAME, DESCRIPTION. Please add the relevant field to proceed...."
        sys.exit(1)
    # print sample_id_and_data
    indent(sample_set)
    # create tree
    tree = ET.ElementTree(sample_set)

    # out_dirput to outfile
    with open(out_dir + "/sample.xml", 'w') as outfile:
        tree.write(outfile, xml_declaration=True, encoding='utf-8', method="xml")

    print "\nSuccessfully created sample.xml file\n"


def experiment_xml(dir_of_input_data, data_file, refname, center_name, library_strategy, library_source,
                   library_selection, read_length, read_sdev, instrument_model, fastq_ends, out_dir=""):
    '''
	experiment_xml(dir_of_input_data,data_file,refname,center_name,library_strategy,library_source,library_selection,read_length,read_sdev,instrument_model,out_dir=""):
	This function generates a experiment xml file needed for submission of data to ENA.  It will contain a subelement for each sample provided in the data_file.

	Params
	------
	dir_of_input_data, dir: This is the directory that contains all the files to be uploaded to ENA.
	data_file, file : this text file must have at least three columns seperated by commas in the following order and with the following headings:  Column 1: SAMPLE, Column 2: TAXON_ID, Column 3: SCIENTIFIC_NAME, Column 4: DESCRIPTION.  If you like to add further data then add it after the DESCRIPTION column.
    center_name, str : name of the center, e.g. PHE
    refname, str: A unique name for the whole submission. This name must not have been used before in any other submission to ENA.
    library_strategy, str : default 'WGS'.
    library_source, str : default 'GENOMIC'
    library_selection, str : default 'RANDOM'
    read_length, int : default 250
    read_sdev, int : default 0.0
    instrument_model, int : default "Illumina HiSeq 2500"
    out_dir, str : name of the new xml file
    fastq_ends, tuple: Tuple of strings of size 2 with fastq files end, e.g. ('.R1.fastq.gz', '.R2.fastq.gz')

    return
    ------

    outfile, file : a experiment xml file needed for ENA submission.

	'''
    sample_id_and_data = create_dict_with_data(dir_of_input_data, refname, data_file, fastq_ends)
    # set the root element
    experiment_set = ET.Element('EXPERIMENT_SET')

    if "SAMPLE" not in sample_id_and_data:
        print "The ", data_file, "file does not contain a SAMPLE field! Please add a SAMPLE field to proceed"
        sys.exit(1)
    else:
        for index, isolate in enumerate(sample_id_and_data["SAMPLE"]):
            experiment = ET.SubElement(experiment_set, 'EXPERIMENT', alias=isolate, center_name=center_name)
            study_ref = ET.SubElement(experiment, "STUDY_REF", refname=refname, refcenter=center_name)
            # indent
            design = ET.SubElement(experiment, "DESIGN")
            # indent
            design_description = ET.SubElement(design, "DESIGN_DESCRIPTION")
            sample_descriptor = ET.SubElement(design, 'SAMPLE_DESCRIPTOR', refname=isolate, refcenter=center_name)
            library_descriptor = ET.SubElement(design, "LIBRARY_DESCRIPTOR")
            library_name = ET.SubElement(library_descriptor, "LIBRARY_NAME")
            library_strategy = ET.SubElement(library_descriptor, "LIBRARY_STRATEGY").text = str(library_strategy)
            library_source = ET.SubElement(library_descriptor, "LIBRARY_SOURCE").text = str(library_source)
            library_selection = ET.SubElement(library_descriptor, "LIBRARY_SELECTION").text = str(library_selection)
            library_layout_dir = ET.SubElement(library_descriptor, "LIBRARY_LAYOUT")
            # indent
            paired = ET.SubElement(library_layout_dir, "PAIRED", NOMINAL_LENGTH=read_length, NOMINAL_SDEV=read_sdev)
            # dedent
            platform = ET.SubElement(experiment, "PLATFORM")
            illumina = ET.SubElement(platform, "ILLUMINA")

            # indent
            instrument_model = ET.SubElement(illumina, "INSTRUMENT_MODEL").text = str(instrument_model)

            # dedent
            processing = ET.SubElement(experiment, "PROCESSING")

    # use the indent function to indent the xml file
    indent(experiment_set)
    # create tree
    tree = ET.ElementTree(experiment_set)

    # out_dirput to outfile
    with open(out_dir + "/experiment.xml", 'w') as outfile:
        tree.write(outfile, xml_declaration=True, encoding='utf-8', method="xml")

    print "\nSuccessfully created experiment.xml file\n"


def run_xml(dir_of_input_data, refname, center_name, filetype, out_dir, fastq_ends):
    '''
	run_xml(dir_of_input_data,refname,center_name,filetype,out_dir):
	
	This function generates a run.xml file needed for submission of data to ENA.

	Params
    ------
    dir_of_input_data, dir: This is the directory that contains all the files to be uploaded to ENA.
    center_name, str : name of the center.  Default is PHE
    refname, str: A unique name for the whole submission. This name must not have been used before in any other submission to ENA.
    filetype, str: the default is fastq.
    out_dir, str : name of the new xml file
    fastq_ends, tuple: Tuple of strings of size 2 with fastq files end, e.g. ('.R1.fastq.gz', '.R2.fastq.gz')

    return
    ------

    outfile, file : a run.xml file needed for ENA submission.

	'''

    run_set = ET.Element('RUN_SET')

    # open the checksum file and get the checksums and file names
    with open(dir_of_input_data + '/' + refname + '_checksums.md5', 'rb') as f:
        for line1 in f:
            read1 = line1.split()
            for fastq_end in fastq_ends:
                sample_name = rchop(read1[1], fastq_end)
                if len(sample_name) < len(read1[1]):
                    break
            checksum_read1 = read1[0]

            # loop through every two lines, for read1 and read2
            line2 = f.next()
            read2 = line2.split()
            checksum_read2 = read2[0]
            # if there are pairs of reads
            if sample_name in str(read2[1]):
                run = ET.SubElement(run_set, 'RUN', alias=sample_name, center_name=center_name,
                                    run_center=center_name)
                # indent
                experiment_ref = ET.SubElement(run, 'EXPERIMENT_REF', refname=sample_name)
                data_block = ET.SubElement(run, 'DATA_BLOCK')
                files = ET.SubElement(data_block, 'FILES')
                file1 = ET.SubElement(files, 'FILE', checksum=checksum_read1, checksum_method="MD5",
                                      filename=refname + "/" + read1[1], filetype=filetype)
                file2 = ET.SubElement(files, 'FILE', checksum=checksum_read2, checksum_method="MD5",
                                      filename=refname + "/" + read2[1], filetype=filetype)
            else:
                sys.exit("ERROR: no second read found for", sample_name)

            # use the indent function to indent the xml file
    indent(run_set)
    # create tree
    tree = ET.ElementTree(run_set)

    # out_dirput to outfile
    with open(out_dir + "/run.xml", 'w') as outfile:
        tree.write(outfile, xml_declaration=True, encoding='utf-8', method="xml")

    print "\nSuccessfully created run.xml file\n"


def study_xml(title_and_abstract_file, center_name, refname, out_dir):
    '''
	study_xml(title_and_abstract_file,center_name,refname,center_project_name,out_dir):
	
	This function generates a study.xml file needed for submission of data to ENA.

	Params
    ------
    title_and_abstract_file, file: This file should contain two coloumns seperated by tabs.  Column 1 is the title of the work and column 2 is the abstract.  Do not add headings.
    center_name, str : name of the center.  Default is PHE
    refname, str: A unique name for the whole submission. This name must not have been used before in any other submission to ENA.
    center_project_name, str: provide a centre project name, default = PHE_SCIENTIFIC_PROJECT
    out_dir, str : name of the new xml file

    return
    ------

    outfile, file : a study.xml file needed for ENA submission.

	'''

    study_set = ET.Element('STUDY_SET')
    try:
        with open(title_and_abstract_file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                cols = line.decode('utf-8').strip().split('\t')
                title = cols[0]
                abstract = cols[1]

                study = ET.SubElement(study_set, 'STUDY', alias=refname, center_name=center_name)
                # indent
                descriptor = ET.SubElement(study, 'DESCRIPTOR')
                # indent
                # center_project_name = ET.SubElement(descriptor, 'CENTER_PROJECT_NAME').text = center_project_name
                study_title = ET.SubElement(descriptor, 'STUDY_TITLE').text = str(title)
                study_type = ET.SubElement(descriptor, 'STUDY_TYPE', existing_study_type="Whole Genome Sequencing")
                study_abstract = ET.SubElement(descriptor, 'STUDY_ABSTRACT').text = abstract
    except EOFError:
        print "problem with the title and abstract file!"
        sys.exit()
    # use the indent function to indent the xml file
    indent(study_set)
    # create tree
    tree = ET.ElementTree(study_set)

    # out_dirput to outfile
    with open(out_dir + "/study.xml", 'w') as outfile:
        tree.write(outfile, xml_declaration=True, encoding='utf-8', method="xml")

    print "\nSuccessfully created study.xml file\n"


def submission_xml(refname, center_name, out_dir, release=False, hold_date=''):
    '''
	submission_xml(refname,center_name,out_dir,release,hold_date='')
	
	This function generates a submission.xml file needed for submission of data to ENA. It is the final of the five xml files needed.

	Params
    ------
    center_name, str : name of the center.  Default is PHE
    refname, str: A unique name for the whole submission. This name must not have been used before in any other submission to ENA.
    center_project_name, str: provide a centre project name, default = PHE_SCIENTIFIC_PROJECT
    release, True or False: If True then the data would be immediatley available publicly.  If FALSE then it would be held for a default of 2 years privately.
    hold_date, date: The date to which you like to release your data publicly.  default is two years.
    out_dir, str : name of the new xml file

    return
    ------

    outfile, file : a submission.xml file needed for ENA submission.

	'''

    xml_files = ["study", "sample", "experiment", "run"]

    submission_set = ET.Element('SUBMISSION_SET')
    submission = ET.SubElement(submission_set, 'SUBMISSION', alias=refname, center_name=center_name)
    actions = ET.SubElement(submission, "ACTIONS")
    for xml_file in xml_files:
        action = ET.SubElement(actions, "ACTION")
        add = ET.SubElement(action, "ADD", source=xml_file + ".xml", schema=xml_file)

    # if a hold date is given until releasing publicly
    action = ET.SubElement(actions, "ACTION")

    if hold_date:
        hold = ET.SubElement(action, "HOLD", HoldUntilDate=hold_date)
    # else if release is given, i.e. release immediatley to the public
    elif release:
        release = ET.SubElement(action, "RELEASE")
    # otherwise hold for two years and then make it public
    else:
        hold = ET.SubElement(action, "HOLD")
    # use the indent function to indent the xml file
    indent(submission_set)
    # create tree
    tree = ET.ElementTree(submission_set)

    # out_dirput to outfile
    with open(out_dir + "/submission.xml", 'w') as outfile:
        tree.write(outfile, xml_declaration=True, encoding='utf-8', method="xml")

    print "\nSuccessfully created submission.xml file\n"


def run_curl_command(ftp_user_name, ftp_password, out):
    '''
	run_curl_command(ftp_user_name,ftp_password)
	
	This function executes the curl command that would upload all the xml files to ENA.  The function first runs a test command and if successfull automatically runs the production command.

	Params
    ------

    ftp_user_name, str: You must provide your ENA ftp username, e.g. Webin-40432
    ftp_password, str: You must provide your ENA ftp password
   

    return
    ------

    receipt.xml, file: stdout of the curl command.

	'''
    # first do a test...

    test_cmd = "curl -k -F \"SUBMISSION=@submission.xml\" -F \"STUDY=@study.xml\" -F \"SAMPLE=@sample.xml\" -F \"EXPERIMENT=@experiment.xml\" -F \"RUN=@run.xml\" \"https://www-test.ebi.ac.uk/ena/submit/drop-box/submit/?auth=ENA%20\"" + ftp_user_name + "%20" + ftp_password
    prod_cmd = "\ncurl -k -F \"SUBMISSION=@submission.xml\" -F \"STUDY=@study.xml\" -F \"SAMPLE=@sample.xml\" -F \"EXPERIMENT=@experiment.xml\" -F \"RUN=@run.xml\" \"https://www.ebi.ac.uk/ena/submit/drop-box/submit/?auth=ENA%20\"" + ftp_user_name + "%20" + ftp_password

    # p = subprocess.Popen(cmd, stdout=subprocess.PIPE, cwd=out, shell=True)
    receipt_xml = open(out + "/receipt.xml", 'w')
    print "\nRunning curl command....\n"
    p = subprocess.Popen(test_cmd, stdout=receipt_xml, cwd=out, shell=True)
    (curl_output, err) = p.communicate()

    if "success=\"false\"" in open(out + "/receipt.xml").read():
        print "\nERROR: There is a problem with the submission.  Please check the file ", out + "/receipt.xml", "and correct the error and re-submit using the -curl command.\n"
        sys.exit()
    # elif "success=\"true\"" in open(out+"/receipt.xml").read():
    # 	print "\nTest submission is successfull!"
    # 	print "\nSubmitting production now..."
    # 	p = subprocess.Popen(prod_cmd, stdout=receipt_xml, cwd=out, shell=True)
    # 	(curl_output, err) = p.communicate()
    elif "success=\"true\"" in open(out + "/receipt.xml").read():
        print "\nSUCCESS! Your data is now ready to be uploaded to production.  Note that if you decide to upload your data to production then it would be very difficult to delete it.  So if you are happy with this then run the following command:\n " + prod_cmd

        print "\n NOTE: you must run the above curl command from the output dir which contains all the xml files."
