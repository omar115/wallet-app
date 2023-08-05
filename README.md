# wallet-app

This is an assignment for creating restful endpoints for the Julo interview process.
The below information is the guideline for developers how to setup the applications locally.

---

# Option-1: Install dependencies in virtualenv and run the application
## Introduction

This guide will walk you through the process of setting up the environment and installing necessary dependencies to run this app.

---

## Prerequisites

- Download and install Python 3.9 or higher from [python.org](https://www.python.org/downloads/)
- Ensure you have pip installed with your Python

---

## Environment Setup

1. **Virtual Environment**:
    
    Execute the bash commands below to create a virtual environment :

    ```
    # Install virtualenv
    pip install virtualenv
    
    # Create a virtual environment (replace 'myenv' with a name you prefer)
    virtualenv myenv
    
    # Activate the virtual environment
    # On Windows:
    .\myenv\Scripts\activate

    # On MacOS/Linux:
    source myenv/bin/activate
    ```

2. **Clone the Repository**:

    ```
    git clone <repository-url>
    cd <repository-name>
    ```

---

## Install Dependencies

Activate the virtual environment and install the dependencies.

1. **Installing Requirements**:

    This project uses a `requirements.txt` file to list its dependencies. Install them using:

    ```
    pip install -r requirements.txt
    ```

---

## Running the FastAPI Application

After setting up the environment and installing the necessary dependencies, you can run the FastAPI application:
Execute the bash command in the root directory (e.g `wallet-app`)
```
uvicorn main:app --reload
```


# Option-2: Use Docker to run the application

## Introduction

The Dockerfile is added in the root directory. If Docker already installed in the system, then 
use the Dockerfile and docker commands to build the image and run the application locally.

---

## Build the docker image

In the root directory where the Docker file located, run the below command to build the Docker image.

```
docker build -t myapp .
```

---

## Run the docker image

Run the docker command so that the application can start and you can hit the api on browser

```
docker run -d -p 8000:8000 myapp
```

- now, go to browser and hit this URL then you can see the detail docs of endpoints.

```
http://localhost:8000/docs
```

---

## Note
Check this technical document to get an overview of my technical work.
[Technical Document of RESTful API development](https://drive.google.com/file/d/1ifJqPWgighAuiNvY30thyegoW4D-6V_R/view?usp=share_link)