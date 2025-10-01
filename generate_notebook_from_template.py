import nbformat as nbf
import re
import json
from tqdm import tqdm
VARIABLE_MAP = {
    "{{BOSSDB_URI}}": "uri", 
    "{{X_RANGE}}" : "xs", 
    "{{Y_RANGE}}" : "ys", 
    "{{Z_RANGE}}": "zs"
}

# Load the template notebook
with open("template/intern_demo.ipynb", "r") as f:
    template_nb = nbf.read(f, as_version=4)

# Get locations
with open('projects.json') as f:
    projects = json.load(f)

locations = []
for key, attr in projects.items():
    try:
        locations.append( (key, attr['locations'][0]))
    except Exception as e:
        print(key)
        continue 

# Function to replace the undefined variable with a specific value
def replace_variable(cell, values):
    if cell['cell_type'] == 'code':
        for vname, vkey in VARIABLE_MAP.items():
            # Convert ranges to slices
            if "RANGE" in  vname:
                val = f"{values[vkey][0]}:{values[vkey][1]}"
            else:
                val = values[vkey]
            cell['source'] = re.sub(vname, val, cell['source'])
    return cell

# Create new notebooks with the specific variable values
for key, location in tqdm(locations):
    new_nb = nbf.v4.new_notebook()
    for cell in template_nb['cells']:
        new_cell = replace_variable(cell.copy(), location)
        new_nb['cells'].append(new_cell)

    # Save the new notebook
    with open(f"notebooks/notebook_{key}.ipynb", "w") as f:
        nbf.write(new_nb, f)