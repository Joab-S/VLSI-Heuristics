from VLSI_class import VLSI

class ResponseFormat:
    def __init__(self, instance: VLSI, runtime: float, hpwl: float, status: str, termination_condition: str, 
                 objective_value: float, solution: dict, infeasible: bool):
        self.instance = instance
        self.runtime = runtime
        self.hpwl = hpwl
        self.status = status
        self.termination_condition = termination_condition
        self.objective_value = objective_value
        self.solution = solution
        self.infeasible = infeasible
