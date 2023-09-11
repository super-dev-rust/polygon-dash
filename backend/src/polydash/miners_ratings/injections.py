INJECTION_DELAY_THRESHOLD = 10000


class InjectionDetector:
    @staticmethod
    def is_transaction_injection(
        tx_finalized_time: int, tx_arrival_time: int = None
    ) -> bool:
        if tx_arrival_time is None:
            return True

        live_time = tx_finalized_time - tx_arrival_time
        if live_time <= -INJECTION_DELAY_THRESHOLD:
            return True
        return False
