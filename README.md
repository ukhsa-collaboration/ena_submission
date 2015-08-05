This tool in a single step will create the necessary xml files and uploads all your fastq files to the ENA repository.

Dependencies: None

    usage: run_xml_generation.py [-h] [--xml_file XML_FILE]
                                 [--dir_of_input_data DIR_OF_INPUT_DATA]
                                 [-data_file DATA_FILE]
                                 [--ftp_user_name FTP_USER_NAME]
                                 [--ftp_password FTP_PASSWORD]
                                 [--title_and_abstract_file TITLE_AND_ABSTRACT_FILE]
                                 [--center_name CENTER_NAME] [--refname REFNAME]
                                 [--library_strategy LIBRARY_STRATEGY]
                                 [--library_source LIBRARY_SOURCE]
                                 [--library_selection LIBRARY_SELECTION]
                                 [--read_length READ_LENGTH]
                                 [--read_sdev READ_SDEV]
                                 [--instrument_model INSTRUMENT_MODEL]
                                 [--filetype FILETYPE] [--hold_date HOLD_DATE]
                                 [--release] [--curl_command]
                                 [--create_checksums_file]
                                 [--upload_data_to_ena_ftp_server]
                                 [--out_dir OUT_DIR]

    optional arguments:
      -h, --help            show this help message and exit
      --xml_file XML_FILE, -x XML_FILE
                            please provide the name for the xml you like to
                            generate, one of the
                            following:all,experiment,run,sample,study,submission
      --dir_of_input_data DIR_OF_INPUT_DATA, -i DIR_OF_INPUT_DATA
                            please provide the path for the files you like to
                            upload to ENA. NOTE: the fastq files must be in the
                            following format: *.R1.fastq.gz and *.R2.fastq.gz.
      -data_file DATA_FILE, -f DATA_FILE
                            data_file, file : this text file must have at least
                            three columns seperated by tabs in the following order
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
      --center_name CENTER_NAME, -c CENTER_NAME
                            Please provide the center name
      --refname REFNAME, -r REFNAME
                            Please provide the unique name for the whole
                            submission. This name must not have been used before
                            in any other submission to ENA.
      --library_strategy LIBRARY_STRATEGY, -s LIBRARY_STRATEGY
                            please provide the library strategy used
      --library_source LIBRARY_SOURCE, -u LIBRARY_SOURCE
                            please provide the library source used
      --library_selection LIBRARY_SELECTION, -e LIBRARY_SELECTION
                            please provide the library selection used
      --read_length READ_LENGTH, -l READ_LENGTH
                            Please provide the read length
      --read_sdev READ_SDEV, -sdev READ_SDEV
                            Please provide the read stdv
      --instrument_model INSTRUMENT_MODEL, -m INSTRUMENT_MODEL
                            please provide the name of the instrument model used
      --filetype FILETYPE, -F FILETYPE
                            Please provide the file type
      --hold_date HOLD_DATE, -ho HOLD_DATE
                            This option will hold the data privately until a
                            specified date. Please provide the specified date
                            using the following format: YYYY-MM-DD
      --release, -R         This option will release the data immediatley to the
                            public domain. Cannot be used with --hold_date
      --curl_command, -curl
                            Run curl command to upload everything to ENA
      --create_checksums_file, -cs
                            Create a checksum file
      --upload_data_to_ena_ftp_server, -ftp
                            Upload data into the ftp server
      --out_dir OUT_DIR, -o OUT_DIR
                            please provide the path to the output directory which
                            will include all the xml files.