import plotly.graph_objects as go
import numpy as np

def plot_diagram(x, y, title, y_label):
    """Generates a Plotly figure for shear or moment."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name=y_label, fill='tozeroy'))
    fig.update_layout(
        title=title,
        xaxis_title="Posición (x)",
        yaxis_title=y_label,
        hovermode="x unified"
    )
    # Add horizontal line at y=0 for reference
    fig.add_hline(y=0, line_width=1, line_dash="dash", line_color="grey")
    return fig

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
        fig.add_trace(go.Scatter(x=[0], y=[0], mode='markers', marker=dict(symbol='square', size=support_marker_size, color='red'), showlegend=False)) # Show marker at connection

    # Right Support
    if support_right == 'Simple':
        fig.add_trace(go.Scatter(x=[L], y=[0], mode='markers', marker=dict(symbol='triangle-up', size=support_marker_size, color='blue'), name='Apoyo Simple (B)'))
    elif support_right == 'Empotrado':
        fig.add_trace(go.Scatter(x=[L, L], y=[-0.5, 0.5], mode='lines', line=dict(color='blue', width=3), name='Apoyo Empotrado (B)'))
        fig.add_trace(go.Scatter(x=[L], y=[0], mode='markers', marker=dict(symbol='square', size=support_marker_size, color='blue'), showlegend=False))
    # No marker for 'Libre'

    # --- Loads ---
    # Adjust scale factors dynamically based on beam length L and potentially load magnitudes
    # Find max absolute reaction or load magnitude for scaling, avoid division by zero
    max_force_mag = max(abs(p_load['magnitude']), abs(w_load['magnitude'])*L, # Estimate total distributed load force
                        abs(reactions.get('R_A', 0)), abs(reactions.get('R_B', 0)), 1.0) # Add 1.0 to prevent zero scale
    max_moment_mag = max(abs(reactions.get('M_A', 0)), abs(reactions.get('M_B', 0)), 1.0)

    # Base scale on length, but adjust slightly by force/moment magnitude?
    # Let's keep it simpler for now, primarily based on L.
    load_y_offset = 0.15 * L # Vertical offset for loads above the beam
    reaction_y_offset = -0.15 * L # Vertical offset for reactions below the beam
    moment_y_offset = -0.25 * L # Offset for moment text

    # Point Load P
    if p_load['magnitude'] != 0:
        p_mag = p_load['magnitude']
        p_pos = p_load['position']
        p_dir = np.sign(p_mag) # +1 for positive (down), -1 for negative (up)
        arrow_y_tip = 0 + p_dir * 0.02 * L # Tip slightly offset from beam
        arrow_y_base = load_y_offset * p_dir # Base further away
        text_y = load_y_offset * 1.1 * p_dir # Text slightly beyond base

        # Draw the arrow for point load P
        fig.add_annotation(
            x=p_pos, y=arrow_y_tip,  # End point of the arrow near the beam
            ax=p_pos, ay=arrow_y_base, # Start point of the arrow away from the beam
            showarrow=True, arrowhead=3, arrowsize=2, arrowwidth=2, arrowcolor="purple",
            # No text in this annotation, just the arrow
        )
        # Add text separately for better control
        fig.add_annotation(
            x=p_pos, y=text_y,
            text=f"P={p_mag:.2f}", showarrow=False,
            font=dict(color="purple", size=10), align="center", yshift=5*p_dir # Shift text slightly away from arrow
        )


    # Distributed Load w
    if w_load['magnitude'] != 0:
        w_mag = w_load['magnitude']
        w_start = w_load['start']
        w_end = w_load['end']
        w_dir = np.sign(w_mag) # +1 for positive (down), -1 for negative (up)
        rect_y0 = 0
        rect_y1 = load_y_offset * 0.4 * w_dir # Rectangle extends up or down
        arrow_y_base = rect_y1 # Arrows start/end at rectangle edge
        arrow_y_tip = 0 + w_dir * 0.01 * L # Arrows point towards beam

        # Draw rectangle for distributed load area
        fig.add_shape(type="rect",
            x0=w_start, y0=rect_y0, x1=w_end, y1=rect_y1,
            line=dict(color="Orange"), fillcolor="rgba(255,165,0,0.2)", layer="below"
        )
        # Add arrows to indicate direction
        num_arrows = max(3, int((w_end - w_start) / (L / 10))) # More arrows for longer spans
        for i in np.linspace(w_start, w_end, num_arrows):
             # Draw small arrows for distributed load w
             fig.add_annotation(
                x=i, y=arrow_y_tip, # End point near beam
                ax=i, ay=arrow_y_base, # Start point at rectangle edge
                showarrow=True, arrowhead=3, arrowsize=1.5, arrowwidth=1, arrowcolor="orange"
                # No text in these annotations
            )
        # Add text label for w
        text_y_w = load_y_offset * 0.5 * w_dir # Place text outside rectangle
        fig.add_annotation(
            x=(w_start + w_end) / 2, y=text_y_w,
            text=f"w={w_mag:.2f}", showarrow=False, font=dict(color="orange", size=10),
            yshift=5*w_dir # Shift text slightly away
        )

    # --- Reactions ---
    # R_A
    if 'R_A' in reactions and abs(reactions['R_A']) > 1e-6: # Check for non-zero
         fig.add_annotation(
            x=0, y=reaction_y_offset * 0.5, ax=0, ay=0, # Arrow pointing up from support
            text=f"R_A={reactions['R_A']:.2f}",
            showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor="green", font=dict(color="green", size=10)
         )
    # M_A
    if 'M_A' in reactions and abs(reactions['M_A']) > 1e-6:
         fig.add_annotation(
             x=0.05*L, y=moment_y_offset, text=f"↺ M_A={reactions['M_A']:.2f}", showarrow=False, font=dict(color="darkgreen", size=10)
         )
    # R_B
    if 'R_B' in reactions and abs(reactions['R_B']) > 1e-6:
         fig.add_annotation(
            x=L, y=reaction_y_offset * 0.5, ax=L, ay=0, # Arrow pointing up from support
            text=f"R_B={reactions['R_B']:.2f}",
            showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor="green", font=dict(color="green", size=10)
         )
     # M_B
    if 'M_B' in reactions and abs(reactions['M_B']) > 1e-6:
         fig.add_annotation(
             x=0.95*L, y=moment_y_offset, text=f"↺ M_B={reactions['M_B']:.2f}", showarrow=False, font=dict(color="darkgreen", size=10)
         )


    # --- Layout ---
    # Determine appropriate y-range based on offsets
    max_y = load_y_offset * 1.2
    min_y = min(reaction_y_offset, moment_y_offset) * 1.2
    fig.update_layout(
        title="Diagrama Esquemático de la Viga",
        xaxis=dict(range=[-0.1*L, 1.1*L], showgrid=False, zeroline=False, showticklabels=False, scaleanchor="y", scaleratio=1), # Maintain aspect ratio
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[min_y, max_y]),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), # Legend top horizontal
        height=max(300, L * 50), # Adjust height based on length?
        margin=dict(l=10, r=10, t=50, b=10) # Increased top margin for title
    )

    return fig
