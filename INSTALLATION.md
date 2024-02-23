# Installation

This file describes the steps required to install and run `MyCryptoBot`, locally as well as remotely (on Heroku).

The first step will be to create a fork of this repository, so that you can make local changes and set 
your own build environment. The fork button can be found in the top right corner of the repo homepage.

## Local Installation

In order to run the bot locally, you'll need to have **`docker`** installed. You can follow 
the instructions [here](https://docs.docker.com/get-docker/) to install it. If you are on a linux based machine, verify that 
you can run docker commands without `sudo` privileges. If not, make sure you do the steps 
detailed in the [post-installation](https://docs.docker.com/engine/install/linux-postinstall/) page.

### Environment variables

The first thing we have to do is define the secret environment variables the app needs to function.

Create an `.env` file at the root of the project, copy the template env variables from 
.env.template. and enter the respective values. 

    $ touch .env
    $ cp .env.template .env

```shell
POSTGRES_DB # Name of the database
POSTGRES_USER # A username to access the database
POSTGRES_PASSWORD # A password to access the database
SECRET_KEY # A secret key to hash your application
BINANCE_API_KEY # Your personal Binance API key (check binance documentation)
BINANCE_API_SECRET # Your personal Binance API secret (check binance documentation)
BINANCE_API_KEY_TEST # Your personal Binance API key (binance testnet)
BINANCE_API_SECRET_TEST # Your personal Binance API secret (binance testnet)
USE_CLOUD_STORAGE # Either true or false - tells the app whether to use a cloud storage
AWS_ACCESS_KEY_ID # Your Personal AWS access key
AWS_SECRET_ACCESS_KEY # Your Personal AWS secret access key
AWS_BUCKET # The name of the S3 bucket where you'll keep your files
```

*Note: The remote cloud storage ones (AWS) are only required to be set if you want to have that option enabled for local usage. 
For remote deployment they will need to be set, as that is the only way to have file persistence on the servers.*

### Database

The database is handled by a postgres docker container as a service, which ensures maximum compatibility and isolation 
from local installations. When the database service is up, the database can be accessed on the local server on 
the port `5433`, instead of the usual `5432`.

In order to set up the database we need to start the services in detached mode via `docker-compose`, as follows:

    $ docker-compose up -d --build

This allows us to access the containers, in order to execute commands to migrate the schema and initialize the 
database. Execute the following commands:

    $ docker-compose exec model-service python database/manage.py migrate
    $ docker-compose exec model-service python database/initial_setup.py

In theory any of the web services can be used for the previous commands, but the other services will crash if 
there is no database yet.

Finally, we create a superuser, whose credentials we'll use in order to log in into the dashboard later on:

    $ docker-compose exec model-service python database/manage.py createsuperuser

If needed, one can access the `psql` console inside the database container with the following steps.
First we enter the database container with:

    $ docker-compose exec db bash

Once inside the container, we can enter the psql console with:

    $ psql -U $POSTGRES_USER

### Local Development

If you want to develop this app locally, whether to submit PR's or to make commits on your fork, it will be best to
have a local environment setup. For this it is best to use Poetry, which can be installed by following the 
instructions on this [page](https://python-poetry.org/docs/). Also, if you have a python version installed other 
than the accepted for this project, you might need to activate a different version. [pyenv](https://github.com/pyenv/pyenv) 
is a straightforward way of achieving that. 

At the root of the project, run: 

    $ poetry install
    $ poetry shell

Which will install the environment and activate the virtual environment. A `requirements.txt` file is also included 
if you want to use another virtual environment package. If you choose to do so, make sure you use a compatible 
python version (`>=3.7.1,<3.10`) when creating your virtual environment.

## Local Usage

Now that everything is set up correctly, we can restart all the services and start all the apps with the following command:

    $ docker-compose up --build

You can now go to [http://localhost:3000](http://localhost:3000) to open the dashboard app and log in 
using your superuser credentials.

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

    $ heroku create <YOUR_UNIQUE_DATA_APP_NAME> --region eu # Replace <YOUR_UNIQUE_DATA_APP_NAME> with a valid and unique name
    $ heroku create <YOUR_UNIQUE_MODEL_APP_NAME> --region eu # ...
    $ heroku create <YOUR_UNIQUE_EXECUTION_APP_NAME> --region eu # ...

#### Create the database

Run the following command to create a new database with a `Basic` plan and attach it to the `data` app.

    $ heroku addons:create heroku-postgresql:basic --app <YOUR_UNIQUE_DATA_APP_NAME>

This command will output the `name` of the database, which we'll need for the next commands. It should be something 
with a similar format to `postgresql-abcde-12345`. You can now run the following commands to attach the database
to the `model` and `execution` apps.

    $ heroku addons:attach <YOUR_DATABASE_NAME> -a <YOUR_UNIQUE_MODEL_APP_NAME> # Replace <YOUR_DATABASE_NAME> and <YOUR_UNIQUE_MODEL_APP_NAME>
    $ heroku addons:attach <YOUR_DATABASE_NAME> -a <YOUR_UNIQUE_EXECUTION_APP_NAME> # ...

#### Create Redis instance

Following a similar process as in the step before, we can create the redis instance with the following command:

    $ heroku addons:create heroku-redis:mini -a <YOUR_UNIQUE_DATA_APP_NAME>

The last command will output the name of your redis instance (with the same format as in `redis-abcde-12345`), 
which we can use on the following step to attach it to the other apps:

    $ heroku addons:attach <YOUR_REDIS_INSTANCE_NAME> -a my-crypto-bot-model
    $ heroku addons:attach <YOUR_REDIS_INSTANCE_NAME> -a my-crypto-bot-execution

#### Uploading the database

In order to upload the data we have locally into the remote database, run the following commands:

    $ heroku pg:reset --app <YOUR_UNIQUE_DATA_APP_NAME> PGUSER=<pg_username> PGPASSWORD=<pg_password> heroku pg:push mycryptobot DATABASE_URL --app <YOUR_UNIQUE_DATA_APP_NAME>

#### Starting the worker

Finally, running the following command will activate the worker dyno on the `model` app:

    $ heroku ps:scale worker=1 --app <YOUR_UNIQUE_MODEL_APP_NAME>

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
USE_CLOUD_STORAGE # Either true or false - tells the app whether to use a cloud storage
AWS_ACCESS_KEY_ID # Your Personal AWS access key
AWS_SECRET_ACCESS_KEY # Your Personal AWS secret access key
AWS_BUCKET # The name of the bucket where you'll keep you files
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

If the installation process went smoothly, you can now go `https://<YOUR_UNIQUE_DATA_APP_NAME>.herokuapp.com`, enter 
your superuser login details and you'll be ready to manage your app through the USER interface, just like when you were 
running things locally. Enjoy!
