import pulp
from pathlib import Path
import geopandas as gpd
from backend.core.data_models.input_models import PatientsGroup, Facility, Region

def read_inputs(file_params_system):
    import json

    with open(file_params_system, "r") as f:
        params_system = json.load(f)

    return params_system


def extract_values(obj):
    if isinstance(obj, list):
        return [extract_values(item) for item in obj]
    elif isinstance(obj, dict):
        # Discard keys, process only values
        return [extract_values(item) for item in obj.values()]
    else:
        return pulp.value(obj)


def package_results(P_gk, P_gkr, P, Q, Delta_plus, Delta_moins, z_hl_plus, z_hl_moins):

    dict_results = {
        "P_gk": extract_values(P_gk),
        "P_gkr": extract_values(P_gkr),
        "P_gkrah": extract_values(P),
        "Q_gkrah": extract_values(Q),
        "Delta_plus": extract_values(Delta_plus),
        "Delta_moins": extract_values(Delta_moins),
        "z_hl_plus": extract_values(z_hl_plus),
        "z_hl_moins": extract_values(z_hl_moins),
    }

    return dict_results


def define_xarray(params_system: dict, dict_results: dict) -> dict:
    """
    Creates a dictionary of xarray items with variables inside dict_results
    """


    import xarray as xr
    import numpy as np
    
    groups = [f"group_{i}" for i in params_system["G"]]
    pathways = [f"pathway_{i}" for i in range(np.array(params_system["A_gk"]).shape[1])]
    regions = [f"region_{i}" for i in params_system["R"]]
    activities = [f"activity_{i}" for i in range(np.array(params_system["t_gkal"]).shape[2])]
    facilities = [f"facility_{i}" for i in params_system["H"]]
    resources = [f"resource_{i}" for i in params_system["L"]]

    P_xr = xr.DataArray(np.array(dict_results["P_gkrah"], dtype=float),
                        dims=["group", "pathway","region","activity","facility"],
                        coords={"group":groups,"pathway":pathways,"region":regions,"activity":activities,"facility":facilities},
                        name = "P")
    
    P_gkr_xr = xr.DataArray(np.array(dict_results["P_gkr"], dtype=float),
                            dims=["group", "pathway","region"],
                            coords={"group":groups,"pathway":pathways,"region":regions},
                            name = "P_gkr")
    
    P_gk_xr = xr.DataArray(np.array(dict_results["P_gk"], dtype=float),
                           dims=["group", "pathway"],
                           coords={"group":groups,"pathway":pathways},
                           name = "P_gk")    
    
    Q_xr = xr.DataArray(np.array(dict_results["Q_gkrah"], dtype=float),
                        dims=["group", "pathway","region","activity","facility"],
                        coords={"group":groups,"pathway":pathways,"region":regions,"activity":activities,"facility":facilities},
                        name = "Q")
    
    Delta_plus_xr = xr.DataArray(np.array(dict_results["Delta_plus"], dtype=float),
                                dims=["facility", "resource"],
                                coords={"facility":facilities,"resource":resources},
                                name = "Delta_plus")
    
    Delta_moins_xr = xr.DataArray(np.array(dict_results["Delta_moins"], dtype=float),
                                  dims=["facility", "resource"],
                                  coords={"facility":facilities,"resource":resources},
                                  name = "Delta_moins")
    
    z_hl_plus_xr = xr.DataArray(np.array(dict_results["z_hl_plus"], dtype=float),
                                dims=["facility", "resource"],
                                coords={"facility":facilities,"resource":resources},
                                name = "z_hl_plus")
    
    z_hl_moins_xr = xr.DataArray(np.array(dict_results["z_hl_moins"], dtype=float),
                                dims=["facility", "resource"],
                                coords={"facility":facilities,"resource":resources},
                                name = "z_hl_moins") 
   
    dict_xarray_results = {
        "P_gk": P_gk_xr,
        "P_gkr": P_gkr_xr,
        "P_gkrah": P_xr,
        "Q_gkrah": Q_xr,
        "Delta_plus": Delta_plus_xr,
        "Delta_moins": Delta_moins_xr,
        "z_hl_plus": z_hl_plus_xr,
        "z_hl_moins": z_hl_moins_xr,
    }

    return dict_xarray_results


