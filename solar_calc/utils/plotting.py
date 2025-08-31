import plotly.graph_objs as go
import plotly.io as pio
import numpy as np

# ---------- helper for monthly collapsing (365-day → 12-month) ----------
MONTH_LENGTHS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

def collapse_to_months(daily_results):
    """Aggregate daily results into 12 monthly averages."""
    if len(daily_results) != 365:
        return daily_results  # Already monthly or other format

    month_results = []
    idx = 0
    for month_len in MONTH_LENGTHS:
        slice_ = daily_results[idx: idx + month_len]
        idx += month_len
        month_results.append({
            'month': len(month_results) + 1,
            'Hd': np.mean([d['Hd'] for d in slice_]),
            'Hb': np.mean([d['Hb'] for d in slice_]),
            'It': np.mean([d['It'] for d in slice_]),
        })
    return month_results

def moving_average(values, window_size=15):
    return np.convolve(values, np.ones(window_size)/window_size, mode='same')

# ------------------------------------------------------------------------

def plot_tilted_radiation(results, label=None):
    days = [r['day'] for r in results]
    it_values = [r['It'] for r in results]

    # Sort if format is DD-MM
    if "-" in str(days[0]):
        days, it_values = zip(*sorted(zip(days, it_values), key=lambda x: int(x[0].split("-")[0])))

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(days),
        y=it_values,
        mode='lines+markers',
        name='Tilted Radiation (It)',
        line=dict(color='green', dash='dash'),
        marker=dict(size=8)
    ))

    # Max It annotation
    max_it = max(it_values)
    max_idx = it_values.index(max_it)
    fig.add_trace(go.Scatter(
        x=[days[max_idx]],
        y=[max_it],
        mode='markers+text',
        text=[f"{max_it:.2f}"],
        textposition="top center",
        marker=dict(color='red', size=12, symbol='star'),
        name='Max It'
    ))

    fig.update_layout(
        title=f'📈 Tilted Solar Radiation (It) over Time - {label}' if label else '📈 Tilted Solar Radiation (It) over Time',
        xaxis=dict(title='Day', type='category', tickangle=45),
        yaxis_title='It (MJ/m²/day)',
        template='plotly_white',
        height=400
    )

    return pio.to_html(fig, full_html=False)

def plot_hd_hb_it_bars(results, label=None):
    days = [str(r['day']) for r in results]
    Hd = [r['Hd'] for r in results]
    Hb = [r['Hb'] for r in results]
    It = [r['It'] for r in results]

    if "-" in str(days[0]):
        sorted_data = sorted(zip(days, Hd, Hb, It), key=lambda x: int(x[0].split("-")[0]))
        days, Hd, Hb, It = zip(*sorted_data)

    fig = go.Figure(data=[
        go.Bar(name='Hd (Diffuse)', x=days, y=Hd, marker_color='skyblue'),
        go.Bar(name='Hb (Beam)', x=days, y=Hb, marker_color='orange'),
        go.Bar(name='It (Tilted)', x=days, y=It, marker_color='seagreen')
    ])

    # Annotate max It
    max_it = max(It)
    max_idx = It.index(max_it)
    fig.add_trace(go.Scatter(
        x=[days[max_idx]],
        y=[max_it],
        mode='text',
        text=[f"{max_it:.2f}"],
        textposition="top center",
        showlegend=False
    ))

    fig.update_layout(
        barmode='group',
        title=f'📊 Daily Radiation Components - {label}' if label else '📊 Daily Radiation Components',
        xaxis=dict(title='Day', type='category', tickangle=45),
        yaxis_title='Radiation (MJ/m²/day)',
        template='plotly_white',
        height=450
    )

    return pio.to_html(fig, full_html=False)

def plot_radiation_vs_tilt(tilt_results):
    tilts = [r['tilt'] for r in tilt_results]
    Hd_vals = [r['Hd'] for r in tilt_results]
    Hb_vals = [r['Hb'] for r in tilt_results]
    It_vals = [r['It'] for r in tilt_results]

    max_it = max(It_vals)
    max_idx = It_vals.index(max_it)
    max_tilt = tilts[max_idx]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=tilts, y=Hd_vals,
        mode='lines+markers',
        name='Hd (Diffuse)',
        line=dict(dash='dot', color='blue'),
        marker=dict(size=7)
    ))

    fig.add_trace(go.Scatter(
        x=tilts, y=Hb_vals,
        mode='lines+markers',
        name='Hb (Beam)',
        line=dict(dash='dash', color='orange'),
        marker=dict(size=7)
    ))

    fig.add_trace(go.Scatter(
        x=tilts, y=It_vals,
        mode='lines+markers',
        name='It (Tilted)',
        line=dict(color='green', width=2),
        marker=dict(size=7)
    ))

    fig.add_trace(go.Scatter(
        x=[max_tilt], y=[max_it],
        mode='markers+text',
        name='Max It',
        marker=dict(color='red', size=12, symbol='star'),
        text=[f"{max_it:.2f}"],
        textposition="top center"
    ))

    fig.update_layout(
        title='🌞 Radiation vs Tilt Angle',
        xaxis_title='Tilt (°)',
        yaxis_title='Radiation (MJ/m²/day)',
        template='plotly_white',
        height=420,
        legend=dict(title="Components", orientation="h", y=1.1)
    )

    return pio.to_html(fig, full_html=False)

def plot_optimal_tilt(data, mode='daily'):
    """Plot optimal tilt either for daily tilt analysis or monthly/yearly view."""
    if mode == 'monthly':
        data = collapse_to_months(data) if len(data) == 365 else data

        x_vals = []
        y_vals = []
        highlight_x = None
        highlight_y = None

        for entry in data:
            if isinstance(entry.get('month'), int):
                month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                               'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                x_label = month_names[entry['month'] - 1]
            else:
                x_label = 'Year'
                highlight_x = x_label
                highlight_y = entry.get('optimal_tilt')

            x_vals.append(x_label)
            y_vals.append(entry.get('optimal_tilt', entry.get('It', 0)))

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=x_vals, y=y_vals, mode='lines+markers',
            name='Optimal Tilt',
            marker=dict(color='royalblue', size=8),
            line=dict(width=2)
        ))

        if highlight_x and highlight_y is not None:
            fig.add_trace(go.Scatter(
                x=[highlight_x],
                y=[highlight_y],
                mode='markers+text',
                name='Max Yearly',
                marker=dict(color='red', size=12, symbol='star'),
                text=[f"Year Max: {highlight_y:.1f}°"],
                textposition="top center"
            ))

        fig.update_layout(
            title='📅 Optimal Tilt Angle (Monthly + Yearly)',
            xaxis_title='Month',
            yaxis_title='Tilt Angle (°)',
            template='plotly_white',
            height=420
        )

    else:
        x_vals = [d['tilt'] for d in data]
        y_vals = [d['It'] for d in data]

        max_idx = y_vals.index(max(y_vals))
        max_tilt = x_vals[max_idx]
        max_it = y_vals[max_idx]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=x_vals, y=y_vals,
            mode='lines+markers',
            name='It vs Tilt',
            line=dict(color='green')
        ))

        fig.add_trace(go.Scatter(
            x=[max_tilt], y=[max_it],
            mode='markers+text',
            name='Max It',
            marker=dict(color='red', size=12, symbol='star'),
            text=[f"{max_it:.2f}"],
            textposition="top center"
        ))

        fig.update_layout(
            title='Optimal Tilt vs Radiation',
            xaxis_title='Tilt (°)',
            yaxis_title='It (MJ/m²)',
            template='plotly_white',
            height=420
        )

    return pio.to_html(fig, full_html=False)
