from polydash.dashboard.routes import dashboard_router
from polydash.dashboard.settings import DashboardSettings
from polydash.polygon.block_retriever.retriever import BlockRetriever
from polydash.polygon.block_retriever.routes import block_router
from polydash.polygon.deanon.deanonymizer import start_deanonymizer
from polydash.polygon.deanon.routes import deanon_router
from polydash.miners_ratings.live_rating import start_live_time_polygon_rating
from polydash.miners_ratings.routes import transaction_risk_router
from polydash.polygon.w3router_watcher.w3router_watcher import W3RouterWatcher


def startup_sequence_polygon(s: DashboardSettings):
    BlockRetriever(s.block_retriever).start()
    start_deanonymizer()
    start_live_time_polygon_rating()
    W3RouterWatcher(s.w3_router).start()


routers_polygon = [block_router,
                   dashboard_router,
                   deanon_router,
                   transaction_risk_router]
