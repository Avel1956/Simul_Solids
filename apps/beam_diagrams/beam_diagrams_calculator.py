import numpy as np
import sympy
from sympy import symbols, integrate, Piecewise, lambdify, DiracDelta, solve, Eq, Function, Heaviside, N
import random

# --- Dice Rolling and Interpretation ---
def roll_dice(num_dice=1):
    """Simulates rolling a specified number of dice."""
    return [random.randint(1, 6) for _ in range(num_dice)]

def interpret_dice_results(dice_values):
    """Interprets dice rolls according to the defined rules."""
    params = {}

    # 1. Left Support (Using first die of the set)
    support_left_die = dice_values['support_left'][0]
    params['support_left'] = 'Empotrado' if support_left_die <= 3 else 'Simple'

    # 2. Length
    params['length'] = sum(dice_values['length']) / 2.0
    L = params['length'] # For use in position calculations

    # 3. Point Load P Magnitude
    p_mag = sum(dice_values['point_load_p_mag'])
    # 4. Point Load P Position (as fraction of L, then scaled)
    p_pos_fraction = sum(dice_values['point_load_p_pos']) / 12.0
    p_pos = p_pos_fraction * L
    params['point_load_p'] = {'magnitude': p_mag, 'position': p_pos}

    # 5. Distributed Load w Magnitude
    w_mag = sum(dice_values['dist_load_w_mag'])
    # 6. Distributed Load w Span (start/end as fractions of L, then scaled)
    w_start_fraction = dice_values['dist_load_w_span'][0] / 6.0
    w_end_fraction = dice_values['dist_load_w_span'][1] / 6.0
    # Ensure start < end
    if w_start_fraction > w_end_fraction:
        w_start_fraction, w_end_fraction = w_end_fraction, w_start_fraction
    # Ensure end > start if they are the same
    if w_start_fraction == w_end_fraction:
         w_end_fraction = min(1.0, w_start_fraction + 1/6.0) # Make it span at least 1/6th L if possible

    w_start = w_start_fraction * L
    w_end = w_end_fraction * L
    params['dist_load_w'] = {'magnitude': w_mag, 'start': w_start, 'end': w_end}

    # 7. Right Support (Using first die of the set)
    support_right_die = dice_values['support_right'][0]
    params['support_right'] = 'Simple' if support_right_die <= 3 else 'Libre'

    # 8. EI
    params['EI'] = float(sum(dice_values['EI'])) # Ensure EI is float

    return params

