FROM mcr.microsoft.com/devcontainers/python:3.13@sha256:0aa711e570b306c02946cdda67587ce8c65978dbb65691341cbcfd4854dfcfff

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
