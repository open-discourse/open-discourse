FROM node:20

RUN apt update \
  && apt install --no-install-recommends -y chromium

COPY . /srv

WORKDIR /srv/

RUN yarn

EXPOSE 5300

CMD ["yarn", "dev"]
