# Argentine Exchange Rates ELT

## Table of Contents
1. [Introduction](#introduction)
2. [Quickstart](#quickstart)
3. [Setup](#setup)
4. [Data Pipeline](#data-pipeline)
5. [DAGs](#dags)
6. [Alerting](#alerting)
7. [Methodology](#methodology)
8. [Documentation](#documentation)

## Introduction
This project implements an ELT (Extract, Load, Transform) pipeline to retrieve exchange rates for various cryptocurrencies and currencies in Argentina. The pipeline uses dbt for data transformation, Airflow DAGs for orchestration, and Amazon Redshift as data storage and computing.

The goal of this project was to monitor the premium among several exchange rates in Argentina in near real-time. Tracking the differences amoung the official exchange rate and the free market dollars is crucial because it reflects devaluation expectations. As economic agents make anticipatory decisions, any significant deviation can impact other economic variables, such as inflation. It is important to mention that the foreign exchange market remains controlled despite the new government, and the regulations and restrictions remain quite similar to those of the previous government.

## Quickstart
To get started, you'll need:

- [Astro CLI](https://docs.astronomer.io/astro/cli/overview) installed
- Docker

## Setup

1. Clone this repository:
    ```bash
    git clone https://github.com/diegorojasucv/argentine-exchange-rates-elt.git
    ```
2. Navigate into the project directory:
    ```bash
    cd argentine-exchange-rates-elt
    ```
3. Start the Airflow instance:
    ```bash
    astro dev start
    ```
4. Access the Airflow user interface in your browser at [http://localhost:8080](http://localhost:8080):
   - **Username**: `admin`
   - **Password**: `admin`
5. Configure a new connection in Airflow:
   - Go to **Admin** -> **Connections**
   - Create a new connection with the following details:
     - **Connection Id**: `redshift_conn`
     - **Connection Type**: `Amazon Redshift`
     - **Host**: `redshift-pda-cluster.cnuimntownzt.us-east-2.redshift.amazonaws.com`
     - **Database**: `pda`
     - **Port**: `5439`
     - **User**: `2024_diego_rojas`
     - **Password**: Contact me at [darb302@gmail.com](mailto:darb302@gmail.com) to obtain the password
6. Create a variable in Airflow:
   - **Variable Name**: `redshift_password`
   - **Value**: Use the Redshift password obtained in the previous step

7. After the above steps, unpuase all the DAGs and trigger the main one (`elt_argentina_exchange_rates`).

## Data Pipeline
### 🏦Source

For all sources, Python code was used to fetch data from APIs.

- **raw_bcra_indicators**: The official exchange rates (wholesale and retailer) were extracted using the Central Bank of Argentina's [API](https://www.bcra.gob.ar/BCRAyVos/catalogo-de-APIs-banco-central.asp).
- **Criptoya API**: This [API](https://criptoya.com/api) provided the crypto dollar (USDT), MEP (Electronic Payment Market), savings dollar, tourist dollar, and blue dollar (or black market). Two different endpoints were used:
  - **raw_usdt_ars_prices** (`/api/{coin}/{fiat}/{volume}`): The **USDT/ARS** pair for all existing exchanges in Argentina (around 30) was obtained here.
  - **raw_mep_ars_prices** (`/api/dolar`): As the MEP had a more complex structure, so it was extracted in a different model.
  - **raw_other_ars_prices** (`/api/dolar`): The rest of the other exchange rates (savings dollar, tourist dollar and blue (black) dollar market) were obtained here.

> It is important to note that these APIs provide the latest available information for each exchange rate, not historical price data.

### 🏗️ Transformations

Several stage models handle data transformations from the source. Below is an explanation of each:

- **stg_exchange_rates_cripto_usdt_ars**: The names of the exchanges were mapped to appropriate names using a new macro called `map_values_from_seed`. As in the previous case, new fields and some averages for bid and ask prices were added.
- **stg_exchange_rates_mep_usd_ars**: Renames were done, and new average fields were added.
- **stg_exchange_rates_official_usd_ars**: Only the indicators needed were filtered, renamed, and new fields were added. The API provided other economic indicators as well.
- **stg_exchange_rates_other_usd_ars**: A variable (dollars_descriptions) was created to rename some names and add descriptions for these variables. A `for` loop in Jinja was used to iterate over the variable, adhering to the DRY principle.
- **int_exchange_rates_unioned**: A model was created that joined all the stage models, allowing all the exchange rates needed to be in a single model. The `union_relations` macro from dbt facilitated this task.

### 📊 Analytics

-   **metrics_exchange_rates**: In this model, all the metrics of interest were created. Metrics measuring the gap amoung all exchange rates and official dollars (retailer and wholesale), MEP, Blue, etc., were created, along with boolean variables to check if the gaps exceeded certain thresholds.
### Data Lineage
![image](https://github.com/user-attachments/assets/9fb3fac8-9994-4483-8d84-063ebe5469b2)


## DAGs
### ETL
- **elt_argentina_exchange_rates.py**: Handles the extraction, transformation, and loading of Argentine exchange rate data from various sources.
- **dbt_trigger**: This script triggers the execution of dbt (Data Build Tool) models, facilitating data transformations in the ETL pipeline.
- **elt_criptoya_other.py**: Extracts and processes cryptocurrency exchange rates (except USDT) from CriptoYa API.
- **elt_criptoya_usdt.py**: Focuses on the extraction and transformation of USDT (Tether) exchange rates from CriptoYa API.
- **elt_criptoya_mep.py**: This ETL pipeline focuses on extracting MEP (USD) prices from the CriptoYa API.
- **elt_bcra_indicators.py**: This ETL pipeline is responsible for extracting, transforming, and loading BCRA (Central Bank of Argentina) indicators data.

### Functions
- **extract_data**: Fetches exchange rates from APIs.
- **transform_data**: Transforms raw data.
- **load_data**: Loads transformed data into a database.

## Alerting

The data pipeline implements an alerting system that notifies the status of ETL (Extract, Transform, Load) processes via email notifications. Below are the key components and how this system operates.

### Key Components

1. **Email Sending Functions (alert_email.py)**:
   - The `send_status_email` function is responsible for sending an email that indicates whether an ETL process was successful or has failed. 
   - This function can receive contextual information that will be included in the email in case of a failure.

2. **Failure Callback**:
   - The `on_failure_callback` function is used as a callback in Airflow to handle task errors. 
   - When a task fails, this function is invoked, which in turn calls `send_status_email` to notify the failure along with relevant information (such as the DAG, the specific task, the execution date, and the encountered error).

### How It Works

1. **Email Configuration**:
   - The system uses the Airflow variable `email_to_send_alert`, which was configured in the Airflow Variables.
   - An email connection (`smtp_default`) was created in the Airflow Connections.
2. **Sending Alerts**:
   - After completing a task in the DAG, its status (success or failure) is evaluated.
   - If the task is successful, a success email is sent informing that the ETL process has completed successfully.
   - If the task fails, an error email is sent that includes details about the error and the task's status.
3. **Example emails sent**:
    ![image](https://github.com/user-attachments/assets/b12e803c-b32d-4a44-b0b3-bf6c41304b0c)

## Methodology

### Tools Used
- **dbt**: For SQL transformations and data modeling.
- **Redshift**: Used for data storage and processing, enabling scalable computation.
- **Airflow**: Handles orchestration and scheduling of the data pipeline.

### Pre-commit Hooks

We have implemented a series of `pre-commit` hooks to ensure code quality before commits are made. These hooks help automate common checks and formatting tasks, ensuring that the code adheres to established standards.

The following hooks have been configured in the `.pre-commit-config.yaml` file:

- **YAML Linting** (`check-yaml`): Verifies that YAML files have correct syntax, which is essential for maintaining clean and error-free configuration files.
- **End of File Fixer** (`end-of-file-fixer`): Ensures that all files end with a newline, improving compatibility and code cleanliness.
- **Trailing Whitespace** (`trailing-whitespace`): Removes any trailing whitespace at the end of lines, which can often be added unintentionally.
- **Python Code Formatter (Black)** (`black`): Automatically formats Python files using `Black`, ensuring a consistent code style throughout the project.
- **Python Linter (Flake8)** (`flake8`): Detects syntax errors and style issues in Python code, improving readability and code quality.
- **Import Sorting (isort)** (`isort`): Automatically organizes imports in Python files, following a defined standard, which helps maintain clean and maintainable code.
- **Docstring Coverage (Interrogate)** (`interrogate`): Checks the coverage of docstrings in Python files, ensuring that at least 95% of the code is properly documented.

### Tests
- **Data Quality Tests**: Built-in dbt tests like `not_null`, `unique`, and `recency` were integrated to ensure the integrity and freshness of the data.
- **Unit Tests**: Custom tests were created to validate the correctness of key transformations, including date calculations, window functions, and conditional logic (`case when` statements). These tests ensure that all business logic is accurately reflected in the data pipeline.
- **Python Function Tests**: Python unit tests were implemented in the `test` folder to verify the consistency and accuracy of individual functions within the project.

### GitHub Actions
We implemented the following automated checks to maintain code quality and consistency:
- **Docstring Coverage**: Ensures that all Python functions and methods are properly documented.
- **Test Coverage**: Monitors the percentage of code covered by unit tests.
- **Python Code Formatter**: Applies consistent formatting to all Python code using `Black`.
- **SQL Linter**: Enforces SQL style and syntax rules using `SQLFluff`.

## Documentation

TBD
