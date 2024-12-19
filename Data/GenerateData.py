import os

import numpy as np
import pandas as pd


VARIANT_FEATURES = {
    "CVRP": {"O": False, "TW": False, "L": False, "B": False, "M": False},
    "OVRP": {"O": True, "TW": False, "L": False, "B": False, "M": False},
    "VRPB": {"O": False, "TW": False, "L": False, "B": True, "M": False},
    "VRPL": {"O": False, "TW": False, "L": True, "B": False, "M": False},
    "VRPTW": {"O": False, "TW": True, "L": False, "B": False, "M": False},
    "OVRPTW": {"O": True, "TW": True, "L": False, "B": False, "M": False},
    "OVRPB": {"O": True, "TW": False, "L": False, "B": True, "M": False},
    "OVRPL": {"O": True, "TW": False, "L": True, "B": False, "M": False},
    "VRPBL": {"O": False, "TW": False, "L": True, "B": True, "M": False},
    "VRPBTW": {"O": False, "TW": True, "L": False, "B": True, "M": False},
    "VRPLTW": {"O": False, "TW": True, "L": True, "B": False, "M": False},
    "OVRPBL": {"O": True, "TW": False, "L": True, "B": True, "M": False},
    "OVRPBTW": {"O": True, "TW": True, "L": False, "B": True, "M": False},
    "OVRPLTW": {"O": True, "TW": True, "L": True, "B": False, "M": False},
    "VRPBLTW": {"O": False, "TW": True, "L": True, "B": True, "M": False},
    "OVRPBLTW": {"O": True, "TW": True, "L": True, "B": True, "M": False},
    "VRPMB": {"O": False, "TW": False, "L": False, "B": True, "M": True},
    "OVRPMB": {"O": True, "TW": False, "L": False, "B": True, "M": True},
    "VRPMBL": {"O": False, "TW": False, "L": True, "B": True, "M": True},
    "VRPMBTW": {"O": False, "TW": True, "L": False, "B": True, "M": True},
    "OVRPMBL": {"O": True, "TW": False, "L": True, "B": True, "M": True},
    "OVRPMBTW": {"O": True, "TW": True, "L": False, "B": True, "M": True},
    "VRPMBLTW": {"O": False, "TW": True, "L": True, "B": True, "M": True},
    "OVRPMBLTW": {"O": True, "TW": True, "L": True, "B": True, "M": True},
}


def get_vehicle_capacity(num_loc):
    if num_loc > 1000:
        extra_cap = 1000 // 5 + (num_loc - 1000) // 33.3
    elif num_loc > 20:
        extra_cap = num_loc // 5
    else:
        extra_cap = 0
    return 30 + extra_cap


