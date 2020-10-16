FROM node:12

COPY package.json /srv/package.json
COPY yarn.lock /srv/yarn.lock
COPY src /srv/src/

WORKDIR /srv/

RUN yarn

EXPOSE 5000
EXPOSE 8080

CMD ["yarn", "dev"]
