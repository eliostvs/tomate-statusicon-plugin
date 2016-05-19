FROM eliostvs/tomate

RUN apt-get update -qq && apt-get install -yq gir1.2-gtk-3.0

WORKDIR /code/

ENTRYPOINT ["make"]

CMD ["test"]
