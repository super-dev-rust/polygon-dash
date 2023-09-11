from polydash.dashboard.routes import dashboard_router
from polydash.dashboard.settings import DashboardSettings
from polydash.polygon.block_retriever.retriever import BlockRetriever
from polydash.polygon.block_retriever.routes import block_router
from polydash.polygon.deanon.deanonymizer import Deanonymizer
from polydash.polygon.deanon.routes import deanon_router
from polydash.miners_ratings.live_rating import PolygonRatingProcessor
from polydash.miners_ratings.routes import transaction_risk_router
from polydash.polygon.w3router_watcher.w3router_watcher import W3RouterWatcher


def startup_sequence_polygon(s: DashboardSettings):
    BlockRetriever(daemon=True, settings=s.block_retriever).start()
    Deanonymizer(daemon=True).start()
    PolygonRatingProcessor(daemon=True).start()
    W3RouterWatcher(daemon=True, settings=s.w3_router).start()


routers_polygon = [
    block_router,
    dashboard_router,
    deanon_router,
    transaction_risk_router,
]
