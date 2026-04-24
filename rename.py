import re

input_fasta = "input.fasta"
output_fasta = "renamed.fasta"

country_db = "countries.tsv"
virus_db = "viruses.tsv"


def load_db(file):
    db = []
    with open(file) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            standard, aliases = line.split("\t")
            alias_list = aliases.split("|")
            db.append((standard, alias_list))
    return db


countries = load_db(country_db)
viruses = load_db(virus_db)


def find_from_db(header, db, default):
    for standard, aliases in db:
        for alias in aliases:
            pattern = rf"\b{re.escape(alias)}\b"
            if re.search(pattern, header, re.IGNORECASE):
                return standard
    return default


def find_year(header):
    match = re.search(r"\b(19|20)\d{2}\b", header)
    return match.group(0) if match else "unknown_year"


def find_id(header):
    header = header.replace(">", "").strip()
    return header.split()[0]


with open(input_fasta) as infile, open(output_fasta, "w") as outfile:
    for line in infile:
        if line.startswith(">"):
            header = line.strip()

            seq_id = find_id(header)
            virus = find_from_db(header, viruses, "unknown_virus")
            year = find_year(header)
            country = find_from_db(header, countries, "unknown_country")

            new_header = f">{seq_id}|{virus}|{year}|{country}"
            outfile.write(new_header + "\n")
        else:
            outfile.write(line)
