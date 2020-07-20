"""blueprint_export_coversheet.py

Create a WES report coversheet for blueprint report PDFs in the input directory.
Blueprint report PDFs must be named in the format: "report_123453.pdf"

Usage:
	python3 blueprint_export_coversheet.py "input_directory\"
"""


import csv
import io
import os
import re
import sys
from collections import namedtuple
from datetime import datetime
from pathlib import Path

import jinja2
import pdfkit
from pdfminer import high_level
from PyPDF2 import PdfFileMerger

# Set file dependencies as global variables
COVERSHEET_DATA_SOURCE = r'S:\Genetics\Bioinformatics\NGS\200511_BlueprintExport\src\html_db.csv'
COVERSHEET_TEMPLATE = r'S:\Genetics\Bioinformatics\NGS\200511_BlueprintExport\src\report_template.html'
PATH_TO_WKHTMLTOPDF= r'\\gstt.local\shared\Genetics_Data2\Array\Software\wkhtmltopdf\bin\wkhtmltopdf.exe'


def list_blueprint_reports(directory):

	dir_path = Path(directory).absolute()
	
	if not dir_path.exists() or not dir_path.is_dir():
		exit("Input path is not an existing directory")

	# Get list of PDF files in input directory
	#input_dir = os.path.dirname(os.path.realpath(directory))
	blueprint_reports = list(dir_path.glob("report*.pdf"))

	### Do nothing if rfiles is empty
	if blueprint_reports:
		return(blueprint_reports)
	else:
		exit("No blueprint PDFs found")

def get_coversheet_data(family_identifier):
	"""Return a tuple containing data to generate WES coversheet.
	Arguments:
		family_identifier(str): The first six digits of the PRU
	Returns:
		(
			patients, # A list of named tuple objects with details for each patient
			clinician, # The name of the referring clinician for the family 
			address, # The address of the referring clinician for the test
			date # Today's date
		)
	"""
	
	# Create a namedtuple object for holding patient coversheet data 
	PatientCoversheetData =  namedtuple('PatientCoversheetData', 'name dob pid nhsno specimen spec_rec spec_taken sex')
	
	# Use CSV reader to get rows for family from coversheet data source
	with open(COVERSHEET_DATA_SOURCE) as csvfile:
		reader_object = csv.reader(csvfile, delimiter=',', quotechar='"')
		data_rows = [ row for row in reader_object if row[5].startswith(family_identifier) ]
	
	if not data_rows:
		exit(f"No data found for patients matching family id: {family_identifier}")
	
	# Set the clinician and address data from the first patient entry
	clinician, address = data_rows[0][11], data_rows[0][12]
	todays_date = datetime.now().date().strftime('%Y-%m-%d')
	
	# Build coversheet data for each patient
	patient_details = []
	for row in data_rows:
		patient_details.append(
			PatientCoversheetData(
			   row[1] + ' ' + row[0], # patient full name 
			   row[2].split(' ')[0], # patient date of birth (split from timestamp)
			   row[5], # patient identifier or PRU
			   row[4].replace(' ', ''), # patient nhsno
			   row[6] + ' ' + row[8], # specimen and specimen type 
			   row[7].split(' ')[0], # date specimen recorded (split from timestamp)
			   row[9].split(' ')[0], # date specimen taken (split from timestamp)
			   row[3] # patient sex
			)
		)
	
	return (patient_details, clinician, address, todays_date)

def generate_report_with_coversheet(report, patient_details, clincian, address, todays_date, output_file_id):
	"""Create new blueprint report PDF with coversheet.
	Arguments:
		report(str): Path to a blueprint report PDF
		patient_details(list): A list of PatientCoversheetData() objects
		clinician(str): Name of referring clinician in HTML format
		address(str): Address of referring clinician in HTML format
		todays_date(str): Current date. E.g. 2020-07-03
		output_file_id(str): A string to include in the output file name
	Returns:
		None. Output PDFs are created with naming convetion (wesreport_123456.pdf) where 
			123456 is the family identifier
	"""
	
	# Generate report template as html text
	template = Path(COVERSHEET_TEMPLATE)
	template_directory, template_filename = str(template.parent), str(template.name)
	html_renderer = jinja2.Environment(loader=jinja2.FileSystemLoader(template_directory))
	html_text = html_renderer.get_template(template_filename).render(
		patients=patient_details,
		clinician=clinician,
		address=address,
		todays_date=todays_date
	)

	# Convert HTML report template to PDF as a bytes object
	cover_pdf = pdfkit.from_string(
		html_text,
		output_path=False,
		configuration=pdfkit.configuration(wkhtmltopdf=PATH_TO_WKHTMLTOPDF),
		options={'quiet':''}
	)
	b_cover_pdf = io.BytesIO(cover_pdf)

	# Create new PDF by merging coversheet with existing report
	pdf_merger = PdfFileMerger()
	for pdf in  [ b_cover_pdf, str(report) ]:
		pdf_merger.append(pdf, import_bookmarks=False)
	output_file = str(Path(r'S:\Genetics\Bioinformatics\NGS\200511_BlueprintExport\reports',f"wes_report_{output_file_id}.pdf"))
	with open(output_file, "wb") as merged_report:
		pdf_merger.write(merged_report)


if __name__ == "__main__":
	blueprint_reports = list_blueprint_reports(sys.argv[1])
	for report in blueprint_reports:
		# Get PRU from pdf report text.
		# re.search(regular_expression, pdf_report_text).group() returns the first string in pdf_report_text
		#    that matches the regular expression.	
		pdf_report_text = high_level.extract_text(str(report))
		pru = re.search("\d+:\d{2}", pdf_report_text).group(0)
		# Get family identifier, the digits preceding the colon in the PRU
		family = pru.split(':')[0]
		# Get coversheet data for family from coversheet database
		patient_details, clinician, address, todays_date = get_coversheet_data(family)
		generate_report_with_coversheet(report, patient_details, clinician, address, todays_date, family)
