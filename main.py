import streamlit as st
import simpy
import pandas as pd

# Service times for each station in seconds
service_times = [25, 15, 34, 37, 38, 56, 25, 15, 19, 25, 17, 17, 7]

# Simulation environment
class ServiceStation:
    def __init__(self, env, service_time):
        self.env = env
        self.service_time = service_time
        self.server = None  # Will be created later

    def serve_customer(self):
        yield self.env.timeout(self.service_time)

def simulate_service(stations, num_customers, simulation_time):
    env = simpy.Environment()

    # Create service stations
    station_objects = [ServiceStation(env, service_time) for service_time in stations]

    # Distribute total available servers (22) among stations based on service times
    total_servers = 22
    total_service_times = sum(stations)
    for i, station in enumerate(station_objects):
        required_servers = max(1, int((stations[i] / total_service_times) * total_servers))
        station.server = simpy.Resource(env, capacity=required_servers)

    # Create customer process
    def customer(env, stations):
        served_customers = 0
        while served_customers < num_customers:
            for station in stations:
                with station.server.request() as request:
                    yield request
                    yield env.process(station.serve_customer())
                    served_customers += 1

    env.process(customer(env, station_objects))

    # Run the simulation
    env.run(until=simulation_time)

    # Calculate the average service time for each station
    average_service_times = [station.service_time for station in station_objects]

    # Calculate the required number of servers at each station
    required_servers = [station.server.capacity for station in station_objects]

    # Create a DataFrame for the results
    results = pd.DataFrame({
        "Service Station": range(1, len(station_objects) + 1),
        "Average Service Time (seconds)": average_service_times,
        "Required Servers": required_servers
    })

    return results

# Streamlit app
def main():
    st.title("Service Station Simulation")

    num_stations = len(service_times)
    station_inputs = [st.number_input(f"Service Time for Station {i+1} (seconds)", value=service_times[i]) for i in range(num_stations)]
    num_customers = st.number_input("Number of Customers", value=1000)
    simulation_time = st.number_input("Simulation Time (seconds)", value=7 * 60 * 60)

    if st.button("Simulate"):
        results = simulate_service(station_inputs, num_customers, simulation_time)
        st.write(results)

if __name__ == "__main__":
    main()
