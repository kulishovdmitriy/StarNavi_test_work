## StarNavi application

- [Requirements](#requirements)
- [Installation](#installation)
- [Features](#features)
- [Setting up moderation with Google application](#setting-up-moderation-with-google-application)
- [Running Tests](#running-tests)
- [Additional Documentation](#additional-documentation)

## Requirements

- Python 3.10+
- FastAPI
- FastAPI User
- SQLAlchemy
- Pydantic
- Docker/docker-compose
- Postgres (database)
- GOOGLE_APPLICATION_CREDENTIALS
- TOKEN_AUTH

## Installation

1. Clone the repository:
```bash
    git clone https://github.com/kulishovdmitriy/StarNavi_test_work.git
    cd StarNavi_test_work
```

### To run on your machine:

1. Create a virtual environment and activate it:
```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use venv\Scripts\activate
```

2. Install the dependencies:
```bash
    pip install -r requirements.txt
```

Create a `.env` file based on the provided `.env.example` file:

    Copy the contents of .env.example to a new file named .env.
    Make sure to fill in any required values specific to your setup.

3. Run the server:
```bash
    python main.py
```
`The API will be available at http://localhost:8000`

### To run with Docker Compose
`(Important: It is assumed that Docker and Docker Compose are already installed on your compute)`

1. Docker-compose run:
```bash
    docker compose up --build
```

## Features

- **User Registration**: Users can register through the API.
- **User Login**: Users can log in to the system using JWT.
- **API for Managing Posts**: Add, edit, delete, and retrieve posts.
- **API for Managing Comments**: Add, edit, delete, and retrieve comments.
- **AI Moderation**: Check posts and comments for profanity or insults during creation.
- **Analytics**: Retrieve the number of comments over a specific period, aggregated by day.
    - Example URL: `/api/comments-daily-breakdown?date_from=2020-02-02&date_to=2022-02-15`
- **Automatic Responses**: Enable automatic replies to comments with user-configurable delays.

## Setting up moderation with Google application

To set up automatic moderation of posts and comments using `GOOGLE_APPLICATION`, follow these steps:

1. **Create a Google Cloud Account**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/).
   - Create a new project or select an existing one.

2. **Enable the API**:
   - Find and enable the necessary APIs for moderation, such as `Cloud Natural Language API` or others based on your needs.

3. **Create Credentials**:
   - In the "Credentials" section, create a new API key or download a credentials file (e.g., JSON).
   - Save this file on your computer.

4. **Set Up the Environment Variable**:
   - Set the environment variable `GOOGLE_APPLICATION_CREDENTIALS` to point to the path of the credentials file:
     ```bash
     export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/credentials.json"
     ```
   - On Windows, use:
     ```bash
     set GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\your\credentials.json"
     ```
     
5. **Obtain Access Token**:
   - Run the following command to get the access token:
     ```bash
     gcloud auth application-default print-access-token
     ```
   - If `gcloud` is not installed, you can follow these steps to install it:
   - Visit the [Google Cloud SDK installation page](https://cloud.google.com/sdk/docs/install).
   - Follow the instructions for your operating system.

`Now your API will utilize Google Cloud for content moderation. 

## Running Tests

The project uses `pytest` for running tests. Run all tests with the following command:
 ```bash
    pytest
 ```

## Additional Documentation

For detailed documentation, you can view it by executing the command:
```bash
    cd docs
    make html
```

This `README.md` provides clear information about the project and its functionality, which will help users better 
understand how to work with our API.