import plotly.colors as pc
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots


def _to_rgba(color, alpha):
    if isinstance(color, str) and color.startswith("#"):
        rgb = pc.hex_to_rgb(color)
        return f"rgba({rgb[0]},{rgb[1]},{rgb[2]},{alpha})"
    if isinstance(color, str) and color.startswith("rgb("):
        rgb = color.replace("rgb(", "").replace(")", "")
        return f"rgba({rgb},{alpha})"
    return f"rgba(0,0,0,{alpha})"


def _plot_overlay(mean_df, treatments, show_sd=True):
    fig = go.Figure()
    color_cycle = pc.qualitative.Plotly
    for idx, treatment in enumerate(treatments):
        subset = mean_df[mean_df["treatment"] == treatment]
        line_color = color_cycle[idx % len(color_cycle)]
        fill_color = _to_rgba(line_color, 0.12)
        if show_sd and not subset["sd"].isna().all():
            upper = subset["mean"] + subset["sd"]
            lower = subset["mean"] - subset["sd"]
            fig.add_trace(
                go.Scatter(
                    x=subset["time"],
                    y=lower,
                    mode="lines",
                    line=dict(width=0),
                    showlegend=False,
                    hoverinfo="skip",
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=subset["time"],
                    y=upper,
                    mode="lines",
                    line=dict(width=0),
                    fill="tonexty",
                    fillcolor=fill_color,
                    showlegend=False,
                    hoverinfo="skip",
                )
            )
        fig.add_trace(
            go.Scatter(
                x=subset["time"],
                y=subset["mean"],
                mode="lines",
                name=str(treatment),
                line=dict(color=line_color),
                hovertemplate=f"Time=%{{x}}<br>OD=%{{y}}<extra>{treatment}</extra>",
            )
        )
    fig.update_layout(
        title="Growth curves (mean across replicates)",
        xaxis_title="Time",
        yaxis_title="OD",
        hovermode="x unified",
    )
    return fig


def _add_window_highlight(fig, time_window):
    if not time_window:
        return fig
    t_min, t_max = time_window
    fig.add_vrect(
        x0=t_min,
        x1=t_max,
        fillcolor="rgba(255,193,7,0.25)",
        line_width=1,
        line_color="rgba(255,193,7,0.6)",
        layer="below",
    )
    return fig


def _add_window_highlight_color(fig, time_window, color):
    if not time_window:
        return fig
    t_min, t_max = time_window
    fig.add_shape(
        type="rect",
        x0=t_min,
        x1=t_max,
        y0=0,
        y1=1,
        yref="paper",
        fillcolor=color,
        line=dict(width=0),
        layer="below",
    )
    return fig


def _plot_small_multiples(mean_df, treatments, cols_per_row=2, show_sd=True, x_label="Time", y_label="OD"):
    rows = int((len(treatments) + cols_per_row - 1) / cols_per_row)
    fig = make_subplots(rows=rows, cols=cols_per_row, subplot_titles=[str(t) for t in treatments])
    color_cycle = pc.qualitative.Plotly
    for idx, treatment in enumerate(treatments):
        r = idx // cols_per_row + 1
        c = idx % cols_per_row + 1
        subset = mean_df[mean_df["treatment"] == treatment]
        line_color = color_cycle[idx % len(color_cycle)]
        fill_color = _to_rgba(line_color, 0.12)
        if show_sd and not subset["sd"].isna().all():
            upper = subset["mean"] + subset["sd"]
            lower = subset["mean"] - subset["sd"]
            fig.add_trace(
                go.Scatter(
                    x=subset["time"],
                    y=lower,
                    mode="lines",
                    line=dict(width=0),
                    showlegend=False,
                    hoverinfo="skip",
                ),
                row=r,
                col=c,
            )
            fig.add_trace(
                go.Scatter(
                    x=subset["time"],
                    y=upper,
                    mode="lines",
                    line=dict(width=0),
                    fill="tonexty",
                    fillcolor=fill_color,
                    showlegend=False,
                    hoverinfo="skip",
                ),
                row=r,
                col=c,
            )
        fig.add_trace(
            go.Scatter(
                x=subset["time"],
                y=subset["mean"],
                mode="lines",
                name=str(treatment),
                line=dict(color=line_color),
                hovertemplate=f"Time=%{{x}}<br>OD=%{{y}}<extra>{treatment}</extra>",
                showlegend=False,
            ),
            row=r,
            col=c,
        )
        fig.update_xaxes(title_text=x_label, showgrid=False, row=r, col=c)
        fig.update_yaxes(title_text=y_label, showgrid=False, row=r, col=c)
    fig.update_layout(height=300 * rows, hovermode="x unified")
    return fig


