from math import log
from collections import namedtuple

Stage = namedtuple('Stage', ['start_mass_tons', 'end_mass_tons', 'thrust_kns', 'isp', 'burn_time'])

# ---------- rocket parameters --------------

payload_mass_tons = 1.0
rocket_cost = 33000

stages = [
    Stage(start_mass_tons=81.4, end_mass_tons=49.4, thrust_kns=2000, isp=280, burn_time=47),
    Stage(start_mass_tons=38.75, end_mass_tons=6.75, thrust_kns=250, isp=350, burn_time=7*60+20),
]

# ---------- simulation constants & helpers ----------

kerbin_radius = 600 * 1000
kerbin_mass = 5.29e22   #Kg
G = 6.67e-11
soi_exit_alt = 86 * 1000 * 1000 # metres

def gravity_at_alt(alt):
    little_mass = 1
    return G * 1 * kerbin_mass / (kerbin_radius + alt)**2

def reaches_exit_soi(cvel, calt):
    coast = 0
    while cvel > 0 and calt < soi_exit_alt:
        accel = 0 - gravity_at_alt(calt)      
        cvel += accel 
        calt += cvel
        coast += 1
    return (calt > soi_exit_alt, calt, coast)
            
print(f'Gravity at sea level = {gravity_at_alt(0):.2f} m/s^2')

# ----------- simulation ------------

def simulate(stages):
    alt = 0
    vel = 0
    scale = 10

    for sno in range(len(stages)):
        s = stages[sno]
        is_last_stage = sno == len(stages)-1

        thrust = s.thrust_kns * 1000       #Kilo-newtons    
        mass = s.start_mass_tons * 1000
        end_mass = s.end_mass_tons * 1000
        mass_step = (mass - end_mass) / (s.burn_time*scale)

        print(f'------- STAGE {sno} --------')
        print('TIME      ALT     VEL      TWR')
        for x in range(s.burn_time * scale):  
            galt = gravity_at_alt(alt)      

            alt = alt + vel * (1.0/scale)
            accel = (thrust - mass * galt) / mass
            vel += accel * (1.0/scale)
            twr = thrust / (mass * galt)
            mass -= mass_step
            if x % 100 == 0 or x == (s.burn_time*scale-1): print(f'{x/10:03.1f}s  {alt:6.0f}  {vel:6.2f}    {twr:.2f}')
            if x % 10 == 0 and is_last_stage:
                if reaches_exit_soi(vel, alt)[0]:
                    print(f'Reached velocity to coast to SOI exit with burn time {x/scale:.1f}s')
                    print(f'Remaining mass = {mass:.0f}kg ; Dry mass = {(end_mass):.0f}kg')
                    delta_v = s.isp * 9.8 * log(mass / end_mass)
                    print(f'Remaining Delta V at SOI exit = {delta_v:.0f} m/s')
                    return delta_v

        if is_last_stage:
            _, alt, coast = reaches_exit_soi(vel, alt)
            print(f'Failed to reach velocity to exit SOI. Coasted for {coast/3600:.2f} hrs')
            print(f'Height reached: {alt/1000:.0f}km')
            return None

soi_exit_delta_v = simulate(stages)

cost_per_kilo = payload_mass_tons * 1000 / rocket_cost
cost_per_unit_dv = soi_exit_delta_v / rocket_cost

# ------------------ scoring ---------------

if soi_exit_delta_v is not None:
    print('\n======== SCORING =========\n')
    print(f'Total Rocket cost: ${rocket_cost}')
    print(f'Cost / kg: ${cost_per_kilo:.4f}')
    print(f'Cost / unit DV: ${cost_per_unit_dv:.4f}')
    print(f'Available DV: {soi_exit_delta_v:.0f} m/s')

    points_absolute_cost = 1 - (rocket_cost / 200000)
    points_absolute_dv = soi_exit_delta_v / 10000
    points_cost_per_kilo = cost_per_kilo / 2.0
    points_cost_per_unit_dv = cost_per_unit_dv / 2.0

    weight_absolute_cost = 0.25
    weight_absolute_dv = 0.25
    weight_cost_per_kilo = 0.25
    weight_cost_per_unit_dv = 0.25

    final_score = points_absolute_cost * weight_absolute_cost + \
                points_absolute_dv * weight_absolute_dv + \
                points_cost_per_kilo * weight_cost_per_kilo + \
                points_cost_per_unit_dv * weight_cost_per_unit_dv

    print(f'FINAL SCORE = {final_score:.2f}')