# --- Core Calculation Function ---
def calculate_beam_diagrams(params):
    """Calculates reactions, shear, and moment diagrams using Sympy."""
    L = params['length']
    EI = params['EI'] # Although EI is passed, it's not used in V & M calculation itself
    support_left = params['support_left']
    support_right = params['support_right']
    p_load = params['point_load_p']
    w_load = params['dist_load_w']

    # Ensure load positions are within beam length
    p_load['position'] = min(max(0, p_load['position']), L)
    w_load['start'] = min(max(0, w_load['start']), L)
    w_load['end'] = min(max(w_load['start'], w_load['end']), L)


    x = symbols('x')
    R_A, R_B, M_A, M_B = symbols('R_A R_B M_A M_B') # Potential reactions

    calculation_steps = []
    calculation_steps.append(f"**1. Parámetros de Entrada:**")
    calculation_steps.append(f"- Longitud (L): {L}")
    calculation_steps.append(f"- Apoyo Izquierdo: {support_left}")
    calculation_steps.append(f"- Apoyo Derecho: {support_right}")
    calculation_steps.append(f"- Carga Puntual P: {p_load['magnitude']} @ x={p_load['position']:.2f}")
    calculation_steps.append(f"- Carga Distribuida w: {w_load['magnitude']} de x={w_load['start']:.2f} a x={w_load['end']:.2f}")
    # calculation_steps.append(f"- Rigidez (EI): {EI}") # EI not directly used for V, M

    # --- Define Loading Function w(x) ---
    w_expr = Piecewise(
        (w_load['magnitude'], (x >= w_load['start']) & (x <= w_load['end'])),
        (0, True)
    )

    calculation_steps.append(f"**2. Función de Carga Distribuida w(x):**")
    calculation_steps.append(f"w(x) = {sympy.latex(w_expr)}")
    calculation_steps.append(f"Carga puntual P = {p_load['magnitude']} en x = {p_load['position']:.2f}")


    # --- Calculate Reactions ---
    reactions = {}
    unknowns = []
    equations = []
    boundary_conditions = {} # Store known reaction values based on supports

    # Define equilibrium equations (symbolically)
    eq_Fy_sym = R_A + R_B - p_load['magnitude'] - integrate(w_expr, (x, 0, L))
    eq_MA_sym = M_A + R_B * L + M_B - p_load['magnitude'] * p_load['position'] - integrate(w_expr * x, (x, 0, L))

    # Left Support Conditions
    if support_left == 'Simple':
        boundary_conditions[M_A] = 0
        unknowns.append(R_A)
    elif support_left == 'Empotrado':
        # Deflection and slope are zero, but for V&M we need R_A, M_A
        unknowns.extend([R_A, M_A])
    else: # Free - Not physically realistic for stable left support in typical problems
          # For calculation purposes, assume R_A=0, M_A=0 if truly free
        boundary_conditions[R_A] = 0
        boundary_conditions[M_A] = 0


    # Right Support Conditions
    if support_right == 'Simple':
        boundary_conditions[M_B] = 0
        unknowns.append(R_B)
    elif support_right == 'Empotrado':
        unknowns.extend([R_B, M_B])
    elif support_right == 'Libre':
        boundary_conditions[R_B] = 0
        boundary_conditions[M_B] = 0

    # Substitute known boundary conditions into equilibrium equations
    eq_Fy = eq_Fy_sym.subs(boundary_conditions)
    eq_MA = eq_MA_sym.subs(boundary_conditions)

    # Add equations to the list to be solved
    if R_A in unknowns or R_B in unknowns: # Need Fy if any force is unknown
        equations.append(eq_Fy)
    if M_A in unknowns or M_B in unknowns or len(unknowns) > 1 : # Need MA if any moment is unknown, or if >1 force unknown
        equations.append(eq_MA)


    calculation_steps.append("**3. Cálculo de Reacciones:**")
    # Solve the system
    if unknowns:
        try:
            # Ensure we have enough equations for the unknowns
            if len(equations) < len(unknowns):
                 # This might happen in statically indeterminate cases if not handled by BCs
                 # Or if the support combination is unstable (e.g., Simple-Free)
                 raise ValueError(f"Sistema indeterminado o inestable. Incógnitas: {len(unknowns)}, Ecuaciones: {len(equations)}")

            sol = solve(equations, unknowns, dict=True) # Request dictionary output

            # Check if solve returned a list (multiple solutions) or empty list (no solution)
            if isinstance(sol, list):
                if not sol: # Empty list means no solution found
                    raise ValueError("No se encontró solución para las reacciones.")
                sol = sol[0] # Take the first solution if multiple exist (shouldn't for determinate beams)


            if not sol or not isinstance(sol, dict):
                 raise ValueError("No se pudo resolver el sistema de ecuaciones para las reacciones.")

            reactions = {**boundary_conditions, **sol} # Combine known and solved reactions
            calculation_steps.append("Reacciones calculadas:")
            for r, val in reactions.items():
                 calculation_steps.append(f"- `{sympy.pretty(r)} = {N(val):.3f}`")

        except Exception as e:
            calculation_steps.append(f"Error al calcular reacciones: {e}")
            # Provide default zero values for all potential reactions on error
            reactions = {R_A: 0, R_B: 0, M_A: 0, M_B: 0}
            # Update boundary conditions based on defaults if they were supposed to be calculated
            for unk in unknowns:
                if unk not in boundary_conditions:
                    reactions[unk] = 0
            calculation_steps.append("Usando reacciones por defecto (0).")
    else:
         calculation_steps.append("No hay incógnitas de reacción (viga estáticamente determinada por condiciones de contorno o libre).")
         reactions = boundary_conditions # All reactions were determined by BCs

    # Ensure all reaction values in the 'reactions' dict are numerical for substitution
    reactions_numeric = {k: N(v) for k, v in reactions.items()}


    # --- Define Shear V(x) using NUMERICAL reaction values ---
    # V(x) = R_A - integral(w(x)) dx - P*Heaviside(x-p_pos)
    V_expr_numeric = reactions_numeric.get(R_A, 0) - integrate(w_expr, (x, 0, x))
    if p_load['magnitude'] != 0:
        V_expr_numeric = V_expr_numeric - p_load['magnitude'] * Heaviside(x - p_load['position'])

    calculation_steps.append("**4. Ecuación de Fuerza Cortante V(x):**")
    # Display the symbolic version with symbols for reactions if possible, or the numeric one
    # Let's keep displaying the one with symbolic reactions for clarity in the steps
    V_expr_symbolic = reactions.get(R_A, 0) - integrate(w_expr, (x, 0, x))
    if p_load['magnitude'] != 0:
         V_expr_symbolic = V_expr_symbolic - p_load['magnitude'] * Heaviside(x - p_load['position'])
    calculation_steps.append(f"V(x) = {sympy.latex(V_expr_symbolic)}")


    # --- Define Moment M(x) using NUMERICAL reaction values ---
    # M(x) = M_A + integral(V(x)) dx
    # IMPORTANT: Integrate the NUMERIC V_expr for consistency in lambdify
    M_expr_numeric = reactions_numeric.get(M_A, 0) + integrate(V_expr_numeric, (x, 0, x))

    calculation_steps.append("**5. Ecuación de Momento Flector M(x):**")
    # Display the symbolic version
    M_expr_symbolic = reactions.get(M_A, 0) + integrate(V_expr_symbolic, (x, 0, x))
    calculation_steps.append(f"M(x) = {sympy.latex(M_expr_symbolic)}")


    # --- Numerical Evaluation ---
    x_vals = np.linspace(0, float(L), 500) # Ensure L is float for linspace
    shear_values = []
    moment_values = []

    calculation_steps.append("**6. Evaluación Numérica:**")
    try:
        # Lambdify the expressions that used NUMERICAL reaction values
        V_func = lambdify(x, V_expr_numeric, modules=['numpy', {'Heaviside': lambda x: np.heaviside(x, 1)}])
        M_func = lambdify(x, M_expr_numeric, modules=['numpy', {'Heaviside': lambda x: np.heaviside(x, 1)}])

        shear_values = V_func(x_vals)
        moment_values = M_func(x_vals)

        # Ensure results are numpy arrays of floats
        # Ensure results are numpy arrays of floats, handle potential complex numbers if any intermediate step produced them
        shear_values = np.array(shear_values, dtype=float)
        moment_values = np.array(moment_values, dtype=float)

        calculation_steps.append("- Evaluación numérica completada usando lambdify.")

    except Exception as e_lambdify:
        calculation_steps.append(f"- Falló Lambdify ({e_lambdify}), volviendo a la sustitución elemento por elemento.")
        shear_values = [] # Reset lists
        moment_values = []
        # Fallback to element-wise substitution using the NUMERIC expressions
        for x_val in x_vals:
            try:
                # Substitute into the expression with numerical reactions
                v_val = V_expr_numeric.subs(x, x_val)
                shear_values.append(float(N(v_val))) # Ensure float conversion
            except (TypeError, ValueError, AttributeError) as eval_err_v: # Added AttributeError
                 calculation_steps.append(f"- Advertencia: No se pudo evaluar V({x_val:.2f}) por sustitución: {eval_err_v}. Usando 0.")
                 shear_values.append(0.0) # Default to 0 on error
            try:
                # Substitute into the expression with numerical reactions
                m_val = M_expr_numeric.subs(x, x_val)
                moment_values.append(float(N(m_val))) # Ensure float conversion
            except (TypeError, ValueError, AttributeError) as eval_err_m: # Added AttributeError
                 calculation_steps.append(f"- Advertencia: No se pudo evaluar M({x_val:.2f}) por sustitución: {eval_err_m}. Usando 0.")
                 moment_values.append(0.0) # Default to 0 on error

        # Ensure conversion to numpy arrays even in fallback
        shear_values = np.array(shear_values, dtype=float)
        moment_values = np.array(moment_values, dtype=float)
        # Check for NaNs which might indicate issues
        if not np.any(np.isnan(shear_values)) and not np.any(np.isnan(moment_values)):
             calculation_steps.append("- Evaluación numérica por sustitución completada.")
        else:
             calculation_steps.append("- Advertencia: Se encontraron NaNs durante la evaluación por sustitución. Se convirtieron a 0.")
             shear_values = np.nan_to_num(shear_values) # Convert NaNs to 0
             moment_values = np.nan_to_num(moment_values) # Convert NaNs to 0


    results = {
        'reactions': {str(k): float(N(v)) for k, v in reactions.items()}, # Store original reactions as floats
        'shear_eq': V_expr_symbolic, # Store the symbolic equation for display
        'moment_eq': M_expr_symbolic, # Store the symbolic equation for display
        'x_values': x_vals,
        'shear_values': shear_values, # Store the final numerical values
        'moment_values': moment_values,
        'calculation_steps': calculation_steps
    }
    return results
