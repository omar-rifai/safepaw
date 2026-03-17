import pulp
from pathlib import Path
import geopandas as gpd
from backend.core.data_models.input_models import PatientsGroup, Facility, Region
import pandas as pd


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



def vars_to_df(curr_var, list_dims, params_system):
    
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
    df = pd.DataFrame(records)
    return df


def package_results(vars_system, params_system):

    dict_results = {
        "P_gkrah": vars_to_df(vars_system.P, ["group","pathway","region","activity","facility"], params_system),
        "Q_gkrah": vars_to_df(vars_system.Q, ["group","pathway","region","activity","facility"], params_system),
        "P_gkr": vars_to_df(vars_system.P_gkr, ["group","pathway","region"], params_system),
        "P_gk": vars_to_df(vars_system.P_gk, ["group","pathway"], params_system),
        "Delta_plus" : pd.DataFrame([{"facility": h, "resource": l, "value": pulp.value(vars_system.Delta_plus[h][l])}
                                         for h in params_system["H"] for l in params_system["L"]]),
                                         
        "Delta_moins": pd.DataFrame([{"facility": h, "resource": l, "value": pulp.value(vars_system.Delta_moins[h][l])}
                                         for h in params_system["H"] for l in params_system["L"]]),

        "z_hl_plus": pd.DataFrame([{"facility": h, "resource": l, "value": pulp.value(vars_system.z_hl_plus[h][l])}
                                         for h in params_system["H"] for l in params_system["L"]]),

        "z_hl_moins": pd.DataFrame([{"facility": h, "resource": l, "value": pulp.value(vars_system.z_hl_moins[h][l])}
                                         for h in params_system["H"] for l in params_system["L"]])
    }
    return dict_results


def read_metadata(inputfile : str | Path):
    """
    Reads metadata from a JSON file.
    """
    import json

    with open(inputfile, "r") as f:
        metadata = json.load(f)

    return metadata


def read_configs(config_category, config_path="backend/config.yaml"):
    import yaml

    with open(config_path, "r") as f:
        configs = yaml.safe_load(f)

    return configs.get(config_category)



def create_metadata(params_system: dict, list_facilities: list[Facility], list_regions: list[Region], list_patients: list[PatientsGroup]) -> dict:
    """Create dictionary with metadata from the problem instance not used in the optimization model"""

    dict_metadata = {"facilities" : {h.facility_id: {"coordinates" : h.coordinates, "name": h.facility_name} for h in list_facilities}} | \
          {"regions" : {r.region_id: {"coordinates" : r.coordinates, "name": r.region_id} for r in list_regions}} | \
          {"patients": {p.group_id: {"name": p.group_id} for p in list_patients} }
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