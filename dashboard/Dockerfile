FROM node:13.12.0-alpine

# set working directory
WORKDIR /app

# add `/app/node_modules/.bin` to $PATH
ENV PATH /app/node_modules/.bin:$PATH
ENV DIRECTORY dashboard

# install app dependencies
COPY $DIRECTORY/package.json $DIRECTORY/package-lock.json ./
RUN npm install --silent
RUN npm install react-scripts -g --silent

# add app
COPY ./$DIRECTORY ./

# start app
CMD ["npm", "start"]