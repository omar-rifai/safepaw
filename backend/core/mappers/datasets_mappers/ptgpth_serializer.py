import pandas as pd
from backend.core.data_models.input_models import Facility, Region, Instance, Resource, PatientsGroup, Activity, Pathway
import geopandas as gpd

specialities = ["CSC", "DERMA", "RHUMA", "URO", "GASTRO", "OPH", "ENDO", "ORL"]
post_op_scenarios = {"DAY_HC":{"PTG_HC":28,"PTH_HC":21,"PTG_DOM":0,"PTH_DOM":0,"PTG_HC_HDJ":21,"PTH_HC_HDJ":14,"PTG_HDJ":0,"PTH_HDJ":0},
                     "KINE_SSR":{"PTG_HC":0,"PTH_HC":0,"PTG_DOM":0,"PTH_DOM":0,"PTG_HC_HDJ":20,"PTH_HC_HDJ":15,"PTG_HDJ":25,"PTH_HDJ":20},
                     "KINE_DOM":{"PTG_HC":0,"PTH_HC":0,"PTG_DOM":25,"PTH_DOM":20,"PTG_HC_HDJ":0,"PTH_HC_HDJ":0,"PTG_HDJ":0,"PTH_HDJ":0}}

finance_PTG = {"CHIR/ORTHO":46, "ANES" : 46, "CSC": 34.75, "DERMA": 40,"ENDO": 40, "GASTRO": 40, "GYNECO": 40,
               "OPH":40, "ORL":40, "RHUMA":40, "URO":40, "KINE_MCO":9.95, "DAY_HC":4365.61, "KINE_DOM":769.56, "KINE_SSR":126.80,"post_ORTH": 370.99}
finance_PTH = {"CHIR/ORTHO": 46, "ANES": 46, "CSC":34.75, "DERMA":40, "ENDO":40, "GASTRO":40, "GYNECO":40, "OPH":40,"ORL": 40,
               "RHUMA":40, "URO":40, "KINE_MCO":9.95, "DAY_HC":3966.66, "KINE_DOM":803.30, "KINE_SSR":127.63, "post_ORTH":370.99}

def load_types_parcours(path: str, min_patients: int, dep_code:str):
    """Read and filter TYPES_PARCOURS for Loire."""
    df = pd.read_csv(path)
    df_loire = reduce_TYPES_PARCOURS_LOIRE(df, min_patients, dep_code)
    return df_loire

def load_mco_data(path: str, dep_code: str):
    """Read MCO data and keep Loire rows only."""
    df = pd.read_csv(path)
    df = df.rename(columns={'420': 'FI_ET'})
    return reduce_MCO_LOIRE(df, dep_code)

def load_ssr_data(path: str, dep_code: str):
    """Read SSR data and keep Loire SSR_A rows only."""
    df = pd.read_csv(path, sep=";")
    df = df.rename(columns={'FI': 'FI_ET'})
    return reduce_SSR_LOIRE(df, dep_code)

def load_data(dep_code:str):
    types_parcours_loire = load_types_parcours("backend/data/legacy/raw_TYPES_PARCOURS.csv", 3, dep_code)
    mco_loire = load_mco_data("backend/data/legacy/raw_MCO_2018r.csv", dep_code)
    ssr_loire = load_ssr_data("backend/data/legacy/raw_SSR_2018r.csv", dep_code)
    return types_parcours_loire, mco_loire, ssr_loire

def reduce_TYPES_PARCOURS_LOIRE(data: pd.DataFrame, min_patients: int, dep_code: str) -> pd.DataFrame:
    """Keep only Loire departments and groups with enough patients."""
    df = data[data['BEN_RES_DPT'].isin(dep_code)].copy()
    df['SSR_TYPE'] = df['SSR_TYPE'].fillna('DOM')
    grouped = df.groupby(['BEN_RES_DPT', 'sej_type', 'type_parcours', 'SSR_TYPE'], as_index=False)['nb'].sum()
    grouped['group_key'] = grouped['sej_type'].astype(str) + grouped['type_parcours'].astype(str)
    totals = grouped.groupby('group_key')['nb'].transform('sum')
    filtered = grouped[totals >= min_patients].drop(columns='group_key')
    return filtered.reset_index(drop=True)


def reduce_MCO_LOIRE(data: pd.DataFrame, dep_code: str) -> pd.DataFrame:
    """Keep only rows corresponding to Loire department in MCO data. (FINESS number starts with 42)"""
    dept_code = data['FI_ET'].astype(str).apply(lambda s: int(s[:2]) if s[:2].isdigit() else 0)
    return data[dept_code.isin(dep_code)].reset_index(drop=True)