def generate_mtvrp_data(
    dataset_size,
    num_loc=20,
    min_loc=0.0,
    max_loc=1.0,
    capacity=None,
    min_demand=1,
    max_demand=9,
    scale_demand=True,
    max_time=4.6,
    max_distance_limit=2.8,  # 2sqrt(2) ~= 2.8
    speed=1.0,
    variant="OVRPMBLTW",
):
    """Generate MTVRP data using NumPy for a specific variant."""

    variant = variant.upper()
    if variant not in VARIANT_FEATURES:
        raise ValueError(f"Unknown variant: {variant}")

    features = VARIANT_FEATURES[variant]

    if capacity is None:
        capacity = get_vehicle_capacity(num_loc)

    # Generate locations
    locs = np.random.uniform(min_loc, max_loc, (dataset_size, num_loc + 1, 2))

    # Generate demands
    def generate_demand(size):
        return (
            np.random.randint(min_demand, max_demand + 1, size).astype(np.float32)
            / capacity
        )

    demand_linehaul = generate_demand((dataset_size, num_loc))
    demand_backhaul = None

    if features["B"]:
        demand_backhaul = np.zeros((dataset_size, num_loc))
        backhaul_mask = (
            np.random.rand(dataset_size, num_loc) < 0.2
        )  # 20% of nodes are backhaul
        demand_backhaul[backhaul_mask] = generate_demand(backhaul_mask.sum())
        demand_linehaul[backhaul_mask] = 0

    # Generate backhaul class
    backhaul_class = (
        np.full((dataset_size, 1), 2 if features["M"] else 1) if features["B"] else None
    )

    # Generate open route
    open_route = np.full((dataset_size, 1), features["O"]) if features["O"] else None

    # Generate time windows and service time
    time_windows = None
    service_time = None
    if features["TW"]:
        a, b, c = 0.15, 0.18, 0.2
        service_time = a + (b - a) * np.random.rand(dataset_size, num_loc)
        tw_length = b + (c - b) * np.random.rand(dataset_size, num_loc)
        d_0i = np.linalg.norm(locs[:, 0:1] - locs[:, 1:], axis=2)
        h_max = (max_time - service_time - tw_length) / d_0i * speed - 1
        tw_start = (
            (1 + (h_max - 1) * np.random.rand(dataset_size, num_loc)) * d_0i / speed
        )
        tw_end = tw_start + tw_length

        time_windows = np.concatenate(
            [np.zeros((dataset_size, 1, 2)), np.stack([tw_start, tw_end], axis=-1)],
            axis=1,
        )
        time_windows[:, 0, 1] = max_time
        service_time = np.pad(service_time, ((0, 0), (1, 0)))

    # Generate distance limits: dist_lower_bound = 2 * max(depot_to_location_distance),
    # max = min(dist_lower_bound, max_distance_limit). Ensures feasible yet challenging
    # constraints, with each instance having a unique, meaningful limit.
    if features["L"]:
        # Calculate the maximum distance from depot to any location
        max_dist = np.max(np.linalg.norm(locs[:, 1:] - locs[:, 0:1], axis=2), axis=1)

        # Calculate the minimum distance limit (2 * max_distance)
        distance_lower_bound = 2 * max_dist + 1e-6  # Add epsilon to avoid zero distance

        # Ensure max_distance_limit is not exceeded
        max_distance_limit = np.maximum(max_distance_limit, distance_lower_bound + 1e-6)

        # Generate distance limits between min_distance_limits and max_distance_limit
        distance_limit = np.random.uniform(
            distance_lower_bound,
            np.full_like(distance_lower_bound, max_distance_limit),
            (dataset_size,),
        )[:, None]
    else:
        distance_limit = None

    # Generate speed
    speed = np.full((dataset_size, 1), speed)

    # Scale demand if needed
    if scale_demand:
        vehicle_capacity = np.full((dataset_size, 1), 1.0)
    else:
        vehicle_capacity = np.full((dataset_size, 1), capacity)
        if demand_backhaul is not None:
            demand_backhaul *= capacity
        demand_linehaul *= capacity

    data = {
        "locs": locs.astype(np.float32),
        "demand_linehaul": demand_linehaul.astype(np.float32),
        "vehicle_capacity": vehicle_capacity.astype(np.float32),
        "speed": speed.astype(np.float32),
    }

    # Only include features that are used in the variant
    if features["B"]:
        data["demand_backhaul"] = demand_backhaul.astype(np.float32)
        data["backhaul_class"] = backhaul_class.astype(np.float32)
    if features["O"]:
        data["open_route"] = open_route
    if features["TW"]:
        data["time_windows"] = time_windows.astype(np.float32)
        data["service_time"] = service_time.astype(np.float32)
    if features["L"]:
        data["distance_limit"] = distance_limit.astype(np.float32)

    return data

data = generate_mtvrp_data(dataset_size=1)
""" dataframe = pd.DataFrame(data=data)
dataframe.to_csv("OVRPMBLTW.csv") """
print(type(data))
print(len(data))

df_parts = []

# Flatten and convert each element in the dictionary into a DataFrame
Ids = pd.DataFrame([i for i in range(1,2*len(data)+2)],columns=['Ids'])
df_parts.append(Ids)
# Flatten 'locs' (2D points into separate x, y columns)
locs_df = pd.DataFrame(data['locs'][0], columns=['x', 'y'])
df_parts.append(locs_df)

# Flatten 'demand_linehaul' and add a readable column name
demand_linehaul_df = pd.DataFrame(data['demand_linehaul'][0], columns=['demand_linehaul'])
df_parts.append(demand_linehaul_df)

# Vehicle capacity (single value, just one column)
vehicle_capacity_df = pd.DataFrame(data['vehicle_capacity'][0], columns=['vehicle_capacity'])
df_parts.append(vehicle_capacity_df)

# Speed (single value, just one column)
speed_df = pd.DataFrame(data['speed'][0], columns=['speed'])
df_parts.append(speed_df)

# Flatten 'demand_backhaul' and add a readable column name
demand_backhaul_df = pd.DataFrame(data['demand_backhaul'][0], columns=['demand_backhaul'])
df_parts.append(demand_backhaul_df)

# Backhaul class (single value)
backhaul_class_df = pd.DataFrame(data['backhaul_class'][0], columns=['backhaul_class'])
df_parts.append(backhaul_class_df)

# Open route (boolean value)
open_route_df = pd.DataFrame(data['open_route'][0], columns=['open_route'])
df_parts.append(open_route_df)

# Flatten 'time_windows' to separate start and end time windows
time_windows_df = pd.DataFrame(data['time_windows'][0], columns=['time_window_start', 'time_window_end'])
df_parts.append(time_windows_df)

# Service time (single value)
service_time_df = pd.DataFrame(data['service_time'][0], columns=['service_time'])
df_parts.append(service_time_df)

# Distance limit (single value)
distance_limit_df = pd.DataFrame(data['distance_limit'][0], columns=['distance_limit'])
df_parts.append(distance_limit_df)
print(len(df_parts))
# Combine all DataFrame parts into one single DataFrame
final_df = pd.concat(df_parts, axis=1)
# Optionally, reset index for better readability
final_df.reset_index(drop=True, inplace=True)
print(len(final_df))

# Save the DataFrame to a CSV file
final_df.to_csv("Data/OVRPMBLTW.csv", index=False)

