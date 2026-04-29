import pandas as pd
from backend.core.data_models.input_models import Facility, Region, Instance, Resource, PatientsGroup, Activity, Pathway
from lark import Lark, Transformer, UnexpectedCharacters
import re
import typer

hospitals = {
    "BPH": {"name": "Brisbane Private Hospital", "coordinates": [153.0226, -27.4646]},
    "GCUH": {"name": "Gold Coast University Hospital", "coordinates": [153.3819, -27.9595]},
    "GCPR": {"name": "Gold Coast Private", "coordinates": [153.3853, -27.9622]},
    "JFN": {"name": "John Flynn Private", "coordinates": [153.488510, -28.153879]},
    "LOG": {"name": "Logan Hospital", "coordinates": [153.1418, -27.6700]},
    "NW": {"name": "North West Hospital", "coordinates": [152.9929, -27.3940]},
    "PA": {"name": "Princess Alexandra", "coordinates": [153.0332, -27.4990]},
    "PIN": {"name": "Pindara Hospital", "coordinates": [153.390936, -28.0070776]},
    "PRCH": {"name": "Prince Charles Hospital", "coordinates": [153.0234, -27.3899]},
    "QE2": {"name": "Queen Elizabeth 2 Jubilee", "coordinates": [153.0489, -27.5594]},
    "RBWH": {"name": "Royal Brisbane & Women's", "coordinates": [153.0282, -27.4471]},
    "RED": {"name": "Redland Hospital", "coordinates": [153.2521, -27.5405]},
    "ROB": {"name": "Robina Hospital", "coordinates": [153.3760, -28.0711]},
    "STAN": {"name": "St Andrews", "coordinates": [153.021088, -27.461105]},
    "WES": {"name": "West Hospital", "coordinates": [152.9978, -27.4778]}
}


def get_Regions(data: dict) -> list[Region]:
    """Creates Region instance"""
    list_regions = [Region(region_id="r0",
                           coordinates=[],
                           facilities_affinity=_get_region_affinities(data))]
    return list_regions


def _get_region_affinities(data, default_affinity=1.0):
    """Returns the affinity of the region for each facility"""
    facilities_idx = [h for inner in data["WH"] for h in inner]
    w_rh = {fid: default_affinity for fid in facilities_idx}
    return w_rh

def get_Facilities(data: dict, df_pathways : pd.DataFrame, perc_allowed: float= 0) -> list[Facility]:
    """Creates Facility objects corresponding to unique wards"""
    list_facilities = []
    df_resources =  _get_df_resources(data)
    wards = [h for inner in data["WH"] for h in inner]
    b_hl_in, b_hl_out = _get_facilities_max_transfers(wards, perc_allowed)
    for fid in wards:
        list_facilities.append(Facility(
                facility_id = fid ,
                facility_name = _get_facility_name(fid) ,
                region_id = "" ,
                coordinates =  _get_facility_coordinates(fid) , 
                resources_capacity =  _get_facility_capacities(fid, df_resources),
                max_transferable_in = b_hl_in[fid],
                max_transferable_out = b_hl_out[fid],
                linked_facilities = [x for x in wards if x.split("_")[0] == fid.split("_")[0]],
                available_pathways= _get_facility_pathways(df_pathways, fid))
        )

    return list_facilities

def _get_facilities_max_transfers(facilities, perc_allowed):
    resources = ["cap_OT", "cap_ICU", "cap_Ward"]
    b_hl_in = {h: {r: 0 if perc_allowed == 0 else 2 for r in resources } for h in facilities}
    b_hl_out = {h: {r: perc_allowed for r in resources} for h in facilities}
    return b_hl_in, b_hl_out

def _get_facility_capacities(fid: str, df_resources: pd.DataFrame) -> dict:
    capacities = {"cap_OT": 0, "cap_ICU": 0, "cap_Ward": 0}
    x = df_resources[df_resources["facility"]==fid][["cap"]].iloc[0]
    r_type = df_resources[df_resources["facility"]==fid]["type"].iloc[0]
    capacities["cap_" + str(r_type)] =  int(x["cap"])
    return capacities

