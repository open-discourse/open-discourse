FROM node:12

WORKDIR /srv/
COPY package.json /srv/package.json
COPY yarn.lock /srv/yarn.lock

RUN yarn

COPY dist/ /srv/




EXPOSE 5000
EXPOSE 8080

CMD ["yarn", "start"]
