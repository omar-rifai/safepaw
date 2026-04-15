## Optimizing Case-Mix Planning at the Territorial Level: A Pathway-Centered and Resource-Aware Approach

The dependencies in this project are managed with `pixi`.  to install, you can run `curl -fsSL https://pixi.sh/install.sh | sh`


#### Getting started

In the project root directory, install the python dependencies with the following command:

````
 pixi install -m backend
````

You can then run the experiments with the following command:

````
 pixi run -m backend/ python -m backend.core.main experiments/<file_name.json>
````

Where `file_name.json` is one of the parameter files found in `experiments`. The outputs are stored in `experiments` as wells.


Datasets available on https://doi.org/10.5281/zenodo.19589604