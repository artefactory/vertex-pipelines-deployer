??? abstract "TL;DR"
    Install from GCS:
    ```bash
    export VERSION=0.2.1
    gsutil -m cp  gs://vertex-pipelines-deployer/vertex_deployer-$VERSION.tar.gz .
    pip install ./vertex_deployer-$VERSION.tar.gz
    ```

    In your requirements:
    ```bash
    file:my/path/to/vertex_deployer-$VERSION.tar.gz
    ```

--8<-- "README.md:installation"
