import io
import json
from datetime import datetime, timezone

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from odyssey.plotting import _plot_to_png_bytes

CONFIG_VERSION = 1


def _build_config(
    sheet_name,
    time_col,
    time_unit,
    time_window,
    fit_window_mode,
    min_points,
    blank_normalized,
    blank_col,
    auc_mode,
    auc_window,
    auc_unit,
    notes,
    column_map,
    growth_rate_unit,
    doubling_time_unit,
    plot_groups,
    plot_mode,
    show_sd,
    charts_per_row,
    plot_labels,
):
    return {
        "version": CONFIG_VERSION,
        "sheet_name": sheet_name,
        "time_col": time_col,
        "time_unit": time_unit,
        "time_window": time_window,
        "fit_window_mode": fit_window_mode,
        "min_points": min_points,
        "blank_normalized": blank_normalized,
        "blank_col": blank_col,
        "auc_mode": auc_mode,
        "auc_window": auc_window,
        "auc_unit": auc_unit,
        "notes": notes,
        "column_map": column_map,
        "growth_rate_unit": growth_rate_unit,
        "doubling_time_unit": doubling_time_unit,
        "plot_groups": plot_groups,
        "plot_mode": plot_mode,
        "show_sd": show_sd,
        "charts_per_row": charts_per_row,
        "plot_labels": plot_labels,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


def _build_report_pdf(title, results_df, fig, notes):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(title or "ODyssey Growth Curve Report", styles["Title"]))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["Normal"]))
    if notes:
        story.append(Paragraph(f"Notes: {notes}", styles["Normal"]))
    story.append(Spacer(1, 12))

    if fig is not None:
        png = _plot_to_png_bytes(fig)
        img = Image(io.BytesIO(png), width=520, height=260)
        story.append(img)
        story.append(Spacer(1, 12))

    story.append(Paragraph("Results (first 30 rows)", styles["Heading3"]))
    cols = results_df.columns.tolist()
    header_row = [Paragraph(str(col), styles["Normal"]) for col in cols]
    table_rows = [header_row]
    for _, row in results_df.head(30).iterrows():
        row_vals = []
        for col in cols:
            val = str(row[col])
            row_vals.append(Paragraph(val, styles["Normal"]))
        table_rows.append(row_vals)

    col_width = (letter[0] - 72) / max(len(cols), 1)
    table = Table(table_rows, colWidths=[col_width] * len(cols), repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    story.append(table)

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
