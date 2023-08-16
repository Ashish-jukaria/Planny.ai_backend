# aiktech-backend

## Setting up the local environment.

### Clone the aiktech backend repo

`git clone git@github.com:phurti-grocery/aiktech-backend.git`

#### Create a virtualenv using following and give name as env

`virtualenv env`

#### Install all the dependencies

`pip3 install -r requirements.txt`

#### Apply all the migration-

- `python3 manage.py makemigrations`
- `python3 manage.py migrate`

## Docker Local Setup

### Env File Setup

- Create .env file
- Copy the ENV variables inside this file

### Docker create Image and run container
Run the following cmd to create image and start the containers <br />
`docker-compose --profile local up -d`

### Make Migrations
`docker exec -it phurti-local python manage.py makemigrations account contactus customer phurti shop operations notifications payments`

### Migrate
`docker exec -it phurti-local python manage.py migrate`
