FROM node:13.12.0-alpine

# set working directory
WORKDIR /app

ENV DIRECTORY dashboard

# install app dependencies
COPY $DIRECTORY/package*.json ./
RUN npm clean-install

# add app
COPY ./$DIRECTORY ./

# start app
CMD ["npm", "start"]