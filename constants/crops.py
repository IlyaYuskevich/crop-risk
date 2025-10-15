import typing as t

from app_types.types import CropSpecies

CROP_SPECIES: tuple[CropSpecies] = t.get_args(CropSpecies)