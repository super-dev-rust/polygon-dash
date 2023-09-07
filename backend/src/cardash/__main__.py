from cardash.live_rating import start_live_time_cardano_rating
from common.dashboard.routes import dashboard_router
from common.start import Dashboard

from polydash.block_retriever.routes import block_router
from polydash.miners_ratings.routes import transaction_risk_router
from polydash.settings import PolydashSettings

routers = [block_router,
           dashboard_router,
           transaction_risk_router]


def startup_sequence(s: PolydashSettings):
    start_live_time_cardano_rating()


if __name__ == "__main__":
    Dashboard(routers, startup_sequence).start()
