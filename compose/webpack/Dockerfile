FROM node:9.4-alpine

COPY client/package.json client/yarn.lock /tmp/

# Install packages
RUN cd /tmp && yarn --pure-lockfile --frozen-lockfile
RUN mkdir -p /app/client/ && cd /app/client && ln -s /tmp/node_modules

# Copy the code
ADD . /app

EXPOSE 8080
VOLUME /app/.webpack

WORKDIR /app/client
CMD ["yarn", "run", "dev"]
