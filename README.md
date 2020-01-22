# Books Review Website

This website has a list of books and provide some information about the books using the goodreads API as well as a user registration and authentication system.
Registered users will have the ability to search for books, leave reviews and rate for individual books

## Code style

- This project is written in python 3.
- Use Flask framework.
- PostgreSQL for database
- Use Bootstrap and CSS in front-end

## Database Installation on Heroku
### User postgresql on Heroku

1. Create App on Heroku.

2. On app’s “Overview” page, click the “Configure Add-ons” button.

3. In the “Add-ons” section of the page, type in and select “Heroku Postgres.

4. Choose the “Hobby Dev - Free” plan, which will give you access to a free PostgreSQL database that will support up to 10,000 rows of data. Click “Provision..

5. Click the “Heroku Postgres :: Database” link.

6. Click on “Settings”, and then “View Credentials.”. This information to hock my App to the DB

7. Use the Credentials to connect the application with the DB

## Create table on DB and Load the data to it

- run `python create_table.py` in order to execute SQL query to create the enrollments table
- run `python import.py` to read the books SCV file and load it to the database table

## Project Files

- create_table.py: Contain the SQL query to create books, users and reviews tables.

- import.py: Read the CSV books file and load the data into books table.

- app.py: application file

- wtform_fields: Contain wtforms class for each forms and validator

- Procfile: To  declare the process type, in this app the type is "web" and Identify thread operation

- requirements.txt: Contain a list of items to be installed, use the command to install all of items `pip install -r requirements.txt`
