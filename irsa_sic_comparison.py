"""
IRSA/CRDSA/FSA comparison with and without SIC.
Reproduces the two-panel throughput and packet-loss plots used in the project slide.

Model: collision-channel abstraction. A slot is decodable when exactly one
undecoded packet remains in it. SIC removes a decoded user's replicas from
all its other slots. This is packet-level simulation, not GNU Radio/RF simulation.
"""
import numpy as np
import matplotlib.pyplot as plt
from collections import deque

NUM_SLOTS = 200
FRAMES_PER_LOAD = 800
LOADS = np.round(np.arange(0.10, 1.001, 0.05), 2)
SEED = 42

# Project IRSA repetition distribution: degree 2, 3, or 8
IRSA_DISTRIBUTION = {2: 0.50, 3: 0.28, 8: 0.22}

def make_graph(n_users, n_slots, degree_distribution, rng, fixed_degree=None):
    """Return each user's replica slots and the users occupying each slot."""
    user_slots = []
    slot_users = [[] for _ in range(n_slots)]
    degrees = np.array(list(degree_distribution.keys()))
    probabilities = np.array(list(degree_distribution.values()), dtype=float)
    probabilities /= probabilities.sum()

    for user in range(n_users):
        degree = fixed_degree if fixed_degree is not None else int(
            rng.choice(degrees, p=probabilities)
        )
        chosen = rng.choice(n_slots, size=min(degree, n_slots), replace=False)
        chosen = np.asarray(chosen, dtype=int)
        user_slots.append(chosen)
        for slot in chosen:
            slot_users[slot].append(user)
    return user_slots, slot_users

def decode_with_sic(user_slots, slot_users, num_users):
    """Iteratively decode singleton slots and cancel that user's replicas."""
    slot_degree = np.array([len(users) for users in slot_users], dtype=int)
    decoded = np.zeros(num_users, dtype=bool)
    queue = deque(np.flatnonzero(slot_degree == 1))

    while queue:
        slot = queue.popleft()
        if slot_degree[slot] != 1:
            continue

        # Find the sole user not already decoded in this slot.
        candidates = [u for u in slot_users[slot] if not decoded[u]]
        if len(candidates) != 1:
            continue
        user = candidates[0]
        decoded[user] = True

        # Ideal packet-level SIC: subtract this user's replicas everywhere.
        for other_slot in user_slots[user]:
            if slot_degree[other_slot] > 0:
                slot_degree[other_slot] -= 1
                if slot_degree[other_slot] == 1:
                    queue.append(int(other_slot))

    return int(decoded.sum())

def decode_without_sic(user_slots, slot_users, num_users):
    """Decode only packets that have a singleton slot before any cancellation."""
    singleton_users = set()
    for occupants in slot_users:
        if len(occupants) == 1:
            singleton_users.add(occupants[0])
    return len(singleton_users)

def run_one_frame(n_users, method, rng):
    if method == "FSA":
        distribution, fixed_degree, use_sic = {1: 1.0}, 1, False
    elif method == "CRDSA + SIC":
        distribution, fixed_degree, use_sic = {2: 1.0}, 2, True
    elif method == "IRSA (no SIC)":
        distribution, fixed_degree, use_sic = IRSA_DISTRIBUTION, None, False
    elif method == "IRSA + SIC":
        distribution, fixed_degree, use_sic = IRSA_DISTRIBUTION, None, True
    else:
        raise ValueError(method)

    user_slots, slot_users = make_graph(
        n_users, NUM_SLOTS, distribution, rng, fixed_degree
    )
    if use_sic:
        decoded = decode_with_sic(user_slots, slot_users, n_users)
    else:
        decoded = decode_without_sic(user_slots, slot_users, n_users)

    plr = (n_users - decoded) / n_users if n_users else 0.0
    throughput = decoded / NUM_SLOTS
    return plr, throughput

def simulate():
    methods = ["IRSA + SIC", "CRDSA + SIC", "FSA", "IRSA (no SIC)"]
    results = {m: {"plr": [], "throughput": []} for m in methods}
    rng = np.random.default_rng(SEED)

    for load in LOADS:
        n_users = max(1, int(round(load * NUM_SLOTS)))
        print(f"Simulating G={load:.2f}, users={n_users} ...")
        for method in methods:
            frame_plr, frame_thr = [], []
            for _ in range(FRAMES_PER_LOAD):
                plr, throughput = run_one_frame(n_users, method, rng)
                frame_plr.append(plr)
                frame_thr.append(throughput)
            results[method]["plr"].append(float(np.mean(frame_plr)))
            results[method]["throughput"].append(float(np.mean(frame_thr)))
    return results

def plot_results(results):
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.2))
    styles = {
        "IRSA + SIC": dict(marker="o", linewidth=2.0),
        "CRDSA + SIC": dict(marker="s", linewidth=1.8),
        "FSA": dict(marker="^", linewidth=1.8),
        "IRSA (no SIC)": dict(marker=".", linewidth=1.8),
    }

    # Throughput panel
    for method, data in results.items():
        axes[0].plot(LOADS, data["throughput"], label=method, **styles[method])
    axes[0].plot(LOADS, LOADS, "--", color="gray", linewidth=1,
                 label="Ideal T = G")
    axes[0].set_xlabel("Offered load G (packets/slot)")
    axes[0].set_ylabel("Throughput T (decoded packets/slot)")
    axes[0].set_title("Throughput versus offered load")
    axes[0].set_xlim(0.1, 1.0)
    axes[0].set_ylim(0, 1.0)
    axes[0].grid(True, alpha=0.3)
    axes[0].legend(fontsize=8)

    # Packet-loss panel (log scale)
    for method, data in results.items():
        axes[1].semilogy(LOADS, np.maximum(data["plr"], 1e-5),
                         label=method, **styles[method])
    axes[1].set_xlabel("Offered load G (packets/slot)")
    axes[1].set_ylabel("Packet loss rate (PLR)")
    axes[1].set_title("Packet loss rate versus offered load")
    axes[1].set_xlim(0.1, 1.0)
    axes[1].set_ylim(1e-5, 1.0)
    axes[1].grid(True, which="both", alpha=0.3)
    axes[1].legend(fontsize=8)

    fig.suptitle(
        f"IRSA/SIC comparison | {NUM_SLOTS} slots/frame | "
        f"{FRAMES_PER_LOAD} frames/load point"
    )
    fig.tight_layout()
    fig.savefig("irsa_sic_comparison.png", dpi=300, bbox_inches="tight")
    plt.show()

if __name__ == "__main__":
    print("IRSA repetition distribution:", IRSA_DISTRIBUTION)
    print("Average IRSA replicas:",
          sum(d * p for d, p in IRSA_DISTRIBUTION.items()))
    simulation_results = simulate()
    plot_results(simulation_results)
