FROM python:3.11.1-alpine3.17

ENV CONTENTAPI_ENV=development

WORKDIR /app

COPY . .

RUN apk add --update make

RUN make install

EXPOSE 8000

CMD ["contentapi", "--host", "0.0.0.0", "--no-reload"]
