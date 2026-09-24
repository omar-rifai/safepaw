import pulp

def read_inputs(file_params_system):
    import json
    with open(file_params_system, "r") as f:
        params_system = json.load(f)

    return params_system

def get_var(curr_var, row, list_dims):
    v = curr_var[row["group"]][row["pathway"]]
    if "region" in list_dims:
        v = v[row["region"]]
    if "activity" in list_dims:
        v = v[row["activity"]]
    if "facility" in list_dims:
        v = v[row["facility"]]
    if "resource" in list_dims:
        v = v[row["resource"]]
    return pulp.value(v)


def hl_to_records(var_hl, params_system):
    """For variables only indexed by h (facilities) and l (resources) (e.g Delta, z, s)"""
    return [
        {"facility": h, "resource": l, "value": pulp.value(var_hl[h][l])}
        for h in params_system["H"]
        for l in params_system["L"]
    ]

def vars_to_records(curr_var, list_dims, params_system):
    records = []
    for g in params_system["G"]:
        for k in params_system["K_idx"][g]:
            for r in (params_system["R"] if "region" in list_dims else [None]):
                for a in (params_system["A_idx"][g][k] if "activity" in list_dims else [None]):
                    for h in (params_system["H"] if "facility" in list_dims else [None]):
                        for l in (params_system["L"] if "resource" in list_dims else [None]):
                                row = { "group": g, "pathway": k}
                                if "region" in list_dims: row["region"] = r
                                if "activity" in list_dims: row["activity"] = a
                                if "facility" in list_dims: row["facility"] = h
                                if "resource" in list_dims: row["resource"]= l
                                row["value"] = get_var(curr_var, row, list_dims)
                                records.append(row)
    return records


def package_results(vars_system, params_system):
    dict_results = {
        "P_gkrah": vars_to_records(vars_system.P, ["group","pathway","region","activity","facility"], params_system),
        "Q_gkrah": vars_to_records(vars_system.Q, ["group","pathway","region","activity","facility"], params_system),
        "P_gkr": vars_to_records(vars_system.P_gkr, ["group","pathway","region"], params_system),
        "P_gk": vars_to_records(vars_system.P_gk, ["group","pathway"], params_system),
        "Delta_plus" : hl_to_records(vars_system.Delta_plus, params_system),
        "Delta_moins": hl_to_records(vars_system.Delta_moins, params_system),
        "z_hl_plus": hl_to_records(vars_system.z_hl_plus, params_system),
        "z_hl_moins": hl_to_records(vars_system.z_hl_moins, params_system),
        "s_hl": hl_to_records(vars_system.s_hl, params_system)
    }
    return dict_results

