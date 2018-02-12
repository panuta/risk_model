FROM node:9.4-alpine

RUN mkdir -p /app/client/

COPY ./client /app/client
RUN cd /app/client && yarn --pure-lockfile --frozen-lockfile

EXPOSE 8080
VOLUME /app/client
VOLUME /app/client/node_modules
VOLUME /app/.webpack

WORKDIR /app/client
CMD ["yarn", "run", "dev"]
