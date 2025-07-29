from bot.core.config import settings
from bot.manager.bookling import Bookling
from bot.manager.e_knygarnya import EKnygarnya
from bot.manager.fabula import Fabula
from bot.manager.ksd import KSD
from bot.manager.mbooks import MegogoBooks
from bot.manager.old_lion import OldLion
from bot.manager.readeat import Readeat
from bot.manager.sens import Sens
from bot.manager.vivat import Vivat
from bot.manager.yakaboo import Yakaboo
from bot.manager.zhupansky_publisher import ZhupanskyPublisher

MANAGER_CONFIGS = [
    (Yakaboo, settings.search_url_yakaboo),
    (Sens, settings.search_url_sens),
    (Readeat, settings.search_api_url_readeat),
    (EKnygarnya, settings.search_url_eknygarnya),
    (ZhupanskyPublisher, settings.search_url_zhupansky),
    (Bookling, settings.search_url_bookling),
    (KSD, settings.search_url_ksd),
    (Vivat, settings.search_url_vivat),
    (OldLion, settings.search_url_old_lion),
    (MegogoBooks, settings.search_url_mbooks),
    (Fabula, settings.search_url_fabula),
]
