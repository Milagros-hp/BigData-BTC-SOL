"""Genera los tableros provisionados. Ejecutar dentro del contenedor Python; JSON a stdout.

    python generar_dashboard.py            -> CryptoPulse · Ejecutivo  (uid cryptopulse-main)
    python generar_dashboard.py operacion  -> CryptoPulse · Operación  (uid cryptopulse-ops)
"""
import json
import sys

PG={'type':'postgres','uid':'cryptopulse-postgres'}
PROM={'type':'prometheus','uid':'cryptopulse-prometheus'}

# Sistema de diseño CryptoPulse: la misma paleta del sitio MkDocs, las presentaciones y el pitch.
NAVY,NAVY_2,INK,MUTED='#12182B','#1B2440','#F4F1EA','#C9CED8'
BTC,SOL,PAIR,REAL='#F2A65A','#4C9BE8','#B48EF0','#C9CED8'
GREEN,AMBER,RED,GRAY='#3FB68B','#E0A030','#E5534B','#7A8296'
STATE_COLORS=[('NORMAL',GREEN),('LISTO',GREEN),('SIN CRUCES',GREEN),('VIGILANCIA',AMBER),('ALERTA',RED),
    ('DESACTUALIZADO',RED),('REVISAR INFERENCIA',RED),('DATOS INCOMPLETOS',RED),('SIN EVALUAR',GRAY),('REFERENCIA',SOL)]

# Estilo global: Grafana OSS no admite temas propios; un panel de texto con HTML sin sanitizar
# (GF_PANELS_DISABLE_SANITIZE_HTML) inyecta estas reglas solo mientras el tablero está abierto.
CSS=f'''<style>
body{{background:#0E1322!important}}
.react-grid-item section{{background:#151C30!important;border:1px solid rgba(201,206,216,.10)!important;border-radius:14px!important;box-shadow:0 8px 24px rgba(0,0,0,.28)!important}}
[data-testid^="data-testid Panel header"] h2{{font-weight:600!important;letter-spacing:.01em}}
[data-testid^="data-testid dashboard-row-title"]{{color:{BTC}!important;text-transform:uppercase;letter-spacing:.08em;font-size:13px!important}}
.cp-chip{{display:inline-block;padding:6px 12px;border-radius:999px;background:rgba(244,241,234,.06);border:1px solid rgba(244,241,234,.14);color:{INK};font-size:12px;margin:3px}}
.cp-chip b{{color:{BTC}}}
</style>'''

def banner(subtitle,links):
    chips=''.join(f'<span class="cp-chip" style="border-left:3px solid {c}"><b style="color:{c}">{d}</b> · {n}</span>'
        for d,n,c in [('Volatilidad','Franck',BTC),('Caídas','Julmer',RED),('Actividad','Abdul',GREEN),('Divergencia','Luz Milagros',PAIR)])
    anchors=''.join(f'<a href="{u}" style="color:{BTC};font-weight:600;margin-right:16px;text-decoration:none">{t} →</a>' for t,u in links)
    return (CSS+f'''<div style="display:flex;align-items:center;justify-content:space-between;gap:24px;padding:16px 24px;border-radius:16px;
background:linear-gradient(120deg,{NAVY} 0%,{NAVY_2} 62%,#2A1F14 100%);border:1px solid rgba(242,166,90,.35)">
<div><div style="color:{BTC};font-weight:700;letter-spacing:.18em;font-size:11px;text-transform:uppercase">Big Data · UPeU 2026-2 · Grupo 3 · {subtitle}</div>
<div style="font-size:30px;font-weight:800;color:{INK};line-height:1.2">CryptoPulse <span style="color:{BTC}">BTC</span> · <span style="color:{SOL}">SOL</span></div>
<div style="color:{MUTED};font-size:14px;max-width:780px">¿Cómo anticipar, con 5 a 30 minutos de antelación, volatilidad alta, caídas fuertes, actividad anómala y desacople entre BTC y SOL?</div>
<div style="margin-top:6px;font-size:13px">{anchors}</div></div>
<div style="text-align:right;max-width:560px">{chips}</div></div>''')

TF='(as_of_ms BETWEEN $__unixEpochFrom()::bigint*1000 AND $__unixEpochTo()::bigint*1000)'
TFO='(open_ms BETWEEN $__unixEpochFrom()::bigint*1000 AND $__unixEpochTo()::bigint*1000)'
TFW='$__timeFilter(window_start)'
VER="model_version=(SELECT value FROM runtime_configuration WHERE key='active_model_version')"
LIVE="source_mode='live' AND "+VER
DIM_NAME="CASE dimension WHEN 'volatility' THEN 'Volatilidad' WHEN 'crash' THEN 'Caída' WHEN 'anomaly' THEN 'Actividad' ELSE 'Divergencia' END"