def get_r_id(uid: int | str) -> str:
    return "region_" + str(uid)

def get_h_id(uid: int | str) -> str:
    return "facility_" + str(uid)


def get_uid_pathway(group_id: int | str, pathway_id: int | str) -> str:
    """
    Creates a unique pathway identifier  by group of the form (g{x}_{y}) 
    where {x} is the group integer id and y the pathway integer id
    """
    return "g" + str(group_id) + "_" + str(pathway_id)


def read_metadata(inputfile : str | Path):
    """
    Reads metadata from a JSON file.
    """
    import json

    with open(inputfile, "r") as f:
        metadata = json.load(f)

    return metadata

def read_configs_file(config_category, file_name, config_path="backend/config.yaml"):

    import yaml
    from pathlib import Path

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    input_file = Path(config[config_category][file_name])


    return input_file


def read_configs(config_category, config_path="backend/config.yaml"):
    import yaml

    with open(config_path, "r") as f:
        configs = yaml.safe_load(f)

    return configs.get(config_category)



def create_metadata(list_facilities: list[Facility], list_regions: list[Region], list_patients: list[PatientsGroup]) -> dict:
    """Create dictionary with metadata from the problem instance not used in the optimization model"""

    facility_index = {h.facility_id: str(i) for i, h in enumerate(list_facilities)}
    region_index = {r.region_id: str(i) for i, r in enumerate(list_regions)}
    patients_index = {p.group_id: str(i) for i, p in enumerate(list_patients)}

    dict_metadata = {"facilities" : {facility_index[h.facility_id]: {"coordinates" : h.coordinates, "name": h.facility_name} for h in list_facilities}} | \
          {"regions" : {region_index[r.region_id]: {"coordinates" : r.coordinates, "name": r.region_id} for r in list_regions}} | \
          {"patients": {patients_index[p.group_id]: {"name": p.group_id} for p in list_patients} }
    return dict_metadata



def read_geojson_projected(filename: str | Path) -> gpd.GeoDataFrame:
    import geopandas as gpd
    gdf = gpd.read_file(Path(filename))
    if gdf.empty:
        raise ValueError(f"GeoJSON file {filename} contains no features.")
    gdf = gdf.to_crs(epsg = 2154)
    return gdf

    

def get_distance_to_dep(dep_name : str, coords: list) -> int:
    """ Returns the distance in kms between a french departments and a point [lon, lat]"""
    from shapely.geometry import Point
    import geopandas as gpd

    geo_deps = read_geojson_projected("/data/departements.geojson")
    try:
        dep_geo = geo_deps.loc[geo_deps["nom"] == dep_name, "geometry"].iloc[0]
    
    except IndexError:
        raise ValueError(f"Departments {dep_name} not found")

    gdf_point = gpd.GeoSeries(Point(coords), crs="EPSG:4326").to_crs(geo_deps.crs)
        
    distance_m = gdf_point.iloc[0].distance(dep_geo)
    distance_km = distance_m / 1000
    
    return distance_km

def get_department_coords(dep_name: str, dep_centroids):
    return dep_centroids[dep_name]


