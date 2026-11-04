"""Sample addresses using familiar localities, not verified collection sites."""

LOCALITIES = (
    'Park Street, Kolkata',
    'Salt Lake, Kolkata',
    'Dum Dum, Kolkata',
    'Kestopur, Kolkata',
    'Howrah, West Bengal',
)

CENTRE_ADDRESSES = {
    'GreenLoop Recycling': '12, Park Street, Kolkata',
    'CircuitCycle Hub': '48, Salt Lake, Kolkata',
    'EarthFirst Recovery': '7, Howrah, West Bengal',
}


def collection_address(index):
    return f'{10 + index}, {LOCALITIES[index % len(LOCALITIES)]}'
