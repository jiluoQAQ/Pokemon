import asyncio
from pathlib import Path
from gsuid_core.utils.download_resource.download_core import download_all_file
from .RESOURCE_PATH import CHAR_ICON_PATH

async def check_use():
    await download_all_file(
        'Pokemon',
        {
            'resource/icon': CHAR_ICON_PATH,
        },
    )
    return 'pm全部资源下载完成!'