def create_maternity_capacity_file():
    from pyproj import Transformer
    import pandas as pd 

    region_code_map = {'Auvergne-Rhône-Alpes': 84, "Provence-Alpes-Côte d'Azur": 93, 'Île-de-France': 11, 'Normandie': 28,
    'Occitanie': 76, 'Hauts-de-France': 32, 'Nouvelle-Aquitaine': 75, 'Grand Est': 44, 'Bretagne': 53, 'Centre-Val de Loire': 24,
    'Bourgogne-Franche-Comté': 27, 'Pays de la Loire': 52, 'Corse': 94
    }


    df_maternites = (
        pd.read_csv("backend/data/open_data/fichier_maternites_112021.csv", sep=";", low_memory=False)
            .rename(columns={"FI_ET": "nofinesset"})
    )
    
    
    df_finess_raw = pd.read_csv("backend/data/open_data/finess_etablissements.csv", sep=";", low_memory=False)
    t = Transformer.from_crs("EPSG:2154", "EPSG:4326", always_xy=True)
    lon, lat = t.transform(df_finess_raw["coordxet"].values, df_finess_raw["coordyet"].values)
 
    df_finess = (
        df_finess_raw
            .loc[:,["nofinesset", "departement"]]
            .assign(department = lambda x :  x["departement"].astype(str).str.zfill(2),
                    coords=[(float(lon_), float(lat_)) for lon_, lat_ in zip(lon, lat)]
                   )
    )
    
    df_regions = pd.read_json("/data/departments-region.json")
    df_regions["num_dep"] = df_regions["num_dep"].astype(str)
    dep_map = df_regions.set_index("num_dep")["dep_name"].to_dict()
    reg_map = df_regions.set_index("num_dep")["region_name"].to_dict()
    
    
    
    df = (
        df_maternites
            .merge(df_finess, on="nofinesset", how="inner")
            .assign(region_name = lambda x : x["department"].map(reg_map),
                    dep_name = lambda x: x["department"].map(dep_map),
                   )
            .dropna(subset=["dep_name"])
    )

    df["region_code"] = df["region_name"].map(region_code_map)

    df = df.rename(columns = {"ANNEE": "year", "NOM_MAT": "facility_name", "TYPE": "type", "department": "dep_code",
                              "NOMCOM": "comm_name", "COM": "comm_code","ACCTOT":"deliveries_per_facility", "LIT_OBS": "beds"})\
        [["year", "nofinesset", "facility_name", "type", "region_code", "region_name","dep_code", "dep_name", "comm_code", "comm_name", "coords", "deliveries_per_facility", "beds"]]

    df["dep_code"] = df["dep_code"].astype(str)

    df.to_csv("backend/data/open_data/summary_maternity_capacity.csv")



def create_maternity_labours_file():
    import pandas as pd 

    df_labour_raw = pd.read_csv("backend/data/open_data/DS_ETAT_CIVIL_NAIS_COMMUNES_data.csv", sep=";", low_memory=False)
    df_communes_raw = pd.read_csv("backend/data/open_data/communes-france.csv", sep=";", low_memory=False)
    
    df_communes = df_communes_raw.rename(columns={"Année": "year", "Code Officiel Région": "region_code",\
                                "Code Officiel Département": "dep_code", "Code Officiel Commune": "comm_code"})
    
    
    df_communes["coordinates"] = df_communes["Geo Point"].apply(lambda v: (str(v).split(",")[0],  str(v).split(",")[1]))
    df_communes = df_communes[["region_code", "dep_code", "comm_code", "coordinates"]]
    df_communes.drop_duplicates()
    
    df_labour = df_labour_raw.loc[df_labour_raw["GEO_OBJECT"] == "COM"]
    df_labour = df_labour[["GEO","TIME_PERIOD", "OBS_VALUE"]].rename(columns={"GEO": "comm_code", "TIME_PERIOD": "year", "OBS_VALUE": "deliveries_per_comm"})
    df_labour = df_labour.merge(df_communes, on=["comm_code"], how="left")[["year", "comm_code","dep_code", "region_code", "coordinates", "deliveries_per_comm" ,]]
    df_labour[["comm_code", "dep_code", "region_code"]] = df_labour[["comm_code", "dep_code", "region_code"]].apply(lambda x: x.astype(str))

    df_labour.to_csv("backend/data/open_data/summary_maternity_labours.csv")

    return 