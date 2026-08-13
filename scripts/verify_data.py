#!/usr/bin/env python3
"""Validate that the downloaded repository inputs have the columns used by the notebook."""

from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data' / 'raw'
MAP = ROOT / 'data' / 'map'

MASTER_REQUIRED = {
    'well_no', 'date', 'gw_level_m_asl',
    'precipitation_mm_eobs', 'temperature_C_eobs',
    'actual_evapotranspiration_mm_gleam', 'potential_evapotranspiration_mm_gleam',
    'gws_mm_tavg_gldas',
}
SINKHOLE_DATE_CANDIDATES = {'date', 'formation_date', 'sinkhole_date', 'data', 'DATE', 'Date'}
MAP_WELLS_REQUIRED = {'WGS_lon', 'WGS_lat'}
GEOJSONS = [
    'karst_lithuania.geojson', 'karst_latvia.geojson', 'baltic_cities.geojson',
    'country_borders.geojson', 'world.geojson', 'elevation.geojson',
    'rivers.geojson', 'karst_regions.geojson',
]


def fail(message: str) -> None:
    raise RuntimeError(message)


def main() -> None:
    master = RAW / 'daily_hydroclimate_groundwater.zip'
    sinkholes = RAW / 'sinkholes.csv'
    wells = MAP / 'wells.csv'

    for path in [master, sinkholes, wells]:
        if not path.exists():
            fail(f'Missing {path.relative_to(ROOT)}. Run python scripts/download_data.py --all')

    if not zipfile.is_zipfile(master):
        fail(f'{master} is not a ZIP archive')

    with zipfile.ZipFile(master) as z:
        csvs = [name for name in z.namelist() if name.lower().endswith('.csv')]
        if not csvs:
            fail('Master ZIP contains no CSV.')
        with z.open(csvs[0]) as f:
            master_df = pd.read_csv(f, nrows=5)

    missing = MASTER_REQUIRED - set(master_df.columns)
    if missing:
        fail(f'Master dataset missing required columns: {sorted(missing)}')

    sink_df = pd.read_csv(sinkholes, nrows=5)
    if not SINKHOLE_DATE_CANDIDATES.intersection(sink_df.columns):
        print('[warning] Sinkhole file date column is not one of the common names; inspect before running.')

    wells_df = pd.read_csv(wells, nrows=5)
    missing = MAP_WELLS_REQUIRED - set(wells_df.columns)
    if missing:
        fail(f'Map wells file missing columns: {sorted(missing)}')

    for name in GEOJSONS:
        path = MAP / name
        if not path.exists():
            fail(f'Missing {path.relative_to(ROOT)}')
        with path.open('r', encoding='utf-8') as f:
            obj = json.load(f)
        if not isinstance(obj, dict) or 'type' not in obj:
            fail(f'Invalid GeoJSON: {path.relative_to(ROOT)}')

    print('All repository data inputs passed basic validation.')


if __name__ == '__main__':
    main()
