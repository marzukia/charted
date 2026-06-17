"""Apply a built-in theme and a named palette.

Theme presets control the overall look: light, dark, high-contrast.
Named palettes set the series colors; resolve_palette turns a name into hex colors.
"""

from charted import BarChart, resolve_palette

# Built-in theme preset.
BarChart(
    title="Monthly Active Users",
    data=[1200, 1450, 1380, 1600, 1720],
    labels=["Jan", "Feb", "Mar", "Apr", "May"],
    theme="dark",
    width=700,
    height=400,
).save("mau_dark.svg")
print("wrote mau_dark.svg")

# Colourblind-safe palette via colors=.
BarChart(
    title="Signups by Channel",
    data=[[40, 55, 30], [22, 18, 35]],
    labels=["Organic", "Referral", "Paid"],
    series_names=["Online", "Retail"],
    colors=resolve_palette("okabe-ito"),
    width=700,
    height=400,
).save("signups.svg")
print("wrote signups.svg")
