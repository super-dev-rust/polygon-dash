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


## Testing
For testing is used Pytest

To test you should call tests manually, something like 
`pytest -s tests/test_dashboard_api.py::test_miner_detailed_endpoint`

