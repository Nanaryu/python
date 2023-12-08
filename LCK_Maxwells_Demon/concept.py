def update_particle_position_velocity(x_initial, v_initial, t):
    # Update position
    x_final = x_initial + v_initial * t

    # Reflect at the wall
    if x_final <= 0:
        v_final = abs(v_initial)
    else:
        v_final = -abs(v_initial)

    return x_final, v_final

def check_particle_collisions(x1, x2, v1, v2, radius):
    # Check if particles collide
    if abs(x1 - x2) < 2 * radius:
        # Simple elastic collision formula for 1D
        v1_final = ((radius - 1) * v1 + (radius + 1) * v2) / (radius + 1)
        v2_final = ((radius + 1) * v1 + (radius - 1) * v2) / (radius + 1)
        return v1_final, v2_final
    else:
        return v1, v2

def return_energy(mass, velocity):
    return 0.5 * mass * velocity**2  # Correcting the energy calculation

# Example usage

time_step = 1.0
for _ in range(int(input())):
    n = input()
    num_particles = int(n.split(" ")[0])
    simulation_time = float(n.split(" ")[1])
    masses = []
    initial_positions = []
    initial_velocities = []
    for _ in range(num_particles):
        p_info = input().split(" ")
        masses.append(float(p_info[0]))
        initial_positions.append(float(p_info[1]))
        initial_velocities.append(float(p_info[2]))
    
    particle_radius = 0.1
    for t in range(int(simulation_time / time_step)):
        # Update particle positions and velocities
        for i in range(num_particles):
            initial_positions[i], initial_velocities[i] = update_particle_position_velocity(
                initial_positions[i], initial_velocities[i], time_step
            )

        # Check for particle-wall collisions
        for i in range(num_particles):
            initial_positions[i], initial_velocities[i] = update_particle_position_velocity(
                initial_positions[i], initial_velocities[i], time_step
            )
            # Reflect at the wall
            if initial_positions[i] <= 0:
                initial_velocities[i] = abs(initial_velocities[i])
            else:
                initial_velocities[i] = -abs(initial_velocities[i])

        # Check for particle-particle collisions
        for i in range(num_particles):
            for j in range(i + 1, num_particles):
                initial_velocities[i], initial_velocities[j] = check_particle_collisions(
                    initial_positions[i], initial_positions[j], initial_velocities[i], initial_velocities[j], particle_radius
                )
    left = 0
    right = 0
    for i in range(num_particles):
        if initial_positions[i] < 0.5:
            left += return_energy(masses[i], initial_velocities[i])
        elif initial_positions[i] > 0.5:
            right += return_energy(masses[i], initial_velocities[i])

    if left < right:
        print("RIGHT")
    elif left > right:
        print("LEFT")
    #print(f"Particle {i+1}: Final Position = {initial_positions[i]}, Final Velocity = {initial_velocities[i]}, Energy = {return_energy(masses[i], initial_velocities[i])}")
