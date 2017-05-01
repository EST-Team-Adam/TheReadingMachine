# Setup


First of all, make sure you have the database `the_reading_machine.db`
in the `data` directory.

Then run the setup script

``sh
source setup.sh
```

This will setup `virtualenv`, install all the `thereadingmachine`
package, and an other dependency from `requirements.txt`.

All dependent `nltk` dataset will also be downloaded into the `data`
directory.

Next it will configure `airflow` and setup the airflow database
(`airflow.db`) that will store all information about the pipeline
scheduling.
