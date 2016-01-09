FROM eliostvs/tomate

ENV PROJECT /code/

COPY ./ $PROJECT

WORKDIR $PROJECT

ENTRYPOINT ["make"]

CMD ["test"]
