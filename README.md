# bossdb-collab-notebooks

**Collection of public notebooks for all projects on BossDB**

This repository generates Google Colab notebooks for every public BossDB project using nightly metadata exports from the BossDB metadata service. Each notebook includes dataset URIs and coordinate ranges for exploring BossDB data through `intern`.
1. Downloads the nightly metadata file `mongo-data.json` from S3
2. Fills a notebook template for each project
3. Writes the generated notebooks to `notebooks/`
4. Keeps them updated through nightly automation
5. Provides a CLI (`create-notebooks`) for local regeneration

## Automated Nightly Notebook Generation (GitHub Actions)
 
The workflow at `.github/workflows/generate-notebooks.yml` runs nightly at **05:20 UTC**, installing dependencies, running `create-notebooks`, and committing updated notebooks to `notebooks/`.

You can also trigger it manually via GitHub Actions → “Nightly Generate Colab Notebooks” → Run workflow.

### GitHub Secrets
`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `GITHUB_TOKEN` (provided automatically) are configured under **Settings → Secrets and Variables → Actions**

## Local Setup and Usage
Notebook generation can also be run locally:

```bash
# Install dependencies and create .venv
uv sync

# Install CLI command so "create-notebooks" becomes available
uv tool install .

# Activate environment
source .venv/bin/activate

# Run the generator locally
create-notebooks   # downloads metadata and writes in notebooks/

# Make sure `bossdb` AWS credentials are configured in your environment.
```
