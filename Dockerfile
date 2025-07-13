# TODO: work in progress

FROM python:3.12

# Packages:
# - R dependencies
# - Mysql client (technically mariadb)
# - Vim for editing in the container
RUN apt-get update && apt-get install -y \
      r-base-core r-base-dev \
      default-mysql-client \
      vim

RUN Rscript -e 'install.packages("growthrates", repos="https://cloud.r-project.org")' &&\
    Rscript -e 'install.packages("jsonlite", repos="https://cloud.r-project.org")'

# Copy microbetag utils
WORKDIR /home

# Expose mount directory for data
RUN mkdir ./var

COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

# Install a text editor
RUN apt-get install -y vim

COPY db/ ./db/
COPY db/config.toml.dockerfile db/config.toml

COPY app/ ./app/
COPY bin/ ./bin/
COPY docs/ ./docs/
COPY initialization/ ./initialization/
COPY scripts/ ./scripts/
COPY tests/ ./tests/

COPY main.py ./main.py
COPY pyproject.toml ./pyproject.toml
COPY .env ./.env
