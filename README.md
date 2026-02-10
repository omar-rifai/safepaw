## Optimizing Case-Mix Planning at the Territorial Level: A Pathway-Centered and Resource-Aware Approach

The dependencies in this project are managed with `poetry`. Please follow the [official instructions](www.poetry.com) to install `poetry` on your system.


#### Getting started

In the project root directory, install the python dependencies with the following command:

````
 poetry install -P backend/ --no-root --only main
````

You can then run the experiments with the following command:

````
 poetry run -P backend/ python -m backend.core.main backend/data/<file_name.json>
````

Where `file_name.json` is one of the parameter files found in `backend/data`. The outputs are stored in `backend/data/temp`.


