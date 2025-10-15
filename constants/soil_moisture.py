from app_types.types import CropToStages, PlotThresholdsConfig

STAGE_MARKERS: CropToStages = {
    "Wheat": [
        {
            "label": "Seeding",
            "start_month": 9,
            "start_day": 1,
            "thresholds": {
                "dry_warn": 0.2,
                "dry_critical": 0.1,
                "wet_warn": 0.8,
                "wet_critical": 0.9,
            },
            "color": "#6c757d",
        },
        {
            "label": "Dormancy",
            "start_month": 12,
            "start_day": 1,
            "thresholds": {
                "dry_warn": 0.2,
                "dry_critical": 0.1,
                "wet_warn": 0.8,
                "wet_critical": 0.9,
            },
            "color": "#6c757d",
        },
        {
            "label": "Growth",
            "start_month": 2,
            "start_day": 1,
            "thresholds": {
                "dry_warn": 0.2,
                "dry_critical": 0.1,
                "wet_warn": 0.8,
                "wet_critical": 0.9,
            },
            "color": "#6c757d",
        },
        {
            "label": "Flowering",
            "start_month": 4,
            "start_day": 1,
            "thresholds": {
                "dry_warn": 0.2,
                "dry_critical": 0.1,
                "wet_warn": 0.8,
                "wet_critical": 0.9,
            },
            "color": "#6c757d",
        },
        {
            "label": "Grain filling",
            "start_month": 5,
            "start_day": 1,
            "thresholds": {
                "dry_warn": 0.2,
                "dry_critical": 0.1,
                "wet_warn": 0.8,
                "wet_critical": 0.9,
            },
            "color": "#6c757d",
        },
        {
            "label": "Harvest",
            "start_month": 7,
            "start_day": 1,
            "thresholds": {
                "dry_warn": 0.2,
                "dry_critical": 0.1,
                "wet_warn": 0.8,
                "wet_critical": 0.9,
            },
            "color": "#6c757d",
        },
    ],
    "Bilberry": [
        {
            "label": "Dormancy",
            "start_month": 11,
            "start_day": 1,
            "thresholds": {
                "dry_warn": 0.2,
                "dry_critical": 0.1,
                "wet_warn": 0.8,
                "wet_critical": 0.9,
            },
            "color": "#6c757d",
        },
        {
            "label": "Bud Swelling \n& Leaf Emergence",
            "start_month": 3,
            "start_day": 1,
            "thresholds": {
                "dry_warn": 0.2,
                "dry_critical": 0.1,
                "wet_warn": 0.8,
                "wet_critical": 0.9,
            },
            "color": "#6c757d",
        },
        {
            "label": "Flowering",
            "start_month": 4,
            "start_day": 1,
            "thresholds": {
                "dry_warn": 0.2,
                "dry_critical": 0.1,
                "wet_warn": 0.8,
                "wet_critical": 0.9,
            },
            "color": "#6c757d",
        },
        {
            "label": "Fruit set",
            "start_month": 5,
            "start_day": 1,
            "thresholds": {
                "dry_warn": 0.2,
                "dry_critical": 0.1,
                "wet_warn": 0.8,
                "wet_critical": 0.9,
            },
            "color": "#6c757d",
        },
        {
            "label": "Berry growth & Ripening",
            "start_month": 6,
            "start_day": 1,
            "thresholds": {
                "dry_warn": 0.2,
                "dry_critical": 0.1,
                "wet_warn": 0.8,
                "wet_critical": 0.9,
            },
            "color": "#6c757d",
        },
        {
            "label": "Harvest",
            "start_month": 7,
            "start_day": 15,
            "thresholds": {
                "dry_warn": 0.2,
                "dry_critical": 0.1,
                "wet_warn": 0.8,
                "wet_critical": 0.9,
            },
            "color": "#6c757d",
        },
        {
            "label": "Leaf Senescence",
            "start_month": 9,
            "start_day": 1,
            "thresholds": {
                "dry_warn": 0.2,
                "dry_critical": 0.1,
                "wet_warn": 0.8,
                "wet_critical": 0.9,
            },
            "color": "#6c757d",
        },
    ],
}

# Band configuration (hashmap). Order matters for correct tonexty fills.
BANDS: PlotThresholdsConfig = {
    "dry_critical": {
        "lo": 0,
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
        "hi": 1,
        "fill": "rgba(220, 53, 69, 0.20)",
        "line": None,
    },
}