def fixed(color):
    return {'mode':'fixed','fixedColor':color}

def build(main):
    panels=[]
    def panel(id,title,type,x,y,w,h,query=None,unit='short',description='',prom=False,legend='{{query}}{{symbol}}{{topic}}'):
        p={'id':id,'title':title,'type':type,'gridPos':dict(x=x,y=y,w=w,h=h),'description':description,
           'fieldConfig':{'defaults':{'unit':unit,'noValue':'Pendiente'},'overrides':[]},'options':{}}
        if query:
            p['datasource']=PROM if prom else PG
            p['targets']=[dict(refId='A',expr=query,instant=type=='stat',legendFormat=legend) if prom else
             dict(refId='A',datasource=PG,rawSql=query,format='time_series' if type in ('stat','timeseries','state-timeline') else 'table',rawQuery=True)]
        if type=='stat':
            p['options']={'reduceOptions':{'calcs':['lastNotNull'],'fields':'','values':False},'textMode':'value','colorMode':'background','graphMode':'none','justifyMode':'center'}
            # Precios y conteos no deben heredar el umbral rojo genérico de Grafana en 80.
            p['fieldConfig']['defaults']['thresholds']={'mode':'absolute','steps':[{'color':NAVY_2,'value':None}]}
        elif type=='timeseries':
            p['fieldConfig']['defaults'].update(custom={'drawStyle':'line','lineWidth':2,'fillOpacity':8,'gradientMode':'opacity','spanNulls':False,'showPoints':'never','lineInterpolation':'smooth'})
            p['options']={'legend':{'displayMode':'list','placement':'bottom'},'tooltip':{'mode':'multi','sort':'desc'}}
        elif type=='table':
            p['options']={'showHeader':True,'cellHeight':'sm','footer':{'show':False}}
            p['fieldConfig']['defaults']['custom']={'align':'left','cellOptions':{'type':'auto'},'filterable':True,'wrapText':True}
        panels.append(p)
        return p
    def row(id,title,y): panel(id,title,'row',0,y,24,1)
    def table(id,title,y,h,query,description='',x=0,w=24):
        p=panel(id,title,'table',x,y,w,h,query,description=description)
        p['fieldConfig']['overrides'].append({'matcher':{'id':'byName','options':'Estado'},'properties':[
          {'id':'custom.cellOptions','value':{'type':'color-background','mode':'basic'}},
          {'id':'mappings','value':[{'type':'value','options':{s:{'text':s,'color':c} for s,c in STATE_COLORS}}]}]})
        return p
    def colored(p):
        """Colores fijos por activo; el pronóstico va punteado y la realidad posterior en puntos."""
        o=p['fieldConfig']['overrides']
        for pattern,color in [('^BTCUSDT.*',BTC),('^SOLUSDT.*',SOL),('^BTC-SOL.*',PAIR)]:
            o.append({'matcher':{'id':'byRegexp','options':pattern},'properties':[{'id':'color','value':fixed(color)}]})
        o.append({'matcher':{'id':'byRegexp','options':'.*pronóstico$'},'properties':[
            {'id':'custom.lineStyle','value':{'fill':'dash','dash':[10,6]}},{'id':'custom.fillOpacity','value':0}]})
        o.append({'matcher':{'id':'byRegexp','options':'.*realidad futura$'},'properties':[
            {'id':'custom.drawStyle','value':'points'},{'id':'custom.pointSize','value':6},{'id':'custom.fillOpacity','value':0}]})
        return p
    def status(id,title,x,y,w,expr,desc):
        p=panel(id,title,'stat',x,y,w,4,expr,'short',desc,prom=True)
        p['fieldConfig']['defaults']['mappings']=[{'type':'value','options':{'1':{'text':'OK','color':GREEN},'0':{'text':'FALLA','color':RED}}}]
        p['fieldConfig']['defaults']['thresholds']={'mode':'absolute','steps':[{'color':RED,'value':None},{'color':GREEN,'value':1}]}
        return p

    if main:
        p=panel(60,'','text',0,0,24,5)
        p['transparent']=True
        p['options']={'mode':'html','content':banner('Tablero ejecutivo',[('Operación del pipeline','/d/cryptopulse-ops'),('Estado JSON','http://localhost:48000/api/status'),('Kafka UI','http://localhost:48085')])}
        p=panel(30,'Estado integral del producto','stat',0,5,6,4,'cryptopulse_product_ready',prom=True,
         description='LISTO exige productor y driver recientes, continuidad de 61 velas en ambos activos, siete pronósticos de la versión activa con menos de 3 minutos y retraso acotado. Un contenedor activo no basta.')
        p['fieldConfig']['defaults']['mappings']=[{'type':'value','options':{'1':{'text':'LISTO','color':GREEN},'0':{'text':'REVISAR DATOS / INFERENCIA','color':RED}}}]
        p['fieldConfig']['defaults']['thresholds']={'mode':'absolute','steps':[{'color':RED,'value':None},{'color':GREEN,'value':1}]}
        for id,symbol,x,color in [(2,'BTCUSDT',6,'#B85F0E'),(3,'SOLUSDT',12,'#2D64B3')]:
            p=panel(id,f'{symbol} · cierre de 1 minuto','stat',x,5,6,4,f"SELECT now() AS time,close::double precision AS value FROM market_candles WHERE symbol='{symbol}' AND source_mode<>'replay' ORDER BY open_ms DESC LIMIT 1",'suffix: USDT','Último cierre confirmado; verificar frescura antes de usarlo. USDT es el activo de cotización.')
            p['fieldConfig']['defaults']['thresholds']['steps'][0]['color']=color
        p=panel(31,'Pronósticos vigentes · objetivo 7/7','stat',18,5,6,4,"SELECT now() AS time,count(*)::double precision AS value FROM cp_signal_board WHERE kind='forecast' AND age_seconds<=180",description='BTC y SOL: volatilidad, caída y anomalía; un pronóstico conjunto SOL−BTC. Frescura máxima: 180 segundos.')
        p['fieldConfig']['defaults']['thresholds']={'mode':'absolute','steps':[{'color':RED,'value':None},{'color':AMBER,'value':5},{'color':GREEN,'value':7}]}
        table(32,'Frescura y continuidad por activo',9,5,"SELECT symbol AS \"Activo\",status AS \"Estado\",round(candle_age_seconds,1) AS \"Edad vela · s\",context_rows AS \"Velas contexto / 61\",missing_minutes AS \"Minutos faltantes\",round(kpi_age_seconds,1) AS \"Edad indicadores · s\",to_timestamp(last_close/1000.0) AS \"Último cierre\" FROM cp_asset_health ORDER BY symbol",w=12)
        p=panel(61,'Riesgo actual · cada pronóstico como % de su umbral de alerta','bargauge',12,9,12,9,
         f"SELECT {DIM_NAME}||' · '||symbol AS \"Serie\",round((100*value/NULLIF(threshold,0))::numeric,1) AS \"% del umbral\" FROM cp_signal_board WHERE kind='forecast' ORDER BY 1",'percent',
         '100 % significa que el pronóstico alcanzó su umbral de alerta (P95 histórico o el umbral elegido en validación). Verde por debajo de 80 %, ámbar entre 80 % y 100 %, rojo desde 100 %.')
        p['options']={'displayMode':'gradient','orientation':'horizontal','showUnfilled':True,'valueMode':'color','namePlacement':'left','sizing':'auto',
            'reduceOptions':{'values':True,'calcs':['lastNotNull'],'fields':''}}
        p['fieldConfig']['defaults'].update(min=0,max=150,thresholds={'mode':'absolute','steps':[{'color':GREEN,'value':None},{'color':AMBER,'value':80},{'color':RED,'value':100}]})
        p=panel(33,'Cómo leer este tablero','text',0,14,12,4)
        p['options']={'mode':'markdown','content':'1. Comprueba **LISTO** y **7/7**. 2. Mira el **riesgo actual** y la línea de tiempo de señales. 3. Abre la dimensión de cada integrante.  \n**NORMAL** = sin cruce · **VIGILANCIA / ALERTA** = cruce real del umbral · **SIN EVALUAR / DESACTUALIZADO** = no interpretar como ausencia de riesgo. Las señales apoyan la revisión; no ejecutan órdenes.'}
        row(40,'Centro de señales · diagnóstico y revisión',18)
        p=panel(62,'Línea de tiempo de señales · pronósticos por dimensión y activo','state-timeline',0,19,24,7,
         f"SELECT to_timestamp(as_of_ms/1000.0) AS time,{DIM_NAME}||' · '||symbol AS metric,CASE WHEN triggered AND severity='high' THEN 2 WHEN triggered THEN 1 ELSE 0 END AS value FROM market_signals WHERE kind='forecast' AND {LIVE} AND {TF} ORDER BY 1",
         description='Cada franja es una serie pronosticada. Verde NORMAL, ámbar VIGILANCIA, rojo ALERTA. Permite ver de un vistazo cuándo y dónde subió el riesgo.')
        p['options']={'showValue':'never','mergeValues':True,'rowHeight':0.8,'alignValue':'left','legend':{'showLegend':False,'displayMode':'list','placement':'bottom'},'tooltip':{'mode':'single'}}
        p['fieldConfig']['defaults'].update(custom={'fillOpacity':85,'lineWidth':0},
            mappings=[{'type':'value','options':{'0':{'text':'NORMAL','color':GREEN},'1':{'text':'VIGILANCIA','color':AMBER},'2':{'text':'ALERTA','color':RED}}}],
            color={'mode':'thresholds'},thresholds={'mode':'absolute','steps':[{'color':GREEN,'value':None},{'color':AMBER,'value':1},{'color':RED,'value':2}]})
        table(10,'Señales de mercado · estado, umbral y explicación',26,11,
         f"SELECT symbol AS \"Activo\",{DIM_NAME} AS \"Dimensión\",CASE kind WHEN 'observed' THEN 'Observada' ELSE 'Pronóstico' END AS \"Origen\",state AS \"Estado\",round(value::numeric,5) AS \"Valor\",round(threshold::numeric,5) AS \"Umbral\",unit AS \"Unidad\",round(age_seconds::numeric,0) AS \"Edad · s\",explanation AS \"Interpretación\",action AS \"Qué revisar\" FROM cp_signal_board ORDER BY dimension,symbol,kind",
         'Siempre muestra las 14 evaluaciones posibles. NORMAL no es un dato ausente. Probabilidades en escala 0–1; las unidades figuran en cada fila. Señales observadas y predictivas se distinguen explícitamente.')
        history=f'''WITH events AS (SELECT to_timestamp(as_of_ms/1000.0) AS "Fecha",symbol AS "Activo",dimension AS "Dimensión",kind AS "Origen",CASE severity WHEN 'high' THEN 'ALERTA' ELSE 'VIGILANCIA' END AS "Estado",value AS "Valor",threshold AS "Umbral",explanation AS "Detalle",action AS "Qué revisar",model_version AS "Versión" FROM market_signals WHERE triggered AND {LIVE} AND {TF} ORDER BY as_of_ms DESC LIMIT 100)
 SELECT * FROM events UNION ALL SELECT NULL,'BTC / SOL','Todas','Estado',CASE WHEN (SELECT count(*) FROM cp_signal_board WHERE kind='forecast' AND age_seconds<=180)=7 THEN 'SIN CRUCES' ELSE 'REVISAR INFERENCIA' END,NULL,NULL,'No hay señales que superen umbrales en el período seleccionado. Comprueba el estado actual arriba.','No se generan alertas artificiales para llenar esta tabla.',NULL WHERE NOT EXISTS(SELECT 1 FROM events)'''
        table(34,'Historial de cruces · período seleccionado',37,8,history,'Solo cruces reales. Muestra una explicación cuando no hay alertas; no confundir un vacío histórico con salud del pipeline.')
        row(63,'Mercado en vivo · velas de 1 minuto',45)
        for id,symbol,x in [(64,'BTCUSDT',0),(65,'SOLUSDT',12)]:
            p=panel(id,f'{symbol} · velas japonesas y volumen','candlestick',x,46,12,10,
             f"SELECT to_timestamp(open_ms/1000.0) AS time,open::double precision AS open,high::double precision AS high,low::double precision AS low,close::double precision AS close,volume::double precision AS volume FROM market_candles WHERE symbol='{symbol}' AND source_mode<>'replay' AND {TFO} ORDER BY open_ms",
             'suffix: USDT','Velas reales de Binance recibidas por Kafka. Verde: cierre mayor que la apertura; rojo: menor. Barras inferiores: volumen del minuto.')
            p['options']={'mode':'candles+volume','candleStyle':'candles','colorStrategy':'open-close','colors':{'up':GREEN,'down':RED},'includeAllFields':False,
                'legend':{'showLegend':False,'displayMode':'list','placement':'bottom'},'tooltip':{'mode':'single'}}
        row(41,'Cuatro dimensiones · un integrante por dimensión',56)
        for id,dim,title,x,y,unit in [(5,'volatility','Volatilidad · Franck · observada y futura a 15 min',0,57,'percent'),(6,'crash','Caída fuerte · Julmer · probabilidad a 30 min',12,57,'percentunit'),(7,'anomaly','Actividad anómala · Abdul · probabilidad a 5 min',0,66,'percentunit'),(8,'divergence','Separación BTC–SOL · Luz Milagros · tamaño |SOL − BTC| a 15 min',12,66,'suffix: p.p.')]:
            series=[('pronóstico','forecast')]
            if dim in ('volatility','divergence'): series=[('observada reciente','observed'),('pronóstico','forecast'),('realidad futura','actual')]
            sql=' UNION ALL '.join(f"SELECT to_timestamp(as_of_ms/1000.0) AS time,symbol||' · {label}' AS metric,{col} AS value FROM predictions WHERE dimension='{dim}' AND {LIVE} AND {TF}"+(" AND actual IS NOT NULL" if col=='actual' else '') for label,col in series)+' ORDER BY 1'
            descriptions={'volatility':'Volatilidad realizada = 100√Σ(log-retorno²), sin anualizar. Línea continua: observada; punteada: pronóstico; puntos: realidad posterior, que solo existe tras 15 minutos completos.',
             'crash':'Probabilidad de rendimiento al cierre de 30 minutos bajo P5 histórico: BTC −0,558 %; SOL −1,116 %. Umbral de alerta elegido en validación: 5,8 %. Modelo limitado: consultar precisión y recall históricos.',
             'anomaly':'Probabilidad de superar P95 de volumen u operaciones en los siguientes 5 minutos, por activo y hora UTC. La anomalía observada se muestra separada en el centro de señales.',
             'divergence':'Tamaño de la separación |SOL − BTC| en puntos porcentuales, sin signo. Línea continua: observada; punteada: pronóstico; puntos: realidad posterior. La referencia es el promedio histórico de entrenamiento.'}
            p=colored(panel(id,title,'timeseries',x,y,12,9,sql,unit,descriptions[dim]))
            if dim in ('crash','anomaly'): p['fieldConfig']['defaults'].update(min=0)
        p=panel(9,'Correlación BTC / SOL · rendimientos 60 min','timeseries',0,75,12,8,f"SELECT to_timestamp(as_of_ms/1000.0) AS time,(metrics->>'correlation_60m')::double precision AS value FROM market_kpis WHERE symbol='BTC-SOL' AND {TF} ORDER BY 1",description='Pearson sobre rendimientos consecutivos de un minuto: −1 a +1. Correlación no implica causalidad.')
        p['fieldConfig']['defaults'].update(min=-1,max=1,color=fixed(PAIR),displayName='Correlación BTC–SOL')
        table(99,'Actividad observada · referencia por hora UTC',75,8,"SELECT DISTINCT ON(symbol) symbol AS \"Activo\",to_timestamp(as_of_ms/1000.0) AS \"Cierre\",round((metrics->>'quote5')::numeric,0) AS \"USDT · 5 min\",round((metrics->>'quote5_p95')::numeric,0) AS \"USDT · P95\",(metrics->>'trades5')::bigint AS \"Operaciones · 5 min\",round((metrics->>'trades5_p95')::numeric,0) AS \"Operaciones · P95\",round((metrics->>'volume_zscore')::numeric,2) AS \"Z volumen\" FROM market_kpis WHERE symbol IN ('BTCUSDT','SOLUSDT') ORDER BY symbol,as_of_ms DESC",'P95 y Z score respecto del entrenamiento 2022–2024 para activo/hora UTC. Comprueba frescura arriba; no atribuye fraude.',x=12,w=12)
        row(42,'Evidencia de utilidad · batch y en vivo lado a lado',83)
        table(11,'Batch · prueba histórica reservada, modelo contra referencia',84,16,
         "SELECT m.dimension AS \"Dimensión\",m.method AS \"Método desplegado\",(m.metrics->>'n')::bigint AS \"Casos\",(m.metrics->>'mae')::float AS \"MAE\",(m.metrics->>'rmse')::float AS \"RMSE\",(b.metrics->>'rmse')::float AS \"RMSE referencia\",(m.metrics->>'pr_auc')::float AS \"PR AUC\",(m.metrics->>'brier')::float AS \"Brier\",(b.metrics->>'brier')::float AS \"Brier referencia\",(m.metrics->>'precision')::float AS \"Precisión\",(m.metrics->>'recall')::float AS \"Recall\",m.model_version AS \"Versión\" FROM model_metrics m JOIN model_metrics b ON b.dimension=m.dimension AND b.model_version=m.model_version AND b.split='test_baseline' WHERE m.split='test_deployed' AND m.model_version=(SELECT value FROM runtime_configuration WHERE key='active_model_version') ORDER BY m.dimension",
         'Prueba enero–septiembre 2026, muestreo cada 15 min. MAE/RMSE en unidad de su objetivo; Brier menor es mejor. Precisión y recall son proporciones. No se reentrena con esta prueba para escoger modelos.',w=12)
        table(12,'En vivo · error real de los pronósticos ya madurados',84,16,
         f"SELECT dimension AS \"Dimensión\",symbol AS \"Activo\",count(*) AS \"Emitidas\",count(actual) AS \"Evaluadas\",count(*) FILTER(WHERE actual IS NULL) AS \"Pendientes\",avg(abs(forecast-actual)) FILTER(WHERE dimension IN ('volatility','divergence')) AS \"MAE regresión\",sqrt(avg(power(forecast-actual,2)) FILTER(WHERE dimension IN ('volatility','divergence'))) AS \"RMSE regresión\",avg(power(forecast-actual,2)) FILTER(WHERE dimension IN ('crash','anomaly')) AS \"Brier clasificación\",avg(power(baseline-actual,2)) AS \"MSE referencia\" FROM predictions WHERE {LIVE} AND {TF} GROUP BY dimension,symbol ORDER BY dimension,symbol",
         'Solo la versión activa y el período elegido. Los horizontes todavía abiertos o con datos incompletos permanecen pendientes. Clasificación usa Brier; no se mezcla con RMSE de precios.',x=12,w=12)
        row(44,'Eventos empresariales · operaciones ejecutadas (Kafka → Spark, ventana 1 min)',100)
        colored(panel(45,'Flujo neto comprador − vendedor por minuto','timeseries',0,101,12,8,
         f"SELECT window_start AS time,symbol||' · flujo neto' AS metric,buy_usdt-sell_usdt AS value FROM trade_flow WHERE {TFW} ORDER BY 1",'currencyUSD',
         'Cada operación de Binance (aggTrade) es un evento empresarial publicado en Kafka (market.trades.*). Spark agrupa por minuto con watermark de 1 min y deduplicación por event_id. Positivo: dominaron las compras agresivas.'))
        p=colored(panel(46,'Presión compradora · % del importe iniciado por compradores','timeseries',12,101,12,8,
         f"SELECT window_start AS time,symbol AS metric,100*buy_usdt/NULLIF(buy_usdt+sell_usdt,0) AS value FROM trade_flow WHERE {TFW} ORDER BY 1",'percent',
         '50 % es equilibrio. Valores sostenidos lejos de 50 % acompañan movimientos direccionales; contrastar con caídas y volatilidad.'))
        p['fieldConfig']['defaults']['custom'].update(thresholdsStyle={'mode':'line+area'})
        p['fieldConfig']['defaults']['thresholds']={'mode':'absolute','steps':[{'color':'transparent','value':None},{'color':'rgba(201,206,216,0.35)','value':50}]}
        table(47,'Último minuto cerrado · operaciones por activo',109,5,
         "SELECT DISTINCT ON (symbol) symbol AS \"Activo\",window_end AS \"Cierre\",trades AS \"Operaciones\",round(buy_usdt::numeric,0) AS \"Compras USDT\",round(sell_usdt::numeric,0) AS \"Ventas USDT\",large_trades AS \"Operaciones ≥ 100k USDT\",round(max_trade_usdt::numeric,0) AS \"Mayor operación USDT\" FROM trade_flow ORDER BY symbol,window_start DESC",
         'Ventanas finalizadas por watermark: aparecen con 1–2 minutos de retraso respecto al reloj.')
        annotations=[
            {'name':'Cambio de versión del modelo','enable':True,'iconColor':BTC,'datasource':PG,
             'target':{'refId':'Anno','rawQuery':True,'format':'table','rawSql':"SELECT extract(epoch FROM registered_at)*1000 AS time,'Modelo activo: '||model_version AS text,'modelo' AS tags FROM model_versions WHERE $__timeFilter(registered_at)"}},
            {'name':'Alertas de mercado','enable':True,'iconColor':RED,'datasource':PG,
             'target':{'refId':'Anno','rawQuery':True,'format':'table','rawSql':f"SELECT as_of_ms AS time,'ALERTA · '||{DIM_NAME}||' · '||symbol AS text,'alerta' AS tags FROM market_signals WHERE triggered AND severity='high' AND {LIVE} AND {TF}"}}]
        return {'uid':'cryptopulse-main','title':'CryptoPulse · BTC y SOL','panels':panels,'annotations':{'list':annotations}}

    p=panel(60,'','text',0,0,24,5)
    p['transparent']=True
    p['options']={'mode':'html','content':banner('Operación del pipeline',[('Tablero ejecutivo','/d/cryptopulse-main'),('Prometheus','http://localhost:49090/alerts'),('Kafka UI','http://localhost:48085')])}
    row(70,'Salud del pipeline · de Binance a Grafana',5)
    for id,title,x,expr,desc in [
        (71,'Binance → velas',0,'cryptopulse_producer_connected','WebSocket de velas cerradas conectado.'),
        (72,'Binance → operaciones',4,'cryptopulse_trades_producer_connected','WebSocket aggTrade conectado.'),
        (73,'Kafka',8,'min(kafka_brokers) >= bool 1','Broker disponible según kafka-exporter.'),
        (74,'Spark Streaming',12,'cryptopulse_stream_heartbeat_age_seconds < bool 60','Señal de vida del driver con menos de 60 s.'),
        (75,'PostgreSQL y exportador',16,'up{job="cryptopulse"}','El exportador consulta PostgreSQL y responde a Prometheus.'),
        (76,'Producto',20,'cryptopulse_product_ready','LISTO: datos continuos y siete pronósticos recientes.')]:
        status(id,title,x,6,4,expr,desc)
    # Las reglas viven en Prometheus; se leen con PromQL (ALERTS) para no depender del ruler de Grafana.
    p=panel(77,'Alertas disparadas ahora','stat',0,10,6,5,'count(ALERTS{alertstate="firing"}) or vector(0)','short',
        'Cuántas reglas de observability/alerts.yml están disparadas en este momento. 0 significa operación normal.',prom=True)
    p['fieldConfig']['defaults']['thresholds']={'mode':'absolute','steps':[{'color':GREEN,'value':None},{'color':RED,'value':1}]}
    p=panel(79,'Reglas evaluadas por Prometheus','stat',6,10,6,5,'sum(prometheus_rule_group_rules)','short',
        'Alertas operativas más reglas de grabación cargadas desde observability/alerts.yml.',prom=True)
    p['fieldConfig']['defaults']['thresholds']['steps'][0]['color']=NAVY_2
    p=panel(80,'Detalle de alertas disparadas','table',0,15,12,5,description='Nombre, severidad y resumen de cada alerta activa. Vacía cuando todo está normal.')
    p['datasource']=PROM
    p['targets']=[dict(refId='A',expr='ALERTS{alertstate="firing"}',instant=True,format='table',legendFormat='')]
    p['fieldConfig']['defaults']['noValue']='Sin alertas disparadas: todas las reglas están en estado normal.'
    p['transformations']=[{'id':'organize','options':{'excludeByName':{'Time':True,'Value':True,'__name__':True,'alertstate':True,'instance':True,'job':True},
        'renameByName':{'alertname':'Alerta','severity':'Severidad','query':'Consulta','topic':'Tópico','symbol':'Activo'}}}]
    p=panel(78,'Kafka · mensajes por minuto por tópico','timeseries',12,10,12,10,'cryptopulse:kafka_mensajes_por_minuto','short',
        'Regla de grabación de Prometheus: tasa de 5 minutos de los offsets, llevada a mensajes por minuto. Las operaciones son ~99 % del volumen.',prom=True,legend='{{topic}}')
    o=p['fieldConfig']['overrides']
    for pattern,color in [('.*btcusdt$',BTC),('.*solusdt$',SOL)]:
        o.append({'matcher':{'id':'byRegexp','options':pattern},'properties':[{'id':'color','value':fixed(color)}]})
    o.append({'matcher':{'id':'byRegexp','options':'^market\\.klines.*'},'properties':[{'id':'custom.lineStyle','value':{'fill':'dash','dash':[10,6]}}]})
    row(43,'Operación · recepción, procesamiento y persistencia',20)
    for id,title,x,expr,unit,desc in [(13,'WebSocket · 1 conectado',0,'cryptopulse_producer_connected','short','La conexión no sustituye continuidad e inferencia.'),(14,'Spark · edad de señal de vida',6,'cryptopulse_stream_heartbeat_age_seconds','s','La alerta integral comprueba además pronósticos.'),(15,'Kafka · eventos pendientes',12,'cryptopulse:lag_total','short','Regla de grabación: suma del lag de todos los tópicos respecto de los offsets disponibles.'),(16,'Escenario de costo · sin facturación',18,'cryptopulse_estimated_monthly_cost_usd','currencyUSD','Hipótesis editables; no cobro Docker ni cotización. CPU, memoria, disco y horas configurados.')]:
        panel(id,title,'stat',x,21,6,5,expr,unit,desc,prom=True)
    p=panel(17,'Spark · duración de micro-lotes (intervalo 15 s)','timeseries',0,26,12,7,'cryptopulse_batch_duration_seconds','s','Comparar duración con intervalo de 15 s. Los lotes de recuperación pueden excederlo.',prom=True)
    # Eje fijo hasta 60 s: un lote de recuperación muy largo no debe ocultar el comportamiento normal.
    p['fieldConfig']['defaults'].update(min=0,max=60)
    p['fieldConfig']['defaults']['custom'].update(thresholdsStyle={'mode':'line+area'})
    p['fieldConfig']['defaults']['thresholds']={'mode':'absolute','steps':[{'color':'transparent','value':None},{'color':'rgba(229,83,75,0.25)','value':15}]}
    p=panel(18,'Kafka · avance acumulado por tópico','timeseries',12,26,12,7,'sum by(topic) (kafka_topic_partition_current_offset{topic=~"market.(klines|trades).*"})','short','Suma de offsets. No es tasa de mensajes por segundo ni número retenido.',prom=True)
    for pattern,color in [('.*btcusdt.*',BTC),('.*solusdt.*',SOL)]:
        p['fieldConfig']['overrides'].append({'matcher':{'id':'byRegexp','options':pattern},'properties':[{'id':'color','value':fixed(color)}]})
    p=panel(1,'Histórico limpio · corte batch','stat',0,33,6,5,'SELECT now() AS time,sum(candles)::double precision AS value FROM batch_kpis',description='2022-01 a 2026-09. Archivos públicos con SHA256. Dos registros inválidos excluidos.')
    p['fieldConfig']['defaults']['thresholds']['steps'][0]['color']=NAVY_2
    table(35,'Ventanas finalizadas · cobertura real',33,5,"SELECT kind AS \"Ventana\",symbol AS \"Activo\",max(window_end) AS \"Último cierre finalizado\",count(*) AS \"Ventanas\",count(*) FILTER(WHERE candles<>5) AS \"Incompletas\" FROM stream_windows GROUP BY kind,symbol ORDER BY kind,symbol",'Fijas 5 min y deslizantes 5 min/paso 1 min. Watermark 2 min: una ventana finalizada puede estar incompleta; el archivo conserva reparaciones tardías.',x=6,w=18)
    row(44,'Eventos empresariales · productores y procesamiento',38)
    for id,title,x,expr,unit,desc in [
     (48,'Productor de operaciones · conectado',0,'cryptopulse_trades_producer_connected','short','1 significa WebSocket aggTrade conectado.'),
     (49,'Productor de operaciones · edad de señal',6,'cryptopulse_trades_heartbeat_age_seconds','s','Más de 60 s degrada el producto y dispara una alerta.'),
     (50,'Flujo Spark · edad de la última ventana',12,'cryptopulse_trade_flow_age_seconds','s','Más de 300 s degrada el producto.'),
     (51,'Kafka · operaciones pendientes',18,'sum(cryptopulse_kafka_checkpoint_lag{topic=~"market.trades.*"})','short','Offsets publicados aún no procesados. Se correlaciona con la duración de los micro-lotes.')]:
        panel(id,title,'stat',x,39,6,5,expr,unit,desc,prom=True)
    return {'uid':'cryptopulse-ops','title':'CryptoPulse · Operación','panels':panels,'annotations':{'list':[]}}

main='operacion' not in sys.argv[1:]
board=build(main)
links=[{'title':'Tableros CryptoPulse','type':'dashboards','tags':['cryptopulse'],'asDropdown':False,'includeVars':False,'keepTime':True},
       {'title':'Estado técnico JSON','type':'link','url':'http://localhost:48000/api/status','targetBlank':True},
       {'title':'Kafka UI','type':'link','url':'http://localhost:48085','targetBlank':True},
       {'title':'Prometheus','type':'link','url':'http://localhost:49090/alerts','targetBlank':True}]
dashboard={**board,'tags':['cryptopulse','bigdata','risk-monitoring'],'schemaVersion':40,'version':3,'refresh':'10s','timezone':'browser',
    'time':{'from':'now-3h','to':'now'},'editable':True,'graphTooltip':1,'links':links}
print(json.dumps(dashboard,ensure_ascii=False,indent=2))