def _get_facility_name(fid: str) -> str:
    return hospitals[fid.split("_")[0]]["name"]

def _get_facility_coordinates(fid: str) -> str:
    return hospitals[fid.split("_")[0]]["coordinates"]


def _get_facility_pathways(df_pathways: pd.DataFrame, fid) -> list:
    """ get the pathways associated with a facility"""
    pathways = list(df_pathways[df_pathways["facility_id"] == fid]["pathway_id"].unique())
    return pathways


def get_Instance(data: dict, df_pathways: pd.DataFrame) -> Instance:
    """Returns object to store optimization instance parameters. Most variables are stores in a global config.yaml file """
   
    return Instance(
            d_total = 1.0,
            d_gr = _get_demand_lower_bound(df_pathways, data),
            under_q_g = _get_under_q_g(data),
            over_q_g = {g: 1.0 for i,g in enumerate(data["G"])} ,
            under_q_gu = _get_under_over_q_gu(data, df_pathways),
            over_q_gu = _get_under_over_q_gu(data, df_pathways),
            p_transf = 1.0,
            delta_l = {"cap_OT": 12.0, "cap_ICU": 12.0,"cap_Ward": 12.0},
            alpha = 0
        )

def _get_under_q_g(data:dict) -> dict:
    G = data["G"]
    values = [round(data["casemix"][i]/100.,4) for i in range(len(G))]
    under_q_g = {g: v for g, v in zip(G, values)}
    return under_q_g

def _get_under_over_q_gu(data: dict, df_pathways: pd.DataFrame):
    """Return the values for under and over q_gu as the submix for that particular pathway (=DRGs)"""
    unique_groups = data["G"]
    lines = 0
    under_q_gu = {}
    for _, g in enumerate(unique_groups):
        under_q_gu[g] = {}
        list_qualities = df_pathways[df_pathways["patient_group_id"]==g]["pathway_idx"].unique()
        for j, u in enumerate(list_qualities):
            if j < len(list_qualities) - 1:
                value = round(data["submix"][lines + j]/100.,4)
                under_q_gu[g][str(u)]  = value
            else:
                last_value = 1 - sum(under_q_gu[g].values())
                under_q_gu[g][str(u)] = last_value
            
            
        lines += len(df_pathways[df_pathways["patient_group_id"]==g]["pathway_idx"].unique())
    return under_q_gu


def _get_demand_lower_bound(df_pathways, data: dict) -> dict:
    groups = list(df_pathways["patient_group_id"].unique())
    regions = ["r0"]
    d_gr = {g: {r: 0 for r in regions } for g in groups}
    return d_gr


def get_Resources() -> list[Resource]:
    """Creates Resource object with id for unique """
    resources = ["OT", "ICU", "Ward"]
    return [Resource(resource_id="cap_"+r) for r in resources]



def get_PatientGroups(data: dict) -> list[PatientsGroup]:
    """Creates PatientGroups """
    list_patientsGroups = []
    df_pathways = _get_df_pathways(data)
    for gid in data["G"]:
        group_pathways = _get_group_pathways(df_pathways, gid)
        list_patientsGroups.append(PatientsGroup(group_id=gid, possible_pathways=group_pathways))
    return list_patientsGroups


def _get_group_pathways(df_pathways:pd.DataFrame, gid)->list:
    """get list of possible pathways for group with id gid"""
    pathways = list(df_pathways[df_pathways["patient_group_id"] == gid]["pathway_id"].unique())
    return pathways

    

