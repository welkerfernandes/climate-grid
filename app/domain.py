"""Explainable operational weather rules, never a safety certification."""
from pydantic import BaseModel, Field, model_validator
from typing import Annotated

Number=Annotated[float,Field(allow_inf_nan=False)]
class Daily(BaseModel):
    time: list[str]=Field(min_length=1,max_length=16)
    temperature_2m_max: list[Number|None]
    precipitation_sum: list[Number|None]
    wind_speed_10m_max: list[Number|None]

    @model_validator(mode='after')
    def aligned(self):
        if any(len(getattr(self,name))!=len(self.time) for name in ('temperature_2m_max','precipitation_sum','wind_speed_10m_max')):
            raise ValueError('Misaligned daily series')
        return self

def assess(daily,heat,rain,wind):
    days=[]
    for date,t,p,w in zip(daily.time,daily.temperature_2m_max,daily.precipitation_sum,daily.wind_speed_10m_max):
        missing=t is None or p is None or w is None
        reasons=[]
        if t is not None and t>=heat: reasons.append('heat')
        if p is not None and p>=rain: reasons.append('rain')
        if w is not None and w>=wind: reasons.append('wind')
        # Missing evidence always prevents a nominal all-clear.
        status='unknown' if missing else 'high' if len(reasons)>=2 else 'watch' if reasons else 'normal'
        days.append({'date':date,'temperature_c':t,'rain_mm':p,'wind_kmh':w,'status':status,'reasons':reasons,'missing_data':missing})
    rank={'normal':0,'watch':1,'high':2,'unknown':3}
    return {'days':days,'overall':max((d['status'] for d in days),key=rank.get),
            'flagged_days':sum(d['status'] in ('watch','high') for d in days),
            'model':'operational-thresholds-v1','thresholds':{'heat_c':heat,'rain_mm':rain,'wind_kmh':wind}}
