import json
from .native import invoke
from typing import Literal
from fastapi import HTTPException
from pydantic import BaseModel,Field,ValidationError
from .domain import Daily,assess
from .infrastructure import demo_metadata

class Command(BaseModel):
    mode: Literal['demo','live']='live'
    site: str=Field(default='Caldas Novas',min_length=1,max_length=100)
    latitude: float=Field(default=-17.74,ge=-90,le=90,allow_inf_nan=False)
    longitude: float=Field(default=-48.63,ge=-180,le=180,allow_inf_nan=False)
    heat_c: float=Field(default=35,ge=20,le=60,allow_inf_nan=False)
    rain_mm: float=Field(default=25,gt=0,le=500,allow_inf_nan=False)
    wind_kmh: float=Field(default=45,gt=0,le=300,allow_inf_nan=False)

def execute(command,api):
    if command.mode=='demo':
        data={'daily':{'time':['2030-01-01','2030-01-02','2030-01-03','2030-01-04','2030-01-05','2030-01-06','2030-01-07'],
              'temperature_2m_max':[31,34,38,36,29,30,32],'precipitation_sum':[0,12,32,4,45,2,0],
              'wind_speed_10m_max':[12,25,52,30,50,14,20]}}
        metadata=demo_metadata(data)
    else:
        data,metadata=api.get('https://api.open-meteo.com/v1/forecast',{'latitude':command.latitude,'longitude':command.longitude,
             'daily':'temperature_2m_max,precipitation_sum,wind_speed_10m_max','timezone':'UTC','forecast_days':7,
             'temperature_unit':'celsius','wind_speed_unit':'kmh','precipitation_unit':'mm'})
    try: daily=Daily.model_validate(data['daily'])
    except (ValidationError,KeyError,TypeError): raise HTTPException(502,'Weather provider schema mismatch')
    analysis=assess(daily,command.heat_c,command.rain_mm,command.wind_kmh)
    native=invoke(json.dumps({'days':[{'date':d['date'],'temperature_c':d['temperature_c'],'rain_mm':d['rain_mm'],'wind_kmh':d['wind_kmh']} for d in analysis['days']], 'heat':command.heat_c,'rain':command.rain_mm,'wind':command.wind_kmh}))
    if native is not None: analysis=native
    else: analysis['engine']='python'
    return {'site':command.site,'coordinates':[command.latitude,command.longitude],'timezone':'UTC',
            **analysis,'provenance':metadata}
