import pandas as pd

from data.tests.setup.test_data.sample_data import exchange_data_2
from database.model.models import ExchangeData

model_class = ExchangeData
data = pd.DataFrame([exchange_data_2])
count_updates = False
