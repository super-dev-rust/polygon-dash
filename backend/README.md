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
    Now run Polydash as Python module (for Polygon mode)
    ```shell
    python -m polydash --settings polygon.yaml polygon
    ```
    (for Cardano mode)
    ```shell
    python -m polydash --settings cardano.yaml cardano
    ```
    
### Important note on DB usage
Be extremely careful about setting the database in the config file:
all the run modes (both Polygon and Cardano) use the same table names.
Therefore, pointing them to the same database, **will corrupt your data**,
and you'll have to either do a (boring) Cinderella cosplay by separating Cardano data from Polygon
data in your DB, or start with a fresh DB(s).

So, when starting the databases, be extra sure to **use different DBs for different blockchain modes**.


## Testing
For testing is used Pytest

To test you should call tests manually, something like 
`pytest -s tests/test_dashboard_api.py::test_miner_detailed_endpoint`

