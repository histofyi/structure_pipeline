from typing import Dict, List, Tuple

def get_facet_path(output_path:str, domain:str, facet:str, pdb_code:str) -> str:
    return f"{output_path}/{domain}/{facet}/{pdb_code}.json"


def build_core_record(pdb_code:str) -> Dict:
    core_record = {
        "accessory_molecules": {},
        "allele": {
            "alpha": None,
            "beta": None
        },
        "assemblies": [],
        "assembly_count": None,
        "chain_count": None,
        "chronology": {
            "deposition_date": None,
            "release_date": None,
            "update_date": None
        },
        "class": None,
        "classical": None,
        "complex_type": None,
        "doi": {
            "doi": None,
            "url": None
        },
        "facets": {},
        "ligands": [],
        "locus": None,
        "manually_edited": {},
        "methodology": None,
        "missing_residues": [],
        "open_access": False,
        "organism": {},
        "pdb_code": pdb_code,
        "pdb_title": None,
        "peptide": {
            "actual_sequence": None,
            "epitope_info": {},
            "features": [],
            "full_sequence": None,
            "gap_info": {},
            "gapped_sequence": None,
            "length": {
                "numeric": None,
                "text": None
            },
            "unnatural_amino_acids": []
        },
        "publication": {},
        "resolution": None,
        "unique_chain_count": None
    }
    return core_record