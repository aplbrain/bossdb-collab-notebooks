#!/usr/bin/env python3

import os
import json
import re
import boto3
import nbformat as nbf
from nbformat import validate
from nbformat.validator import normalize
from argparse import ArgumentParser
from tqdm import tqdm

# Notebook variable substitution map
VARIABLE_MAP = {
    "{{BOSSDB_URI}}": "uri",
    "{{X_RANGE}}": "xs",
    "{{Y_RANGE}}": "ys",
    "{{Z_RANGE}}": "zs",
}

DEFAULT_BUCKET = "bossdb-metadata-snapshot"
DEFAULT_OBJECT_KEY = "mongo-data.json"

def parse():
    parser = ArgumentParser(description="Generate notebooks using mongo-data.json from S3.")
    parser.add_argument(
        "--template", "-t",
        default="template/intern_demo.ipynb",
        help="Path to the template notebook"
    )
    parser.add_argument(
        "--outdir", "-o",
        default="notebooks",
        help="Directory to output notebooks"
    )
    parser.add_argument(
        "--bucket",
        default=os.environ.get("S3_BUCKET", DEFAULT_BUCKET),
        help="S3 bucket containing mongo-data.json"
    )
    parser.add_argument(
        "--key",
        default=os.environ.get("S3_OBJECT_KEY", DEFAULT_OBJECT_KEY),
        help="S3 object key for metadata JSON"
    )
    return parser.parse_args()


def replace_variable(cell, values):
    """Replace variable placeholders inside a notebook code cell."""
    if cell["cell_type"] == "code":
        for template_var, key in VARIABLE_MAP.items():
            if "RANGE" in template_var:
                start, end = values[key]
                replacement = f"{start}:{end}"
            else:
                replacement = values[key]

            cell["source"] = re.sub(template_var, str(replacement), cell["source"])
    return cell


def main():
    args = parse()

    # Load template
    with open(args.template, "r") as f:
        template_nb = nbf.read(f, as_version=4)

    os.makedirs(args.outdir, exist_ok=True)

    # Download metadata from S3
    print(f"Downloading {args.key} from bucket {args.bucket}...")
    s3 = boto3.client("s3")
    tmp_path = "/tmp/mongo-data.json"
    s3.download_file(args.bucket, args.key, tmp_path)

    with open(tmp_path, "r") as f:
        projects = json.load(f)

    # Create notebooks
    print("Generating notebooks...")

    for project_id, meta in tqdm(projects.items()):
        if "locations" not in meta or not meta["locations"]:
            continue

        location = meta["locations"][0]

        new_nb = nbf.v4.new_notebook()

        for cell in template_nb["cells"]:
            new_nb["cells"].append(replace_variable(cell.copy(), location))

        normalize(new_nb)
        validate(new_nb)

        out = os.path.join(args.outdir, f"notebook_{project_id}.ipynb")
        with open(out, "w") as f:
            nbf.write(new_nb, f)

    print("Notebook generation complete.")


if __name__ == "__main__":
    main()
