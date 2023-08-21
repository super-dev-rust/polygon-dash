## Polygon Dash

Polygon Dash contain two projects in a one repo:
 - Python backend app
 - Vue dashboard frontend


# Polygon Dashboard

## Usage
Polydash uses Poetry dependency manager.
 1. Install [Poetry](https://python-poetry.org/)
    ```shell
    curl -sSL https://install.python-poetry.org | python3 -
    ```
 2. Install dependencies
    ```shell
    poetry install
    ```
 3. Enter Poetry-managed Python environment
    ```shell
    poetry shell
    ```
 4. The shell should change to something like `(polydash-py3.10) ~/.../backend`. 
    Now run Polydash as Python module
    ```shell
    python -m polydash
    ```
## Frontend

Run script to deploy:

    ```
     ./deploy_frontend.sh
    ```


## Installing Node.js using NVM

### Ubuntu or MacOS:

1. Install NVM (Node Version Manager):

    ```sh
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash
    ```
    
    For MacOS run
    ```sh
    source .zshrc
    ```

2. Install the latest LTS version of Node.js using NVM:

    ```sh
    nvm install --lts
    ```

3. After running the above command, you can confirm your installation by checking the version of node:

    ```sh
    node -v
    ```



## Project Setup

```sh
npm install
```

### Compile and Hot-Reload for Development

```sh
npm run dev
```

### Compile and Minify for Production

```sh
npm run build
```

### Lint with [ESLint](https://eslint.org/)

```sh
npm run lint
```



## Run app in a docker

Run up and rebuild backed
```bash
docker compose up --build
```