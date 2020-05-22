import os
# open up a file containing cases to be sent away. this is a csv copy of the worksheet used by Jodie (easier to read in python)
with open(r"S:\Genetics_Data2\Array\Audits and Projects\200506_phenotips_json\200522_blueprint_sendaways.csv",'r') as sendaway_list_file:
    sendaway_list = sendaway_list_file.readlines()
    # manually anonymised copy of phenotips csv export.
with open(r"S:\Genetics_Data2\Array\Audits and Projects\200506_phenotips_json\phenotips_2020-05-22_16-14.txt",'r') as phenotips_all_file:
    phenotips_all = phenotips_all_file.readlines()
    # a copy of the phenotips column headers
with open(r"S:\Genetics_Data2\Array\Audits and Projects\200506_phenotips_json\header_template.txt",'r') as phenotips_header_file:
    phenotips_header = phenotips_header_file.readlines()

# for each sample to be sent away
for sample in sendaway_list:
    # create list to hold the patient specific lines from phenotips
    phenotips_list = []
    # just select for the batches to be sent - some batches may not have all the required info yet eg spec numbers
    if sample.startswith("BG1") or sample.startswith("BG2"):# or sample.startswith("BG3") or sample.startswith("BG4") or sample.startswith("BG5") or sample.startswith("BG6"):
        #define columns in the sendaway list
        batch,batch_date,batch_count,sdt,dna_number,specimen_number,pru,last_name,first_name,all_name,nd_dna,vol_sent,relationship,clinician,pheno_status,DNANoMoka,Status,NGSTestID,dob = sample.split("\t")
        if batch in ("BG1","BG2"):
            #set flags to aid data extraction            
            start_copying = False
            seen = False
            # loop through the phenotips export to find data for this sample
            for line in phenotips_all:
                phenotips_pru = line.split("\t")[0]    
                # if the PRU matches we want to capture all the lines from phenotips until the PRU changes
                if phenotips_pru == pru:
                    start_copying = True
                    seen = True
                    # if PRUs match it's the first line of phenotips - first write the header into the output list
                    for header_line in phenotips_header:
                        phenotips_list.append(header_line)
                # if the phenotips field in phenotips output is not empty mean's we're onto the next patient so stop copying
                elif len(phenotips_pru) > 1:
                    start_copying = False
                # if it's a line to be copied append line to list
                if start_copying:
                    phenotips_list.append(line)
            # report where the patient wasn't identified in phenotips
            if not seen:
                print "not found phenotips export for " + pru
            # otherwise create the output file with the expected format using 2 identifiers
            else:        
                phenotype_file_name =  pru.replace(":","-") + "_" + str(dna_number) + "_phenotype.txt"
                with open(os.path.join(r"S:\Genetics_Data2\Array\Audits and Projects\200506_phenotips_json\to_send",phenotype_file_name),'w') as phenotips_output:
                    # write all lines to file
                    for line in phenotips_list:
                        phenotips_output.write(line)