def get_Activities(df_pathways : pd.DataFrame) -> list[Activity]:
    """ get activities """
    activities = {1: {"name":"OT" , "transferable": True, "transfer_to":"ICU"},
                  2: {"name": "ICU", "transferable": True, "transfer_to":"Ward"},
                  3: {"name": "Ward", "transferable": False, "transfer_to":""}}
    
    df_pathways["pathway_activity"] = df_pathways["resource_id"].map(activities).str["name"]
    df_activities = df_pathways[["pathway_id", "patient_group_id", "resource_id", "resource_consumption", "pathway_activity"]].drop_duplicates()

    list_activities = []
    for _, row in df_activities.iterrows():
        list_activities.append(
            Activity(activity_id= row["pathway_activity"], associated_pathway=row["pathway_id"],
                        associated_group=row["patient_group_id"], transferable=_get_transferable(row["pathway_activity"], activities),
                        transfer_to= _get_transfer_to(row["pathway_activity"], activities), required_resources= _get_activity_resources(row))
        )
    return list_activities

def _get_transferable(activity_name: str, activities_dict:dict) -> str:
    """Returns the group ID associated with pathway ID: pid"""
    transferable = next(v["transferable"] for v in activities_dict.values() if v["name"] == activity_name)
    return transferable

def _get_transfer_to(activity_name: str, activities_dict:dict) -> str:
    """Returns the group ID associated with pathway ID: pid"""
    transfer_to = next(v["transfer_to"] for v in activities_dict.values() if v["name"] == activity_name)
    return transfer_to

def _get_activity_resources(row: tuple) -> dict:
    """Retruns the needed resource consumption of this activity"""
    
    resources = ["cap_OT", "cap_ICU", "cap_Ward"]
    required = {r: 0 for r in resources}
    
    consumption =row["resource_consumption"]
    resource = row["resource_id"]
    required[resources[resource - 1]] = consumption
    return required

def get_PatientPathways(df_pathways : pd.DataFrame) -> list[Pathway]:
    """ get patients pathways"""    
    list_pathways = []
    for _, row in df_pathways[["pathway_id", "patient_group_id", "pathway_idx"]].drop_duplicates().iterrows():   
        list_pathways.append(Pathway(pathway_id= str(row["pathway_id"]),
                                  associated_group_id = str(row["patient_group_id"]),
                                  quality_level = str(row["pathway_idx"]), list_activities= ["OT","ICU","Ward"],
                                  group_benefit = 1))
    return list_pathways



def _get_df_pathways(data: dict) -> pd.DataFrame:
    """Converts the list of pathway dictionaries into a pandas Dataframe
    for easier querying"""
    import pandas as pd
    rows = []
    for pathway in data["profile"]:
        pathway_id = pathway["key"]
        category = pathway["category"]
        entries = pathway["entries"]

        for entry in entries:
            group_id, pathway_idx, resource_id, resource_consumption, facilities = entry

            for facility_id in facilities:
                rows.append({
                    "pathway_id": pathway_id,
                    "category": category,
                    "patient_group_id": group_id,
                    "pathway_idx": pathway_idx,
                    "resource_id": resource_id,
                    "resource_consumption": resource_consumption,
                    "facility_id": facility_id,
                })
    df = pd.DataFrame(rows)

    return df


def _get_df_resources(data: dict) -> pd.DataFrame:
    import pandas as pd
    rows = []
    for x in data["INFO"]:
        rows.append({"facility": x[1], "type": _get_resource_type(x[1].split("_")[1]), "cap": x[2]*x[3]*data["nbWeeks"]})
    return pd.DataFrame(rows)

def _get_resource_type(suffix:str)->str:
    if suffix == "ICU" or suffix == "OT":
        return suffix
    else:
        return "Ward"

class TreeToJSON(Transformer):
    def start(self, items):
        return dict(items)

    def statement(self, items):
        key = str(items[0])
        value = items[1]
        return (key, value)

    def NAME(self, token):
        return str(token)

    def NUMBER(self, token):
        return float(token) if '.' in token else int(token)

    def list(self, items):
        return list(items)

    def block(self, items):
        return list(items)

    def tuple(self, items):
        return list(items)
    
    def profile_entry(self, items):
        key = str(items[0])  # F01A|B
        category = str(items[1])  # SUR
        value = items[2]  # the block of CARD/ENDO entries
        return {'key': key, 'category': category, 'entries': value}
        


