import os
import pandas as pd
import numpy as np
from backend.core.mappers.datasets_mappers.ptgpth_serializer import serialize_ptgpth_core
from backend.core.main import run_driver
from backend.core.utils.data_utils import get_results



def run_pthptg_experiments(dep_codes = ["42"], ps_transfers = np.arange(0, 1.1, 0.1), ps_orths=[0,0.04,0.08,0.12], mults= np.arange(1, 1.26, 0.05)):
    
    list_results = []
    
    for d in dep_codes:
        for p in ps_transfers:
            for p_orth in ps_orths:
                opt_params = {"dep_code": d, "p_transf": p, "p_orth": p_orth, "resources_mult": 1}

                params_system = serialize_ptgpth_core(opt_params["dep_code"],opt_params["p_transf"], opt_params["p_orth"], opt_params["resources_mult"], False)

                status, objective, dict_results = run_driver(params_system)
                results = get_results(dict_results, params_system, objective)
                results = results | opt_params
                list_results.append(results)

    for d in dep_codes:
        for mult in mults:
            opt_params = {"dep_code": d, "p_transf": 1, "p_orth": 0, "resources_mult": mult}

            params_system = serialize_ptgpth_core(opt_params["dep_code"],opt_params["p_transf"], opt_params["p_orth"], opt_params["resources_mult"], False)

            status, objective, dict_results = run_driver(params_system)
            results = get_results(dict_results, params_system, objective)
            results = results | opt_params
            list_results.append(results)
    

    df_main = pd.DataFrame([{"dep_code": d["dep_code"], "p_transf": d["p_transf"], "p_orth": d["p_orth"], "resources_mult": d["resources_mult"], "obj": d["obj"],
                             "n_patients": d["n_patients"], "spi": d["spi"], "qci": d["qci"]} for d in list_results])
    df_res = pd.DataFrame([{"dep_code": d["dep_code"], "p_transf": d["p_transf"], "p_orth": d["p_orth"], "resources_mult": d["resources_mult"], "resource": r, "usage": val}\
                            for d in list_results for r, val in d["resources_usage"].items()])
    df_path = pd.DataFrame([{"dep_code": d["dep_code"], "p_transf": d["p_transf"], "p_orth": d["p_orth"], "resources_mult": d["resources_mult"], "pathway": p, "share": val}\
                            for d in list_results for p, val in d["pathway_distribution"].items()])
    df_main.to_csv("experiments/results_main_pthptg.csv", index=False)
    df_res.to_csv("experiments/results_resources_pthptg.csv",index=False)
    df_path.to_csv("experiments/results_pathways_pthptg.csv", index=False)

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
