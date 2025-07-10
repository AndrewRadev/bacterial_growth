# TODO: work in progress

FROM python:3.12

# # Install R
# WORKDIR /usr/local/lib/
# RUN wget https://ftp.cc.uoc.gr/mirrors/CRAN/src/base/R-3/R-3.6.0.tar.gz
# RUN tar -xf R-3.6.0.tar.gz
# WORKDIR /usr/local/lib/R-3.6.0
# RUN ./configure &&\
#     make &&\
#     make install

# RUN Rscript -e 'install.packages("dplyr", repos="https://cran.rstudio.com")' &&\
#     Rscript -e 'install.packages("RColorBrewer2", repos="https://cran.rstudio.com")'

# Install a text editor
# RUN apt-get install -y vim

# Set paths to mount
WORKDIR /mnt/
RUN chmod 777 /mnt/ &&\
    chmod g+s /mnt/

# Copy microbetag utils
WORKDIR /home

COPY app/ ./app/
COPY bin/ ./bin/
COPY db/ ./db/
COPY docs/ ./docs/
COPY initialization/ ./initialization/
COPY scripts/ ./scripts/
COPY tests/ ./tests/

COPY main.py ./main.py
COPY pyproject.toml ./pyproject.toml
COPY requirements.txt ./requirements.txt
COPY .env ./.env

# Expose mount directory for data
RUN mkdir ./var
VOLUME ./var

RUN pip install -r requirements.txt

# Set ports
EXPOSE 8081

CMD ["./bin/server"]
