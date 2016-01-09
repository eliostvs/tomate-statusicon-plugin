FROM eliostvs/tomate

ENV PROJECT /code/

RUN apt-get update -qq && apt-get install -yq gir1.2-gtk-3.0

COPY ./ $PROJECT

WORKDIR $PROJECT

ENTRYPOINT ["make"]

CMD ["test"]
