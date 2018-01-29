# README for ena_submission tool
------------------------------

This tool in a single step will create the necessary xml files and uploads all your files to the ENA repository.


## Description of the Process
--------------------------
In order to submit your files as a batch to ENA, you need to create some files that have information about your samples which then you can use to upload to ENA.  It can be a tedious task.  This script would make this possible in one step.  This is how it works (provided that you have provided the necessary files, see 'Required files' below):

1. Creates a checksum file of all your files needed for submission.
2. Uploads the files to the ENA server using FTP.  It will use the authentications you have provided it.
3. Provided the data format is correct, the script will create five xml files: sample.xml, experiment.xml, run.xml, study.xml and submission.xml.
4. If all the .xml files have been successfully created, the script will run a test curl command that will upload all the .xml files to the ENA server and returns a receipt.xml file.  If this process failes, you will be notified and you must correct the error and re-submit using the -curl option.  The script will run a test command to test if its sucessful. You must then run the production curl command to upload your data to production.


## Dependencies
---------------

Python >= 2.7

## Required files
--------------

To upload your files to ENA, you will need the following:

1. A directory which contains all your files.  If you are uploading fastq files, the files must be in the following format (see examples in the examples folder):

  SAMPLE_NAME.R1.fastq.gz

  SAMPLE_NAME.R2.fastq.gz

  E.g. 

  MN127.R1.fastq.gz
  
  MN127.R2.fastq.gz
  
  If your files end differently (from ".R1.fastq.gz" and ".R2.fastq.gz"), provide the proper files end with --fastq_end option

  Otherwise, if you are uploading a different type of file, like bam files or fasta files, you can name them whatever you like but they should have the prefix at the end, e.g. .bam or .fasta.  Use the -F flag to do so, e.g. -F bam.

2. A csv (comma separated values) file that contains all the information for each of your samples.  The text file should contain four required columns.  You may add as many columns of data as you wish after the fourth required column.  The columns are separated by commas.  e.g. (note the headings are required as seen below):


  SAMPLE,TAXON_ID,SCIENTIFIC_NAME,DESCRIPTION

  data....

  You may like to use the template file provided in the examples folder.  You might also like to see an example file in the examples folder. Please note that ENA now check that the Scientific_name should be matching to taxon_id so please make sure you write the correct scientific_name.

3. A text file that contains the title for your project and an abstract explaining the project.  The two columns must be separated by tabs. There are no headings needed here. e.g (see examples in the examples folder):

  Bioinformatics for biologists \t Bioinformatics is great for biologists.....etc

4. An ENA ftp username and password.  If you do not have one, you need to contact ENA at: datasubs@ebi.ac.uk.

NOTE!! If you are uploading files other than fastq files, you must use the -F flag and add the prefix, e.g. -F bam.

## Before you run the script....
-------------------

Before you run the script, make sure you have the following ready as you cannot proceed without it:

    -i : full path to your files you would like to upload to ENA. (point 1 above)
    -r : a reference name for your project
    -f : the path to the data file (point 2 above)
    -a : the path to the title and abstract text file (point 3 above)
    -o : the path to the output directory
    -user : ENA username (point 4 above)
    -pass : ENA password (point 4 above)

You should familarise yourself with the other options before you begin running the script.  To do so, run python ena_submission.py -h


## Examples of commands
--------------------

  If you like to run a single command that does EVERYTHING, i.e. creates checksums, uploads your files to ftp, creates the xml files, uploads the xml files and run the curl command, then use the -d option, e.g. |n


  E.g. for fastq submission (otherwise use -F suffix)|n

      python ena_submission.py -d -i /PATH/TO/SAMPLES_FILES_DIR -r phe_mycoplasma -f /PATH/TO/DATA_FILE.txt -o /PATH/TO/OUTPUT_DIR -a /PATH/TO/TITLE_ABSTRACT_FILE.txt -c CENTRE_NAME -user Webin-YYYYY -pass XXXXX 

  You may wish to run each step individually. These are the different steps you may run manually:

  ----

  To just create the checksums file:

  --create_checksums_file : only create the checksums file for my fastqs. e.g.

    python ena_submission.py -cs -i /PATH/TO/SAMPLES_FILES_DIR -r test3

  ----

  To just upload your data to the ENA server:

  --upload_data_to_ena_ftp_server : only upload the data to ENA. e.g.

    python ena_submission.py -ftp -i /PATH/TO/SAMPLES_FILES_DIR -r NAME_OF_YOUR_PROJECT -user Webin-YYYYY -pass XXXXX

  ----

  To just create sample.xml file:

  -x sample : use the word 'sample' (same goes for the rest) to create sample.xml only. e.g.

    python ena_submission.py -x sample -i /PATH/TO/SAMPLES_FILES_DIR -r NAME_OF_YOUR_PROJECT -f /PATH/TO/DATA_FILE.txt -c YOUR_CENTRE_NAME -o /PATH/TO/OUTPUT_DIR

  ----
  To just create experiment.xml file:

  -x experiment : to create experiment.xml only. e.g.

    python ena_submission.py -x experiment -i /PATH/TO/SAMPLES_FILES_DIR -r NAME_OF_YOUR_PROJECT -f /PATH/TO/DATA_FILE.txt -c YOUR_CENTRE_NAME -o /PATH/TO/OUTPUT_DIR  
  ----

  To just create run.xml file:

  -x run : to create run.xml only. e.g.

    python ena_submission.py -x run -i /PATH/TO/SAMPLES_FILES_DIR -r NAME_OF_YOUR_PROJECT -c YOUR_CENTRE_NAME -o /PATH/TO/OUTPUT_DIR
  ----

  To just create study.xml file:
  -x study : to create study.xml only. e.g.

    python ena_submission.py -x study -a /PATH/TO/TITLE_ABSTRACT_FILE.txt -r NAME_OF_YOUR_PROJECT -i /PATH/TO/SAMPLES_FILES_DIR -c YOUR_CENTRE_NAME -o /PATH/TO/OUTPUT_DIR

  ----

  To just create submission.xml file:

  -x submission : to create submission.xml only. e.g.

    python ena_submission.py -x submission -i /PATH/TO/SAMPLES_FILES_DIR -o /PATH/TO/OUTPUT_DIR -r NAME_OF_YOUR_PROJECT -c YOUR_CENTRE_NAME

  NOTE: Here you may hold your data from release publicly if you use -ho option and specify the date.
  ----

  To just run the curl command:

  -curl : just run curl command.  Note: you must have uploaded the data and created all the xml files to run the curl command. e.g.

    python ena_submission.py -curl -user Webin-YYYYY -pass XXXX -o /PATH/TO/OUTPUT_DIR


