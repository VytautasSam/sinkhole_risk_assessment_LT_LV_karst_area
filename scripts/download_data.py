#!/usr/bin/env python3
"""Download the public reproducibility inputs.

Core data:
    python scripts/download_data.py --core

Map data:
    python scripts/download_data.py --map

Everything:
    python scripts/download_data.py --all

The master groundwater/hydroclimate ZIP is first downloaded with the same
Google Drive direct-download pattern used in the original successful notebook.
If that response is not the expected file, gdown is used as a fallback.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path

import gdown
import requests

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = REPO_ROOT / 'data' / 'raw'
DATA_MAP = REPO_ROOT / 'data' / 'map'

SOURCES = [
    {
        'key': 'daily_master',
        'group': 'core',
        'kind': 'gdrive',
        'id': '11TvlNdqSQv6PPooHwt7f9A68Ibz1sQIU',
        'share_url': 'https://drive.google.com/file/d/11TvlNdqSQv6PPooHwt7f9A68Ibz1sQIU/view?usp=sharing',
        'path': DATA_RAW / 'daily_hydroclimate_groundwater.zip',
    },
    {
        'key': 'sinkholes',
        'group': 'core',
        'kind': 'sheet',
        'id': '160ntRKCTC3CzqCW8kwEuQ6fKoR7KPXtC',
        'sheet': 'Sheet1',
        'path': DATA_RAW / 'sinkholes.csv',
    },
    {
        'key': 'map_wells',
        'group': 'map',
        'kind': 'sheet',
        'id': '1JA6k672nA5W4eEvTDRCT7RGJPK_aWKRZ',
        'sheet': 'Sheet1',
        'path': DATA_MAP / 'wells.csv',
    },
    {
        'key': 'karst_lithuania',
        'group': 'map',
        'kind': 'gdrive',
        'id': '1JuVp_mN1_1hPf_JFYa64NO4lMwnOtDFB',
        'share_url': 'https://drive.google.com/file/d/1JuVp_mN1_1hPf_JFYa64NO4lMwnOtDFB/view?usp=drive_link',
        'path': DATA_MAP / 'karst_lithuania.geojson',
    },
    {
        'key': 'karst_latvia',
        'group': 'map',
        'kind': 'gdrive',
        'id': '1xc1lgdmSOYS2XMPkK2bYjwfG4-nYOEtT',
        'share_url': 'https://drive.google.com/file/d/1xc1lgdmSOYS2XMPkK2bYjwfG4-nYOEtT/view?usp=drive_link',
        'path': DATA_MAP / 'karst_latvia.geojson',
    },
    {
        'key': 'baltic_cities',
        'group': 'map',
        'kind': 'gdrive',
        'id': '1t-zXz455_8Ku7OEIp5KdIpFtzaC0mmjx',
        'share_url': 'https://drive.google.com/file/d/1t-zXz455_8Ku7OEIp5KdIpFtzaC0mmjx/view?usp=drive_link',
        'path': DATA_MAP / 'baltic_cities.geojson',
    },
    {
        'key': 'country_borders',
        'group': 'map',
        'kind': 'gdrive',
        'id': '1OtQC3aoqDlR9HJri_TJVmWCy-md6TD0y',
        'share_url': 'https://drive.google.com/file/d/1OtQC3aoqDlR9HJri_TJVmWCy-md6TD0y/view?usp=drive_link',
        'path': DATA_MAP / 'country_borders.geojson',
    },
    {
        'key': 'world',
        'group': 'map',
        'kind': 'gdrive',
        'id': '13h_dMZ46UwB4Q1Eyh9fYYS2xhJHUn-P_',
        'share_url': 'https://drive.google.com/file/d/13h_dMZ46UwB4Q1Eyh9fYYS2xhJHUn-P_/view?usp=drive_link',
        'path': DATA_MAP / 'world.geojson',
    },
    {
        'key': 'elevation',
        'group': 'map',
        'kind': 'gdrive',
        'id': '1ouZHxIkmc1bNwg5X2Jquv_VZqomCGyYr',
        'share_url': 'https://drive.google.com/file/d/1ouZHxIkmc1bNwg5X2Jquv_VZqomCGyYr/view?usp=drive_link',
        'path': DATA_MAP / 'elevation.geojson',
    },
    {
        'key': 'rivers',
        'group': 'map',
        'kind': 'gdrive',
        'id': '1tGmaPScF6fkxzKbG1CINDmDDeBG4oxPm',
        'share_url': 'https://drive.google.com/file/d/1tGmaPScF6fkxzKbG1CINDmDDeBG4oxPm/view?usp=drive_link',
        'path': DATA_MAP / 'rivers.geojson',
    },
    {
        'key': 'karst_regions',
        'group': 'map',
        'kind': 'gdrive',
        'id': '1DELR18mmEPG1oV_rHGyMrGqkwRXftNt2',
        'share_url': 'https://drive.google.com/file/d/1DELR18mmEPG1oV_rHGyMrGqkwRXftNt2/view?usp=drive_link',
        'path': DATA_MAP / 'karst_regions.geojson',
    },
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def _looks_like_html(path: Path) -> bool:
    try:
        head = path.read_bytes()[:512].lower()
    except Exception:
        return False
    return b'<html' in head or b'<!doctype html' in head


def download_gdrive(item: dict) -> None:
    """Download a public Google Drive file using three independent methods."""
    path = item['path']
    file_id = item['id']
    path.parent.mkdir(parents=True, exist_ok=True)

    attempts = []

    def try_requests(url: str, label: str) -> bool:
        try:
            print(f'  trying {label} ...', flush=True)
            with requests.get(
                url,
                stream=True,
                timeout=600,
                allow_redirects=True,
                headers={'User-Agent': 'Mozilla/5.0'},
            ) as response:
                print(
                    f'    HTTP {response.status_code}; '
                    f'content-type={response.headers.get("content-type")}; '
                    f'final-url={response.url}',
                    flush=True,
                )
                response.raise_for_status()

                with path.open('wb') as f:
                    for chunk in response.iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            f.write(chunk)

            size = path.stat().st_size if path.exists() else 0

            if size == 0:
                attempts.append(f'{label}: empty response')
                path.unlink(missing_ok=True)
                return False

            if _looks_like_html(path):
                preview = path.read_bytes()[:250].decode('utf-8', errors='replace')
                attempts.append(f'{label}: HTML response: {preview!r}')
                path.unlink(missing_ok=True)
                return False

            print(f'    downloaded {size / (1024 * 1024):.2f} MB', flush=True)
            return True

        except Exception as exc:
            attempts.append(f'{label}: {type(exc).__name__}: {exc}')
            path.unlink(missing_ok=True)
            return False

    # 1. Classic Google Drive endpoint used by the original notebook.
    if try_requests(
        f'https://drive.google.com/uc?export=download&id={file_id}',
        'drive.google.com/uc',
    ):
        return

    # 2. Google user-content endpoint. This often works better for larger
    # public Drive files in hosted notebook environments.
    if try_requests(
        f'https://drive.usercontent.google.com/download?id={file_id}&export=download&confirm=t',
        'drive.usercontent.google.com',
    ):
        return

    # 3. gdown handles Drive confirmation forms/cookies.
    try:
        print('  trying gdown ...', flush=True)
        result = gdown.download(
            id=file_id,
            output=str(path),
            quiet=False,
        )

        if result is not None and path.exists() and path.stat().st_size > 0:
            if not _looks_like_html(path):
                print(
                    f'    downloaded {path.stat().st_size / (1024 * 1024):.2f} MB',
                    flush=True,
                )
                return

        attempts.append('gdown: no valid file returned')
        path.unlink(missing_ok=True)

    except Exception as exc:
        attempts.append(f'gdown: {type(exc).__name__}: {exc}')
        path.unlink(missing_ok=True)

    details = '\n'.join(f'    - {attempt}' for attempt in attempts)

    raise RuntimeError(
        f'All Google Drive download methods failed for {item["key"]}.\n'
        f'File ID: {file_id}\n'
        f'Share URL: {item.get("share_url")}\n'
        f'Attempts:\n{details}\n\n'
        'Open the share URL in an incognito/private browser window. '
        'If it does not download/view without signing in, set Google Drive '
        'General access to "Anyone with the link" and role to "Viewer".'
    )

def download_sheet(item: dict) -> None:
    path = item['path']
    path.parent.mkdir(parents=True, exist_ok=True)

    url = (
        f'https://docs.google.com/spreadsheets/d/{item["id"]}/gviz/tq'
        f'?tqx=out:csv&sheet={item["sheet"]}'
    )
    response = requests.get(
        url,
        timeout=180,
        headers={'User-Agent': 'Mozilla/5.0'},
    )
    response.raise_for_status()

    if not response.content:
        raise RuntimeError(f'Google Sheet export was empty: {item["key"]}')

    path.write_bytes(response.content)

    if _looks_like_html(path):
        path.unlink(missing_ok=True)
        raise RuntimeError(
            f'Google Sheets returned HTML instead of CSV for {item["key"]}. '
            'Check that the sheet is publicly viewable.'
        )


def validate_download(item: dict) -> None:
    path = item['path']

    if not path.exists() or path.stat().st_size == 0:
        raise RuntimeError(f'Missing or empty file: {path}')

    if item['key'] == 'daily_master':
        if not zipfile.is_zipfile(path):
            raise RuntimeError(
                f'{path.name} is not a ZIP archive. '
                f'First bytes: {path.read_bytes()[:80]!r}'
            )
        with zipfile.ZipFile(path) as z:
            csv_names = [n for n in z.namelist() if n.lower().endswith('.csv')]
            if not csv_names:
                raise RuntimeError(f'{path.name} does not contain a CSV file.')

    elif path.suffix.lower() in {'.geojson', '.json'}:
        try:
            with path.open('r', encoding='utf-8') as f:
                obj = json.load(f)
        except Exception as exc:
            raise RuntimeError(f'Invalid GeoJSON/JSON: {path.name}: {exc}') from exc

        if not isinstance(obj, dict):
            raise RuntimeError(f'Unexpected JSON structure in {path.name}.')


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--all', action='store_true')
    group.add_argument('--core', action='store_true')
    group.add_argument('--map', action='store_true')
    parser.add_argument('--force', action='store_true')
    args = parser.parse_args()

    wanted = {'core', 'map'} if args.all else ({'core'} if args.core else {'map'})

    selected = [item for item in SOURCES if item['group'] in wanted]

    for item in selected:
        path = item['path']

        if path.exists() and path.stat().st_size > 0 and not args.force:
            print(f'[validate] {path.relative_to(REPO_ROOT)}')
        else:
            print(f'[download] {item["key"]} -> {path.relative_to(REPO_ROOT)}')
            try:
                if item['kind'] == 'gdrive':
                    download_gdrive(item)
                elif item['kind'] == 'sheet':
                    download_sheet(item)
                else:
                    raise ValueError(item['kind'])

                validate_download(item)

            except Exception as exc:
                print()
                print('=' * 70, file=sys.stderr)
                print(f'FAILED INPUT: {item["key"]}', file=sys.stderr)
                print(f'TARGET: {path.relative_to(REPO_ROOT)}', file=sys.stderr)
                print(f'ERROR: {exc}', file=sys.stderr)
                print('=' * 70, file=sys.stderr)
                return 1

        # Validate pre-existing files too.
        try:
            validate_download(item)
        except Exception as exc:
            print(f'Validation failed for {item["key"]}: {exc}', file=sys.stderr)
            return 1

        print(f'  OK: {path.stat().st_size / (1024 * 1024):.2f} MB')

    checksum_path = REPO_ROOT / 'data' / 'checksums.sha256'
    checksum_path.parent.mkdir(parents=True, exist_ok=True)
    with checksum_path.open('w', encoding='utf-8') as f:
        for item in SOURCES:
            path = item['path']
            if path.exists() and path.stat().st_size > 0:
                f.write(
                    f'{sha256(path)}  '
                    f'{path.relative_to(REPO_ROOT).as_posix()}\n'
                )

    print()
    print(f'Validated {len(selected)} requested input(s).')
    print(f'Checksums: {checksum_path.relative_to(REPO_ROOT)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
