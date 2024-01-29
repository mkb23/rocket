from collections import namedtuple
from math import log

# ---------- simulation constants & helpers ----------

kerbin_radius = 600 * 1000
kerbin_mass = 5.29e22  # Kg
G = 6.67e-11
soi_exit_alt = 86 * 1000 * 1000  # metres

Stage = namedtuple('Stage', ['start_mass_tons', 'end_mass_tons', 'thrust_kns', 'isp', 'burn_time'])
Weights = namedtuple('Weights', ['absolute_dv', 'absolute_payload', 'cost_per_kilo', 'cost_per_unit_dv'])


def gravity_at_alt(alt):
    little_mass = 1
    return G * 1 * kerbin_mass / (kerbin_radius + alt) ** 2


def reaches_exit_soi(cvel, calt):
    coast = 0
    while cvel > 0 and calt < soi_exit_alt:
        accel = 0 - gravity_at_alt(calt)
        cvel += accel
        calt += cvel
        coast += 1
    return calt > soi_exit_alt, calt, coast


# ----------- simulation ------------

def simulate(stages):
    stages = stages[::-1]

    alt = 0
    vel = 0
    scale = 10

    tot_burn_time = sum(s.burn_time for s in stages)
    if tot_burn_time > 60 * 5:
        print(f'WARNING!!! THIS ROCKET WILL TAKE UP TO {tot_burn_time} SEC TO FLY QUALIFICATION FLIGHT')
        print('            YOU MAY RUN OUT OF TIME TO QUALIFY IT')
        input('Press RETURN to fly or CTRL+C to abort\n')

    print(f'Gravity at sea level = {gravity_at_alt(0):.2f} m/s^2')

    for sno in range(len(stages)):
        s = stages[sno]
        is_last_stage = sno == len(stages) - 1

        thrust = s.thrust_kns * 1000  # Kilo-newtons
        mass = s.start_mass_tons * 1000
        end_mass = s.end_mass_tons * 1000
        mass_step = (mass - end_mass) / (s.burn_time * scale)

        print(f'------- STAGE {sno} --------')
        print('TIME      ALT     VEL      TWR')
        for x in range(s.burn_time * scale):
            galt = gravity_at_alt(alt)

            alt = alt + vel * (1.0 / scale)
            accel = (thrust - mass * galt) / mass
            vel += accel * (1.0 / scale)
            twr = thrust / (mass * galt)
            mass -= mass_step
            if x % 100 == 0 or x == (s.burn_time * scale - 1): print(
                f'{x / 10:03.1f}s  {alt:6.0f}  {vel:6.2f}    {twr:.2f}')
            if x % 10 == 0:
                if reaches_exit_soi(vel, alt)[0]:
                    print(f'Reached velocity to coast to SOI exit with burn time {x / scale:.1f}s')
                    print(f'Remaining mass = {mass:.0f}kg ; Dry mass = {(end_mass):.0f}kg')

                    def delta_v_calc(isp, mwet, mdry):
                        return isp * 9.8 * log(mwet / mdry)

                    delta_v = delta_v_calc(s.isp, mass, end_mass)
                    delta_v += sum(
                        delta_v_calc(st.isp, st.start_mass_tons, st.end_mass_tons) for st in stages[sno + 1:])

                    print(f'Remaining Delta V at SOI exit = {delta_v:.0f} m/s')
                    return delta_v

        if is_last_stage:
            _, alt, coast = reaches_exit_soi(vel, alt)
            print(f'Failed to reach velocity to exit SOI. Coasted for {coast / 3600:.2f} hrs')
            print(f'Height reached: {alt / 1000:.0f}km')
            return None
