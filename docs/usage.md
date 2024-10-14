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
        --skip-validation
    ```

    Check pipelines:
    <!-- termynal -->
    ```bash
    > vertex-deployer check --all
    2024-10-11 22:47:19.187 | INFO     | deployer.cli:check:411 - Checking pipelines ['dummy_pipeline', 'my_pipeline']
    ┏━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┓
    ┃ Status ┃ Pipeline       ┃ Config File ┃
    ┡━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━┩
    │   ✅   │ dummy_pipeline │ dev.yaml    │
    ├────────┼────────────────┼─────────────┤
    │   ✅   │ dummy_pipeline │ stg.yaml    │
    ├────────┼────────────────┼─────────────┤
    │   ✅   │ dummy_pipeline │ prd.yaml    │
    ├────────┼────────────────┼─────────────┤
    │   ✅   │ my_pipeline    │ dev.yaml    │
    ├────────┼────────────────┼─────────────┤
    │   ✅   │ my_pipeline    │ stg.yaml    │
    ├────────┼────────────────┼─────────────┤
    │   ✅   │ my_pipeline    │ prd.yaml    │
    └────────┴────────────────┴─────────────┘
    ```

<!-- termynal -->
```bash
> vertex-deployer init
Welcome to Vertex Deployer!
Do you want to instantly create the full vertex structure and templates
without configuration prompts? This will use the default settings. [y/n]:
> n
This command will help you getting fired up! 🔥

Do you want to configure the deployer? [y/n]:
> n
Do you want to build default folder structure [y/n]:
> y
Path 'deployer.env' already exists. Skipping creation of path.
Path 'requirements-vertex.txt' already exists. Skipping creation of path.

 Complete folder structure created ✨

your_project_root
┣━━ 📁 vertex
┃   ┣━━ 📁 configs
┃   ┃   ┗━━ your_pipeline
┃   ┃       ┗━━ config.type
┃   ┣━━ 📁 components
┃   ┃   ┗━━ your_component.py
┃   ┣━━ 📁 deployment
┃   ┃   ┣━━ Dockerfile
┃   ┃   ┣━━ cloudbuild_local.yaml
┃   ┃   ┗━━ build_base_image.sh
┃   ┣━━ 📁 lib
┃   ┃   ┗━━ your_lib.py
┃   ┗━━ 📁 pipelines
┃       ┗━━ your_pipeline.py
┣━━ deployer.env
┣━━ requirements-vertex.txt
┗━━ pyproject.toml


Do you want to create a pipeline? [y/n]:
> y
What is the name of the pipeline?: dummy_pipeline
What is the type of the config file? [yaml/json/toml/py]:
> yaml
Creating pipeline ['dummy_pipeline'] with config type: yaml

 Pipeline 'dummy_pipeline' created at 'vertex/pipelines/dummy_pipeline.py'
 with config files: ['vertex/configs/dummy_pipeline/dev.yaml', 'vertex/configs/dummy_pipeline/stg.yaml',
'vertex/configs/dummy_pipeline/prd.yaml']. ✨

All done ✨

Do you want to see some instructions on how to use the deployer [y/n]:
> y

Now that your deployer is configured, make sure that you're also done with the setup!
You can find all the instructions in the README.md file.

If your setup is complete you're ready to start building your pipelines! 🎉
Here are the commands you need to run to build your project:

1. Build the base image:
$ bash vertex/deployment/build_base_image.sh

2. Check all the pipelines:
$ vertex-deployer check --all

3. Deploy a pipeline and run it:
$ vertex-deployer deploy pipeline_name --run
If not set during configuration, you will need to provide the config path or name:
$ vertex-deployer deploy pipeline_name --cfp=path/to/your/config.type

4. Schedule a pipeline:
you can add the following flags to the deploy command if not set in your config:
--schedule --cron=cron_expression --scheduler-timezone=IANA_time_zone
```

--8<-- "README.md:usage"
