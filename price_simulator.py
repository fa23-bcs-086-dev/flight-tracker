import math, random

def simulate_price(base_price: float, days_until_flight: int, sample_index: int = 0):
    urgency_factor = 1 + max(0, (180 - days_until_flight) / 400)
    drift = 1 + (math.sin(sample_index / 7) * 0.02)
    jitter = (math.sin(days_until_flight + sample_index * 1.3) * 6) + (random.random() * 10 - 5)
    price = max(20, round((base_price * urgency_factor * drift) + jitter))
    return price