def _plot_compare_runs(analyses, treatment, show_sd=True):
    fig = go.Figure()
    color_cycle = pc.qualitative.Plotly
    for idx, analysis in enumerate(analyses):
        mean_df = analysis["mean_df"]
        subset = mean_df[mean_df["treatment"] == treatment]
        if subset.empty:
            continue
        line_color = color_cycle[idx % len(color_cycle)]
        fill_color = _to_rgba(line_color, 0.12)
        if show_sd and not subset["sd"].isna().all():
            upper = subset["mean"] + subset["sd"]
            lower = subset["mean"] - subset["sd"]
            fig.add_trace(
                go.Scatter(
                    x=subset["time"],
                    y=lower,
                    mode="lines",
                    line=dict(width=0),
                    showlegend=False,
                    hoverinfo="skip",
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=subset["time"],
                    y=upper,
                    mode="lines",
                    line=dict(width=0),
                    fill="tonexty",
                    fillcolor=fill_color,
                    showlegend=False,
                    hoverinfo="skip",
                )
            )
        fig.add_trace(
            go.Scatter(
                x=subset["time"],
                y=subset["mean"],
                mode="lines",
                name=analysis["name"],
                line=dict(color=line_color),
                hovertemplate=f"Time=%{{x}}<br>OD=%{{y}}<extra>{analysis['name']}</extra>",
            )
        )
    return fig


def _style_plot(fig, title, x_label, y_label, show_grid=False):
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(color="black"),
        legend=dict(bgcolor="rgba(255,255,255,0.8)", font=dict(color="black")),
        title=dict(text=title, font=dict(color="black", size=18)),
        xaxis_title=x_label,
        yaxis_title=y_label,
    )
    fig.update_xaxes(
        showgrid=show_grid,
        zeroline=False,
        showline=True,
        linecolor="black",
        tickfont=dict(color="black"),
        title_font=dict(color="black"),
    )
    fig.update_yaxes(
        showgrid=show_grid,
        zeroline=False,
        showline=True,
        linecolor="black",
        tickfont=dict(color="black"),
        title_font=dict(color="black"),
    )
    return fig


def _apply_tick_intervals(fig, x_interval=None, y_interval=None):
    if x_interval:
        fig.update_xaxes(dtick=x_interval)
    if y_interval:
        fig.update_yaxes(dtick=y_interval)
    return fig


def _prepare_download_figure(fig):
    fig_download = go.Figure(fig)
    title = fig_download.layout.title.text if fig_download.layout.title else ""
    x_label = fig_download.layout.xaxis.title.text if fig_download.layout.xaxis.title else ""
    y_label = fig_download.layout.yaxis.title.text if fig_download.layout.yaxis.title else ""
    _style_plot(fig_download, title, x_label, y_label, show_grid=False)
    return fig_download


def _plot_to_png_bytes(fig, width=900, height=520, scale=1.5, timeout=30):
    try:
        scope = pio.kaleido.scope
        scope.default_format = "png"
        scope.default_width = width
        scope.default_height = height
        scope.default_scale = scale
        scope.timeout = timeout
    except Exception:
        pass
    image_bytes = pio.to_image(
        fig,
        format="png",
        width=width,
        height=height,
        scale=scale,
        engine="kaleido",
    )
    return image_bytes
