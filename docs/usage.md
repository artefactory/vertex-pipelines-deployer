??? abstract "TL;DR"
    Deploy pipeline:
    ```bash
    vertex-deployer deploy dummy_pipeline \
        --compile \
        --upload \
        --run \
        --env-file example.env \
        --local-package-path . \
        --tags my-tag \
        --config-filepath vertex/configs/dummy_pipeline/config_test.json \
        --experiment-name my-experiment \
        --enable-caching \
        -y
    ```

    Check pipelines:
    ```bash
    vertex-deployer check --all
    ```

--8<-- "README.md:usage"
