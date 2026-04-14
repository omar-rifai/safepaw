import os
import pandas as pd
import numpy as np
from backend.core.mappers.datasets_mappers.ptgpth_serializer import serialize_ptgpth_core
from backend.core.main import run_driver
from backend.core.utils.data_utils import get_results
from pathlib import Path

def experiment_exists(file_path: str, opt_params: dict)-> bool:
    """Return True if the experiment already saved in file_path"""
    if not Path(file_path).is_file():
        return False
    df = pd.read_csv(file_path)
    if not set(opt_params).issubset(df.columns):
        return False
    mask = pd.concat([pd.Series(np.isclose(pd.to_numeric(df[k], errors="coerce"), float(v)),index=df.index) for k, v in opt_params.items()],axis=1).all(axis=1)
    return mask.any()


def write_entry(file_path, df):
    """Write or append entry to file"""
    if Path(file_path).is_file():
        df.to_csv(file_path, mode="a", header = False, index=False)
    else:
        df.to_csv(file_path, mode="w", header = True, index=False)    


def run_pthptg_instance(opt_params, files_paths):
    """Run a single instance of the experiments with paramseters opt_params"""   
    if experiment_exists(files_paths["main"], opt_params) and experiment_exists(files_paths["resources"], opt_params) and \
        experiment_exists(files_paths["pathways"], opt_params):
        return
    
    params_system = serialize_ptgpth_core(opt_params["dep_code"], opt_params["p_transf"], opt_params["p_orth"], opt_params["resources_mult"],save_params=False)

    _, objective, dict_results = run_driver(params_system)
    results = get_results(dict_results, params_system, objective)
    results = results | opt_params
    
    base = {k: results[k] for k in ["dep_code", "p_transf", "p_orth", "resources_mult"]}

    df_main = pd.DataFrame([{**base, "obj": results["obj"], "n_patients": results["n_patients"],
                            "spi": results["spi"], "qci": results["qci"]}])
    write_entry(files_paths["main"], df_main)
    
    df_res = pd.DataFrame([{**base, "resource": r, "usage": val}
        for r, val in results["resources_usage"].items()
    ])
    write_entry(files_paths["resources"], df_res)

    df_path = pd.DataFrame([{**base,"pathway": pth, "share": val}
    for pth, val in results["pathway_distribution"].items()])
    
    write_entry(files_paths["pathways"], df_path)

    return


def run_pthptg_experiments(
    dep_codes= ["42"],
    ps_transfers= np.arange(0, 1.1, 0.1),
    ps_orths= [0, 0.04, 0.08, 0.12],
    mults= np.arange(1, 1.26, 0.05),
    clear_files = False
):

    files_paths = { "main": "experiments/results_main_pthptg.csv", "resources": "experiments/results_resources_pthptg.csv",
    "pathways": "experiments/results_pathways_pthptg.csv"}
    if clear_files:
        for p in files_paths.values():
            if os.path.exists(p):
                os.remove(p)

    for d in dep_codes:
        for p_orth in ps_orths:
            for p_transf in ps_transfers:
                opt_params = {"dep_code": d, "p_transf": p_transf, "p_orth": p_orth, "resources_mult": 1}
                run_pthptg_instance(opt_params, files_paths)
            
        for p_mult in mults:
            opt_params = {"dep_code": d, "p_transf": 1, "p_orth": 0, "resources_mult": p_mult}
            run_pthptg_instance(opt_params, files_paths)
            
    return 


def run_experiements_burdett():
    from backend.core.mappers.datasets_mappers.burdett_serializer import serialize_burdett_core
    p_transfers = np.arange(0, 1.1, 0.1)

    list_results = []

    for p in p_transfers:

        params_system = serialize_burdett_core(p, False)

        _, objective, dict_results = run_driver(params_system)
        results = get_results(dict_results, params_system, objective)
        results = {"p_transf": p} | results 
        list_results.append(results)


    df_main = pd.DataFrame([{"p_transf": d["p_transf"], "obj": d["obj"],"n_patients": d["n_patients"], "spi": d["spi"], "qci": d["qci"]} for d in list_results])
    df_res = pd.DataFrame([{"p_transf": d["p_transf"],"resource": r, "usage": val}\
                            for d in list_results for r, val in d["resources_usage"].items()])
    df_path = pd.DataFrame([{"p_transf": d["p_transf"], "pathway": p, "share": val}\
                            for d in list_results for p, val in d["pathway_distribution"].items()])

    df_main.to_csv("experiments/results_main_burdett.csv", index=False)
    df_res.to_csv("experiments/results_resources_burdett.csv",index=False)
    df_path.to_csv("experiments/results_pathways_burdett.csv", index=False)


if __name__ == "__main__":
    os.makedirs("experiments", exist_ok=True)
    run_pthptg_experiments()
    run_experiements_burdett()
