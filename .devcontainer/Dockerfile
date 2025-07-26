FROM mcr.microsoft.com/devcontainers/python:3.11@sha256:b726eb94f42fcddb10056835f2c474c9f9e12e717ba2b2d2f9a8b1d78feeb68b

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
