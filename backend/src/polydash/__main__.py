from common.dashboard.routes import dashboard_router
from common.start import Dashboard
from polydash.block_retriever.retriever import BlockRetriever
from polydash.block_retriever.routes import block_router
from polydash.deanon.deanonymizer import start_deanonymizer
from polydash.deanon.routes import deanon_router
from polydash.miners_ratings.live_rating import start_live_time_polygon_rating
from polydash.miners_ratings.routes import transaction_risk_router
from polydash.settings import PolydashSettings
from polydash.w3router_watcher.w3router_watcher import W3RouterWatcher

routers = [block_router,
           dashboard_router,
           deanon_router,
           transaction_risk_router]


def startup_sequence(s: PolydashSettings):
    BlockRetriever(s.block_retriever).start()
    start_deanonymizer()
    start_live_time_polygon_rating()
    W3RouterWatcher(s.w3_router).start()


if __name__ == "__main__":
    Dashboard(routers, startup_sequence).start()
