#################################################################################
# GLOBALS                                          								#
#################################################################################

PROJECT_NAME = vertex-deployer
PYTHON_VERSION = 3.10

#################################################################################
# Commands                                                     					#
#################################################################################


.PHONY: download-poetry
## Download poetry
download-poetry:
	curl -sSL https://install.python-poetry.org | python3 -


.PHONY: install
## Install Python Dependencies using poetry
install:
	@poetry env use $(PYTHON_VERSION)
	@poetry lock -n
	@poetry install -n
	@poetry run pre-commit install -t pre-commit -t pre-push


.PHONY: install-requirements
## Install Python Dependencies
install-requirements:
	@poetry install -n


.PHONY: install-dev-requirements
## Install Python Dependencies for development
install-dev-requirements:
	@poetry install -n --with dev


.PHONY: update-requirements
## Update Python Dependencies (requirements.txt and requirements-dev.txt)
update-requirements:
	@poetry lock -n


.PHONY: format-code
## Format/lint all-files using pre-commit hooks (black, flake8, isort, ...)
format-code:
	@poetry run pre-commit run -a


.PHONY: run-test
## Run unit tests
run-test:
	@poetry run pytest


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
