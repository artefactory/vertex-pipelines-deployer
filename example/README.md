# `vertex-deployer` usage examples

This folder can be used as a template repo.

You can either copy paste snippets from different parts, or push it and test it with your own GCP project.

To do so, setup your gcp project and create your own repo from this folder:
```bash
# TODO: replace with your own repo url
git clone https://github.com/artefactory/vertex-pipelines-deployer.git
cd vertex-pipelines-deployer
cd example
git init
git add .
git commit -m "first commit"
git remote add origin "your_repo_url"
git push -u origin master
```

# Running the example

Running inside example/

Before the start, add this environment variable, so the pipelines are found: `export PYTHONPATH=.`

**Check pipeline validity**
```
vertex-deployer check dummy_pipeline
```

**Build the custom image**

Replace with the env file you wish to use:
```
set -a && source example.env && set +a && make build-base-image
```
