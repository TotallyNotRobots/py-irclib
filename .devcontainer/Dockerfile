FROM mcr.microsoft.com/devcontainers/python:3.14@sha256:2e0589f0725c951ac8ae0d7169784a9694f5818ec5264ed5231f23c6bf0ab7be

RUN \
    pipx uninstall mypy \
    && pipx uninstall pylint \
    && pipx uninstall pytest \
    && pipx uninstall flake8 \
    && pipx uninstall black

RUN pipx install commitizen \
    && pipx install hatch

RUN umask 0002 \
    && mkdir -p ${PIPX_BIN_DIR} \
    && chown -R "vscode:pipx" ${PIPX_HOME} \
    && chmod -R g+r+w "${PIPX_HOME}"

ENV SHELL=/bin/bash
