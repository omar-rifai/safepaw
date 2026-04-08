import os
import pandas as pd
import numpy as np
from backend.core.mappers.datasets_mappers.ptgpth_serializer import serialize_ptgpth_core
from backend.core.main import run_driver
from backend.core.utils.data_utils import get_results



import pandas as pd
import numpy as np
import os

def run_pthptg_experiments(
    dep_codes=["42"],
    ps_transfers=np.arange(0, 0.4, 0.05),
    ps_orths=[0, 0.04, 0.08, 0.12],
    mults=np.arange(1, 1.26, 0.05)
):

    main_path = "experiments/results_main_pthptg.csv"
    res_path = "experiments/results_resources_pthptg.csv"
    path_path = "experiments/results_pathways_pthptg.csv"

    # Clean previous files (optional but recommended)
    for p in [main_path, res_path, path_path]:
        if os.path.exists(p):
            os.remove(p)

    write_header = True

    for d in dep_codes:
        for p in ps_transfers:
            for p_orth in ps_orths:

                opt_params = {
                    "dep_code": d,
                    "p_transf": p,
                    "p_orth": p_orth,
                    "resources_mult": 1
                }

                params_system = serialize_ptgpth_core(
                    opt_params["dep_code"],
                    opt_params["p_transf"],
                    opt_params["p_orth"],
                    opt_params["resources_mult"],
                    False
                )

                status, objective, dict_results = run_driver(params_system)
                results = get_results(dict_results, params_system, objective)
                results = results | opt_params

                # ---- MAIN ----
                df_main = pd.DataFrame([{
                    "dep_code": results["dep_code"],
                    "p_transf": results["p_transf"],
                    "p_orth": results["p_orth"],
                    "resources_mult": results["resources_mult"],
                    "obj": results["obj"],
                    "n_patients": results["n_patients"],
                    "spi": results["spi"],
                    "qci": results["qci"]
                }])

                df_main.to_csv(main_path, mode="a", header=write_header, index=False)

                # ---- RESOURCES ----
                df_res = pd.DataFrame([
                    {
                        "dep_code": results["dep_code"],
                        "p_transf": results["p_transf"],
                        "p_orth": results["p_orth"],
                        "resources_mult": results["resources_mult"],
                        "resource": r,
                        "usage": val
                    }
                    for r, val in results["resources_usage"].items()
                ])

                df_res.to_csv(res_path, mode="a", header=write_header, index=False)

                # ---- PATHWAYS ----
                df_path = pd.DataFrame([
                    {
                        "dep_code": results["dep_code"],
                        "p_transf": results["p_transf"],
                        "p_orth": results["p_orth"],
                        "resources_mult": results["resources_mult"],
                        "pathway": pth,
                        "share": val
                    }
                    for pth, val in results["pathway_distribution"].items()
                ])

                df_path.to_csv(path_path, mode="a", header=write_header, index=False)

                write_header = False  # only once
                print(f"Done dep={d}, p={p:.2f}, p_orth={p_orth:.2f}, obj={results['obj']}")


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
    #run_experiements_burdett()
