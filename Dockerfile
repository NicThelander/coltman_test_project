FROM postgres:15
ADD ./01.sql /docker-entrypoint-initdb.d/
