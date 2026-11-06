export type Field = {name:string;label:string;type?:string;options?:{value:string;label:string}[]};
export const config: {title:string;symbol:string;subtitle:string;headline:string;description:string;provider:string;source:string;notice:string;defaults:Record<string,string>;fields:Field[]} = {
  "title": "Climate Grid",
  "symbol": "◈",
  "subtitle": "Operational climate intelligence",
  "headline": "Antecipe o impacto do clima.",
  "description": "Transforme previsões em sinais operacionais rastreáveis.",
  "provider": "Open-Meteo",
  "source": "https://open-meteo.com/en/docs",
  "notice": "Critérios operacionais explicáveis. Não substitui alertas oficiais ou avaliação de segurança.",
  "defaults": {
    "site": "Caldas Novas",
    "latitude": "-17.74",
    "longitude": "-48.63",
    "heat_c": "35",
    "rain_mm": "25",
    "wind_kmh": "45"
  },
  "fields": [
    {
      "name": "site",
      "label": "Unidade operacional",
      "type": "text"
    },
    {
      "name": "latitude",
      "label": "Latitude",
      "type": "number"
    },
    {
      "name": "longitude",
      "label": "Longitude",
      "type": "number"
    },
    {
      "name": "heat_c",
      "label": "Limite de calor (°C)",
      "type": "number"
    },
    {
      "name": "rain_mm",
      "label": "Limite de chuva (mm/dia)",
      "type": "number"
    },
    {
      "name": "wind_kmh",
      "label": "Limite de vento (km/h)",
      "type": "number"
    }
  ]
};
