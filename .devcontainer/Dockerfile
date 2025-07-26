FROM mcr.microsoft.com/devcontainers/python:3.10@sha256:a90782d21105d72b30d6eea6664da023d5cf3a5c57e4ef0da91351881105dee4

RUN \
    pipx uninstall mypy \
    && pipx uninstall pylint \
    && pipx uninstall pytest \
    && pipx uninstall flake8 \
    && pipx uninstall black \
    && pipx install commitizen \
    && pip install -U hatch hatch-containers

RUN su vscode -c "hatch config set dirs.env.virtual /home/vscode/.virtualenvs"

ENV SHELL /bin/bash
