# Argentine Exchange Rates ELT

## Table of Contents
1. [Introduction](#introduction)
2. [Quickstart](#quickstart)
3. [Setup](#setup)
4. [Data Pipeline](#data-pipeline)
5. [Methodology](#methodology)

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

For all sources, we use the Python Source to fetch data from the API using a Python script.

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
- **int_exchange_rates_unioned**: A model was created that joined all the stage models, allowing all the exchange rates needed to be in a single model. The `union_relations` macro from dbt facilitated this task. Since the data were immutable event streams, an incremental model was created to append data to this table every run, maintaining historical information in this model.

### 📊 Analytics

-   **metrics_exchange_rates**: In this model, all the metrics of interest for sending alerts to Slack were created. Metrics measuring the gap amoung all exchange rates and official dollars (retailer and wholesale), MEP, Blue, etc., were created, along with boolean variables to check if the gaps exceeded certain thresholds. Additionally, price variations from the last available value were added to detect abrupt price changes. Metrics to capture arbitrage opportunities were also included.

### Data Lineage
TBD

## Methodology
### Tools Used
- dbt: SQL and transformations
- Redshift: Data storage and computing
- Airflow: Orchestration

### Github Actions
TBD
