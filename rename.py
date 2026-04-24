import sys
import re 
if len(sys.argv) != 3:
    print("Usage: python rename_fasta_headers.py input.fasta output.fasta")
    sys.exit(1)

input_fasta = sys.argv[1]
output_fasta = sys.argv[2]
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

def attach_number_to_virus(header, virus):
    """
    If a number is near the virus name, attach it to the virus.
    Example:
    Human adenovirus 89 -> human_adenovirus_89
    HAdV-C1 -> human_adenovirus_1
    """
    
    if virus == "unknown_virus":
        return virus

    patterns = [
        rf"{virus.replace('_', r'[\s_-]+')}[\s_-]*(\d+)",
        r"HAdV[\s_-]*[A-G]?[\s_-]*(\d+)",
        r"human[\s_-]+adenovirus[\s_-]*(?:type[\s_-]*)?(\d+)",
        r"adenovirus[\s_-]*(?:type[\s_-]*)?(\d+)"
    ]

    for pattern in patterns:
        match = re.search(pattern, header, re.IGNORECASE)
        if match:
            return f"{virus}_{match.group(1)}"

    return virus
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
