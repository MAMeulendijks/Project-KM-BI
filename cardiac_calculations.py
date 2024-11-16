import numpy as np

class CardiacCalculator:
    def __init__(self, time_points, cycle_times, n_beats, V_lv=None):
        """
        Initialize the CardiacCalculator with shared parameters.

        Parameters:
        time_points (ndarray): Array of time points corresponding to flow values.
        cycle_times (list): List of cycle times for each beat.
        n_beats (int): Number of heartbeats.
        V_lv (ndarray, optional): Array of left ventricular volume values for ejection fraction calculation.
        """
        self.time_points = time_points
        self.cycle_times = cycle_times
        self.n_beats = n_beats
        self.V_lv = V_lv  # Optional parameter, used only for ejection fraction calculation

    def calculate_EF(self, flow):
        """
        Calculate ejection fraction for each beat.

        Parameters:
        flow (ndarray): Array of flow values (e.g., flow_aortic_valve or flow_pulmonary_valve).

        Returns:
        list: A list of calculated ejection fraction values for each beat.
        """
        if self.V_lv is None:
            raise ValueError("V_lv is required for ejection fraction calculation")

        EF_values = []
        timer = 0

        for i in range(self.n_beats):
            cycle_time = self.cycle_times[i + 1] * 1e3  # Cycle time in ms
            start_index = int(timer / 2)
            end_index = int((timer + cycle_time) / 2)

            flow_i = flow[start_index:end_index]
            V_lv_i = self.V_lv[start_index:end_index]
            EDV = np.max(V_lv_i)
            time_points_i = self.time_points[start_index:end_index]
            stroke_volume_i = np.trapezoid(flow_i, time_points_i) * 1e6  # L

            EF_i = stroke_volume_i / EDV
            EF_values.append(EF_i)
            timer += cycle_time

        EF_values = [f"{value:.3f}" for value in EF_values]

        return EF_values

    def calculate_CO(self, flow):
        """
        Calculate cardiac output for each beat.

        Parameters:
        flow (ndarray): Array of flow values (e.g., flow_aortic_valve or flow_pulmonary_valve).

        Returns:
        list: A list of calculated cardiac output values for each beat.
        """
        cardiac_output_values = []
        timer = 0
        list_cycle_times = self.cycle_times[1:]  # Exclude the first 0

        for i in range(self.n_beats):
            cycle_time = self.cycle_times[i + 1] * 1e3  # Cycle time in ms
            start_index = int(timer / 2)
            end_index = int((timer + cycle_time) / 2)

            flow_i = flow[start_index:end_index]
            time_points_i = self.time_points[start_index:end_index]
            stroke_volume_i = np.trapezoid(flow_i, time_points_i) * 1e3  # L

            heart_rate_i = 60 / list_cycle_times[i]
            cardiac_output_i = stroke_volume_i * heart_rate_i  # L/min
            cardiac_output_values.append(cardiac_output_i)
            timer += cycle_time

        return cardiac_output_values
    def calculate_LA_pressure(self, LA_pressure_data):
        """
        Calculate the left atrial pressure for each beat.

        Parameters:
        LA_pressure_data (ndarray): Array of LA pressure values for each time point (in kPa).

        Returns:
        list: A list of calculated LA pressure values for each beat.
        """
        LA_pressure_values = []
        timer = 0
        list_cycle_times = self.cycle_times[1:]  # Exclude the first 0

        for i in range(self.n_beats):
            cycle_time = self.cycle_times[i + 1] * 1e3  # Cycle time in ms
            start_index = int(timer / 2)
            end_index = int((timer + cycle_time) / 2)

            LA_pressure_i = LA_pressure_data[start_index:end_index]  # Extract LA pressure data for this beat
            time_points_i = self.time_points[start_index:end_index]

            # Calculate mean LA pressure for this cycle (you can modify this to use other metrics if needed)
            mean_LA_pressure_i = np.mean(LA_pressure_i)  # Mean LA pressure for the current beat
            LA_pressure_values.append(mean_LA_pressure_i)
            timer += cycle_time

        return LA_pressure_values