def reduce_SSR_LOIRE(data: pd.DataFrame, dep_code) -> pd.DataFrame:
    """Keep only SSR_A rows corresponding to Loire department"""
    dept_code = data['FI_ET'].astype(str).apply(lambda s: int(s[:2]) if s[:2].isdigit() else 0)
    return data[dept_code.isin(dep_code) & (data['GDE'] == "SSR_A")].reset_index(drop=True)


import pandas as pd
def get_Regions(df_instance: pd.DataFrame, dep_code: int) -> list[Region]:
    """Creates Region instance (cantons) given a department code (cantons are grouped by bureau de voe)"""
    gdf_cantons = get_geo_polygon()
    gdf_geo = summarize_geo_data(gdf_cantons, get_pop65p(), dep_code)
    list_regions = [Region(region_id="",
                           coordinates="",
                           facilities_affinity=_get_affinities()) for c in []]
    return list_regions


def _get_affinities():
    return

def get_Facilities(df_mco : pd.DataFrame, df_ssr : pd.DataFrame, dep_code: int,
                   max_transferable_in: int = 10, max_transferable_out : int = 1) -> list[Facility]:
    """Creates Facility objects corresponding to unique nofinesset ids """
    list_facilities = []
    gdf_cantons = get_geo_polygon()
    gdf_geo = summarize_geo_data(gdf_cantons, get_pop65p(), dep_code)
    df_finess = get_finness_info(df_mco, df_ssr, gdf_geo)
    list_finess = list(df_finess["nofinesset"].unique())
    list_finess.append("DOM")
    
    for row in df_finess.itertuples():
        
        list_facilities.append(Facility(
            facility_id = row.nofinesset,
            facility_name = "" ,
            region = row.can_code,
            coordinates =[row.lat, row.lon] , 
            resources_capacity = _get_resources_capacity(row.nofinesset) ,
            max_transferable_in = 0,
            max_transferable_out = 0,
            linked_facilities = [],
            available_pathways= _get_available_pathways()))
    #list_facilities = df_instance.apply(row_to_facility, axis=1).tolist()
    return list_facilities

def _get_available_pathways():
    """Returns available pathways for each facility ``type''"""
    return  []

def _get_m_hl(list_finess: list, df_types_parcours_init: pd.DataFrame, df_ssr: pd.DataFrame, df_mco: pd.DataFrame,
                            df_types_parcours: pd.DataFrame, ) -> dict:
    """Returns a dict with each available resource and its capacity given a finess number"""
    
    m_hl = _get_resource_capacity(m_hl, list_finess,  df_mco, df_types_parcours, "ORTH/CHIR", "JLI_CHI", 3)
    m_hl = _get_resource_capacity(m_hl, list_finess,  df_mco, df_types_parcours, "ANES", "JLI_CHI", 2)
    m_hl = _get_specialities_cap(m_hl, df_mco, df_types_parcours, list_finess)
    m_hl = _get_resource_capacity(m_hl, list_finess,  df_mco, df_types_parcours, "KINE_MCO", "ACTCLI_PM", {"PTG":10, "PTH":15})
    m_hl = _get_resource_capacity(m_hl, list_finess,  df_ssr,
                                df_types_parcours_init
                                    .assign(sej_type = \
                                            df_types_parcours_init["sej_type"].str.cat(df_types_parcours_init["SSR_TYPE"], sep="_")),
                                "DAY_HC", "JOUHC", post_op_scenarios["DAY_HC"])
    m_hl = _get_resource_capacity(m_hl, list_finess,  df_ssr,
                                df_types_parcours_init
                                    .assign(sej_type = \
                                            df_types_parcours_init["sej_type"].str.cat(df_types_parcours_init["SSR_TYPE"], sep="_")),
                                "KINE_SSR", "JOUHP", post_op_scenarios["KINE_SSR"])
    m_hl = _get_resource_capacity(m_hl, list_finess, None,
                                df_types_parcours_init
                                    .assign(sej_type = \
                                            df_types_parcours_init["sej_type"].str.cat(df_types_parcours_init["SSR_TYPE"], sep="_")),
                                "KINE_DOM", None, post_op_scenarios["KINE_DOM"])
    return m_hl

