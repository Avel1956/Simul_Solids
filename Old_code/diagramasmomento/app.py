import streamlit as st
import numpy as np
import plotly.graph_objects as go
import sympy
from sympy import symbols, integrate, Piecewise, lambdify
import random

# --- Configuration ---
st.set_page_config(layout="wide", page_title="Beam Diagram Generator")

# --- Title ---
st.title("📊 Generador Interactivo de Diagramas de Viga")
st.markdown("""
Esta aplicación simula la configuración de una viga basada en lanzamientos de dados (o entrada manual)
y genera los diagramas de cortante y momento, junto con una memoria de cálculo interactiva.
""")

# --- Placeholder for future functions ---
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


from sympy import symbols, integrate, Piecewise, lambdify, DiracDelta, solve, Eq, Function, Heaviside, N

def calculate_beam_diagrams(params):
    """Calculates reactions, shear, and moment diagrams using Sympy."""
    L = params['length']
    EI = params['EI']
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
    calculation_steps.append(f"- Rigidez (EI): {EI}")

    # --- Define Loading Function w(x) ---
    w_expr = Piecewise(
        (w_load['magnitude'], (x >= w_load['start']) & (x <= w_load['end'])),
        (0, True)
    )

    calculation_steps.append(f"**2. Función de Carga Distribuida w(x):**")
    # Use LaTeX for equations
    calculation_steps.append(f"w(x) = {sympy.latex(w_expr)}")
    calculation_steps.append(f"Carga puntual P = {p_load['magnitude']} en x = {p_load['position']:.2f}")


    # --- Calculate Reactions ---
    # This part needs to be robust for different support combinations.
    # Using equilibrium equations.
    reactions = {}
    unknowns = []

    # Define equilibrium equations
    eq_Fy = R_A + R_B - p_load['magnitude'] - integrate(w_expr, (x, 0, L))
    eq_MA = M_A + R_B * L + M_B - p_load['magnitude'] * p_load['position'] - integrate(w_expr * x, (x, 0, L))

    equations = []
    boundary_conditions = {} # Store reaction values

    # Left Support Conditions
    if support_left == 'Simple':
        boundary_conditions[M_A] = 0
        unknowns.extend([R_A])
    elif support_left == 'Empotrado':
        unknowns.extend([R_A, M_A])
    else: # Free - Not typical for left support, treat as error or simple?
        st.warning("Apoyo izquierdo 'Libre' no es típico, tratando como Simple.")
        boundary_conditions[M_A] = 0
        unknowns.extend([R_A])


    # Right Support Conditions
    if support_right == 'Simple':
        boundary_conditions[M_B] = 0
        unknowns.extend([R_B])
    elif support_right == 'Empotrado':
         unknowns.extend([R_B, M_B])
    elif support_right == 'Libre':
        boundary_conditions[R_B] = 0
        boundary_conditions[M_B] = 0
        # R_A and M_A should be the only unknowns if left is fixed

    # Add equilibrium equations if needed
    if len(unknowns) > 0:
        equations.append(eq_Fy.subs(boundary_conditions))
    if len(unknowns) > 1: # Need moment equation if more than one unknown force/moment
         # Substitute known boundary conditions into the moment equation
         eq_MA_subbed = eq_MA
         # Check which moments are known and substitute
         if M_A in boundary_conditions:
             eq_MA_subbed = eq_MA_subbed.subs(M_A, boundary_conditions[M_A])
         if M_B in boundary_conditions:
             eq_MA_subbed = eq_MA_subbed.subs(M_B, boundary_conditions[M_B])
         # Check which forces are known and substitute (e.g., R_B for free end)
         if R_B in boundary_conditions:
              eq_MA_subbed = eq_MA_subbed.subs(R_B, boundary_conditions[R_B])

         equations.append(eq_MA_subbed)


    calculation_steps.append("**3. Cálculo de Reacciones:**")
    # Solve the system
    if unknowns:
        try:
            # Filter equations to only include those necessary for the unknowns
            # This logic might need refinement for complex cases like fixed-fixed
            num_eq = len(unknowns)
            sol = solve(equations[:num_eq], unknowns)

            if not sol or not isinstance(sol, dict):
                 # Handle cases where solve returns a list or empty set
                 raise ValueError("No se encontró una solución única para las reacciones.")

            reactions = {**boundary_conditions, **sol} # Combine known and solved reactions
            calculation_steps.append("Reacciones calculadas:")
            for r, val in reactions.items():
                 # Use N() to force numerical evaluation for display
                 calculation_steps.append(f"- `{sympy.pretty(r)} = {N(val):.3f}`")

        except Exception as e:
            calculation_steps.append(f"Error al calcular reacciones: {e}")
            reactions = {R_A: 0, R_B: 0, M_A: 0, M_B: 0} # Default on error
            calculation_steps.append("Usando reacciones por defecto (0).")
    else:
         calculation_steps.append("No hay incógnitas de reacción (viga libre o estáticamente determinada por condiciones de contorno).")
         reactions = boundary_conditions


    # --- Integrate for Shear V(x) ---
    # V(x) = R_A - integral(w(x)) dx - P*Heaviside(x-p_pos)
    V_expr = reactions.get(R_A, 0) - integrate(w_expr, (x, 0, x)) # Integrate from 0 to x
    # Add jump for point load P
    if p_load['magnitude'] != 0:
        V_expr = V_expr - p_load['magnitude'] * Heaviside(x - p_load['position'])

    calculation_steps.append("**4. Ecuación de Fuerza Cortante V(x):**")
    # calculation_steps.append(st.latex(f"V(x) = R_A - \\int_0^x w(t) dt - P \\cdot H(x - x_P)")) # Keep as comment or remove
    # Use LaTeX for equations
    calculation_steps.append(f"V(x) = {sympy.latex(V_expr)}")


    # --- Integrate for Moment M(x) ---
    # M(x) = M_A + integral(V(x)) dx
    M_expr = reactions.get(M_A, 0) + integrate(V_expr, (x, 0, x)) # Integrate from 0 to x

    calculation_steps.append("**5. Ecuación de Momento Flector M(x):**")
    # calculation_steps.append(st.latex(f"M(x) = M_A + \\int_0^x V(t) dt")) # Keep as comment or remove
    # Use LaTeX for equations
    calculation_steps.append(f"M(x) = {sympy.latex(M_expr)}")


    # --- Numerical Evaluation using element-wise substitution ---
    x_vals = np.linspace(0, float(L), 500) # Ensure L is float for linspace
    shear_values = []
    moment_values = []

    calculation_steps.append("**6. Evaluación Numérica:**")
    try:
        for x_val in x_vals:
            try:
                # Evaluate Shear
                v_val = V_expr.subs(x, x_val)
                # Ensure it's a number, handle potential symbolic results if substitution fails
                shear_values.append(float(N(v_val)))
            except (TypeError, ValueError) as eval_err_v:
                 calculation_steps.append(f"- Advertencia: No se pudo evaluar V({x_val:.2f}): {eval_err_v}. Usando 0.")
                 shear_values.append(0.0) # Default to 0 on error

            try:
                 # Evaluate Moment
                m_val = M_expr.subs(x, x_val)
                # Ensure it's a number
                moment_values.append(float(N(m_val)))
            except (TypeError, ValueError) as eval_err_m:
                 calculation_steps.append(f"- Advertencia: No se pudo evaluar M({x_val:.2f}): {eval_err_m}. Usando 0.")
                 moment_values.append(0.0) # Default to 0 on error

        # Convert lists to numpy arrays
        shear_values = np.array(shear_values, dtype=float)
        moment_values = np.array(moment_values, dtype=float)
        calculation_steps.append("- Evaluación numérica completada.")

    except Exception as e:
        st.error(f"Error general durante la evaluación numérica: {e}")
        calculation_steps.append(f"Error general durante la evaluación numérica: {e}")
        shear_values = np.zeros_like(x_vals)
        moment_values = np.zeros_like(x_vals)


    results = {
        'reactions': {str(k): float(N(v)) for k, v in reactions.items()}, # Store reactions as floats
        'shear_eq': V_expr,
        'moment_eq': M_expr,
        'x_values': x_vals,
        'shear_values': shear_values,
        'moment_values': moment_values,
        'calculation_steps': calculation_steps
    }
    return results

