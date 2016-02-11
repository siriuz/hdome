NR>1 {  #  exclude header
printf "%s ",$13;  # peptide_sequence
printf "%.8f %.8f ", $12, $17  # idestimate_confidence, idestimate_dmass
printf "%.8f %.4f %d %s %.5f ", $18, $19, $22, $24, $25;  #  ion_precursor_mass ion_mz ion_charge ion_spectrum ion_retention_time
split($7, prot_sep, ";");  #  split accessions if there are multiple accessions separated by ;
split($14,ptms,";"); asort(ptms) #  split ptms if there are multiple ptms separated by ;
for (i in prot_sep) { split(prot_sep[i], prot_id, "\|") ; printf "%s " ,prot_id[2]};  #  protein_uniprot_id (there may come a time when this needs to be sorted)
for (y in ptms) { printf "%s ", ptms[y]};  #  ptms_description
print ""}