def _get_specialities_frac(df_mco: pd.DataFrame, list_finess: list) -> dict:
    """Returns a proxy of facilities' capacity for a speciality. When there is no info on availability,
        we assume the speciality is present following other specialists patterns"""
    
    df_mco_flag_fields = {"CSC": "PCAR", "DERMA": "PDER", "RHUMA": "PRHU", "URO": "PNEU",
                           "GASTRO": "PGAS", "OPH": "POPH", "ENDO": "PEND", "ORL": "PPNE"}
    total_cap_regional = {}
    
    for speciality in df_mco_flag_fields.keys():
        flag_field = df_mco_flag_fields[speciality]
        total_cap_regional[speciality] = sum(df_mco[df_mco[flag_field]!=0]["ACTCLI_PM"])
    
    facility_specialty_frac= {}
    for finess in list_finess:
        facility_specialty_frac[finess] = {} 
        for speciality in df_mco_flag_fields.keys():
            flag_field = df_mco_flag_fields[speciality]
            if finess in list(df_mco["FI_ET"].unique()):
                if df_mco[df_mco["FI_ET"]==finess][flag_field].iloc[0] != 0:
                    facility_specialty_frac[finess][speciality] = \
                        df_mco[df_mco["FI_ET"]==finess]["ACTCLI_PM"].iloc[0] / total_cap_regional[speciality]
                else:
                    facility_specialty_frac[finess][speciality] = 0
            else:
                facility_specialty_frac[finess][speciality] = 0

    return facility_specialty_frac

def _get_specialities_cap(m_hl: dict, df_mco: pd.DataFrame, df_types_parcours: pd.DataFrame,
                          list_finess: list) -> dict:
    import math
    import copy
    
    frac_specialities =  _get_specialities_frac(df_mco, list_finess)
    nb_groups = {x:0 for x in specialities}

    for i,row in df_types_parcours.iterrows():
        for s in specialities:
            if s in row["type_parcours"].split(" + "):
                nb_groups[s] += 1

    cap_specialities = copy.deepcopy(frac_specialities)
    for facility in frac_specialities.keys():
        for speciality in specialities:
            cap_specialities[facility][speciality] = math.ceil(frac_specialities[facility][speciality] * nb_groups[speciality])
    
    m_hl = _extend_nested_dict(m_hl, cap_specialities)
    return  m_hl



def _get_resource_capacity(m_hl_init: dict, list_finess: list, df_activity: pd.DataFrame, df_types_parcours: pd.DataFrame,
                           resource_name: str, resource_table_field: str, resource_consumption: dict) -> dict:
    """ 
    Calculates capacity of resource using a proxy of total departmental number of visits times
    the proportion of resrouce available at a facility (we assume that visit consumes ``resource_consumption'' resources
    # Hypothesis: all resources except specialists are present in all facilities by type either MCO or SSR   
    """
    import math
    m_hl = {h: {resource_name: 0} for h in list_finess}    
   
    if isinstance(resource_consumption, dict):
        resource_consumption = df_types_parcours["sej_type"].map(resource_consumption)
    total_consumption_resource = float((resource_consumption * df_types_parcours["nb"]).sum())

    if df_activity is None:
         m_hl["DOM"][resource_name] = math.ceil(total_consumption_resource)
    else:  
        for h in list_finess:
            if h in df_activity["FI_ET"].unique():
                    total_dep_resources = df_activity[resource_table_field].sum()
                    current_facility_resources = df_activity[df_activity["FI_ET"]==h][resource_table_field].iloc[0]
                    capacity_resource = math.ceil(total_consumption_resource * ( current_facility_resources / total_dep_resources))
                    m_hl[h][resource_name] = capacity_resource
            else:
                current_facility_resources =  m_hl_init[h].get(resource_name, 0)    
    
    m_hl = _extend_nested_dict(m_hl_init, m_hl)
    return m_hl  


def _extend_nested_dict(init_dict: dict, ext_dict: dict):
    """Helper function to update capacity of m_hl with an extension containg capacity of new resources"""
    res_dict = {k: init_dict.get(k, {}) | ext_dict[k] for k in set(init_dict) | set(ext_dict)}
    return res_dict


def get_Instance(df_instance : pd.DataFrame) -> Instance:
    """Returns object to store optimization instance parameters. Most variables are stores in a global config.yaml file """
   
    return Instance(
            d_total = 0 ,
            d_gr = get_demand_lower_bounds(),
            under_q_g = {} ,
            over_q_g = {},
            under_q_gu = {},
            over_q_gu = {},
            p_transf = 0,
            delta_l = 0,
            alpha = 0
        )


def get_demand_lower_bounds() -> dict:
    """ Returns ``d_gr'', the lower bound on patients asssigments per patient group, per canton"""
    
    return d_gr


def get_Resources(df_instance : pd.DataFrame) -> list[Resource]:
    """Creates Resource object with id for unique """
    return [Resource(resource_id="")]


def get_PatientGroups(df_instance: pd.DataFrame) -> list[PatientsGroup]:
    """Creates PatientGroups """
    list_patientsGroups = []
    
    for gid in group_ids:
        possible_pathways = _get_possible_pathways(gid)
        list_patientsGroups.append(PatientsGroup(group_id="", possible_pathways=possible_pathways))
    return list_patientsGroups


def _get_possible_pathways(gid):
    """get list of possible passways for that group"""
    return []

    

