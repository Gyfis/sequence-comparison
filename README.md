# Sequence comparison
### A little project for comparing two biological sequences

The main script of the project recieves two IDs of some biological sequences, along with some specified databases and formats, compares them to each other, and generates a pdf with contents of this comparison.

## Example input:
```bash
> python sequence_comparison.py LN906603 UPI0000000001 -sa ebi -sb uniprot_uniparc -ga pam120 blosum62::-2,-1 -la 1,-1::-2,-1
```
This input  

- downloads sequence _LN906603_ from **ebi_ena** database

- downloads sequence _UPI0000000001_ from **uniprot_uniparc** database

- asks the script to find a global alignment using **pam120** matrix (_pam120_)

- finds another global alignment using **blosum62** matrix with custom gap opening/extension scores (_blosum62::-2,-1_)

- and finally asks the script to find a local alignment using **match/mismatch** and gap opening/extension scores (_1,-1::-2,-1_)

