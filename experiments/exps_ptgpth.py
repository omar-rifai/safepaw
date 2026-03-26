import os
import pandas as pd
import numpy as np
from backend.core.mappers.datasets_mappers.ptgpth_serializer import serialize_ptgpth_core
from backend.core.main import run_driver
from backend.core.utils.data_utils import get_results



def run_pthpth_experiments(dep_codes = ["42"], p_transfers = np.arange(0, 1.1, 0.1)):
    
    list_results = []
    
    for d in dep_codes:
        for p in p_transfers:
            opt_params = {"dep_code": d, "p_transf": p, "p_orth": 0, "resources_mult": 1}

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
    df_main.to_csv("experiments/results_main_ptgpth.csv", index=False)
    df_res.to_csv("experiments/results_resources_ptgpth.csv",index=False)
    df_path.to_csv("experiments/results_pathways.csv", index=False)

    return


if __name__ == "__main__":
    os.makedirs("experiments", exist_ok=True)
    run_pthpth_experiments()