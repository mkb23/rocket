from math import log
from collections import namedtuple

Stage = namedtuple('Stage', ['start_mass_tons', 'end_mass_tons', 'thrust_kns', 'isp', 'burn_time'])

# ---------- rocket parameters --------------

qualification_soi_exit_delta_v = None   # set this to "None" if you want to simulate
payload_mass_tons = 1
rocket_cost = 4151

# Read these stage stats out of mechjeb, but be sure to pick the vacuum ISP for the final
# stage as this will determine the final delta V estimate
#         start mass             end mass            max thrust       ISP      time
stages = [
    Stage(start_mass_tons=1.580, end_mass_tons=1.180, thrust_kns=20,  isp=320, burn_time=62),
    Stage(start_mass_tons=3.070, end_mass_tons=1.870, thrust_kns=20,  isp=320, burn_time=188),
    Stage(start_mass_tons=27.080,  end_mass_tons=7.580, thrust_kns=670, isp=195, burn_time=62)
]

# ---------- simulation constants & helpers ----------

stages = stages[::-1]
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
            
# ----------- simulation ------------

def simulate(stages):
    alt = 0
    vel = 0
    scale = 10

    tot_burn_time = sum(s.burn_time for s in stages)
    if tot_burn_time > 60*5:
        print(f'WARNING!!! THIS ROCKET WILL TAKE UP TO {tot_burn_time} SEC TO FLY QUALIFICATION FLIGHT')
        print('            YOU MAY RUN OUT OF TIME TO QUALIFY IT')
        input('Press RETURN to fly or CTRL+C to abort\n')

    print(f'Gravity at sea level = {gravity_at_alt(0):.2f} m/s^2')

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
            if x % 10 == 0:
                if reaches_exit_soi(vel, alt)[0]:
                    print(f'Reached velocity to coast to SOI exit with burn time {x/scale:.1f}s')
                    print(f'Remaining mass = {mass:.0f}kg ; Dry mass = {(end_mass):.0f}kg')
                    def delta_v_calc(isp, mwet, mdry):
                        return isp * 9.8 * log(mwet/mdry)
                    
                    delta_v = delta_v_calc(s.isp, mass, end_mass)
                    delta_v += sum(delta_v_calc(st.isp, st.start_mass_tons, st.end_mass_tons) for st in stages[sno+1:])

                    print(f'Remaining Delta V at SOI exit = {delta_v:.0f} m/s')                    
                    return delta_v

        if is_last_stage:
            _, alt, coast = reaches_exit_soi(vel, alt)
            print(f'Failed to reach velocity to exit SOI. Coasted for {coast/3600:.2f} hrs')
            print(f'Height reached: {alt/1000:.0f}km')
            return None

soi_exit_delta_v = qualification_soi_exit_delta_v or simulate(stages)

# ------------------ scoring ---------------

if soi_exit_delta_v is not None:
    cost_per_kilo = rocket_cost / (payload_mass_tons * 1000)
    cost_per_unit_dv = rocket_cost / soi_exit_delta_v

    points_absolute_payload = min(float(payload_mass_tons) / 25, 1)
    points_absolute_dv = min(soi_exit_delta_v / 5000, 1)
    points_cost_per_kilo = 1 - min(cost_per_kilo / 20.0, 1)
    points_cost_per_unit_dv = 1 - min(cost_per_unit_dv / 50.0, 1)

    print('\n======== SCORING =========\n')
    print(f'Total payload mass : {payload_mass_tons:5.1f} tons    / 25t   = {points_absolute_payload:.2f} pts')
    print(f'Available DV       : {soi_exit_delta_v:5.0f} m/s     / 5K    = {points_absolute_dv:.2f} pts')
    print(f'Cost / kg          : {cost_per_kilo:5.2f} $       / 20    = {points_cost_per_kilo:.2f} pts')
    print(f'Cost / unit DV     : {cost_per_unit_dv:5.2f} $       / 50    = {points_cost_per_unit_dv:.2f} pts')


    weight_absolute_payload = 0.25
    weight_absolute_dv = 0.25
    weight_cost_per_kilo = 0.25
    weight_cost_per_unit_dv = 0.25

    final_score = points_absolute_payload * weight_absolute_payload + \
                points_absolute_dv * weight_absolute_dv + \
                points_cost_per_kilo * weight_cost_per_kilo + \
                points_cost_per_unit_dv * weight_cost_per_unit_dv

    print('\nWEIGHTINGS')
    print(f'   payload_mass     {weight_absolute_payload*100:4.0f}%')
    print(f'   absolute_dv      {weight_absolute_payload*100:4.0f}%')
    print(f'   cost_per_kilo    {weight_absolute_payload*100:4.0f}%')
    print(f'   cost_per_unit_dv {weight_absolute_payload*100:4.0f}%')
    print(f'\nFINAL SCORE = {final_score:.2f}')