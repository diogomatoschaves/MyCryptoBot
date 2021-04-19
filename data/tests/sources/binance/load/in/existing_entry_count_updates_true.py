import pandas as pd

from data.tests.helpers.sample_data import exchange_data_1
from database.model.models import ExchangeData

model_class = ExchangeData
data = pd.DataFrame([exchange_data_1])
count_updates = True
