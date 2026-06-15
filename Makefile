#################################################################################
# GLOBALS                                          								#
#################################################################################

PROJECT_NAME = vertex-deployer
PYTHON_VERSION = 3.10

#################################################################################
# Commands                                                     					#
#################################################################################


.PHONY: install
## Install Python Dependencies using uv
install:
	@uv venv --python $(PYTHON_VERSION) --clear
	@uv sync --all-groups
	@uv run pre-commit install -t pre-commit
	@uv run pre-commit install -t pre-push
	@uv run python -m ipykernel install --user --name $(PROJECT_NAME) --display-name "Python ($(PROJECT_NAME))"


.PHONY: install-requirements
## Install Python Dependencies
install-requirements:
	@uv sync --no-group dev --no-group docs


.PHONY: install-dev-requirements
## Install Python Dependencies for development
install-dev-requirements:
	@uv sync --group dev


.PHONY: update-requirements
## Update Python Dependencies (uv.lock)
update-requirements:
	@uv lock


.PHONY: format-code
## Format/lint all-files using pre-commit hooks (ruff, codespell, ...)
format-code:
	@uv run pre-commit run -a --hook-stage pre-push


.PHONY: run-unit-tests
## Run unit tests
run-unit-tests:
	@uv run pytest tests/unit_tests --cov=deployer --cov-report=term-missing -s -vv -W ignore:::pkg_resources

.PHONY: run-integration-tests
## Run integration tests
run-integration-tests:
	@uv run pytest tests/integration_tests -s -vv -W ignore:::pkg_resources


.PHONY: run-tests
## Run all tests
run-tests: run-unit-tests run-integration-tests


.PHONY: profile-cli
## Profile CLI using pyinstrument (https://pyinstrument.readthedocs.io/en/latest/index.html)
profile-cli:
	@echo "Check that you have pyinstrument installed: uv sync --extra profiling"
	@uv run pyinstrument -r html -o pyinstrument.html --from-path vertex-deployer --version
	@open pyinstrument.html


#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := help

# Inspired by <http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html>
# sed script explained:
# /^##/:
# 	* save line in hold space
# 	* purge line
# 	* Loop:
# 		* append newline + line to hold space
# 		* go to next line
# 		* if line starts with doc comment, strip comment character off and loop
# 	* remove target prerequisites
# 	* append hold space (+ newline) to line
# 	* replace newline plus comments by `---`
# 	* print line
# Separate expressions are necessary because labels cannot be delimited by
# semicolon; see <http://stackoverflow.com/a/11799865/1968>
.PHONY: help
help:
	@echo "$$(tput bold)Available rules:$$(tput sgr0)"
	@echo
	@sed -n -e "/^## / { \
		h; \
		s/.*//; \
		:doc" \
		-e "H; \
		n; \
		s/^## //; \
		t doc" \
		-e "s/:.*//; \
		G; \
		s/\\n## /---/; \
		s/\\n/ /g; \
		p; \
	}" ${MAKEFILE_LIST} \
	| LC_ALL='C' sort --ignore-case \
	| awk -F '---' \
		-v ncol=$$(tput cols) \
		-v indent=19 \
		-v col_on="$$(tput setaf 6)" \
		-v col_off="$$(tput sgr0)" \
	'{ \
		printf "%s%*s%s ", col_on, -indent, $$1, col_off; \
		n = split($$2, words, " "); \
		line_length = ncol - indent; \
		for (i = 1; i <= n; i++) { \
			line_length -= length(words[i]) + 1; \
			if (line_length <= 0) { \
				line_length = ncol - indent - length(words[i]) - 1; \
				printf "\n%*s ", -indent, " "; \
			} \
			printf "%s ", words[i]; \
		} \
		printf "\n"; \
	}' \
	| more $(shell test $(shell uname) = Darwin && echo '--no-init --raw-control-chars')
