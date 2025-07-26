FROM mcr.microsoft.com/devcontainers/python:3.9@sha256:c2aa5aa38e96eff7119c728d22149848ec7ae3934abef4ddf37adc5590d57353

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
