import os
import re
import pandas as pd

# Conversion factor: Hartree to kcal/mol
H_TO_KCAL = 627.509

# change BASE_PATH according to yout path to the project root
BASE_PATH = "/path/to/crest-pl-rex-analysis"
TABLES_DIR = os.path.join(BASE_PATH, "tables")

# Change for different table name
output_file = 'master_energy_table_sample.csv'

def get_xtb_energy(file_path):
    """Extracts 'TOTAL ENERGY' from an xTB log file."""
    ENERGY_PATTERN = re.compile(r"TOTAL ENERGY\s+(-?\d+\.\d+)")
    if not os.path.exists(file_path): return None
    energy = None
    try:
        with open(file_path, 'r', encoding="utf-8") as f:
            for line in f:
                match = ENERGY_PATTERN.search(line)
                if match:
                    energy = float(match.group(1))
        return energy
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

def get_crest_entropy(file_path):
    """Extracts 'Sconf' or conformational entropy from CREST output."""
    if not os.path.exists(file_path): return None
    with open(file_path, 'r', encoding="utf-8") as f:
        for line in f:
            # Looking for the entropy term in the CREST summary
            # if "= S(total)" in line or "Conformational Entropy" in line:
                # Adjusting split based on standard CREST output format
                # return float(line.split()[3])
                
            if "Sconf" in line or "Conformational Entropy" in line:
                # Adjusting split based on standard CREST output format
                return float(line.split()[2])    
    return None

def get_pm6_energy(file_path):
    """Extract energy from PM6 output. """
    if not os.path.exists(file_path): return None
    with open(file_path, 'r', encoding="utf-8") as f:
        for line in f:
            # Looking for the ent
            if "Energy" in line:
                # Adjusting split based on standard CREST output format
                return float(line.split()[1])
    return None

def get_partly_optimized_energy(file_path):
    """Extract energy from partly relaxed structures. """
    if not os.path.exists(file_path): return None
    data = []
    with open(file_path, 'r', encoding="utf-8") as f:
        for line in f:
            target, ligand, energy = line.split("/")[0], line.split("/")[1].split("_")[-1], line.split(" ")[-1].strip("\n")
            data.append({
                'Target': target,
                'Ligand': ligand,
                'Partially_opt_energy': energy
            })
    return data

def get_charge(file_path):
    """Extract charge from sdf. """
    if not os.path.exists(file_path): return None
    with open(file_path, 'r', encoding="utf-8") as f:
        lines = f.readlines()
        
    for i, line in enumerate(lines):
        # Look for the line that starts with > <charge>
        if line.strip().startswith('>  <charge>'):
            # The value is always on the very next line
            return lines[i+1].strip()
            
    return None

def extract_sconf_precise(file_path, target_temp="998.15"):
    if not os.path.exists(file_path): return None
    s_conf = None
    in_target_section = False
    
    with open(file_path, 'r', encoding="utf-8") as f:
        for line in f:
            # Step 1: Detect the start of the specific table you want
            if "Final CONFORMATIONAL quantities" in line:
                in_target_section = True
                continue
            
            # Step 2: Once inside, look for the row matching your temperature
            if in_target_section:
                parts = line.split()
                
                # Check if we hit the end of the table (the dashed line)
                if "---" in line and len(parts) == 0:
                    break 
                
                # Identify the data row
                if len(parts) > 1 and parts[0] == target_temp:
                    try:
                        s_conf = float(parts[1])
                        # We found it! Exit the loop.
                        break
                    except ValueError:
                        continue
                        
            # Optional: Stop looking if we hit another main header 
            # to prevent accidental matches elsewhere in the file
            if in_target_section and "---" in line and len(parts) == 0:
                in_target_section = False
                
    return s_conf

# --- Configuration: Adjust these paths to your actual folder names ---
ligands = [d for d in os.listdir(f"{BASE_PATH}/data/01_data/gfn2_on_pl_rex") if os.path.isdir(os.path.join(f"{BASE_PATH}/data/01_data/gfn2_on_pl_rex", d))]
data = []

