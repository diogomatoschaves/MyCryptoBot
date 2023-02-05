# Installation

This file describes the steps required to install and run `MyCryptoBot`, locally as well as remotely (on Heroku).

The first step will be to create a fork of this repository, so that you can make local changes and set 
your own build environment. The fork button can be found in the top right corner of the repo homepage. 


## Local Installation

### Environment

The first thing we'll need to do is to set up a virtual environment, so that we can run the rest of the commands.
This project uses Poetry for package management, so if you don't have it installed yet you can follow the 
instructions on this [page](https://python-poetry.org/docs/).

At the root of the project, run: 
```shell
poetry install # it may take a while
poetry shell
```
Which will install the environment and activate the virtual environment.

At this stage we can also define the environment variables that the application will use.
Create an `.env` file at the root of the project, copy the template env variables from 
.env.template. and enter the respective values. 

```shell
touch .env
cp .env.template .env
```

### Database

This project uses PostgreSQL as a database engine in order to keep consistency between local development and production.
Therefore, it is assumed that PostgreSQL is installed on your machine. If not, please visit this
[page](https://www.postgresql.org/download/).

We must first create the database by entering into `psql` and executing a command there:
```shell
psql -U <pg_username> # Replace <pg_username> with your own postgres username
CREATE DATABASE <database_name>; # Enter the same name as the env variable $POSTGRES_DB
exit
```
In order to initialize the database, run the following commands:
```shell
python database/manage.py migrate
python database/initial_setup.py
```
This will load the schema onto the database and load some required initial data 
from binance. You can then create a superuser with the following command and follow the
instructions:

```shell
python database/manage.py createsuperuser
```

### Dashboard

Install the frontend dependencies with the following commands:

```shell
cd dashboard
npm install
```

## Local Usage

Now that everything is installed locally, we can run the whole system using `docker-compose`, as follows:
(click [here](https://docs.docker.com/get-docker/) if you don't have `docker` installed).

```shell
docker-compose up --build
```

You can now go to [http://localhost:3000](http://localhost:3000) to open the dashboard app. 



## Remote Installation (On Heroku)


### Heroku

The steps to deploy the apps onto remote servers will be using a heroku account, which you can sign up for 
[here](https://signup.heroku.com/) in case you don't have one already. You'll also need the Heroku CLI, which can be 
downloaded [here](https://devcenter.heroku.com/articles/heroku-cli)

**Note**: *This setup will incur some basic costs, which
can increase depending on the plans you choose for your infrastructure. As a minimum, you'll need the 
`Basic` database plan, the `Mini` Redis instance and the `Eco` Dynos plan. This has a minimum cost of 17$/month at the time
of writing.*

#### Create the apps

After you've logged in to the Heroku CLI, choose a name prefix for your app, and run the following commands to 
create the `data`, `model` and `execution` apps on Heroku.

```shell
heroku create <YOUR_UNIQUE_DATA_APP_NAME> --region eu # Replace <YOUR_UNIQUE_DATA_APP_NAME> with a valid and unique name
heroku create <YOUR_UNIQUE_MODEL_APP_NAME> --region eu # ...
heroku create <YOUR_UNIQUE_EXECUTION_APP_NAME> --region eu # ...
```

#### Create the database

Run the following command to create a new database with a `Basic` plan and attach it to the `data` app.

```shell
heroku addons:create heroku-postgresql:basic --app <YOUR_UNIQUE_DATA_APP_NAME>
```

This command will output the `name` of the database, which we'll need for the next commands. It should be something 
with a similar format to `postgresql-abcde-12345`. You can now run the following commands to attach the database
to the `model` and `execution` apps.

```shell
heroku addons:attach <YOUR_DATABASE_NAME> -a <YOUR_UNIQUE_MODEL_APP_NAME> # Replace <YOUR_DATABASE_NAME> and <YOUR_UNIQUE_MODEL_APP_NAME>
heroku addons:attach <YOUR_DATABASE_NAME> -a <YOUR_UNIQUE_EXECUTION_APP_NAME> # ...
```

#### Create Redis instance

Following a similar process as in the step before, we can create the redis instance with the following command:

```shell
heroku addons:create heroku-redis:mini -a <YOUR_UNIQUE_DATA_APP_NAME>
```

The last command will output the name of your redis instance (with the same format as in `redis-abcde-12345`), 
which we can use on the following step to attach it to the other apps:

```shell
heroku addons:attach <YOUR_REDIS_INSTANCE_NAME> -a my-crypto-bot-model
heroku addons:attach <YOUR_REDIS_INSTANCE_NAME> -a my-crypto-bot-execution
```

#### Uploading the database

In order to upload the data we have locally into the remote database, run the following commands:

```shell
heroku pg:reset --app <YOUR_UNIQUE_DATA_APP_NAME>
PGUSER=<pg_username> PGPASSWORD=<pg_password> heroku pg:push mycryptobot DATABASE_URL --app <YOUR_UNIQUE_DATA_APP_NAME>
```

Finally, running the following command will activate the worker dyno on the `model` app:
```shell
heroku ps:scale worker=1 --app <YOUR_UNIQUE_MODEL_APP_NAME>
```

### Github

On the page of your forked repository, navigate to
https://github.com/<your-github-username>/MyCryptoBot/settings/secrets/actions. There you'll need to create the following
repository secrets, which will be used for deploying the apps to production.

```shell
HEROKU_API_KEY # Can be found in the heroku account settings page 
HEROKU_EMAIL # The email address you use to login to Heroku
HEROKU_DATA_APP_NAME # The same name as <YOUR_UNIQUE_DATA_APP_NAME>
HEROKU_MODEL_APP_NAME # The same name as <YOUR_UNIQUE_MODEL_APP_NAME>
HEROKU_EXECUTION_APP_NAME # The same name as <YOUR_UNIQUE_EXECUTION_APP_NAME>
BINANCE_API_KEY # The API key associated with your live Binance account
BINANCE_API_SECRET # The API secret associated with your live Binance account
BINANCE_API_KEY_TEST # The API key associated with your test Binance account
BINANCE_API_SECRET_TEST # The API secret associated with your test Binance account
SECRET_KEY # An unique alphanumeric secret created by you
```

Then, navigate to the tab `Actions` and click on `I understand my workflows, go ahead and enable them`. We can now
trigger the workflows on Github actions required to deploy our apps onto Heroku. We can achieve that by sending a 
request to the Github API as shown below:

```shell

# - Replace <YOUR_GITHUB_TOKEN> with a github api token, see https://github.com/settings/tokens
# - Replace <YOUR_GITHUB_USERNAME> with your github username

curl \
  -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer <YOUR_GITHUB_TOKEN>"\
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/<YOUR_GITHUB_USERNAME>/MyCryptoBot/dispatches \
  -d '{"event_type":"on-demand-run","client_payload":{"testing":true,"build":true}}'
```

## Remote Usage

If the installation process went smoothly, you can now go https://<YOUR_UNIQUE_DATA_APP_NAME>.herokuapp.com, enter 
your superuser login details and you'll be ready to manage your app through the USER interface, just like when you were 
running things locally. Enjoy!