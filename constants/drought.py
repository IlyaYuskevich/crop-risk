from app_types.types import CropToStages, PlotThresholdsConfig

STAGE_MARKERS: CropToStages = {
    "Wheat": [
        {
            "label": "Seeding",
            "start_month": 9,
            "start_day": 1,
            "thresholds": {
                "dry_warn": -0.4,
                "dry_critical": -0.8,
                "wet_warn": 0.6,
                "wet_critical": 1,
            },
            "color": "#6c757d",
        },
        {
            "label": "Dormancy",
            "start_month": 12,
            "start_day": 1,
            "thresholds": {
                "dry_warn": -0.8,
                "dry_critical": -1.2,
                "wet_warn": 1.0,
                "wet_critical": 1.6,
            },
            "color": "#6c757d",
        },
        {
            "label": "Growth",
            "start_month": 2,
            "start_day": 1,
            "thresholds": {
                "dry_warn": -0.5,
                "dry_critical": -1.0,
                "wet_warn": 0.8,
                "wet_critical": 1.4,
            },
            "color": "#6c757d",
        },
        {
            "label": "Flowering",
            "start_month": 4,
            "start_day": 1,
            "thresholds": {
                "dry_warn": -0.3,
                "dry_critical": -0.6,
                "wet_warn": 0.8,
                "wet_critical": 1.4,
            },
            "color": "#6c757d",
        },
        {
            "label": "Grain filling",
            "start_month": 5,
            "start_day": 1,
            "thresholds": {
                "dry_warn": -0.5,
                "dry_critical": -1.0,
                "wet_warn": 0.8,
                "wet_critical": 1.4,
            },
            "color": "#6c757d",
        },
        {
            "label": "Harvest",
            "start_month": 7,
            "start_day": 1,
            "thresholds": {
                "dry_warn": -1.0,
                "dry_critical": -1.5,
                "wet_warn": 0.6,
                "wet_critical": 1.0,
            },
            "color": "#6c757d",
        },
    ],
    "Bilberry": [
        {
            "label": "Winter Dormancy",
            "start_month": 11,
            "start_day": 1,
            "thresholds": {
                "dry_warn": -0.8,
                "dry_critical": -1.2,
                "wet_warn": 1.0,
                "wet_critical": 1.6,
            },
            "color": "#6c757d",
        },
        {
            "label": "Bud Swell",
            "start_month": 4,
            "start_day": 1,
            "thresholds": {
                "dry_warn": -0.3,
                "dry_critical": -1.0,
                "wet_warn": 0.6,
                "wet_critical": 1.0,
            },
            "color": "#6c757d",
        },
        {
            "label": "Leaf Emergence",
            "start_month": 5,
            "start_day": 1,
            "thresholds": {
                "dry_warn": -0.2,
                "dry_critical": -0.8,
                "wet_warn": 0.6,
                "wet_critical": 1.0,
            },
            "color": "#6c757d",
        },
        {
            "label": "Flowering & Bloom",
            "start_month": 5,
            "start_day": 15,
            "thresholds": {
                "dry_warn": -0.2,
                "dry_critical": -0.8,
                "wet_warn": 0.6,
                "wet_critical": 1.0,
            },
            "color": "#6c757d",
        },
        {
            "label": "Fruit set & Growth",
            "start_month": 6,
            "start_day": 15,
            "thresholds": {
                "dry_warn": -0.3,
                "dry_critical": -0.9,
                "wet_warn": 0.6,
                "wet_critical": 1.0,
            },
            "color": "#6c757d",
        },
        {
            "label": "Harvest",
            "start_month": 8,
            "start_day": 15,
            "thresholds": {
                "dry_warn": -0.3,
                "dry_critical": -0.8,
                "wet_warn": 0.6,
                "wet_critical": 1.0,
            },
            "color": "#6c757d",
        },
        {
            "label": "Leaf Senescence",
            "start_month": 9,
            "start_day": 1,
            "thresholds": {
                "dry_warn": -0.5,
                "dry_critical": -1.2,
                "wet_warn": 0.6,
                "wet_critical": 1.0,
            },
            "color": "#6c757d",
        },
    ],
}

# Band configuration (hashmap). Order matters for correct tonexty fills.
BANDS: PlotThresholdsConfig = {
    "dry_critical": {
        "lo": -5,
        "hi": "dry_critical",
        "fill": "rgba(220, 53, 69, 0.25)",
        "line": "rgba(220, 53, 69, 0.9)",
    },
    "dry_warn": {
        "lo": "dry_critical",
        "hi": "dry_warn",
        "fill": "rgba(255, 193, 7, 0.20)",
        "line": "rgba(255, 193, 7, 0.9)",
    },
    "suitable": {
        "lo": "dry_warn",
        "hi": "wet_warn",
        "fill": "rgba(109, 215, 193, 0.25)",
        "line": "rgba(255, 193, 7, 0.9)",
    },
    "wet_warn": {
        "lo": "wet_warn",
        "hi": "wet_critical",
        "fill": "rgba(255, 193, 7, 0.20)",
        "line": "rgba(220, 53, 69, 0.9)",
    },
    "wet_critical": {
        "lo": "wet_critical",
        "hi": 5,
        "fill": "rgba(220, 53, 69, 0.20)",
        "line": None,
    },
}
