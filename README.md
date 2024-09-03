# accunox
# Social Networking API

This project is a simple social networking API built using Django Rest Framework (DRF) and PostgreSQL. It includes functionalities like user signup/login, searching users, handling friend requests, and listing friends. The project is containerized using Docker.

## Table of Contents

- [Installation](#installation)
- [Running the Project](#running-the-project)
- [Postman Collection](#postman-collection)

## Installation
pip install -r requirements.txt

### Prerequisites

Before running this project, ensure you have the following installed on your system:

- Docker
- Docker Compose

### Clone the Repository

git clone https://github.com/kripalsinghparwal/accunox.git
cd project_socialize

### Running the Project
Use Docker Compose to build and run the application:
- docker-compose up --build

To set up the database schema, apply the Django migrations:
- docker-compose exec web python manage.py migrate

To create a superuser to access the Django admin:
- docker-compose exec web python manage.py createsuperuser

To run the project, simply start the Docker containers:
- docker-compose up

To stop the project:
- docker-compose down

### Running the project without docker
python manage.py runserver

### Postman collection link
- https://web.postman.co/workspace/262e2f10-e6fc-49f7-86d8-268b2ec0513f/collection/29179500-90469bc7-2d9c-45c6-808b-9f95b3feb012?action=share&source=email&creator=29179500&action_performed=google_login
