from collections import abc
from copy import deepcopy
from typing import Any, Optional, Union, Dict

import pyproj
import rasterio as rio


def epsg_from_utm_zone_number(utm_zone_number, south):
    """Return the EPSG code for a UTM zone number.

    Args:
        utm_zone_number (int): The UTM zone number.
        south (bool): Whether this UTM zone is a south zone.

    Returns:
        int: The EPSG code number for the UTM zone.
    """
    crs = pyproj.CRS.from_dict({
        'proj': 'utm',
        'zone': utm_zone_number,
        'south': south
    })

    return int(crs.to_authority()[1])


def reproject_geom(src_crs: Union[pyproj.CRS, rio.crs.CRS, ],
                   dest_crs: Any,
                   geom: Dict[str, Any],
                   precision: Optional[int] = None):
    """Reprojects a geometry represented as GeoJSON
    from the src_crs to the dest crs.

    Args:
        src_crs: pyproj.crs.CRS, rasterio.crs.CRS or str used to create one
            Projection of input data.
        dest_crs: pyproj.crs.CRS, rasterio.crs.CRS or str used to create one
            Projection of output data.
        geom (dict): The GeoJSON geometry
        precision

    Returns:
        dict: The reprojected geometry
    """
    transformer = pyproj.Transformer.from_crs(src_crs,
                                              dest_crs,
                                              always_xy=True)
    result = deepcopy(geom)

    def fn(coords):
        coords = list(coords)
        for i in range(0, len(coords)):
            coord = coords[i]
            if isinstance(coord[0], abc.Sequence):
                coords[i] = fn(coord)
            else:
                x, y = coord
                reprojected_coords = transformer.transform(x, y)
                if precision is not None:
                    reprojected_coords = [
                        round(n, precision) for n in reprojected_coords
                    ]
                coords[i] = reprojected_coords
        return coords

    result['coordinates'] = fn(result['coordinates'])

    return result
