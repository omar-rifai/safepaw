
from typing import Tuple
import logging
logging.basicConfig(level=logging.DEBUG)


class ExecutableNotFound(Exception):
    pass


def check_executable():
    #TODO: check for gurobi or HiGHS
    return True



def run_optimization(params: dict) -> Tuple[str, str, list, dict]:
    """Returns status, objective function as str and a dict of result variables"""
    from backend.core.main import run_driver
    check_executable()
    print("Starting optimization driver...")
    status, objective, results = run_driver(params)
    print("Optimization driver finished with status:", status)
    objective_str = f"{objective:.2f}" if objective is not None else None
    return status, objective_str, results
