# TheReadingMachine - A Mean, Lean, Reading Machine

This repository contains the complete implementation of the
`thereadingmachine`, a program to scrap, process, score and model the
sentiment of news articles for the purpose of predicting the future
trend of commodity prices.


## Setup

First of all, make sure you have the database `the_reading_machine.db`
in the `data` directory.

Then run the setup script

```sh
source setup.sh
```

This will setup `virtualenv`, install all the `thereadingmachine`
package, and any other dependency from `requirements.txt`.

All dependent `nltk` dataset will also be downloaded into the `data`
directory.

Next it will configure `airflow` and setup the airflow database
(`airflow.db`) that will store all information about the pipeline
scheduling.


## Structure

The repository is structured as follow:

```
root/
  ├── airflow/
  ├── data/
  ├── pipeline/
  ├── thereadingmachine/
  ├── sandbox/  
  ├── ...
  └── requirements.txt
```

### airflow

This folder contains the configuration, logs, and the database for
running airflow.

When a new procedure is to be added to the pipeline, it needs to be
added to the [DAG file](airflow/dags/the_reading_machine.py).

### data

This folder contains all the data required. This includes the database
(`the_reading_machine.db`), and all supplementary data such as `nltk
corpus`.


### pipeline

All processes that will eventually be scheduled in the pipeline will
be implemented under this folder.

The standard structure is to have a sub-folder containing two
files. `controller.*` and `processor.*`. The `controller.*` will
contain all the class and function definitions, while the
`processor.*` file will load the definitions and perform the actual
processing.

This is designed for maximum flexibility during the development. The
`controller.*` class and functions will eventually be refactored into
`thereadingmachine`.


### thereadingmachine

This will eventually become a Python module when the codes in the
pipeline are refactored during the end of the phase of the
development.

### sandbox

Any old, obsolete, unused code will be moved here for future
reference.



## Starting and killing the pipeline

There are two scripts provided to `start` and `kill` the pipeline.

To start the pipeline, simply execute

```sh
./start_pipeline.sh
```

You can then navigate to `localhost:8080` to see the web interface of
the pipeline.

To kill the pipeline, simple enter the following in the command line.

```sh
./kill_pipeline.sh
```