for lig in ligands:
    # 1. Paths to log files
    path_gfn2_c2 = f"{BASE_PATH}/data/01_data/gfn2_on_pl_rex/{lig}/crest2/{lig}_log.txt"
    path_gfn2_xtb_opt = f"{BASE_PATH}/data/01_data/gfn2_on_pl_rex/{lig}/xtb_opt2/{lig}_log.txt"
    path_gfn2_020_xtb_opt = f"{BASE_PATH}/data/01_data/020_gfn2_xtb/{lig}/xtb_opt/{lig}_log.txt"
    path_pm6_on_gfn2 = f"{BASE_PATH}/data/03_data/pm6_on_gfn2/{lig}/pm6/{lig}_log.txt"
    path_pm6_on_020 = f"{BASE_PATH}/data/03_data/020_structures_pm6/{lig}/{lig}_log.txt"
    path_pl_rex = f"{BASE_PATH}/data/pl_rex/{lig}.sdf"
    path_no_solvent_gfn2 = f"{BASE_PATH}/data/01_data/no_solvent_001/{lig}/crest2/{lig}_log.txt"
    path_001_protonated = f"{BASE_PATH}/data/01_data/001_protonated_results/{lig}/crest2/{lig}_log.txt"
    path_001_protonated_no_solvent = f"{BASE_PATH}/data/01_data/001_protonated_no_solvent_results/{lig}/crest2/{lig}_log.txt"
    path_001_protonated_energy = f"{BASE_PATH}/data/01_data/001_protonated_results/{lig}/xtb_opt2/{lig}_log.txt"
    path_001_protonted_complex_energy = f"{BASE_PATH}/data/01_data/001_protonated_results/{lig}/xtb_opt0/{lig}_log.txt"
    
    # 2. Extract raw Hartree values
    e_020_gfn2_c2_xtb_opt = get_xtb_energy(path_gfn2_xtb_opt)
    e_020_gfn2_xtb_opt =  get_xtb_energy(path_gfn2_020_xtb_opt)
    pm6_on_gfn2_energy = get_pm6_energy(path_pm6_on_gfn2)
    e_020_pm6 = get_pm6_energy(path_pm6_on_020)
    s_conf_gfn2 = get_crest_entropy(path_gfn2_c2)
    charge = get_charge(path_pl_rex)
    no_solvent_gfn2_sconf = get_crest_entropy(path_no_solvent_gfn2)
    ca_protonated_sconf = get_crest_entropy(path_001_protonated)
    ca_protonated_no_solvent_sconf = get_crest_entropy(path_001_protonated_no_solvent)
    e_020_gfn2_protonated = get_xtb_energy(path_001_protonated_energy)
    e_complex_gfn2_protonated = get_xtb_energy(path_001_protonted_complex_energy)

    # 3. Calculations (Deltas in kcal/mol)
    # experimenting with minus
    delta_gfn2_c2_xtb = (e_020_gfn2_c2_xtb_opt - e_020_gfn2_xtb_opt) * H_TO_KCAL if (e_020_gfn2_xtb_opt and e_020_gfn2_c2_xtb_opt) else None
    delta_pm6_on_gfn2 = (pm6_on_gfn2_energy - e_020_pm6) if (e_020_pm6 and pm6_on_gfn2_energy) else None
    delta_001_protonated = (e_020_gfn2_protonated - e_complex_gfn2_protonated) * H_TO_KCAL if (e_complex_gfn2_protonated and e_020_gfn2_protonated) else None
    
    # -TS calculation (assuming T=298.15K)
    ts_term_gfn2 = 298.15 * s_conf_gfn2 / 1000 if s_conf_gfn2 is not None else None
    if s_conf_gfn2 == 0: ts_term_gfn2 = 0
    
    no_solvent_gfn2_ts = 298.15 * no_solvent_gfn2_sconf / 1000 if no_solvent_gfn2_sconf is not None else None
    if no_solvent_gfn2_sconf == 0: no_solvent_gfn2_ts
    
    ca_protonated_ts = 298.15 * ca_protonated_no_solvent_sconf / 1000 if ca_protonated_sconf else None
    if ca_protonated_no_solvent_sconf ==0: ca_protonated_ts = 0
    
    target, ligand = lig.split("__")
    
    data.append({
        'Target': target,
        'Ligand': ligand,
        'GFN2_S_conf': 0.4 * s_conf_gfn2 if s_conf_gfn2 else None, 
        'Minus_TS_gfn2_kcal': ts_term_gfn2,
        'Delta_gfn2_xtb_kcal': delta_gfn2_c2_xtb, 
        'GFN2_crest_xtb_energy': e_020_gfn2_c2_xtb_opt * H_TO_KCAL if e_020_gfn2_c2_xtb_opt else None,
        'Charge': charge, 
        'No_solvent_gfn2_ts': no_solvent_gfn2_ts,
        '001_protonated_sconf': ca_protonated_sconf,
        '001_protonated_ts': ca_protonated_ts,
        '001_protonated_no_solvent': ca_protonated_no_solvent_sconf, 
        'Delta_gfn2_xtb_protonated': delta_001_protonated, 
        'Delta_pm6_on_gfn2': delta_pm6_on_gfn2
    })

df = pd.DataFrame(data)

# Create DataFrame and Export
df.sort_values(by=['Target', 'Ligand'], inplace=True)
df.to_csv(os.path.join(TABLES_DIR, output_file), index=False)
print(f"Done! Check '{output_file}'.")