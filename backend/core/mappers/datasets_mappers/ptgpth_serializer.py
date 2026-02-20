import pandas as pd
from backend.core.data_models.input_models import Facility, Region, Instance, Resource, PatientsGroup, Activity, Pathway
import geopandas as gpd


def load_types_parcours(path: str, min_patients: int, dep_code:str):
    """Read and filter TYPES_PARCOURS for Loire."""
    df = pd.read_csv(path)
    df_loire = reduce_TYPES_PARCOURS_LOIRE(df, min_patients, dep_code)
    return df_loire

def load_mco_data(path: str, dep_code: str):
    """Read MCO data and keep Loire rows only."""
    df = pd.read_csv(path)
    return reduce_MCO_LOIRE(df, dep_code)

def load_ssr_data(path: str, dep_code:str):
    """Read SSR data and keep Loire SSR_A rows only."""
    df = pd.read_csv(path, sep=";")
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
    dept_code = data['FI_EJ'].astype(str).apply(lambda s: int(s[:2]) if s[:2].isdigit() else 0)
    return data[dept_code.isin(dep_code)].reset_index(drop=True)


def reduce_SSR_LOIRE(data: pd.DataFrame, dep_code) -> pd.DataFrame:
    """Keep only SSR_A rows corresponding to Loire department"""
    dept_code = data['FI_EJ'].astype(str).apply(lambda s: int(s[:2]) if s[:2].isdigit() else 0)
    return data[dept_code.isin(dep_code) & (data['GDE'] == "SSR_A")].reset_index(drop=True)


import pandas as pd
def get_Regions(df_instance: pd.DataFrame) -> list[Region]:
    """Creates Region instance using public data on French communes (Commune code and coordinates)"""
    cantons = []
    list_regions = [Region(region_id="",
                           coordinates="",
                           facilities_affinity=_get_affinities()) for c in cantons]
    return list_regions


def _get_affinities():
    return

def get_Facilities(df_instance : pd.DataFrame, max_transferable_in : int = 10, max_transferable_out : int = 1) -> list[Facility]:
    """Creates Facility objects corresponding to unique nofinesset ids 
    """
    all_ids = []
    def row_to_facility(row):
        return Facility(
            facility_id ="" ,
            facility_name ="" ,
            region = "" ,
            coordinates = [] , 
            resources_capacity = 0 ,
            max_transferable_in = 0,
            max_transferable_out = 0,
            linked_facilities = [],
            available_pathways= _get_available_pathways())
    list_facilities = df_instance.apply(row_to_facility, axis=1).tolist()
    return list_facilities

def _get_available_pathways():
    """Returns available pathways for each facility ``type''"""
    return  []


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
    
    all_finess = pd.concat([df_ssr["FI"], df_mco["420"]]).dropna().unique()
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