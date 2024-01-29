from sim import simulate, Stage, Weights
from score import calc_score

# ---------- rocket parameters --------------

# read these out from KSP
soi_exit_delta_v = None  # set this to "None" if you want to simulate
payload_mass_tons = 0.5
rocket_cost = 50000

if soi_exit_delta_v is None:
    # ----------- simulation parameters

    # Read these stage stats out of mechjeb, but be sure to pick the vacuum ISP for the final
    # stage as this will determine the final delta V estimate. You don't need these if
    # you are just calculating the scores from your run
    #         start mass             end mass            max thrust       ISP      time
    stages = [
        Stage(start_mass_tons=3, end_mass_tons=2, thrust_kns=20, isp=320, burn_time=100),
        Stage(start_mass_tons=20, end_mass_tons=5, thrust_kns=670, isp=280, burn_time=20),
        Stage(start_mass_tons=80, end_mass_tons=25, thrust_kns=2500, isp=195, burn_time=40)
    ]
    soi_exit_delta_v = simulate(stages)

# ----------- scoring weights ... how important is each parameter? These should sum to 1.0
weights = Weights(
    absolute_payload=0.25,
    absolute_dv=0.25,
    cost_per_kilo=0.25,
    cost_per_unit_dv=0.25)

calc_score(soi_exit_delta_v, payload_mass_tons, rocket_cost, weights)