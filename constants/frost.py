from app_types.types import CropToStages, PlotThresholdsConfig

STAGE_MARKERS: CropToStages = {
    "Wheat": [
        {
            "label": "Seeding",
            "start_month": 9,
            "start_day": 1,
            "thresholds": {"warn_temp": -2, "alert_temp": -8, "high_temp": 30},
            "color": "#6c757d",
        },
        {
            "label": "Dormancy",
            "start_month": 12,
            "start_day": 1,
            "thresholds": {"warn_temp": -2, "alert_temp": -8, "high_temp": 30},
            "color": "#6c757d",
        },
        {
            "label": "Growth",
            "start_month": 2,
            "start_day": 1,
            "thresholds": {"warn_temp": -2, "alert_temp": -8, "high_temp": 30},
            "color": "#6c757d",
        },
        {
            "label": "Flowering",
            "start_month": 4,
            "start_day": 1,
            "thresholds": {"warn_temp": -2, "alert_temp": -8, "high_temp": 30},
            "color": "#6c757d",
        },
        {
            "label": "Grain filling",
            "start_month": 5,
            "start_day": 1,
            "thresholds": {"warn_temp": -2, "alert_temp": -8, "high_temp": 30},
            "color": "#6c757d",
        },
        {
            "label": "Harvest",
            "start_month": 7,
            "start_day": 1,
            "thresholds": {"warn_temp": -2, "alert_temp": -8, "high_temp": 30},
            "color": "#6c757d",
        },
    ],
    "Bilberry": [
        {
            "label": "Dormancy",
            "start_month": 11,
            "start_day": 1,
            "thresholds": {"warn_temp": -2, "alert_temp": -8, "high_temp": 30},
            "color": "#6c757d",
        },
        {
            "label": "Bud Swelling \n& Leaf Emergence",
            "start_month": 3,
            "start_day": 1,
            "thresholds": {"warn_temp": -2, "alert_temp": -8, "high_temp": 30},
            "color": "#6c757d",
        },
        {
            "label": "Flowering",
            "start_month": 4,
            "start_day": 1,
            "thresholds": {"warn_temp": -2, "alert_temp": -8, "high_temp": 30},
            "color": "#6c757d",
        },
        {
            "label": "Fruit set",
            "start_month": 5,
            "start_day": 1,
            "thresholds": {"warn_temp": -2, "alert_temp": -8, "high_temp": 30},
            "color": "#6c757d",
        },
        {
            "label": "Berry growth & Ripening",
            "start_month": 6,
            "start_day": 1,
            "thresholds": {"warn_temp": -2, "alert_temp": -8, "high_temp": 30},
            "color": "#6c757d",
        },
        {
            "label": "Harvest",
            "start_month": 7,
            "start_day": 15,
            "thresholds": {"warn_temp": -2, "alert_temp": -8, "high_temp": 30},
            "color": "#6c757d",
        },
        {
            "label": "Leaf Senescence",
            "start_month": 9,
            "start_day": 1,
            "thresholds": {"warn_temp": -2, "alert_temp": -8, "high_temp": 30},
            "color": "#6c757d",
        },
    ],
}

# Band configuration (hashmap). Order matters for correct tonexty fills.
BANDS: PlotThresholdsConfig = {
    "alert_temp": {
        "lo": -10,
        "hi": "alert_temp",
        "fill": "rgba(220, 53, 69, 0.20)",
        "line": None,
    },
    "warn_temp": {
        "lo": "alert_temp",
        "hi": "warn_temp",
        "fill": "rgba(255, 193, 7, 0.20)",
        "line": "rgba(220, 53, 69, 0.9)",
    },
    "suitable": {
        "lo": "warn_temp",
        "hi": "high_temp",
        "fill": "rgba(109, 215, 193, 0.25)",
        "line": "rgba(255, 193, 7, 0.9)",
    },
    "high_temp": {"lo": "high_temp", "hi": 40, "fill": "rgba(0, 0, 0, 0)", "line": None},
}
