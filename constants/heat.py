from app_types.types import CropToStages, PlotThresholdsConfig

STAGE_MARKERS: CropToStages = {
    "Wheat": [
        {
            "label": "Seeding",
            "start_month": 9,
            "start_day": 1,
            "thresholds": {"warn_temp": 28, "alert_temp": 32, "low_temp": 6},
            "color": "#6c757d",
        },
        {
            "label": "Dormancy",
            "start_month": 12,
            "start_day": 1,
            "thresholds": {"warn_temp": 12, "alert_temp": 15, "low_temp": 0},
            "color": "#6c757d",
        },
        {
            "label": "Growth",
            "start_month": 2,
            "start_day": 1,
            "thresholds": {"warn_temp": 30, "alert_temp": 34, "low_temp": 8},
            "color": "#6c757d",
        },
        {
            "label": "Flowering",
            "start_month": 4,
            "start_day": 1,
            "thresholds": {"warn_temp": 28, "alert_temp": 30, "low_temp": 12},
            "color": "#6c757d",
        },
        {
            "label": "Grain filling",
            "start_month": 5,
            "start_day": 1,
            "thresholds": {"warn_temp": 30, "alert_temp": 35, "low_temp": 14},
            "color": "#6c757d",
        },
        {
            "label": "Harvest",
            "start_month": 7,
            "start_day": 1,
            "thresholds": {"warn_temp": 32, "alert_temp": 36, "low_temp": 12},
            "color": "#6c757d",
        },
    ],
    "Bilberry": [
        {
            "label": "Winter Dormancy",
            "start_month": 11,
            "start_day": 1,
            "thresholds": {"warn_temp": 5, "alert_temp": 10, "low_temp": 0},
            "color": "#6c757d",
        },
        {
            "label": "Bud Swell",
            "start_month": 4,
            "start_day": 1,
            "thresholds": {"warn_temp": 20, "alert_temp": 25, "low_temp": 8},
            "color": "#6c757d",
        },
        {
            "label": "Leaf Emergence",
            "start_month": 5,
            "start_day": 1,
            "thresholds": {"warn_temp": 24, "alert_temp": 28, "low_temp": 10},
            "color": "#6c757d",
        },
        {
            "label": "Flowering & Bloom",
            "start_month": 5,
            "start_day": 15,
            "thresholds": {"warn_temp": 28, "alert_temp": 32, "low_temp": 15},
            "color": "#6c757d",
        },
        {
            "label": "Fruit set & Growth",
            "start_month": 6,
            "start_day": 15,
            "thresholds": {"warn_temp": 27, "alert_temp": 31, "low_temp": 18},
            "color": "#6c757d",
        },
        {
            "label": "Harvest",
            "start_month": 8,
            "start_day": 15,
            "thresholds": {"warn_temp": 27, "alert_temp": 31, "low_temp": 15},
            "color": "#6c757d",
        },
        {
            "label": "Post-Harvest Hardening",
            "start_month": 9,
            "start_day": 15,
            "thresholds": {"warn_temp": 20, "alert_temp": 25, "low_temp": 8},
            "color": "#6c757d",
        },
    ],
}

# Band configuration (hashmap). Order matters for correct tonexty fills.
BANDS: PlotThresholdsConfig = {
    "low_temp": {"lo": -10, "hi": "low_temp", "fill": "rgba(0, 0, 0, 0)", "line": None},
    "suitable": {
        "lo": "low_temp",
        "hi": "warn_temp",
        "fill": "rgba(109, 215, 193, 0.25)",
        "line": "rgba(255, 193, 7, 0.9)",
    },
    "warn_temp": {
        "lo": "warn_temp",
        "hi": "alert_temp",
        "fill": "rgba(255, 193, 7, 0.20)",
        "line": "rgba(220, 53, 69, 0.9)",
    },
    "alert_temp": {
        "lo": "alert_temp",
        "hi": 40,
        "fill": "rgba(220, 53, 69, 0.20)",
        "line": None,
    },
}