def plot_diagram(x, y, title, y_label):
    """Generates a Plotly figure for shear or moment."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name=y_label))
    fig.update_layout(
        title=title,
        xaxis_title="Posición (x)",
        yaxis_title=y_label,
        hovermode="x unified"
    ) # <-- Added closing parenthesis here
    # Add horizontal line at y=0 for reference
    fig.add_hline(y=0, line_width=1, line_dash="dash", line_color="grey")
    # Fill area under curve for the main trace
    fig.update_traces(fill='tozeroy', selector=dict(name=y_label)) # Target the specific trace
    return fig # <-- Moved return statement to the end of the function

def plot_beam_schematic(params, results):
    """Generates a Plotly figure visualizing the beam, supports, and loads."""
    fig = go.Figure()
    L = params['length']
    p_load = params['point_load_p']
    w_load = params['dist_load_w']
    support_left = params['support_left']
    support_right = params['support_right']
    reactions = results.get('reactions', {}) # Get calculated reactions

    # Beam Line
    fig.add_trace(go.Scatter(x=[0, L], y=[0, 0], mode='lines', line=dict(color='black', width=5), name='Viga'))

    # --- Supports ---
    support_marker_size = 15
    # Left Support
    if support_left == 'Simple':
        fig.add_trace(go.Scatter(x=[0], y=[0], mode='markers', marker=dict(symbol='triangle-up', size=support_marker_size, color='red'), name='Apoyo Simple (A)'))
    elif support_left == 'Empotrado':
        fig.add_trace(go.Scatter(x=[0, 0], y=[-0.5, 0.5], mode='lines', line=dict(color='red', width=3), name='Apoyo Empotrado (A)'))
        fig.add_trace(go.Scatter(x=[0], y=[0], mode='markers', marker=dict(symbol='square', size=support_marker_size, color='red'), name='')) # Show marker at connection

    # Right Support
    if support_right == 'Simple':
        fig.add_trace(go.Scatter(x=[L], y=[0], mode='markers', marker=dict(symbol='triangle-up', size=support_marker_size, color='blue'), name='Apoyo Simple (B)'))
    elif support_right == 'Empotrado':
        fig.add_trace(go.Scatter(x=[L, L], y=[-0.5, 0.5], mode='lines', line=dict(color='blue', width=3), name='Apoyo Empotrado (B)'))
        fig.add_trace(go.Scatter(x=[L], y=[0], mode='markers', marker=dict(symbol='square', size=support_marker_size, color='blue'), name=''))
    # No marker for 'Libre'

    # --- Loads ---
    load_scale = 0.1 * L # Adjust scale factor for visual clarity
    arrow_scale = 0.05 * L

    # Point Load P
    if p_load['magnitude'] != 0:
        p_mag = p_load['magnitude']
        p_pos = p_load['position']
        fig.add_annotation(
            x=p_pos, y=load_scale, # Position arrow above beam
            ax=p_pos, ay=load_scale * 1.5, # Arrow start point
            text=f"P={p_mag}", showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor="purple",
            font=dict(color="purple")
        )

    # Distributed Load w
    if w_load['magnitude'] != 0:
        w_mag = w_load['magnitude']
        w_start = w_load['start']
        w_end = w_load['end']
        # Draw rectangle for distributed load area
        fig.add_shape(type="rect",
            x0=w_start, y0=load_scale * 0.1, x1=w_end, y1=load_scale * 0.6,
            line=dict(color="Orange"), fillcolor="rgba(255,165,0,0.2)", layer="below"
        )
        # Add arrows to indicate direction
        num_arrows = 5
        for i in np.linspace(w_start, w_end, num_arrows):
             fig.add_annotation(
                x=i, y=load_scale * 0.1, ax=i, ay=load_scale * 0.6,
                showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=1, arrowcolor="orange"
            )
        # Add text label for w
        fig.add_annotation(
            x=(w_start + w_end) / 2, y=load_scale * 0.7, text=f"w={w_mag}", showarrow=False, font=dict(color="orange")
        )

    # --- Reactions (Optional Display) ---
    reaction_scale = load_scale * 1.2
    # R_A
    if 'R_A' in reactions and reactions['R_A'] != 0:
         fig.add_annotation(
            x=0, y=-reaction_scale*0.5, ax=0, ay=0, text=f"R_A={reactions['R_A']:.2f}",
            showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor="green", font=dict(color="green")
         )
    # M_A
    if 'M_A' in reactions and reactions['M_A'] != 0:
         # Represent moment with a curved arrow (approximation with text)
         fig.add_annotation(
             x=0.05*L, y=-reaction_scale*0.2, text=f"↺ M_A={reactions['M_A']:.2f}", showarrow=False, font=dict(color="darkgreen", size=10)
         )
    # R_B
    if 'R_B' in reactions and reactions['R_B'] != 0:
         fig.add_annotation(
            x=L, y=-reaction_scale*0.5, ax=L, ay=0, text=f"R_B={reactions['R_B']:.2f}",
            showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor="green", font=dict(color="green")
         )
     # M_B
    if 'M_B' in reactions and reactions['M_B'] != 0:
         fig.add_annotation(
             x=0.95*L, y=-reaction_scale*0.2, text=f"↺ M_B={reactions['M_B']:.2f}", showarrow=False, font=dict(color="darkgreen", size=10)
         )


    # --- Layout ---
    fig.update_layout(
        title="Diagrama Esquemático de la Viga",
        xaxis=dict(range=[-0.1*L, 1.1*L], showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-load_scale*2, load_scale*2]),
        showlegend=True,
        height=300, # Adjust height as needed
        margin=dict(l=10, r=10, t=40, b=10)
    )
    # Ensure beam is visible
    fig.update_yaxes(range=[-load_scale * 1.5, load_scale * 1.5])


    return fig


# --- Main App Logic ---

# Sidebar for Inputs
st.sidebar.header("⚙️ Configuración de la Viga")
input_method = st.sidebar.radio("Método de Entrada:", ("Lanzar Dados", "Entrada Manual"))

beam_params = {}

if input_method == "Lanzar Dados":
    st.sidebar.subheader("🎲 Lanzamiento de Dados")
    if st.sidebar.button("Lanzar Dados"):
        # Define how many dice for each parameter based on the image
        dice_rolls = {
            'support_left': roll_dice(3), # Example: 3 dice for left support
            'length': roll_dice(2),       # 2 dice for length
            'support_left': roll_dice(3),     # Section 1
            'length': roll_dice(2),           # Section 2 (L)
            'point_load_p_pos': roll_dice(2), # Section 2 (P) - Position
            'point_load_p_mag': roll_dice(3), # Section 3 (P) - Magnitude
            'dist_load_w_mag': roll_dice(3),  # Section 3 (w) - Magnitude
            'dist_load_w_span': roll_dice(2), # Section 3 (w) - Span
            'support_right': roll_dice(3),    # Section 4 - Right Support
            'EI': roll_dice(4)                # Section 5 - EI
        }
        st.session_state.dice_rolls = dice_rolls # Store rolls in session state
        # Interpret results immediately after rolling
        interpreted_params = interpret_dice_results(dice_rolls)
        st.session_state.beam_params = interpreted_params
        st.sidebar.write("Resultados Dados:", dice_rolls) # Display dice results

    # Display stored parameters if they exist and were generated by dice
    if 'beam_params' in st.session_state and 'dice_rolls' in st.session_state:
        beam_params = st.session_state.beam_params # Use the interpreted params
        st.sidebar.write("--- Parámetros Generados ---")
        st.sidebar.json(beam_params) # Display generated params clearly
    elif 'beam_params' not in st.session_state:
         st.sidebar.info("Lanza los dados para generar la configuración.")


elif input_method == "Entrada Manual":
    st.sidebar.subheader("✍️ Entrada Manual")
    # Use defaults that are plausible if no dice have been rolled yet
    defaults = st.session_state.get('beam_params', {
        'length': 10.0, 'support_left': 'Simple', 'support_right': 'Simple',
        'point_load_p': {'magnitude': 5.0, 'position': 5.0},
        'dist_load_w': {'magnitude': 2.0, 'start': 2.0, 'end': 8.0},
        'EI': 20.0
    })

    # Ensure nested dicts exist for defaults
    defaults.setdefault('point_load_p', {'magnitude': 0, 'position': 0})
    defaults.setdefault('dist_load_w', {'magnitude': 0.0, 'start': 0.0, 'end': 0.0}) # Ensure floats here too


    L = st.sidebar.number_input("Longitud (L)", min_value=1.0, value=float(defaults.get('length', 10.0)), step=0.5, key="manual_L")
    support_left = st.sidebar.selectbox("Apoyo Izquierdo", ('Simple', 'Empotrado'), index=('Simple', 'Empotrado').index(defaults.get('support_left', 'Simple')), key="manual_support_left")
    support_right = st.sidebar.selectbox("Apoyo Derecho", ('Libre', 'Simple', 'Empotrado'), index=('Libre', 'Simple', 'Empotrado').index(defaults.get('support_right', 'Simple')), key="manual_support_right")

    st.sidebar.markdown("--- Carga Puntual (P) ---")
    # Ensure value is float if step is float
    p_mag = st.sidebar.number_input("Magnitud P", min_value=0.0, value=float(defaults['point_load_p'].get('magnitude', 5.0)), step=0.5, key="manual_p_mag")
    p_pos = st.sidebar.number_input("Posición P", min_value=0.0, max_value=L, value=float(min(defaults['point_load_p'].get('position', L/2), L)), step=0.1, key="manual_p_pos")

    st.sidebar.markdown("--- Carga Distribuida (w) ---")
    # Ensure value is float if step is float
    w_mag = st.sidebar.number_input("Magnitud w", min_value=0.0, value=float(defaults['dist_load_w'].get('magnitude', 2.0)), step=0.1, key="manual_w_mag")
    w_start = st.sidebar.number_input("Inicio w", min_value=0.0, max_value=L, value=float(min(defaults['dist_load_w'].get('start', L/4), L)), step=0.1, key="manual_w_start")
    w_end = st.sidebar.number_input("Fin w", min_value=w_start, max_value=L, value=float(min(max(w_start, defaults['dist_load_w'].get('end', 3*L/4)), L)), step=0.1, key="manual_w_end")

    st.sidebar.markdown("--- Propiedades ---")
    # Ensure value is float if step is float (step=1.0 is float)
    EI = st.sidebar.number_input("Módulo de Elasticidad (EI)", min_value=1.0, value=float(defaults.get('EI', 20.0)), step=1.0, key="manual_EI")

    # Update beam_params dictionary for manual input
    beam_params = {
        'length': L,
        'support_left': support_left,
        'support_right': support_right,
        'point_load_p': {'magnitude': p_mag, 'position': p_pos},
        'dist_load_w': {'magnitude': w_mag, 'start': w_start, 'end': w_end},
        'EI': EI
    }
    st.session_state.beam_params = beam_params # Store manual params

# --- Calculation and Display Area ---
st.header("🔍 Análisis de la Viga")

if 'beam_params' in st.session_state and st.session_state.beam_params:
    current_params = st.session_state.beam_params
    st.subheader("Parámetros Actuales")
    st.json(current_params) # Display the parameters being used

    # Calculate results
    results = calculate_beam_diagrams(current_params)

    # Display Beam Schematic
    st.subheader("📝 Memoria de Cálculo Interactiva")
    fig_beam = plot_beam_schematic(current_params, results)
    st.plotly_chart(fig_beam, use_container_width=True)


    # Display Calculation Steps in Expander
    st.write("**Pasos del Cálculo:**")
    with st.expander("Ver Pasos Detallados del Cálculo", expanded=True):
        for step in results['calculation_steps']:
            # Check if the step likely contains a LaTeX equation generated by sympy.latex
            # A simple check for common LaTeX patterns like '\', '{', '}'
            if isinstance(step, str) and ('\\' in step or '{' in step or '}' in step or '^' in step or '_' in step) and not step.startswith("**"):
                st.latex(step) # Render as LaTeX
            elif isinstance(step, str) and step.startswith("`"): # Render reaction results in code blocks
                 st.code(step.strip("`"), language='text')
            elif isinstance(step, str): # Render other steps as markdown
                 st.markdown(step, unsafe_allow_html=True)

    # Display Final Equations Clearly (already using st.latex here, which is good)
    st.markdown("**Ecuaciones Finales:**")
    st.latex(f"V(x) = {sympy.latex(results['shear_eq'])}")
    st.latex(f"M(x) = {sympy.latex(results['moment_eq'])}")


    # Display Diagrams
    st.subheader("📈 Diagramas Resultantes")
    col1, col2 = st.columns(2)
    with col1:
        fig_shear = plot_diagram(results['x_values'], results['shear_values'], "Diagrama de Fuerza Cortante (V)", "Cortante (V)")
        st.plotly_chart(fig_shear, use_container_width=True)
    with col2:
        fig_moment = plot_diagram(results['x_values'], results['moment_values'], "Diagrama de Momento Flector (M)", "Momento (M)")
        st.plotly_chart(fig_moment, use_container_width=True)

else:
    st.info("Configure la viga usando el panel lateral para ver los resultados.")