## Usage
-----
-----
    -h, --help            show this help message and exit
    --generate_xml_file_for GENERATE_XML_FILE_FOR, -x GENERATE_XML_FILE_FOR
                          please provide the name for the xml you like to
                          generate, one of the
                          following:all,experiment,run,sample,study,submission
    --dir_of_input_data DIR_OF_INPUT_DATA, -i DIR_OF_INPUT_DATA
                          please provide the path for the files you like to
                          upload to ENA. NOTE: the fastq files must be in the
                          following format: *.R1.fastq.gz and *.R2.fastq.gz.
    --data_file DATA_FILE, -f DATA_FILE
                          data_file, file : this text file must have at least
                          four columns seperated by TABS in the following order
                          and with the following headings: Column 1: SAMPLE,
                          Column 2: TAXON_ID, Column 3: SCIENTIFIC_NAME, Column
                          4: DESCRIPTION. If you like to add further data then
                          add it after the DESCRIPTION column.
    --ftp_user_name FTP_USER_NAME, -user FTP_USER_NAME
                          please provide the ftp user name
    --ftp_password FTP_PASSWORD, -pass FTP_PASSWORD
                          please provide the ftp password
    --title_and_abstract_file TITLE_AND_ABSTRACT_FILE, -a TITLE_AND_ABSTRACT_FILE
                          please provide the title and abstract text file. This
                          is needed to generate the study.xml file. The file
                          should be in the following format: full title of the
                          project abstract
    -c "Public Health England", --center_name "Public Health England"
                          Please provide the center name. The center name is a
                          controlled vocabulary identifying the sequencing
                          center, core facility, consortium, or laboratory
                          responsible for the study.
    -r PHE_20180125, --refname PHE_20180125
                          Please provide the unique name for the whole
                          submission. This name must not have been used before
                          in any other submission to ENA.
    --library_strategy LIBRARY_STRATEGY, -s LIBRARY_STRATEGY
                          please provide the library strategy used. default =
                          WGS
    --library_source LIBRARY_SOURCE, -u LIBRARY_SOURCE
                          please provide the library source used. default =
                          GENOMIC
    --library_selection LIBRARY_SELECTION, -e LIBRARY_SELECTION
                          please provide the library selection used. default =
                          RANDOM
    --read_length READ_LENGTH, -l READ_LENGTH
                          Please provide the read length. default = 100
    --read_sdev READ_SDEV, -sdev READ_SDEV
                          Please provide the read stdv. default = 0.0
    --instrument_model INSTRUMENT_MODEL, -m INSTRUMENT_MODEL
                          please provide the name of the instrument model used.
                          default = Illumina HiSeq 2500
    --filetype FILETYPE, -F FILETYPE
                          Please provide the file type, default=fastq
    --hold_date HOLD_DATE, -ho HOLD_DATE
                          This option will hold the data privately until a
                          specified date. Please provide the specified date
                          using the following format: YYYY-MM-DD
    --release, -R         This option will release the data immediatley to the
                          public domain. Cannot be used with --hold_date.
                          default = False
    --curl_command, -curl
                          Run curl command to upload everything to ENA
    --create_checksums_file, -cs
                          Create a checksum file
    --upload_data_to_ena_ftp_server, -ftp
                          Upload data into the ftp server
    --out_dir OUT_DIR, -o OUT_DIR
                          please provide the path to the output directory which
                          will include all the xml files.
    --fastq_ends .R1.fastq.gz .R2.fastq.gz
                          By default, ena_submission.py searches for pair-end
                          fastq files ending with ".R1.fastq.gz" and
                          ".R2.fastq.gz". If your fastq files end differently,
                          you can provide two strings containing the end of
                          fastq files names (for example, "_1.fastq.gz" and
                          "_2.fastq.gz")


## Contact

Ali Al-Shahib
ali.al-shahib@phe.gov.uk
