from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event

from ..utils.resource.download_from_cos import check_use

sv_sr_download_config = SV('pm下载资源', pm=1)


@sv_sr_download_config.on_fullmatch('pm下载全部资源')
async def send_download_resource_msg(bot: Bot, ev: Event):
    await bot.send('pm正在开始下载~可能需要较久的时间!')
    im = await check_use()
    await bot.send(im)


async def startup():
    await check_use()
