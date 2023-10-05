# CHANGELOG



## v0.0.1 (2023-10-03)

### Ci

* ci: update ci trigger policy (#45) ([`f1171d2`](https://github.com/artefactory/vertex-pipelines-deployer/commit/f1171d248ac329ee60f7d4100760f229105ac658))

### Fix

* fix: rm unused files (#5) ([`e220dc8`](https://github.com/artefactory/vertex-pipelines-deployer/commit/e220dc88d243e5c484e34b19edb10f639ae401ba))

* fix: readme typos (#4) ([`3ebcf4a`](https://github.com/artefactory/vertex-pipelines-deployer/commit/3ebcf4af0ddd318160c677b4ce38852796aa61b0))

### Unknown

* Release v0.1.0 (#48) ([`a3c18df`](https://github.com/artefactory/vertex-pipelines-deployer/commit/a3c18df36af02d64f64a493abbdfca18d5413def))

* Ci: Update Continuous Deployment (CD) Trigger Policy and Documentation (#47)

* ci: update cd trigger policy

* ci: update cd doc

* ci: test reusable ci

* ci: fix reusable ci ref

* ci: fix reusable ci

* ci: add need for CI to be completed

* ci: fix cd on main to be triggered only when pushing to main

* ci: update doc for cd ([`a08b581`](https://github.com/artefactory/vertex-pipelines-deployer/commit/a08b581f112e0a62b824e2a58248dfcdf313c7ac))

* Chore: prepare for release (#38)

* chore: add release drafter

* chore: add release drafter

* chore: add __init__ with __version__

* ci: update release action

* ci: update release action linting

* ci: add semantic release configuration

* doc: update CONTRIBUTING.md for release management ([`f59b795`](https://github.com/artefactory/vertex-pipelines-deployer/commit/f59b79583eb873422e8a754a581d33e009fa0fd3))

* Feat: make it python 38 39 compatible (#41)

* feat: typing back to 3.8

* doc: update readme with new python versions

* fix: update ci with new python versions ([`4e50c99`](https://github.com/artefactory/vertex-pipelines-deployer/commit/4e50c99481e819bf17fdb6c18fd79006db6732f7))

* Feat: add cli checks to ci (#40)

* feat: add cli integration tets to ci

* fix: use poetry to run commands in ci

* fix: fix paths before launching cli commands ([`9500a03`](https://github.com/artefactory/vertex-pipelines-deployer/commit/9500a036d63721e902a7ef34a300aef73e6e525c))

* Feat/add create and list commands (#39)

* feat: add comand list to list pipelines

* feat: add command create to cli and folder structure reorg

* enh: renamed pipelines_deployer.py -&gt; pipeline_deployer.py

* test: update tests

* doc: update readme

* enh: factorize get config paths ([`9b973bf`](https://github.com/artefactory/vertex-pipelines-deployer/commit/9b973bf7c5d5ff9d87b58bff14932dce38f25a43))

* Test: add unit tests (#31)

* test: add tests for make_enum_from_python_package

* test: make them work

* test: add pytest cov

* fix: make file command name to run tests

* tests: add tests create_model_from_pipeline ([`d01d60c`](https://github.com/artefactory/vertex-pipelines-deployer/commit/d01d60c89d2e136045fa64688d05a2c24085d159))

* Feat: pass artifacts as inputs (#28)

* feat: add argument input_artifacts_filepath to cli

* feat: add possibility to have python or json config files

* fix: update check command to support python files as config

* feat: allow to specify config path to check only one config file

* fix: change artifact type in pipeline dynamic model to allow valiation

* test: add tests to convert_artifact_type_to_str

* doc: update readme

* fix: change config file path option name

* enh: add and remove temp dir when checking pipelines ([`4d163bd`](https://github.com/artefactory/vertex-pipelines-deployer/commit/4d163bd5f68a27bbbc1f98c361bdf61c6a8083d1))

* Fix/deploy command (#36)

* fix: iam rights for service account

* fix: multiple formatting issues when uploading pipeline template

* fix: typo in readme instruction for gcs bucket iam binding ([`ead427f`](https://github.com/artefactory/vertex-pipelines-deployer/commit/ead427fb6628358393e658789a48a3078a4606b2))

* Feat/misc code improvements (#32)

* enh: use urljoin to make urls

* enh: add TagNotFoundError

* fix: vertex settings loading and errors

* enh: use decortor to check garhost in deployer

* enh: check experiment anme and check gar host

* feat: add missing gar host error

* feat: add message in no configs were checked for pipeline

* fix: path for pipeline should be relative not absolute

* fix: temp fix for vertex artifacts validation; arbitrary types allowed

* fix: upload does not work if lpp is not . ([`94c8061`](https://github.com/artefactory/vertex-pipelines-deployer/commit/94c8061241709be01b3bb54f672e5a3ad383babf))

* Feat: add command to check pipelines (#19)

* feat: add comment to check pipelines (import, compile, config files)

* enh: creation of pipeline model only once

* feat: use pydantic to validate configs and get all validation errors in one exception

* feat: add error if no pipelines found in check and log of pipelines / config checked

* feat: add specific validator for import pipeline computed field (works as a property)

* doc: update docstring for  command

* doc: update readme and add --all flag

* doc: update README table of contents links

* feat: add context manager to disable loguru logger temporarily ([`9f41c8e`](https://github.com/artefactory/vertex-pipelines-deployer/commit/9f41c8e1f5d96b7acbb8355da85e85c7a7c5ef51))

* Feat: add pr_agent (#29)

* feat: add pr_agent

* feat: update pr agent action name ([`92e1acb`](https://github.com/artefactory/vertex-pipelines-deployer/commit/92e1acb63e0a2eabc126e0f9d23f6b4e54a29da9))

* Fix: multiple issues raised in alpha testing (#27)

* fix: typos in code to make upload and run work

* doc: update readme

* doc: fix ruff and license badge

* doc: add why this tool in readme

* doc: add table of content

* enh: use --parameter-values-filepath instead of --config-name for clarity for user

* enh: put the vertex repository in example/

* doc: fix typo

* doc: update repo structure

* doc: update CONTRIBUTE.md ([`05deb15`](https://github.com/artefactory/vertex-pipelines-deployer/commit/05deb15d9ed8e881d771f1a607bcfa7ceccdbaf5))

* enh: use pydantic settings to get deployment variables from env file instead of os.environ (#24) ([`879c14a`](https://github.com/artefactory/vertex-pipelines-deployer/commit/879c14a168510e5388489e55b34399c9efe0eb45))

* Feat/switch logging to loguru (#20)

* enh: use loguru instead of python logging

* feat: add typer callback to set logging level ([`6c65c09`](https://github.com/artefactory/vertex-pipelines-deployer/commit/6c65c09ba1fa89bb0af99010744e79dbb161b485))

* Fix/inconsistencies in pipeline names (#18)

* fix: use pipelines names with underscore instead of hyphen

* fix: rename module different from package

* doc: update readme accordingly ([`7194c70`](https://github.com/artefactory/vertex-pipelines-deployer/commit/7194c70b59e42ec96de06a87c5e28098991cc239))

* Feat: switch cli to typer (#8)

* feat: switch cli to typer

* fix: add options short names + use enum value ([`267d169`](https://github.com/artefactory/vertex-pipelines-deployer/commit/267d1695891d4de10d4d27fff01560643b64e294))

* Feat: add constants file (#7)

* feat: add constants file

* fix: package name in pyproject.toml

* fix: pr template contributing link ([`54f59f7`](https://github.com/artefactory/vertex-pipelines-deployer/commit/54f59f7bd42c15ae1313753a78d97b06cdacf6c3))

* Chore: add issue and pr templates (#6)

* chore: add pr template

* chore: add issue templates

* chore: add CONTRIBUTING.md ([`b736c3a`](https://github.com/artefactory/vertex-pipelines-deployer/commit/b736c3ac93c715e3e57f55fae7a6d36429ddd5cd))

* Feat: vertex deployer (#3)

* feat/add vertex deployer and cli

* feat: add entrypoint for deployer

* fix: paths to pipeline folder and root path

* feat: add vertex foledr with dummy pipelines and example.env

* doc: update doc with how-to section ([`f00c231`](https://github.com/artefactory/vertex-pipelines-deployer/commit/f00c2314ae9b54b7226f58968fb9cf6d4f391707))

* Chore/update readme and add gitignore (#2)

* doc: update readme

* chore: add .gitignore ([`3070873`](https://github.com/artefactory/vertex-pipelines-deployer/commit/30708733d249770268a72ef3ba17f365a6121ad1))

* Chore: setup repo (#1)

* chore: setup repo

* fix: deployer is not a package error

* fix: rm pytest from prepush hooks

* chore: add to do list on the readme

* fix: add dummy test for the ci to pass ([`f154389`](https://github.com/artefactory/vertex-pipelines-deployer/commit/f154389359d10d143537fa0337bbcbb63727a480))

* Initial commit ([`cab9963`](https://github.com/artefactory/vertex-pipelines-deployer/commit/cab9963c573a4f56fba249722124c926deebdcd4))