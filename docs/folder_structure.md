
??? abstract "TL;DR"
    You need to respect the following file structure from
    [Vertex Pipeline Starter Kit](https://github.com/artefactory/vertex-pipeline-starter-kit):
    ```bash
    vertex
    ├─ configs/
    │  └─ {pipeline_name}
    │     └─ {config_name}.json
    └─ pipelines/
        └─ {pipeline_name}.py
    ```

    A pipeline file looks like this:
    ```python
    ```python title="vertex/pipelines/dummy_pipeline.py"
    import kfp.dsl

    @kfp.dsl.pipeline()
    def dummy_pipeline():
        ...
    ```

    You can use either `.py`, `.toml` or `.json` files for your config files.

--8<-- "README.md:folder_structure"