def _define_grammar():
    parser = Lark(r"""
                      start :(statement)*
                      statement: NAME "=" value [";"]
                      profile_entry : SPECIALTY "[" CAT "]" block
                      ?value : tuple
                             | block
                             | list
                             | NUMBER
                             | profile_entry
                             | NAME
                      list : "[" (value [","])* "]"
                      block : "{" value ("," value)* ","? "}"   
                      tuple: "<" value ("," value)* ">"
                      SPECIALTY.2: /[A-Z]\d{2,}[a-zA-Z]?(_[A-Z])?(?:\|[A-Z])*/
                      CAT: /(SUR|MED)(-AVG)?/
                      NAME: /[a-zA-Z_][a-zA-Z0-9_]*/
                      NUMBER: /-?\d+(\.\d+)?/
                           
                      %ignore /\s+/

    """)
    return parser


def _remove_trailing_comments(data):
    # Remove block comments /* ... */
    data = re.sub(r'/\*.*?\*/', '', data, flags=re.S)
    data = _preserve_specialty_lines(data)
    # Remove any remaining inline comments
    data = re.sub(r'//.*', '', data)
    # Remove leading/trailing whitespace from each line
    lines = [line.strip() for line in data.splitlines()]
    # Remove empty lines
    lines = [line for line in lines if line]
    # Join back into a single string
    return "\n".join(lines)

def _preserve_specialty_lines(data):
    # This matches lines that start with // and a specialty code, optional category
    pattern = r'^\s*//([A-Z]\d{2}[A-Z]?(?:\|[A-Z]){0,2}(?:\s*\[[A-Z]+\])?)'
    # Remove the leading //
    return re.sub(pattern, r'\1', data, flags=re.M)

def read_burdett():
    filename = "backend/data/raw/data_burdett.txt"
    with open(filename, "r") as fp:
        data = fp.read()
    data = _remove_trailing_comments(data)
    burdett_parser = _define_grammar()
    try:
        tree = burdett_parser.parse(data)
    except UnexpectedCharacters as e:
        print("Error at line:", e.line)

    data_json = TreeToJSON().transform(tree)

    return data_json

def serialize_burdett(
        perc_allowed: float = typer.Option(0, help="Maximum allowed resources out percentage"),
        save_params: bool = typer.Option(True))-> dict:
    return serialize_burdett_core(perc_allowed, save_params)

def serialize_burdett_core(
        perc_allowed: float = 0,
        save_params: bool = True) -> dict:
    from backend.core.data_models.input_models import SystemData
    from backend.core.mappers.input_mappers import convert_dm_to_json
    import json, os
    
    data = read_burdett()
    df_pathways = _get_df_pathways(data)
 
    list_regions = get_Regions(data)
    list_facilities = get_Facilities(data, df_pathways, perc_allowed)
    list_resources = get_Resources()
    list_patients = get_PatientGroups(data)
    list_pathways = get_PatientPathways(df_pathways)
    list_activities = get_Activities(df_pathways)
    instance = get_Instance(data, df_pathways)

    burdett_data = SystemData(regions = list_regions, resources=list_resources, facilities=list_facilities, patients=list_patients ,\
                pathways=list_pathways, activities= list_activities, instance=instance)
    params_system = convert_dm_to_json(burdett_data)

    if save_params:
        os.makedirs("experiments", exist_ok=True)
        with open("experiments/params_burdett.json", "w") as fp:
            json.dump(params_system, fp)
    return params_system

if __name__ == "__main__":
     import pyproj
     pyproj.datadir.set_data_dir(pyproj.datadir.get_data_dir())
     typer.run(serialize_burdett)