def get_Activities(df_instance : pd.DataFrame) -> list[Activity]:
    """ get activities """
    list_activities = [Activity(activity_id= "", associated_pathway="",
                     associated_group="", transferable="",
                     transfer_to="", required_resources={})]
    return list_activities


def get_PatientPathways(df_instance : pd.DataFrame) -> list[Pathway]:
    """ get patients pathways"""                      
    pathways = [Pathway(pathway_id= "p"+g, associated_group_id = g, quality_level = "0", list_activities= [],
                         group_benefit = 1, list_next = []) for g in group_ids]
    return pathways




def get_pop65p() -> pd.DataFrame:
    """ Returns a dataframe with the total population over 65 by Canton code and department code"""
    df_pop = pd.read_csv("backend/data/open_data/pop65.csv", sep=";", low_memory=False)
    df_pop= df_pop[["codgeo", "pop65p"]]\
        .rename(columns = {"codgeo":"comm_code"})\
        .fillna(0)
    df_comm = pd.read_csv("backend/data/open_data/data_cantons/v_commune_2025.csv")
    df_comm = df_comm[["COM", "CAN", "DEP"]].rename(columns={"COM": "comm_code", "CAN": "can_code", "DEP": "dep_code"})
    df_merged = pd.merge(df_comm, df_pop, on="comm_code", how="inner").drop_duplicates()
    df_merged["pop65p"] = df_merged["pop65p"].astype(int)
    df_pop65p = df_merged.groupby(["can_code"], as_index=False).aggregate({
        "dep_code": "first",
        "pop65p": "sum"
    })
    return df_pop65p
    

def get_geo_polygon()->gpd.GeoDataFrame:
    """Returns a dataframe with the geographic polygon of each canton along with the total population"""
    gdf = gpd.read_file("backend/data/open_data/data_cantons/cantons_2015_simpl.json")
    gdf["population"] = gdf["population"].astype(int)
    gdf["can_code"] = gdf["dep"].astype(str).str.zfill(2) + gdf["canton"].astype(str).str.zfill(2)
    gdf = gdf[["can_code", "bureau", "population", "dep", "geometry"]].drop_duplicates()
    gdf = gdf.rename(columns={"dep": "dep_code"})
    return gdf.to_crs("EPSG:4326")


def get_finness_info(df_mco: pd.DataFrame, df_ssr: pd.DataFrame, gdf_geo: gpd.GeoDataFrame) -> pd.DataFrame:
    """Returns a dataframe with the canton code of each finess"""
    from pyproj import Transformer
    from shapely.geometry import Point
    df_finess = pd.read_csv("backend/data/open_data/finess_2018.csv", sep=";", encoding="latin1",\
                            usecols=["nofinesset", "coordx", "coordy"],  dtype={"coordx": str, "coordy": str},\
                            low_memory=False)
    
    all_finess = pd.concat([df_ssr["FI_ET"], df_mco["FI_ET"]]).dropna().unique()
    df_finess = df_finess[df_finess["nofinesset"].isin(all_finess)]
    
    transformer = Transformer.from_crs(2154, 4326, always_xy=True)
    df_finess["lon"], df_finess["lat"] = transformer.transform(
        df_finess["coordx"].str.replace(",", "").astype(float),
        df_finess["coordy"].str.replace(",", "").astype(float)
    )
    gdf_finess = gpd.GeoDataFrame(df_finess, geometry=[Point(xy) for xy in zip(df_finess["lon"],df_finess["lat"])], crs="EPSG:4326")
    gdf_finess = gpd.sjoin(gdf_finess, gdf_geo[["can_code", "geometry"]], how="left", predicate="intersects")
    
    return gdf_finess[["nofinesset","lon","lat","can_code"]]
    
def summarize_geo_data(gdf_cantons: gpd.GeoDataFrame, df_pop65p:pd.DataFrame, dep_code: str) ->gpd.GeoDataFrame:
    """Returns a dataframe of all the geographic information needed merged"""
    gdf_cantons = gdf_cantons.merge(df_pop65p, on= ["can_code","dep_code"], how="left")
    gdf_cantons = gdf_cantons[gdf_cantons["dep_code"] == dep_code]
    gdf_cantons.fillna(0)
    gdf_geo = gdf_cantons.dissolve(
        by="bureau",
        aggfunc= {
            "can_code": "first", 
            "dep_code": "first",
            "population": "sum",
            "pop65p": "sum"
    }).reset_index().rename(columns={"bureau":"nom"})
    gdf_geo  = gdf_geo.explode(index_parts=False).reset_index(drop=True)
    gdf_geo["perc_65p"] = gdf_geo["pop65p"] / gdf_geo["population"] * 100
    gdf_geo["adjacent"] = gdf_geo.apply(lambda x: gdf_geo.loc[gdf_geo.geometry.touches(x.geometry),"can_code"].to_list(), axis=1)
    return gdf_geo