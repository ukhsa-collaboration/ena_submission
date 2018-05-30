#!/usr/bin/env python
import os, os.path, sys, subprocess, getopt, glob, argparse
from subprocess import call
from xml.dom import minidom
import csv
import collections
import ast

import xml.etree.ElementTree

def set_up_argparse():
    parser = argparse.ArgumentParser(description="""

    **This tool will take the receipt.xml file (output from the curl command used to submit all files to ENA repository) and create a csv file which will contain all the ENA accession numbers.**""")

    # parser = argparse.ArgumentParser(epilog="Good luck! If your jobs breaks, don't blame me :-)", add_help=True)

    parser.add_argument('--input_receipt_xml_file', '-i', help='please provide the path for the receipt.xml file.',default="required")
    parser.add_argument('--out_dir', '-o', help='please provide the path to the output directory.')
    opts = parser.parse_args()

    return opts

def extract_ena_accession_from_receipt_xml(receipt_xml_file,out_dir):

    user_sample_names_and_ENA_numbers = {}
    final_dict = collections.defaultdict(list)
    xmldoc = minidom.parse(receipt_xml_file)
    experiments = xmldoc.getElementsByTagName('EXPERIMENT')
    runs = xmldoc.getElementsByTagName('RUN')
    samples = xmldoc.getElementsByTagName('SAMPLE')
    studies = xmldoc.getElementsByTagName('STUDY')

    project_number = ""
    for study in studies:
        project_number = study.attributes['accession'].value

    for experiment in experiments:
        user_sample_names_and_ENA_numbers[experiment.attributes['accession'].value] = experiment.attributes['alias'].value
    for run in runs:
        user_sample_names_and_ENA_numbers[run.attributes['accession'].value] = run.attributes['alias'].value
    for sample in samples:
        user_sample_names_and_ENA_numbers[sample.attributes['accession'].value] = sample.attributes['alias'].value

    for key,value in user_sample_names_and_ENA_numbers.items():
        final_dict[value].append(key)

    outfile = open(out_dir+"/"+project_number+"_data.csv", 'w')
    outfile.write("ID," + "Run accession," + "Study accession," + "Experiment accession\n" )
    for key, value in sorted( final_dict.items() ): 
        outfile.write( str(key) + ',' + ",".join(sorted(value)) + '\n')

def main(opts):

    extract_ena_accession_from_receipt_xml(opts.input_receipt_xml_file,opts.out_dir)

if __name__ == '__main__':
    opts = set_up_argparse()
    main(opts)