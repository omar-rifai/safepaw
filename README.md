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

Where `file_name.json` is one of the parameter files found in `experiments`.

> [!TIP]
> Ready-to-use anonymized parameter files can be found on the following link : https://doi.org/10.5281/zenodo.20051926

 The outputs are stored in `experiments` as wells. Open source datasets on French maternity Facilities are available for testing using: 
````
 pixi run -m backend python -m backend.core.mappers.datasets_mappers.maternite_serializer --dep-code <dep_code> (or --region-code <region_code>)
````

where `<dep_code>` and `<region_code>` are respectively, french department and region code


