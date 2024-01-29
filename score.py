def calc_score(soi_exit_delta_v, payload_mass_tons, rocket_cost, weights):
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

    final_score = points_absolute_payload * weights.absolute_payload + \
                  points_absolute_dv * weights.absolute_dv + \
                  points_cost_per_kilo * weights.cost_per_kilo + \
                  points_cost_per_unit_dv * weights.cost_per_unit_dv

    print('\nWEIGHTINGS')
    print(f'   payload_mass     {weights.absolute_payload * 100:4.0f}%')
    print(f'   absolute_dv      {weights.absolute_dv * 100:4.0f}%')
    print(f'   cost_per_kilo    {weights.cost_per_kilo * 100:4.0f}%')
    print(f'   cost_per_unit_dv {weights.cost_per_unit_dv * 100:4.0f}%')
    print(f'\nFINAL SCORE = {final_score:.2f}')
