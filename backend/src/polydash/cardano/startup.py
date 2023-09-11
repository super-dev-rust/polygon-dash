from polydash.cardano.live_rating import CardanoRatingProcessor
from polydash.cardano.retriever import CardanoBlockRetriever
from polydash.dashboard.routes import dashboard_router
from polydash.dashboard.settings import DashboardSettings

from polydash.polygon.block_retriever.routes import block_router
from polydash.miners_ratings.routes import transaction_risk_router


def startup_sequence_cardano(s: DashboardSettings):
    CardanoRatingProcessor(daemon=True).start()
    CardanoBlockRetriever(daemon=True, settings=s.block_retriever).start()


routers_cardano = [block_router, dashboard_router, transaction_risk_router]
