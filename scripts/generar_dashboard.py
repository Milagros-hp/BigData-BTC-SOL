"""Genera los tableros provisionados. Ejecutar dentro del contenedor Python; JSON a stdout.

    python generar_dashboard.py            -> CryptoPulse · BTC y SOL  (uid cryptopulse-main)
    python generar_dashboard.py detalle    -> CryptoPulse · Detalle    (uid cryptopulse-detalle)
    python generar_dashboard.py operacion  -> CryptoPulse · Operación  (uid cryptopulse-ops)
    python generar_dashboard.py franck     -> Cómo se obtiene, por integrante (franck, julmer, abdul, milagros)
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

def banner(subtitle):
    chips=''.join(f'<span class="cp-chip" style="border-left:3px solid {c}"><b style="color:{c}">{d}</b> · {n}</span>'
        for d,n,c in [('Volatilidad','Franck',BTC),('Caídas','Julmer',RED),('Actividad','Abdul',GREEN),('Separación','Luz Milagros',PAIR)])
    return (CSS+f'''<div style="display:flex;align-items:center;justify-content:space-between;gap:24px;padding:8px 20px;border-radius:14px;
background:linear-gradient(120deg,{NAVY} 0%,{NAVY_2} 62%,#2A1F14 100%);border:1px solid rgba(242,166,90,.35)">
<div><div style="font-size:24px;font-weight:800;color:{INK};line-height:1.2">CryptoPulse <span style="color:{BTC}">BTC</span> · <span style="color:{SOL}">SOL</span> <span style="color:{MUTED};font-size:14px;font-weight:500">{subtitle}</span></div>
<div style="color:{MUTED};font-size:13px">Anticipar el riesgo con 5 a 30 minutos de antelación · Grupo 3 · Big Data UPeU 2026-2</div></div>
<div style="text-align:right">{chips}</div></div>''')

TF='(as_of_ms BETWEEN $__unixEpochFrom()::bigint*1000 AND $__unixEpochTo()::bigint*1000)'
TFO='(open_ms BETWEEN $__unixEpochFrom()::bigint*1000 AND $__unixEpochTo()::bigint*1000)'
TFW='$__timeFilter(window_start)'
VER="model_version=(SELECT value FROM runtime_configuration WHERE key='active_model_version')"
LIVE="source_mode='live' AND "+VER
DIM_NAME="CASE dimension WHEN 'volatility' THEN 'Volatilidad' WHEN 'crash' THEN 'Caída' WHEN 'anomaly' THEN 'Actividad' ELSE 'Divergencia' END"

def fixed(color):
    return {'mode':'fixed','fixedColor':color}


# Tableros "cómo se obtiene": un recorrido del dato por integrante. Solo se muestran valores guardados.
MEMBERS={
 'franck':dict(name='Franck',color=BTC,dim='volatility',title='Volatilidad a 15 minutos',unit='percent',model='Random Forest',horizon=15,kind='reg',
  q='¿Qué volatilidad tendrá cada activo en los próximos 15 minutos, según lo que está pasando ahora?',
  why='Avisa cuánto se puede mover el precio. Mide la **intensidad**, no la dirección: por eso se lee junto con la caída.',
  how='**Fórmula:** 100 × √(suma de los cuadrados de 15 rendimientos logarítmicos de 1 minuto), sin anualizar.\n\n**Abajo** se ven los indicadores guardados del último minuto. El modelo usa 14 variables: además, rendimiento a 5 min, volumen y operaciones, rango y cuerpo de la vela, hora del día y activo.\n\n**Sin fuga:** solo usa velas ya cerradas.',
  u1='En U1 comparó referencia, Ridge, Lasso y Random Forest con datos 2022–2026. Ganó Random Forest, con RMSE de validación 0,140.',
  limit='El pronóstico se mueve en un rango más estrecho que la realidad, así que puede quedarse corto en los picos.',
  kpi="SELECT DISTINCT ON(symbol) replace(symbol,'USDT','') AS \"Activo\",round((metrics->>'rv15')::numeric,3) AS \"Volatilidad 15 min %\",round((metrics->>'rv60')::numeric,3) AS \"Volatilidad 60 min %\",round((metrics->>'r1')::numeric,3) AS \"Rendimiento 1 min %\",round((metrics->>'r15')::numeric,3) AS \"Rendimiento 15 min %\",round((metrics->>'r30')::numeric,3) AS \"Rendimiento 30 min %\" FROM market_kpis WHERE symbol IN ('BTCUSDT','SOLUSDT') ORDER BY symbol,as_of_ms DESC"),
 'julmer':dict(name='Julmer',color=RED,dim='crash',title='Caída fuerte a 30 minutos',unit='percentunit',model='Regresión logística calibrada',horizon=30,kind='cls',
  q='¿Qué probabilidad hay de que BTC o SOL tengan una caída fuerte en los próximos 30 minutos?',
  why='Aporta la **dirección bajista** del riesgo. Sirve para priorizar una revisión, no para decidir sola.',
  how='**Caída fuerte:** rendimiento a 30 minutos por debajo del percentil 5 del entrenamiento de ese activo.\n\n**Abajo** se compara el rendimiento reciente con ese umbral. El modelo usa 14 variables de precio, volumen y hora; la probabilidad está calibrada.\n\n**Sin fuga:** solo velas cerradas y embargo de 30 minutos entre tramos.',
  u1='En U1 comparó referencia, dos logísticas y Random Forest. Ganó la logística L2, con AUC-PR de validación 0,125.',
  limit='En la prueba de 2026, de cada 100 alertas unas 14 acertaron. Las caídas fuertes son raras y difíciles de anticipar.',
  kpi="SELECT replace(symbol,'USDT','') AS \"Activo\",round(value::numeric,3) AS \"Rendimiento 30 min %\",round(threshold::numeric,3) AS \"Umbral de caída %\",state AS \"Estado\" FROM cp_signal_board WHERE dimension='crash' AND kind='observed' ORDER BY symbol"),
 'abdul':dict(name='Abdul',color=GREEN,dim='anomaly',title='Actividad anómala a 5 minutos',unit='percentunit',model='Regresión logística calibrada',horizon=5,kind='cls',
  q='¿Qué probabilidad hay de que en los próximos 5 minutos el volumen o las operaciones sean inusualmente altos para esa hora del día?',
  why='Detecta **actividad inusual**, que suele acompañar a noticias o movimientos fuertes. No atribuye fraude.',
  how='**Actividad anómala:** volumen u operaciones de 5 minutos sobre el percentil 95 de ese activo y esa hora UTC.\n\n**Abajo** se ve la actividad actual frente a esa referencia. Se compara por hora porque lo normal cambia durante el día.\n\n**Sin fuga:** las referencias salen solo del entrenamiento 2022–2024.',
  u1='En U1 comparó referencia, dos logísticas y Random Forest. Ganó la logística L2, con AUC-PR de validación 0,820.',
  limit='En vivo, en BTC, ha tenido más error que su referencia en algunos períodos. La muestra es corta y hay que seguir midiéndolo.',
  kpi="SELECT DISTINCT ON(symbol) replace(symbol,'USDT','') AS \"Activo\",round((metrics->>'quote5')::numeric,0) AS \"Volumen 5 min USDT\",round((metrics->>'quote5_p95')::numeric,0) AS \"Referencia P95 USDT\",(metrics->>'trades5')::bigint AS \"Operaciones 5 min\",round((metrics->>'trades5_p95')::numeric,0) AS \"Referencia P95 operaciones\" FROM market_kpis WHERE symbol IN ('BTCUSDT','SOLUSDT') ORDER BY symbol,as_of_ms DESC"),
 'milagros':dict(name='Luz Milagros',color=PAIR,dim='divergence',title='Separación BTC–SOL a 15 minutos',unit='suffix: p.p.',model='Regresión Ridge',horizon=15,kind='reg',
  q='¿Qué tamaño de separación entre los rendimientos de SOL y BTC se espera en los próximos 15 minutos?',
  why='Mide el **desacople**: cuándo los dos activos dejan de moverse juntos, algo que un promedio del mercado no muestra.',
  how='**Separación:** |rendimiento de SOL − rendimiento de BTC| a 15 minutos, en puntos porcentuales.\n\n**Abajo** se ven la separación actual y la correlación de la última hora. El modelo combina las variables de ambos activos.\n\n**Decisión clave:** predecir la dirección con signo no mejoró la referencia cero, así que se cambió a tamaño.',
  u1='En U1 midió cuánto y cuándo se separaron. La regresión con signo no aportó, y por eso U2 pronostica el tamaño.',
  limit='La ventaja en vivo sobre la referencia es pequeña y varía según el período.',
  kpi="SELECT DISTINCT ON(symbol) 'BTC-SOL' AS \"Par\",round((metrics->>'current_spread15')::numeric,3) AS \"Separación 15 min p.p.\",round((metrics->>'correlation_60m')::numeric,3) AS \"Correlación 60 min\",(SELECT round(threshold::numeric,3) FROM cp_signal_board WHERE dimension='divergence' AND kind='observed') AS \"Umbral p.p.\" FROM market_kpis WHERE symbol='BTC-SOL' ORDER BY symbol,as_of_ms DESC"),
}

def flow(color):
    steps=[('Binance','vela o operación real'),('Kafka','tópico con contrato'),('Spark','valida y calcula'),('Modelo','pronóstico cada minuto'),('PostgreSQL','guarda y evalúa'),('Grafana','lo que ves')]
    boxes=f'<span style="color:{MUTED};font-size:20px;margin:0 3px">→</span>'.join(
        f'<span style="display:inline-block;padding:8px 8px;border-radius:10px;background:{color if t=="Modelo" else "rgba(244,241,234,.07)"};color:{NAVY if t=="Modelo" else INK};text-align:center;min-width:74px"><b>{t}</b><br><span style="font-size:11px">{d}</span></span>' for t,d in steps)
    return f'<div style="display:flex;align-items:center;justify-content:center;flex-wrap:nowrap;height:100%;gap:0">{boxes}</div>'

def build(kind):
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
            p['fieldConfig']['defaults'].update(custom={'drawStyle':'line','lineWidth':2,'fillOpacity':8,'gradientMode':'opacity','spanNulls':False,'showPoints':'never','lineInterpolation':'smooth','axisGridShow':False})
            p['options']={'legend':{'displayMode':'list','placement':'bottom'},'tooltip':{'mode':'multi','sort':'desc'}}
        elif type=='table':
            p['options']={'showHeader':True,'cellHeight':'sm','footer':{'show':False}}
            p['fieldConfig']['defaults']['custom']={'align':'left','cellOptions':{'type':'auto'},'filterable':False,'wrapText':True}
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
        for pattern,color in [('^BTC(USDT)?( ·.*)?$',BTC),('^SOL(USDT)?( ·.*)?$',SOL),('^BTC-SOL.*',PAIR)]:
            o.append({'matcher':{'id':'byRegexp','options':pattern},'properties':[{'id':'color','value':fixed(color)}]})
        o.append({'matcher':{'id':'byRegexp','options':'.*(pronóstico|referencia)$'},'properties':[
            {'id':'custom.lineStyle','value':{'fill':'dash','dash':[10,6]}},{'id':'custom.fillOpacity','value':0}]})
        o.append({'matcher':{'id':'byRegexp','options':'.*realidad futura$'},'properties':[
            {'id':'custom.drawStyle','value':'points'},{'id':'custom.pointSize','value':6},{'id':'custom.fillOpacity','value':0}]})
        return p
    def status(id,title,x,y,w,expr,desc):
        p=panel(id,title,'stat',x,y,w,4,expr,'short',desc,prom=True)
        p['fieldConfig']['defaults']['mappings']=[{'type':'value','options':{'1':{'text':'OK','color':GREEN},'0':{'text':'FALLA','color':RED}}}]
        p['fieldConfig']['defaults']['thresholds']={'mode':'absolute','steps':[{'color':RED,'value':None},{'color':GREEN,'value':1}]}
        return p

    def head(subtitle):
        p=panel(60,'','text',0,0,24,3)
        p['transparent']=True
        p['options']={'mode':'html','content':banner(subtitle)}
    def signal_table():
        table(10,'Señales de mercado · estado, umbral y explicación',3,11,
         f"SELECT symbol AS \"Activo\",{DIM_NAME} AS \"Dimensión\",CASE kind WHEN 'observed' THEN 'Observada' ELSE 'Pronóstico' END AS \"Origen\",state AS \"Estado\",round(value::numeric,3) AS \"Valor\",round(threshold::numeric,3) AS \"Umbral\",explanation AS \"Interpretación\",action AS \"Qué revisar\" FROM cp_signal_board ORDER BY dimension,symbol,kind",
         'Siempre muestra las 14 evaluaciones posibles. NORMAL no es un dato ausente. Las señales apoyan la revisión; no ejecutan órdenes.')

    if kind=='main':
        head('Tablero principal')
        p=panel(30,'Estado del producto','stat',0,3,6,4,'cryptopulse_product_ready',prom=True,
         description='LISTO exige productor y driver recientes, continuidad de 61 velas en ambos activos, flujo de operaciones activo y siete pronósticos recientes. Un contenedor activo no basta.')
        p['fieldConfig']['defaults']['mappings']=[{'type':'value','options':{'1':{'text':'LISTO','color':GREEN},'0':{'text':'REVISAR','color':RED}}}]
        p['fieldConfig']['defaults']['thresholds']={'mode':'absolute','steps':[{'color':RED,'value':None},{'color':GREEN,'value':1}]}
        for id,symbol,x,color,decimals in [(2,'BTCUSDT',6,'#8A4A10',0),(3,'SOLUSDT',12,'#234E8C',2)]:
            p=panel(id,f'{symbol[:3]} · último cierre','stat',x,3,6,4,f"SELECT to_timestamp(open_ms/1000.0) AS time,close::double precision AS value FROM market_candles WHERE symbol='{symbol}' AND source_mode<>'replay' AND {TFO} ORDER BY open_ms",'suffix: USDT','Último cierre confirmado y su evolución en el período elegido.')
            p['fieldConfig']['defaults']['thresholds']['steps'][0]['color']=color
            p['fieldConfig']['defaults']['decimals']=decimals
            p['options']['graphMode']='area'
        p=panel(31,'Pronósticos vigentes · de 7','stat',18,3,6,4,"SELECT now() AS time,count(*)::double precision AS value FROM cp_signal_board WHERE kind='forecast' AND age_seconds<=180",description='BTC y SOL: volatilidad, caída y actividad; un pronóstico conjunto SOL−BTC. Frescura máxima: 180 segundos.')
        p['fieldConfig']['defaults']['thresholds']={'mode':'absolute','steps':[{'color':RED,'value':None},{'color':AMBER,'value':5},{'color':GREEN,'value':7}]}
        row(41,'1 · Cuatro dimensiones · un integrante por dimensión',7)
        for id,tile,dim,title,person,x,y,unit in [(5,81,'volatility','Volatilidad · Franck · observada y futura a 15 min','Franck · Volatilidad',0,8,'percent'),(6,82,'crash','Caída fuerte · Julmer · probabilidad a 30 min','Julmer · Caída fuerte',12,8,'percentunit'),(7,83,'anomaly','Actividad anómala · Abdul · probabilidad a 5 min','Abdul · Actividad anómala',0,18,'percentunit'),(8,84,'divergence','Separación BTC–SOL · Luz Milagros · tamaño |SOL − BTC| a 15 min','Luz Milagros · Separación',12,18,'suffix: p.p.')]:
            slug={'volatility':'franck','crash':'julmer','anomaly':'abdul','divergence':'milagros'}[dim]
            p=panel(tile,f'{person} · pulsa para ver cómo se obtiene','stat',x,y,12,3,
             f"SELECT now() AS time,replace(symbol,'USDT','') AS metric,100*value/NULLIF(threshold,0) AS value FROM cp_signal_board WHERE kind='forecast' AND dimension='{dim}' ORDER BY symbol",'percent',
             '100 % significa que el pronóstico alcanzó su umbral de alerta. Verde por debajo de 80 %, ámbar entre 80 % y 100 %, rojo desde 100 %.')
            p['options']['textMode']='value_and_name'
            p['fieldConfig']['defaults']['links']=[{'title':'Ver cómo se obtiene','url':f'/d/cryptopulse-{slug}?${{__url_time_range}}'}]
            p['links']=[{'title':'Ver cómo se obtiene','url':f'/d/cryptopulse-{slug}','targetBlank':False}]
            p['fieldConfig']['defaults'].update(decimals=0,thresholds={'mode':'absolute','steps':[{'color':'#24795C','value':None},{'color':AMBER,'value':80},{'color':RED,'value':100}]})
            series=[('pronóstico','forecast')]
            if dim in ('volatility','divergence'): series=[('observada','observed'),('pronóstico','forecast'),('realidad futura','actual')]
            sql=' UNION ALL '.join(f"SELECT to_timestamp(as_of_ms/1000.0) AS time,replace(symbol,'USDT','')||' · {label}' AS metric,{col} AS value FROM predictions WHERE dimension='{dim}' AND {LIVE} AND {TF}"+(" AND actual IS NOT NULL" if col=='actual' else '') for label,col in series)+' ORDER BY 1'
            descriptions={'volatility':'Volatilidad realizada = 100√Σ(log-retorno²), sin anualizar. Continua: observada; punteada: pronóstico; puntos: realidad posterior, que solo existe tras 15 minutos completos.',
             'crash':'Probabilidad de rendimiento al cierre de 30 minutos bajo P5 histórico: BTC −0,558 %; SOL −1,116 %. Umbral de alerta elegido en validación: 5,8 %.',
             'anomaly':'Probabilidad de superar P95 de volumen u operaciones en los siguientes 5 minutos, por activo y hora UTC.',
             'divergence':'Tamaño de la separación |SOL − BTC| en puntos porcentuales, sin signo. Continua: observada; punteada: pronóstico; puntos: realidad posterior.'}
            p=colored(panel(id,title,'timeseries',x,y+3,12,7,sql,unit,descriptions[dim]))
            p['links']=[{'title':'Ver cómo se obtiene','url':f'/d/cryptopulse-{slug}','targetBlank':False}]
            if dim in ('crash','anomaly'): p['fieldConfig']['defaults'].update(min=0)
        row(40,'2 · Riesgo y señales',28)
        p=panel(61,'Riesgo actual · % de cada umbral de alerta','bargauge',0,29,10,8,
         f"SELECT {DIM_NAME}||' · '||replace(symbol,'USDT','') AS \"Serie\",round((100*value/NULLIF(threshold,0))::numeric,0) AS \"% del umbral\" FROM cp_signal_board WHERE kind='forecast' ORDER BY 1",'percent',
         '100 % significa que el pronóstico alcanzó su umbral de alerta. Verde por debajo de 80 %, ámbar entre 80 % y 100 %, rojo desde 100 %.')
        p['options']={'displayMode':'basic','orientation':'horizontal','showUnfilled':True,'valueMode':'color','namePlacement':'left','sizing':'auto',
            'reduceOptions':{'values':True,'calcs':['lastNotNull'],'fields':''}}
        p['fieldConfig']['defaults'].update(min=0,max=150,thresholds={'mode':'absolute','steps':[{'color':GREEN,'value':None},{'color':AMBER,'value':80},{'color':RED,'value':100}]})
        p=panel(62,'Línea de tiempo · verde normal, ámbar vigilancia, rojo alerta','state-timeline',10,29,14,8,
         f"SELECT to_timestamp(as_of_ms/1000.0) AS time,{DIM_NAME}||' · '||replace(symbol,'USDT','') AS metric,CASE WHEN triggered AND severity='high' THEN 2 WHEN triggered THEN 1 ELSE 0 END AS value FROM market_signals WHERE kind='forecast' AND {LIVE} AND {TF} ORDER BY 1",
         description='Cada franja es una serie pronosticada. Permite ver de un vistazo cuándo y dónde subió el riesgo.')
        p['options']={'showValue':'never','mergeValues':True,'rowHeight':0.8,'alignValue':'left','legend':{'showLegend':False,'displayMode':'list','placement':'bottom'},'tooltip':{'mode':'single'}}
        p['fieldConfig']['defaults'].update(custom={'fillOpacity':85,'lineWidth':0},
            mappings=[{'type':'value','options':{'0':{'text':'NORMAL','color':GREEN},'1':{'text':'VIGILANCIA','color':AMBER},'2':{'text':'ALERTA','color':RED}}}],
            color={'mode':'thresholds'},thresholds={'mode':'absolute','steps':[{'color':GREEN,'value':None},{'color':AMBER,'value':1},{'color':RED,'value':2}]})
        row(63,'3 · Mercado y eventos empresariales',37)
        for id,symbol,x in [(64,'BTCUSDT',0),(65,'SOLUSDT',8)]:
            p=panel(id,f'{symbol[:3]} · velas de 1 minuto','candlestick',x,38,8,8,
             f"SELECT to_timestamp(open_ms/1000.0) AS time,open::double precision AS open,high::double precision AS high,low::double precision AS low,close::double precision AS close,volume::double precision AS volume FROM market_candles WHERE symbol='{symbol}' AND source_mode<>'replay' AND {TFO} ORDER BY open_ms",
             'suffix: USDT','Velas reales de Binance recibidas por Kafka. Verde: cierre mayor que la apertura; rojo: menor.')
            p['options']={'mode':'candles+volume','candleStyle':'candles','colorStrategy':'open-close','colors':{'up':GREEN,'down':RED},'includeAllFields':False,
                'legend':{'showLegend':False,'displayMode':'list','placement':'bottom'},'tooltip':{'mode':'single'}}
        colored(panel(45,'Flujo neto · compras menos ventas por minuto','timeseries',16,38,8,8,
         f"SELECT window_start AS time,replace(symbol,'USDT','')||' · flujo neto' AS metric,buy_usdt-sell_usdt AS value FROM trade_flow WHERE {TFW} ORDER BY 1",'currencyUSD',
         'Cada operación de Binance es un evento empresarial publicado en Kafka (market.trades.*). Spark agrupa por minuto con watermark de 1 min y deduplicación por event_id. Positivo: dominaron las compras agresivas.'))
        row(42,'4 · ¿Funcionan los modelos? · prueba 2026 y error en vivo',46)
        table(11,'Modelo contra referencia · prueba histórica y en vivo',47,6,
         f"""WITH v AS (SELECT dimension d,count(actual) n,avg(abs(forecast-actual)) m,avg(abs(baseline-actual)) b FROM predictions WHERE {LIVE} AND {TF} AND actual IS NOT NULL GROUP BY 1)
 SELECT CASE x.dimension WHEN 'volatility' THEN 'Volatilidad · Franck' WHEN 'crash' THEN 'Caída · Julmer' WHEN 'anomaly' THEN 'Actividad · Abdul' ELSE 'Separación · Milagros' END AS "Dimensión",
 CASE x.method WHEN 'random_forest' THEN 'Random Forest' WHEN 'logistic_regression' THEN 'Logística calibrada' WHEN 'ridge' THEN 'Ridge' ELSE x.method END AS "Modelo",
 CASE WHEN x.metrics ? 'pr_auc' THEN 'PR-AUC (más es mejor)' ELSE 'RMSE (menos es mejor)' END AS "Métrica prueba 2026",
 round(COALESCE((x.metrics->>'pr_auc')::numeric,(x.metrics->>'rmse')::numeric),3) AS "Modelo · prueba",
 round(COALESCE((b.metrics->>'pr_auc')::numeric,(b.metrics->>'rmse')::numeric),3) AS "Referencia · prueba",
 v.n AS "Evaluados en vivo",round(v.m::numeric,3) AS "MAE modelo · vivo",round(v.b::numeric,3) AS "MAE referencia · vivo",
 CASE WHEN v.m IS NULL THEN 'Madurando' WHEN v.m<0.98*v.b THEN 'Supera' WHEN v.m>1.02*v.b THEN 'Por debajo' ELSE 'Empate' END AS "En vivo"
 FROM model_metrics x JOIN model_metrics b ON b.dimension=x.dimension AND b.model_version=x.model_version AND b.split='test_baseline' LEFT JOIN v ON v.d=x.dimension
 WHERE x.split='test_deployed' AND x.model_version=(SELECT value FROM runtime_configuration WHERE key='active_model_version') ORDER BY x.dimension""",
         'Prueba enero–septiembre 2026, reservada. En vivo se usa el error absoluto medio del período elegido; es una muestra corta. Detalle completo en el tablero CryptoPulse · Detalle.')
        annotations=[
            {'name':'Cambio de versión del modelo','enable':False,'iconColor':BTC,'datasource':PG,
             'target':{'refId':'Anno','rawQuery':True,'format':'table','rawSql':"SELECT extract(epoch FROM registered_at)*1000 AS time,'Modelo activo: '||model_version AS text,'modelo' AS tags FROM model_versions WHERE $__timeFilter(registered_at)"}},
            {'name':'Alertas de mercado','enable':False,'iconColor':RED,'datasource':PG,
             'target':{'refId':'Anno','rawQuery':True,'format':'table','rawSql':f"SELECT as_of_ms AS time,'ALERTA · '||{DIM_NAME}||' · '||symbol AS text,'alerta' AS tags FROM market_signals WHERE triggered AND severity='high' AND {LIVE} AND {TF}"}}]
        return {'uid':'cryptopulse-main','title':'CryptoPulse · BTC y SOL','panels':panels,'annotations':{'list':annotations}}

    if kind=='detalle':
        head('Detalle de señales y evidencia')
        signal_table()
        history=f"""WITH events AS (SELECT to_timestamp(as_of_ms/1000.0) AS "Fecha",symbol AS "Activo",{DIM_NAME} AS "Dimensión",CASE kind WHEN 'observed' THEN 'Observada' ELSE 'Pronóstico' END AS "Origen",CASE severity WHEN 'high' THEN 'ALERTA' ELSE 'VIGILANCIA' END AS "Estado",round(value::numeric,3) AS "Valor",round(threshold::numeric,3) AS "Umbral",explanation AS "Detalle" FROM market_signals WHERE triggered AND {LIVE} AND {TF} ORDER BY as_of_ms DESC LIMIT 100)
 SELECT * FROM events UNION ALL SELECT NULL,'BTC / SOL','Todas','Estado',CASE WHEN (SELECT count(*) FROM cp_signal_board WHERE kind='forecast' AND age_seconds<=180)=7 THEN 'SIN CRUCES' ELSE 'REVISAR INFERENCIA' END,NULL,NULL,'No hay señales que superen umbrales en el período seleccionado.' WHERE NOT EXISTS(SELECT 1 FROM events)"""
        table(34,'Historial de cruces · período seleccionado',14,8,history,'Solo cruces reales. No se generan alertas artificiales para llenar esta tabla.')
        table(32,'Frescura y continuidad por activo',22,5,"SELECT symbol AS \"Activo\",status AS \"Estado\",round(candle_age_seconds,0) AS \"Edad vela · s\",context_rows AS \"Velas / 61\",missing_minutes AS \"Minutos faltantes\" FROM cp_asset_health ORDER BY symbol",w=12)
        p47=table(47,'Último minuto cerrado · operaciones',22,5,
         "SELECT DISTINCT ON (symbol) symbol AS \"Activo\",trades AS \"Operaciones\",round(buy_usdt::numeric,0) AS \"Compras USDT\",round(sell_usdt::numeric,0) AS \"Ventas USDT\",large_trades AS \"≥ 100k USDT\" FROM trade_flow ORDER BY symbol,window_start DESC",
         'Ventanas finalizadas por watermark: aparecen con 1–2 minutos de retraso respecto al reloj.',x=12,w=12)
        p47['fieldConfig']['defaults'].update(unit='locale',decimals=0)
        table(12,'En vivo · error real por activo',27,7,
         f"SELECT {DIM_NAME} AS \"Dimensión\",symbol AS \"Activo\",count(actual) AS \"Evaluadas\",count(*) FILTER(WHERE actual IS NULL) AS \"Madurando\",round(avg(abs(forecast-actual))::numeric,3) AS \"MAE modelo\",round(avg(abs(baseline-actual))::numeric,3) AS \"MAE referencia\" FROM predictions WHERE {LIVE} AND {TF} GROUP BY dimension,symbol ORDER BY dimension,symbol",
         'Solo la versión activa y el período elegido. Los horizontes todavía abiertos permanecen madurando.',w=12)
        p=table(99,'Actividad observada · referencia por hora UTC',27,7,"SELECT DISTINCT ON(symbol) symbol AS \"Activo\",round((metrics->>'quote5')::numeric,0) AS \"USDT · 5 min\",round((metrics->>'quote5_p95')::numeric,0) AS \"USDT · P95\",(metrics->>'trades5')::bigint AS \"Operaciones · 5 min\",round((metrics->>'trades5_p95')::numeric,0) AS \"Operaciones · P95\" FROM market_kpis WHERE symbol IN ('BTCUSDT','SOLUSDT') ORDER BY symbol,as_of_ms DESC",'P95 respecto del entrenamiento 2022–2024 para activo y hora UTC. No atribuye fraude.',x=12,w=12)
        p['fieldConfig']['defaults'].update(unit='locale',decimals=0)
        p=panel(9,'Correlación BTC / SOL · rendimientos 60 min','timeseries',0,34,12,8,f"SELECT to_timestamp(as_of_ms/1000.0) AS time,(metrics->>'correlation_60m')::double precision AS value FROM market_kpis WHERE symbol='BTC-SOL' AND {TF} ORDER BY 1",description='Pearson sobre rendimientos consecutivos de un minuto: −1 a +1. Correlación no implica causalidad.')
        p['fieldConfig']['defaults'].update(min=-1,max=1,color=fixed(PAIR),displayName='Correlación BTC–SOL')
        p=colored(panel(46,'Presión compradora · % del importe iniciado por compradores','timeseries',12,34,12,8,
         f"SELECT window_start AS time,symbol AS metric,100*buy_usdt/NULLIF(buy_usdt+sell_usdt,0) AS value FROM trade_flow WHERE {TFW} ORDER BY 1",'percent',
         '50 % es equilibrio. Valores sostenidos lejos de 50 % acompañan movimientos direccionales.'))
        return {'uid':'cryptopulse-detalle','title':'CryptoPulse · Detalle','panels':panels,'annotations':{'list':[]}}

    if kind in MEMBERS:
        m=MEMBERS[kind];dim=m['dim'];reg=m['kind']=='reg'
        back=' · <a href="/d/cryptopulse-main" style="color:#F2A65A">volver al tablero</a>'
        head(f"{m['name']} · cómo se obtiene: {m['title']}")
        def text(id,title,x,y,w,h,content,html=False):
            q=panel(id,title,'text',x,y,w,h)
            q['options']={'mode':'html' if html else 'markdown','content':content}
            return q
        row(100,'1 · La pregunta y el recorrido del dato',3)
        text(101,'¿Qué responde?',0,4,10,6,f"**{m['q']}**\n\n{m['why']}\n\n**Modelo:** {m['model']} · **Horizonte:** {m['horizon']} minutos")
        text(102,'¿Por dónde pasa el dato?',10,4,14,6,flow(m['color']),html=True)
        row(103,'2 · El dato que entra',10)
        table(104,'Últimas velas cerradas recibidas por Kafka',11,7,"SELECT replace(symbol,'USDT','') AS \"Activo\",to_timestamp(close_ms/1000.0) AS \"Cierre\",open::double precision AS \"Apertura\",high::double precision AS \"Máximo\",low::double precision AS \"Mínimo\",close::double precision AS \"Cierre USDT\",round(quote_asset_volume::numeric,0) AS \"Volumen USDT\",number_of_trades AS \"Operaciones\" FROM market_candles WHERE source_mode<>'replay' ORDER BY close_ms DESC,symbol LIMIT 8",'Cada fila viene de un mensaje real de market.klines.*, validado contra su contrato.',w=16)['fieldConfig']['defaults'].update(unit='locale')
        text(105,'Cómo llega',16,11,8,7,'**Tópicos:** `market.klines.btcusdt` y `market.klines.solusdt`\n\n**Frecuencia:** una vela por activo cada minuto\n\n**Contrato:** `market-kline-v1`. Lo que no lo cumple se rechaza.\n\n**Si cae:** se recupera por REST, sin inventar velas.')
        row(106,'3 · Cómo se calcula',18)
        text(107,'La lógica',0,19,10,8,m['how'])
        table(108,'Indicadores del último minuto',19,8,m['kpi'],'Valores reales guardados en cada cierre de minuto.',x=10,w=14)['fieldConfig']['defaults'].update(unit='locale',decimals=3)
        row(109,'4 · Qué predijo',27)
        q=panel(110,'Pronóstico actual como % de su umbral','stat',0,28,6,8,f"SELECT now() AS time,replace(symbol,'USDT','') AS metric,100*value/NULLIF(threshold,0) AS value FROM cp_signal_board WHERE kind='forecast' AND dimension='{dim}' ORDER BY symbol",'percent','100 % significa que alcanzó su umbral de alerta.')
        q['options']['textMode']='value_and_name';q['options']['orientation']='vertical'
        q['fieldConfig']['defaults'].update(decimals=0,thresholds={'mode':'absolute','steps':[{'color':'#24795C','value':None},{'color':AMBER,'value':80},{'color':RED,'value':100}]})
        series=[('pronóstico','forecast')]
        if reg: series=[('observada','observed'),('pronóstico','forecast'),('realidad futura','actual')]
        sql=' UNION ALL '.join(f"SELECT to_timestamp(as_of_ms/1000.0) AS time,replace(symbol,'USDT','')||' · {label}' AS metric,{col} AS value FROM predictions WHERE dimension='{dim}' AND {LIVE} AND {TF}"+(" AND actual IS NOT NULL" if col=='actual' else '') for label,col in series)+' ORDER BY 1'
        colored(panel(111,'Pronóstico en el tiempo','timeseries',6,28,18,8,sql,m['unit'],'Punteada: pronóstico. Continua: observada. Puntos: lo que pasó después.'))
        row(112,'5 · ¿Acertó?',36)
        if reg:
            table(113,'Últimos pronósticos ya comprobados',37,8,f"SELECT to_timestamp(as_of_ms/1000.0) AS \"Emitido\",replace(symbol,'USDT','') AS \"Activo\",round(forecast::numeric,3) AS \"Pronóstico\",round(actual::numeric,3) AS \"Realidad\",round(abs(forecast-actual)::numeric,3) AS \"Error modelo\",round(abs(baseline-actual)::numeric,3) AS \"Error referencia\" FROM predictions WHERE dimension='{dim}' AND {LIVE} AND actual IS NOT NULL ORDER BY as_of_ms DESC,symbol LIMIT 10",'Se comparan cuando madura el horizonte.',w=14)['fieldConfig']['defaults'].update(unit='locale',decimals=3)
            colored(panel(114,'Error del modelo y de la referencia','timeseries',14,37,10,8,f"SELECT to_timestamp(as_of_ms/1000.0) AS time,replace(symbol,'USDT','')||' · error modelo' AS metric,abs(forecast-actual) AS value FROM predictions WHERE dimension='{dim}' AND {LIVE} AND {TF} AND actual IS NOT NULL UNION ALL SELECT to_timestamp(as_of_ms/1000.0),replace(symbol,'USDT','')||' · error referencia',abs(baseline-actual) FROM predictions WHERE dimension='{dim}' AND {LIVE} AND {TF} AND actual IS NOT NULL ORDER BY 1",'','Continua: error del modelo. Punteada: error de la referencia. Más abajo es mejor.'))
        else:
            table(113,'Últimas probabilidades ya comprobadas',37,8,f"SELECT to_timestamp(as_of_ms/1000.0) AS \"Emitido\",replace(symbol,'USDT','') AS \"Activo\",round(100*forecast::numeric,1) AS \"Probabilidad %\",round(100*baseline::numeric,1) AS \"Referencia %\",CASE WHEN alert THEN 'Sí' ELSE 'No' END AS \"¿Alertó?\",CASE WHEN actual>=1 THEN 'Sí' ELSE 'No' END AS \"¿Ocurrió?\" FROM predictions WHERE dimension='{dim}' AND {LIVE} AND actual IS NOT NULL ORDER BY as_of_ms DESC,symbol LIMIT 10",'Se comprueban cuando madura el horizonte.',w=14)['fieldConfig']['defaults'].update(unit='none',decimals=1)
            table(114,'Aciertos y errores en vivo · período elegido',37,8,f"SELECT replace(symbol,'USDT','') AS \"Activo\",count(*) FILTER(WHERE alert AND actual>=1) AS \"Alertó y ocurrió\",count(*) FILTER(WHERE alert AND actual<1) AS \"Falsa alarma\",count(*) FILTER(WHERE NOT alert AND actual>=1) AS \"No alertó y ocurrió\",count(*) FILTER(WHERE NOT alert AND actual<1) AS \"Sin alerta y no ocurrió\" FROM predictions WHERE dimension='{dim}' AND {LIVE} AND {TF} AND actual IS NOT NULL GROUP BY symbol ORDER BY symbol",'Conteo real de pronósticos ya madurados. Con pocas horas la muestra es corta.',x=14,w=10)
        row(115,'6 · Validación, evolución y límite',45)
        keys="ARRAY['rmse','mae']" if reg else "ARRAY['pr_auc','brier','precision','recall']"
        table(116,'Prueba 2026 · modelo contra referencia',46,7,f"SELECT CASE k WHEN 'rmse' THEN 'RMSE (menos es mejor)' WHEN 'mae' THEN 'MAE (menos es mejor)' WHEN 'pr_auc' THEN 'PR-AUC (más es mejor)' WHEN 'brier' THEN 'Brier (menos es mejor)' WHEN 'precision' THEN 'Precisión en el umbral' ELSE 'Recall en el umbral' END AS \"Métrica\",round((x.metrics->>k)::numeric,3) AS \"Modelo\",round((b.metrics->>k)::numeric,3) AS \"Referencia\" FROM unnest({keys}) k CROSS JOIN model_metrics x JOIN model_metrics b ON b.dimension=x.dimension AND b.model_version=x.model_version AND b.split='test_baseline' WHERE x.dimension='{dim}' AND x.split='test_deployed' AND x.model_version=(SELECT value FROM runtime_configuration WHERE key='active_model_version')",'Prueba reservada de enero a septiembre de 2026, usada una sola vez.',w=9)['fieldConfig']['defaults'].update(unit='none')
        table(117,'En vivo · por activo',46,7,f"SELECT replace(symbol,'USDT','') AS \"Activo\",count(*) AS \"Evaluados\",round(avg(abs(forecast-actual))::numeric,3) AS \"MAE modelo\",round(avg(abs(baseline-actual))::numeric,3) AS \"MAE referencia\" FROM predictions WHERE dimension='{dim}' AND {LIVE} AND {TF} AND actual IS NOT NULL GROUP BY symbol ORDER BY symbol",'Solo el período elegido. Es una muestra corta.',x=9,w=7)['fieldConfig']['defaults'].update(unit='none')
        text(118,'De U1 a U2 y límite',16,46,8,7,f"**U1:** {m['u1']}\n\n**U2:** el mismo tipo de modelo trabaja en vivo y se evalúa solo.\n\n**Límite real:** {m['limit']}")
        return {'uid':'cryptopulse-'+kind,'title':f"CryptoPulse · {m['name']} · cómo se obtiene",'panels':panels,'annotations':{'list':[]},'member':True}

    head('Operación del pipeline')
    row(70,'Salud del pipeline · de Binance a Grafana',3)
    for id,title,x,expr,desc in [
        (71,'Binance → velas',0,'cryptopulse_producer_connected','WebSocket de velas cerradas conectado.'),
        (72,'Binance → operaciones',4,'cryptopulse_trades_producer_connected','WebSocket aggTrade conectado.'),
        (73,'Kafka',8,'min(kafka_brokers) >= bool 1','Broker disponible según kafka-exporter.'),
        (74,'Spark Streaming',12,'cryptopulse_stream_heartbeat_age_seconds < bool 60','Señal de vida del driver con menos de 60 s.'),
        (75,'PostgreSQL y exportador',16,'up{job="cryptopulse"}','El exportador consulta PostgreSQL y responde a Prometheus.'),
        (76,'Producto',20,'cryptopulse_product_ready','LISTO: datos continuos y siete pronósticos recientes.')]:
        status(id,title,x,4,4,expr,desc)
    # Las reglas viven en Prometheus; se leen con PromQL (ALERTS) para no depender del ruler de Grafana.
    p=panel(77,'Alertas disparadas ahora','stat',0,8,6,5,'count(ALERTS{alertstate="firing"}) or vector(0)','short',
        'Cuántas reglas de observability/alerts.yml están disparadas en este momento. 0 significa operación normal.',prom=True)
    p['fieldConfig']['defaults']['thresholds']={'mode':'absolute','steps':[{'color':GREEN,'value':None},{'color':RED,'value':1}]}
    p=panel(79,'Reglas evaluadas por Prometheus','stat',6,8,6,5,'sum(prometheus_rule_group_rules)','short',
        'Alertas operativas más reglas de grabación cargadas desde observability/alerts.yml.',prom=True)
    p['fieldConfig']['defaults']['thresholds']['steps'][0]['color']=NAVY_2
    p=panel(80,'Detalle de alertas disparadas','table',0,13,12,5,description='Nombre, severidad y resumen de cada alerta activa. Vacía cuando todo está normal.')
    p['datasource']=PROM
    p['targets']=[dict(refId='A',expr='ALERTS{alertstate="firing"}',instant=True,format='table',legendFormat='')]
    p['fieldConfig']['defaults']['noValue']='Sin alertas disparadas: todas las reglas están en estado normal.'
    p['transformations']=[{'id':'organize','options':{'excludeByName':{'Time':True,'Value':True,'__name__':True,'alertstate':True,'instance':True,'job':True},
        'renameByName':{'alertname':'Alerta','severity':'Severidad','query':'Consulta','topic':'Tópico','symbol':'Activo'}}}]
    p=panel(78,'Kafka · mensajes por minuto por tópico','timeseries',12,8,12,10,'cryptopulse:kafka_mensajes_por_minuto','short',
        'Regla de grabación de Prometheus: tasa de 5 minutos de los offsets, llevada a mensajes por minuto. Las operaciones son ~99 % del volumen.',prom=True,legend='{{topic}}')
    o=p['fieldConfig']['overrides']
    for pattern,color in [('.*btcusdt$',BTC),('.*solusdt$',SOL)]:
        o.append({'matcher':{'id':'byRegexp','options':pattern},'properties':[{'id':'color','value':fixed(color)}]})
    o.append({'matcher':{'id':'byRegexp','options':'^market\\.klines.*'},'properties':[{'id':'custom.lineStyle','value':{'fill':'dash','dash':[10,6]}}]})
    def graded(p,amber,red):
        p['fieldConfig']['defaults']['thresholds']={'mode':'absolute','steps':[{'color':'#24795C','value':None},{'color':AMBER,'value':amber},{'color':RED,'value':red}]}
        return p
    row(43,'Procesamiento · Spark y Kafka',18)
    graded(panel(14,'Spark · edad de señal de vida','stat',0,19,6,4,'cryptopulse_stream_heartbeat_age_seconds','s','Verde hasta 30 s. Más de 60 s degrada el producto.',prom=True),30,60)
    graded(panel(15,'Kafka · eventos pendientes','stat',6,19,6,4,'cryptopulse:lag_total','short','Un lote normal de 15 s ya trae cientos de operaciones. Ámbar desde 2 000 y rojo desde 5 000 en total.',prom=True),2000,5000)
    p=panel(16,'Costo estimado · sin facturación','stat',12,19,6,4,'cryptopulse_estimated_monthly_cost_usd','currencyUSD','Hipótesis editables; no es cobro ni cotización. CPU, memoria, disco y horas configurados.',prom=True)
    p['fieldConfig']['defaults'].update(decimals=2)
    p=panel(1,'Histórico limpio · velas','stat',18,19,6,4,'SELECT now() AS time,sum(candles)::double precision AS value FROM batch_kpis','locale','2022-01 a 2026-09. Archivos públicos con SHA256. Dos registros inválidos excluidos.')
    p['fieldConfig']['defaults'].update(decimals=0)
    p=panel(17,'Spark · duración de micro-lotes (intervalo 15 s)','timeseries',0,23,12,7,'cryptopulse_batch_duration_seconds','s','Comparar duración con intervalo de 15 s. Los lotes de recuperación pueden excederlo.',prom=True,legend='{{query}}')
    # Eje fijo hasta 60 s: un lote de recuperación muy largo no debe ocultar el comportamiento normal.
    p['fieldConfig']['defaults'].update(min=0,max=60)
    p['fieldConfig']['defaults']['custom'].update(thresholdsStyle={'mode':'line'})
    p['fieldConfig']['defaults']['thresholds']={'mode':'absolute','steps':[{'color':'transparent','value':None},{'color':RED,'value':15}]}
    p=panel(18,'Kafka · avance acumulado por tópico','timeseries',12,23,12,7,'sum by(topic) (kafka_topic_partition_current_offset{topic=~"market.(klines|trades).*"})','short','Suma de offsets. Punteado: velas; continuo: operaciones.',prom=True)
    for pattern,color in [('.*btcusdt.*',BTC),('.*solusdt.*',SOL)]:
        p['fieldConfig']['overrides'].append({'matcher':{'id':'byRegexp','options':pattern},'properties':[{'id':'color','value':fixed(color)}]})
    p['fieldConfig']['overrides'].append({'matcher':{'id':'byRegexp','options':'^market\\.klines.*'},'properties':[{'id':'custom.lineStyle','value':{'fill':'dash','dash':[10,6]}}]})
    row(44,'Eventos empresariales y ventanas',30)
    graded(panel(49,'Productor de operaciones · edad','stat',0,31,4,5,'cryptopulse_trades_heartbeat_age_seconds','s','Más de 60 s degrada el producto y dispara una alerta.',prom=True),30,60)
    graded(panel(50,'Última ventana · edad','stat',4,31,4,5,'cryptopulse_trade_flow_age_seconds','s','Más de 300 s degrada el producto.',prom=True),180,300)
    graded(panel(51,'Operaciones pendientes','stat',8,31,4,5,'sum(cryptopulse_kafka_checkpoint_lag{topic=~"market.trades.*"})','short','Ámbar desde 2 000 y rojo desde 5 000, igual que la alerta.',prom=True),2000,5000)
    table(35,'Ventanas finalizadas · cobertura real',31,5,"SELECT CASE kind WHEN 'fixed' THEN 'Fija' ELSE 'Deslizante' END AS \"Ventana\",symbol AS \"Activo\",max(window_end) AS \"Último cierre\",count(*) AS \"Ventanas\",count(*) FILTER(WHERE candles<>5) AS \"Incompletas\" FROM stream_windows GROUP BY kind,symbol ORDER BY kind,symbol",'Fijas 5 min y deslizantes 5 min/paso 1 min. Watermark 2 min: una ventana finalizada puede estar incompleta.',x=12,w=12)
    return {'uid':'cryptopulse-ops','title':'CryptoPulse · Operación','panels':panels,'annotations':{'list':[]}}

kind=sys.argv[1] if len(sys.argv)>1 else 'main'
board=build(kind)
links=[{'title':'Tableros CryptoPulse','type':'dashboards','tags':['cryptopulse'],'asDropdown':False,'includeVars':False,'keepTime':True},
       {'title':'Estado técnico JSON','type':'link','url':'http://localhost:48000/api/status','targetBlank':True},
       {'title':'Kafka UI','type':'link','url':'http://localhost:48085','targetBlank':True},
       {'title':'Prometheus','type':'link','url':'http://localhost:49090/alerts','targetBlank':True}]
member=board.pop('member',False)
if member:
    links=[{'title':'← Volver al tablero','type':'link','url':'/d/cryptopulse-main','targetBlank':False}]
dashboard={**board,'tags':['cryptopulse-integrante'] if member else ['cryptopulse','bigdata','risk-monitoring'],'schemaVersion':40,'version':4,'refresh':'10s','timezone':'browser',
    'time':{'from':'now-3h','to':'now'},'editable':True,'graphTooltip':1,'links':links}
print(json.dumps(dashboard,ensure_ascii=False,indent=2))
