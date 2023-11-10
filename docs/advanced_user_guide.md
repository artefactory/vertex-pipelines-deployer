!!! tip
    Add code provided in this page is available in the [repo example](https://github.com/artefactory/vertex-pipelines-deployer/tree/main/example).



## 💻 Dev: Compile and run to fasten your dev cycle


When developing a vertex pipeline locally, you may want to iterate quickly. The process is often the following:

1. write new code and test its integration in the pipeline workflow code in a notebook
2. script this new code in vertex/lib/
3. modify associated component(s) in `vertex/components` and pipelines in `vertex/pipelines`
4. run the pipeline with dev settings to test the new code on Vertex

The latest may include:

- rebuilding the base image
- compiling the pipeline
- running the pipeline


### 🏗️ Build base image

You can use this generic Dockerfile:

```Dockerfile
--8<-- "example/vertex/deployment/Dockerfile::3"
--8<-- "example/vertex/deployment/Dockerfile:10:10"
--8<-- "example/vertex/deployment/Dockerfile:16:"
```

Then build it with docker or Cloud Build. For the latest, here is a sample [cloudbuild.yaml](https://github.com/artefactory/vertex-pipelines-deployer/tree/main/example/vertex/deployment/cloudbuild_local.yaml):

```yaml
--8<-- "example/vertex/deployment/cloudbuild_local.yaml"
```

Then you can trigger the build manually using this make command:

```bash
export $(cat .env | xargs)
make build-base-image
```

This command includes the following:
```makefile
--8<-- "example/Makefile:build-base-image"
```

### 🚀 Compile and run

Now that you have a base image, you can compile your pipeline and trigger a run that will use the latest version of your docker base image

```bash
vertex-deployer deploy --compile --run --env-file .env --config-name my_config.json
```

## 🧪 CI: Check your pipelines and config integrity

### 💻 Check your pipelines locally

You can check pipelines integrity and config integrity using the following command:

```bash
vertex-deployer check --all
```

To check a specific pipeline:
```bash
vertex-deployer check my_pipeline
```

### ➕ Add to CI

You can add a github workflow checking your pipelines integrity using the following file:
```yaml
--8<-- "example/.github/workflows/check_pipelines.yaml"
```

### ➕ Add to pre-commit hooks

You can add a pre-commit hook checking your pipelines integrity using a local hook:
```yaml
--8<-- "example/.pre-commit-config.yaml"
```

## 🚀 CD: Deploy your pipelines in a standardized manner

Once you have a valid pipeline, you want to deploy it on Vertex. To automate deployment when merging to `develop` or `main`, you have multiple options.

- [use CloudBuild and CloudBuild triggers](#use-cloudbuild-trigger-preferred-option)
- [use Github Action to trigger CloudBuild job](#github-action-cloudbuild)
- [🚧 use Github Action only](#github-action-only)


!!! note
    To use cloudbuild for CD, please update you Dockerfile with all these arguments.
    This will allow you to use `vertex-deployer` from your base image in CloudBuild.

    ```Dockerfile
    --8<-- "example/vertex/deployment/Dockerfile"
    ```

### ☁️ CloudBuild

You can use the following [cloudbuild.yaml](https://github.com/artefactory/vertex-pipelines-deployer/tree/main/example/vertex/deployment/cloudbuild_cd.yaml) to trigger a deployment on Vertex when merging to `develop` or `main`:

```yaml
--8<-- "example/vertex/deployment/cloudbuild_cd.yaml"
```

#### 🎯 Use CloudBuild trigger \[PREFERRED OPTION\]

Then, you'll need to link your repo to CloudBuild and create a trigger for each branch you want to deploy on Vertex.
The documentation to link your repo is available [here](https://cloud.google.com/build/docs/automating-builds/github/connect-repo-github?generation=2nd-gen#console).

Then, you can create create a trigger using this make command:

```bash
export $(cat .env | xargs)
make create-trigger-cd
```

This command includes the following:
```makefile
--8<-- "example/Makefile:create-trigger-cd"
```

#### 🐙 Github Action + CloudBuild

You can also use Github Action to trigger CloudBuild job. You'll need to setup GCp authentication from your repo using Workload Identity Federation.

```yaml
--8<-- "example/.github/workflows/deploy_pipelines.yaml"
```

### 🚧 Github Action only

!!! warning
    This is a work in progress. Please use CloudBuild for CD.
    Docker build and push to GCR example is not yet implemented.
