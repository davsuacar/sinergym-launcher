from datetime import datetime
from math import exp
from typing import Any, Dict, List, Optional, Tuple, Union
from numpy import mean, sqrt

from sinergym.utils.constants import LOG_REWARD_LEVEL, YEAR
from sinergym.utils.logger import TerminalLogger

class MultiZoneOccupancyReward(MultiZoneRewardV1):

# TODO: Change occupancy variables because EnergyPlus already give you a Dict.

    def __init__(
        self,
        energy_variables: List[str],
        temperature_and_setpoints_conf: Dict[str, str],
        occupancy_variables: Dict[str, str],
        comfort_threshold: float = 0.5,
        unoccupied_threshold: float = 2.0,
        energy_weight: float = 0.5,
        lambda_energy: float = 1.0,
        lambda_temperature: float = 1.0
    ):
        """
        A linear reward function for environments with different comfort ranges in each zone and occupancy consideration.
        Similar to MultiZoneRewardV2 but takes into account whether each zone is occupied or not when calculating comfort violations.
        Occupied zones have a strict comfort range (±0.5°C by default) while unoccupied zones have a wider range (±2.0°C by default).

        Args:
            energy_variables (List[str]): Name(s) of the energy/power variable(s).
            temperature_and_setpoints_conf (Dict[str, str]): Dictionary with the temperature variable name (key) and the setpoint variable name (value) of the observation space.
            occupancy_variables (Dict[str, str]): Dictionary with the temperature variable name (key) and the occupancy variable name (value) of the observation space.
            comfort_threshold (float, optional): Comfort threshold for temperature range (+/-) for occupied zones. Defaults to 0.5.
            unoccupied_threshold (float, optional): Comfort threshold for temperature range (+/-) for unoccupied zones. Defaults to 2.0.
            energy_weight (float, optional): Weight given to the energy term. Defaults to 0.5.
            lambda_energy (float, optional): Constant for removing dimensions from power(1/W). Defaults to 1e-4.
            lambda_temperature (float, optional): Constant for removing dimensions from temperature(1/C). Defaults to 1.0.
        """

        super().__init__(energy_variables,
                         temperature_and_setpoints_conf,
                         comfort_threshold,
                         energy_weight,
                         lambda_energy,
                         lambda_temperature)
        
        # Store occupancy configuration and thresholds
        self.occupancy_configuration = occupancy_variables
        self.unoccupied_threshold = unoccupied_threshold

    def _get_comfort_ranges(
            self, obs_dict: Dict[str, Any]):
        """Calculate the comfort range for each zone in the current observation.
        Different thresholds are used for occupied and unoccupied zones.

        Returns:
            Dict[str, Tuple[float, float]]: Comfort range for each zone.
        """
        # Calculate current comfort range for each zone
        self.comfort_ranges = {}
        for temp_var, setpoint_var in self.comfort_configuration.items():
            if (setpoint := obs_dict[setpoint_var]) is not None:
                # Check if zone is occupied
                is_occupied = False
                if temp_var in self.occupancy_configuration:
                    occupancy_var = self.occupancy_configuration[temp_var]
                    is_occupied = obs_dict.get(occupancy_var, 0) > 0
                
                # Use appropriate threshold based on occupancy
                threshold = self.comfort_threshold if is_occupied else self.unoccupied_threshold
                self.comfort_ranges[temp_var] = (setpoint - threshold, setpoint + threshold)

    def _get_temperature_violation(
            self, obs_dict: Dict[str, Any]) -> List[float]:
        """Calculate the total temperature violation (ºC) in the current observation.
        Considers different thresholds for occupied and unoccupied zones.

        Returns:
           List[float]: List with temperature violation (ºC) in each zone.
        """
        # Calculate current comfort range for each zone
        self._get_comfort_ranges(obs_dict)

        temp_violations = []
        for temp_var, comfort_range in self.comfort_ranges.items():
            if (T := obs_dict[temp_var]):
                violation = max(0, min(abs(T - comfort_range[0]), abs(T - comfort_range[1])))
                temp_violations.append(violation)

        return temp_violations

    def _get_reward(self) -> Tuple[float, ...]:
        """Compute the final reward value.

        Args:
            energy_penalty (float): Negative absolute energy penalty value.
            comfort_penalty (float): Negative absolute comfort penalty value.

        Returns:
            Tuple[float, ...]: Total reward calculated and reward terms.
        """
        comfort_term = self.lambda_temp * \
            (1 - self.W_energy) * self.comfort_penalty
        energy_term = self.lambda_energy * self.W_energy * - \
            (self.total_energy / sqrt(1 + self.total_temp_violation / len(self.comfort_configuration)))
        reward = energy_term + comfort_term
        return reward, energy_term, comfort_term