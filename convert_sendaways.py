"""convert_sendaways.py

Convert internal blueprint document to correct format for sendaway. 

usage: python3 convert_sendaways.py 200701_blueprint_sendaways.csv
"""

from collections import namedtuple
import csv
import sys

# Define a namedtuple for easy access to hold records from the input CSV file
RECORD = namedtuple('CSVData', (
	'batch batch_date batch_count test_type dna_number specimen_number pru'
	' last_name first_name all_name nd_dna vol_sent relationship clinician'
	' pheno_status dnanomoka status ngstestid dob gender')
	)

# Open the input CSV file
with open(sys.argv[1]) as csvfile:
	csvr = csv.reader(csvfile, delimiter=',', quotechar='"')
	# Store the first line as the header
	header = next(csvr)
	# Store the data in a list of RECORD objects
	data = [ RECORD(*rows) for rows in csvr ]

# Define variables for output file header and data
OUTPUT_HEADER = ['batch', 'identifier', 'dna', 'specimen', 'dob', 'gender', 'referral', 'family_id', 'pedigree', 'affected_status', 'phenotype_file']
OUTPUT_DATA = []
# Parse records from input and append to output data variable
for rec in data:
	OUTPUT_DATA.append((
		rec.batch, f'"{rec.pru}"', rec.dna_number, rec.specimen_number, rec.dob,
		rec.gender, rec.test_type.lower(), f'"{rec.pru.split(":")[0]}"', rec.relationship, rec.pheno_status,
		rec.pru.replace(':','-') + '_' + rec.dna_number + '_phenotype.csv'
		)
	)

# Write output file
with open('BLUEPRINT_EXPORT.csv','w',newline='') as csvfile:
	wr = csv.writer(csvfile, delimiter=',')
	wr.writerow(OUTPUT_HEADER)
	wr.writerows(OUTPUT_DATA)
