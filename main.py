#To implement:
# 1) portfolio performance
# 2) stock images for title screen
# 3) start with 1m defult button green

from cmu_graphics import *
import pandas as pd
import pandas_datareader.data as web
import datetime as dt
from datetime import date
from dateutil.relativedelta import relativedelta
import yfinance as yf
from pygooglenews import GoogleNews

class Button: #class for stock buttons main and analysis screen
    def __init__(self, stock, x, y, width, height, fill):
        self.stock = stock
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.fill = fill
        self.selected = -1
class dateButton: #class for graph date buttons
    def __init__(self, weeks, months, x, y, width, height, selected=-1):
        self.weeksBack = weeks
        self.monthsBack = months
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.fill = None
        self.selected = selected
class statButton: #class for RSI and MACD buttons for analysis screen
    def __init__(self, x, y, metric):
        self.x = x
        self.y = y
        self.width = 200
        self.height = 70
        self.metric = metric
        self.selected = -1

def onAppStart(app):
    app.stockDict = {'MSFT': 'Microsoft', 'AAPL': 'Apple', 'AMZN': 'Amazon', 
                     'JPM': 'JP Morgan', 'TSLA': 'Tesla', 'AVGO': 'Broadcom',
                     'LLY': 'Eli Lilly', 'BRK-B': 'Berkshire Hathaway'}
    app.height = 800
    app.width = 1000
    app.cx = app.width/2
    app.cy = app.height/2
    app.stock = None
    app.screen = 0
    app.setMaxShapeCount(10**10)
    #variable for title screen
    app.loadbar = 1
    #variables for graphing
    app.datapoints = []
    app.plotpoints = []
    app.highs = []
    app.lows = []
    app.data = None #dict
    app.stockButtons = []
    app.dateButtons = []
    app.loading = 0
    app.todayM, app.todayD, app.todayY = getTodayDate(app)
    #variables for analysis
    app.statButtons = []
    app.metric = None

def redrawAll(app):
    if app.screen == 0:
        drawTitleScreen(app)
    if app.screen == 1:
        drawMainScreen(app)
    if app.screen == 2:
        drawAnalysisScreen(app)
    # if app.screen == 3:
    #     drawPortfolioScreen(app)

#Title screen code
def drawTitleScreen(app):
    drawRect(0, 0, app.width, app.height, fill='black')
    logosize = (0.15)*app.width
    drawLogo(app, app.cx, (1/6)*app.height, logosize)
    if app.loadbar < (5/8*app.width):
        drawLoadingBar(app)
    if app.loadbar >= (5/8)*app.width:
        drawRect(225,(13/16)*app.height-25, 250, 50, fill='green', opacity=50, 
                 border='green', borderWidth=5)
        drawLabel('View Market Data', 350, (13/16)*app.height, size=16, fill='white')
        drawRect(525, (13/16)*app.height-25, 250, 50, fill='green', opacity=50,
                 border='green', borderWidth=5)
        drawLabel('Track Portfolio Performance', 650, (13/16)*app.height, 
                  size=16, fill='white')

def drawLogo(app, cx, cy, size):
    textCenter = cx+size - (15/35)*size
    rectHeight, rectWidth, rectTop = 0.75*size, 0.25*size, cy - (7/20)*size
    rectGLeft, rectRLeft = (cx-((15/35)*size) - (42.5/20)*size, 
                            cx-((15/35)*size) - (32.5/20)*size)
    triHeight, triWidth = 0.3*size, (10.5/20)*size
    triGMid, triRMid = ((rectGLeft + rectGLeft+rectWidth)/2, 
                        (rectRLeft + rectRLeft+rectWidth)/2)
    rBaseY, rLeftX = cy + (7/20)*size, triRMid - triWidth/2
    gBaseY, gLeftX = cy - (7/20)*size + 1, triGMid - triWidth/2
    drawLabel('2 Finance', textCenter, cy, bold=True, fill='green', size=size, 
              font='cinzel')
    drawRect(rectGLeft, rectTop, rectWidth, rectHeight, fill='green')
    drawPolygon(gLeftX, gBaseY, triGMid, gBaseY-triHeight, gLeftX+triWidth, gBaseY, 
                fill='green')
    drawRect(rectRLeft, rectTop, rectWidth, rectHeight, fill='red')
    drawPolygon(rLeftX, rBaseY, triRMid, rBaseY+triHeight, rLeftX+triWidth, rBaseY,
                fill='red')

def drawLoadingBar(app):
    barWidth = (5/8)*app.width
    barY = (13/16)*app.height
    barHeight = (0.05)*app.width
    loadbarLeft = app.cx - barWidth/2
    loadbarTop  = barY - barHeight/2
    drawRect(app.cx, barY, barWidth, barHeight, align='center', border='white')
    drawLabel('Loading Data...', app.cx, barY - 42.5, align='center', size = 16, fill = 'white')
    drawRect(loadbarLeft, loadbarTop, app.loadbar, barHeight, border='white', fill='cyan')

#Main screen code
def drawMainScreen(app):
    drawRect(0, 0, 2*app.width, 180, align='center', fill='black')
    drawDateButtons(app)
    drawAxis(app)
    drawLogo(app, 160, 45, 35)
    drawButtons(app)
    drawRect(910, 45, 150, 60, align='center', fill='green', opacity=50, 
                border='green', borderWidth=5)
    drawLabel('Portfolio', 910, 45, fill='white', size=22)
    if app.stock == None:
        drawLabel('Choose a stock', app.cx, 45, fill='white', size=30)
        pass
    else:
        drawLabel(f'{app.stockDict[app.stock]}', app.cx, 45, fill='white', size=35)
        drawAxis(app)
        drawCandles(app)
        drawRect(745, 45, 150, 60, align='center', fill='green', opacity=50, 
                border='green', borderWidth=5)
        drawLabel('Analysis', 745, 45, fill='white', size=22)
        drawStats(app)

def createStockButtons(app): #create stock buttons and add to app.stockButtons
    msft = Button('MSFT', 60, 120, 200, 70, None)
    app.stockButtons.append(msft)
    aapl = Button('AAPL', 60, 200, 200, 70, None)
    app.stockButtons.append(aapl)
    amzn = Button('AMZN', 60, 280, 200, 70, None)
    app.stockButtons.append(amzn)
    jpm = Button('JPM', 60, 360, 200, 70, None)
    app.stockButtons.append(jpm)
    tsla = Button('TSLA', 60, 440, 200, 70, None)
    app.stockButtons.append(tsla)
    avgo = Button('AVGO', 60, 520, 200, 70, None)
    app.stockButtons.append(avgo)
    lly = Button('LLY', 60, 600, 200, 70, None)
    app.stockButtons.append(lly)
    brk = Button('BRK-B', 60, 680, 200, 70, None)
    app.stockButtons.append(brk)

def drawAxis(app): #create chart axis
    drawLine(350, 605, 950, 605)
    drawLabel('Price', 327.5, 405, rotateAngle=-90, size=18)
    drawLine(350, 605, 350, 205)
    drawLabel(f'{app.todayM}-{app.todayD}', 930, 620, size=18)

def getOpenHighLowCloseVol(app, stock, period):
    result = dict()
    ticker = yf.Ticker(stock)
    temp = ticker.history(period=period)
    df = temp.drop(columns=['Dividends', 'Stock Splits'])
    df['Volume'] = df['Volume'].round().astype(int)
    values = df.values.tolist()
    counter = 0
    for index, row in df.iterrows():
        result[str(index)[:10]] = values[counter]
        counter += 1
    return result
#^get financial info from inputed timeframe
def drawCandles(app): #plot candlesticks
    priceMin = min(app.lows) - 5
    priceMax = max(app.highs) + 5
    yScale = abs(priceMax-priceMin)/400 #price each pixel in y-axis represents
    graphX = 350
    graphLength = 600
    graphY = 605
    candleWidth = (graphLength/len(app.plotpoints) - 
                   (graphLength/len(app.plotpoints)/10))
    candleX = graphX + candleWidth/2 + 5
    for datapoint in app.plotpoints:
        open = datapoint[0]
        high = datapoint[1]
        low = datapoint[2]
        close = datapoint[3]
        volume = datapoint[4]
        openY = graphY-((open-priceMin)/yScale)
        highY = graphY-((high-priceMin)/yScale)
        lowY = graphY-((low-priceMin)/yScale)
        closeY = graphY-((close-priceMin)/yScale)
        if close > open:
            drawLine(candleX, highY, candleX, closeY)
            drawLine(candleX, lowY, candleX, openY)
            drawRect(candleX-candleWidth/2, closeY, candleWidth, 
                     abs(closeY-openY), fill = 'green')
            candleX += graphLength/len(app.plotpoints)
        elif open > close:
            drawLine(candleX, highY, candleX, openY)
            drawLine(candleX, lowY, candleX, closeY)
            drawRect(candleX-candleWidth/2, openY, candleWidth, 
                     abs(closeY-openY), fill = 'red')
            candleX += graphLength/len(app.plotpoints)
    drawPrices(app)


def drawPrices(app): #draw dynamic prices on chart
    drawLabel(f'{int(min(app.lows))}', 327.5, 597.5, size=18)
    drawLabel(f'{int(max(app.highs))}', 327.5, 212.5, size=18)

def drawButtons(app): #draw stock buttons on left side of screen
    createStockButtons(app)
    for button in app.stockButtons:
        drawRect(button.x, button.y, button.width, button.height, 
                    border='black', borderWidth=4, fill=None)
        if button.selected == True:
            drawRect(button.x, button.y, button.width, button.height, 
                    border='black', borderWidth=4, fill='green')
    drawLabels(app)

def drawLabels(app): #draw stock names for stock buttons
    drawLabel('Microsoft (MSFT)', 160, 155, align='center', size=17)
    drawLabel('Apple (AAPL)', 160, 235, align='center', size=17)
    drawLabel('Amazon (AMZN)', 160, 315, align='center', size=17)
    drawLabel('JP Morgan Chase & Co', 160, 385, align='center', size=15)
    drawLabel('(JPM)', 160, 405, align='center', size=15)
    drawLabel('Tesla (TSLA)', 160, 475, align='center', size=17)
    drawLabel('Broadcom Inc (AVGO)', 160, 555, align='center', size=17)
    drawLabel('Eli Lilly and Co (LLY)', 160, 635, align='center', size=17)
    drawLabel('Berkshire Hathaway', 160, 705, align='center', size=15)
    drawLabel('(BRK-B)', 160, 725, align='center', size=15)

def getTodayDate(app):
    today = str(date.today())
    year = int(today[:4])
    month = int(today[5:7])
    day = int(today[8:])
    return month, day, year

def getStartDate(weeks, months):
    today = date.today()
    if weeks == 0:
        result = str(today - relativedelta(months=months))
        return (int(result[5:7]), int(result[8:]), int(result[:4]))
    elif months == 0:
        result = str(today - relativedelta(weeks=weeks))
        return (int(result[5:7]), int(result[8:]), int(result[:4]))

def createDateButtons(app): #create buttons to change chart timeframe
    oneY = dateButton(0, 12, 405, 125, 100, 50)
    app.dateButtons.append(oneY)
    sixM = dateButton(0, 6, 538+(1/3), 125, 100, 50)
    app.dateButtons.append(sixM)
    oneM = dateButton(0, 1, 671+(2/3), 125, 100, 50)
    # oneM.selected = 1
    app.dateButtons.append(oneM)
    oneW = dateButton(1, 0, 805, 125, 100, 50)
    app.dateButtons.append(oneW)

def drawDateButtons(app): #draw buttons to change chart timeframe
    createDateButtons(app)
    for button in app.dateButtons:
        drawRect(button.x, button.y, button.width, button.height, fill=button.fill,
                 border='black', borderWidth=2.5)
        if button.selected == True and app.stock != None:
            drawRect(button.x, button.y, button.width, button.height, fill='green',
                 border='black', borderWidth=2.5)
    drawLabel('1Y', 455, 150, size=22)
    drawLabel('6M', 588+(1/3), 150, size=22)
    drawLabel('1M', 721+(2/3), 150, size=22)
    drawLabel('1W', 855, 150, size=22)

def drawStats(app): #draw financial info under chart
    drawRect(372.5, 645, 170, 80, fill=None, border='black', borderWidth=2.5)
    drawRect(565, 645, 170, 80, fill=None, border='black', borderWidth=2.5)
    drawRect(757.5, 645, 170, 80, fill=None, border='black', borderWidth=2.5)
    drawLabel('Volume:', 457.5, 665, size=20)
    drawLabel('Market Cap:', 650, 665, size=20)
    drawLabel('PE Ratio (TTM):', 842.5, 665, size=20)
    stock = yf.Ticker(app.stock)
    vol = stock.info['volume'] / 10**6 #in millions
    mc = stock.info['marketCap'] / 10**12 #in trillions
    pe = stock.info['trailingPE']
    drawLabel(f'{pythonRound(vol, 1)} M', 457.5, 700, size=20)
    drawLabel(f'{pythonRound(mc, 2)} T', 650, 700, size=20)
    drawLabel(f'{pythonRound(pe, 2)}', 842.5, 700, size=20)

#Analysis screen code
def drawAnalysisScreen(app):
    drawRect(0, 0, 2*app.width, 180, align='center', fill='black')
    drawLogo(app, 160, 40, 40)
    drawButtons(app)
    try:
        drawLabel(f'{app.stockDict[app.stock]}', 629.5, 140, size=40)
    except:
        drawLabel('None', 629.5, 140, size=40)
    drawRect(745, 45, 150, 60, align='center', fill='green', opacity=50, 
                border='green', borderWidth=5)
    drawLabel('Market Data', 745, 45, fill='white', size=22)
    drawRect(910, 45, 150, 60, align='center', fill='green', opacity=50, 
                border='green', borderWidth=5)
    drawLabel('Portfolio', 910, 45, fill='white', size=22)
    drawStatButtons(app)
    drawRating(app)
    drawHeadlines(app)

def createStatButtons(app): #create RSI and MACD buttons
    rsi = statButton(370+(1/3), 195, 'RSI')
    app.statButtons.append(rsi)
    macd = statButton(688+(2/3), 195, 'MACD')
    app.statButtons.append(macd)

def drawStatButtons(app): #draw RSI and MACD buttons
    createStatButtons(app)
    for sb in app.statButtons:
        if sb.selected == 1:
            drawRect(sb.x, sb.y, sb.width, sb.height, border='black', borderWidth=5, 
                     fill='green')
        elif sb.selected == -1:
            drawRect(sb.x, sb.y, sb.width, sb.height, border='black', borderWidth=5, 
                     fill=None)
    drawLabel('RSI', 470+(1/3), 230, size=24)
    drawLabel('MACD', 788+(2/3), 230, size=24)

def drawRating(app): #draw RSI and MACD values
    drawRect(529.5, 295, 200, 120, fill=None,
             border='black', borderWidth=5)
    if app.metric == None:
        drawLabel('Rating:', 629.5, 320, size=22)
    elif app.metric == 'RSI':
        result, color = getRSI(app, app.stock)
        drawLabel(f'RSI: {pythonRound(result, 2)}', 629.5, 320, size=20)
        if color == 'green':
            drawLabel('BUY', 629.5, 370, fill=color, size=30, bold=True)
        elif color == 'grey':
            drawLabel('HOLD', 629.5, 370, fill=color, size=30, bold=True)
        elif color == 'red':
            drawLabel('SELL', 629.5, 370, fill=color, size=30, bold=True)
    elif app.metric == 'MACD':
        result, color = getMACD(app, app.stock)
        drawLabel(f'MACD: {result}', 629.5, 320, size=18)
        if color == 'green':
            drawLabel('BUY', 629.5, 370, fill=color, size=30, bold=True)
        elif color == 'grey':
            drawLabel('HOLD', 629.5, 370, fill=color, size=30, bold=True)
        elif color == 'red':
            drawLabel('SELL', 629.5, 370, fill=color, size=30, bold=True)

def drawHeadlines(app): #grab and draw news headlines
    if app.stock == None:
        drawLabel('Headlines', 629.5, 487.5, size=28)
        drawLine(314.5, 487.5, 550, 487.5, lineWidth=5)
        drawLine(944.5, 487.5, 705, 487.5, lineWidth=5)
    else:
        drawLabel(f'{app.stock} Headlines', 629.5, 487.5, size=28)
    drawLine(314.5, 487.5, 314.5, 747.5, lineWidth=5)
    drawLine(314.5, 747.5, 944.5, 747.5, lineWidth=5)
    drawLine(944.5, 747.5, 944.5, 487.5, lineWidth=5)
    drawLine(314.5, 487.5, 510, 487.5, lineWidth=5)
    drawLine(944.5, 487.5, 750, 487.5, lineWidth=5)
    gn = GoogleNews()
    try:
        news = gn.search(query=f'{app.stockDict[app.stock]}', helper=True)
        headlines = []
        for item in news['entries']:
            if len(headlines) < 3:
                headlines.append(item['title'])
        headlineY = 530
        for item in headlines:
            dashIndex = item.find(' - ')
            headline = item[:dashIndex]
            if headline[-1] == '.':
                headline = headline[:-1]
            publisher = item[dashIndex+3:]
            if len(headline) > 130:
                drawLabel(f'- {headline[:65]}-', 325, headlineY, align='left', size=18)
                headlineY += 30
                drawLabel(f'- {headline[65:130]}-', 325, headlineY, align='left', size=18)
                headlineY += 30
                drawLabel(f'  {headline[130:]}, per: {publisher}', 325, headlineY, 
                align='left', size=18)
                headlineY += 30
            elif len(headline) > 65:
                drawLabel(f'- {headline[:65]}-', 325, headlineY, align='left', size=18)
                headlineY += 30
                drawLabel(f'  {headline[65:]}, per: {publisher}', 325, headlineY, 
                align='left', size=18)
                headlineY += 30
            else:
                drawLabel(f'- {headline}, ', 325, headlineY, size=18, align='left')
                headlineY += 30
                drawLabel(f'  per: {publisher}', 325, headlineY, size=18, align='left')
                headlineY += 30
    except:
        return

def getRSI(app, stock): #calculate RSI and return rating
    df = close60Day(app, stock)
    change = df['PriceChange']
    df = df.drop(columns=['PriceChange'])
    changeUp = change.copy()
    changeDown = change.copy()
    changeUp[changeUp<0] = 0 #set all negative changes to 0
    changeDown[changeDown>0] = 0 #set all positive changes to 0
    df['Gain'] = changeUp
    df['Loss'] = changeDown
    df['EMA Gain'] = df['Gain'].ewm(span=14, min_periods=14).mean()
    df['EMA Loss'] = df['Loss'].ewm(span=14, min_periods=14).mean()
    df['RS'] = abs(df['EMA Gain'] / df['EMA Loss'])
    df['RSI'] = 100 - (100 / (df['RS'] + 1))
    currRSI = df.loc[df.index[-1], 'RSI']
    if currRSI >= 65:
        return currRSI, 'red'
    elif currRSI >= 40 and currRSI < 65:
        return currRSI, 'grey'
    elif currRSI < 40:
        return currRSI, 'green'
#used this formula in calculations: https://www.macroption.com/rsi-calculation/ 
#but coded it into python myself

def getMACD(app, stock): #calculate MACD and return rating
    df = close60Day(app, stock)
    df = df.drop(columns=['Open', 'PriceChange'])
    df['EMA12'] = df['Close'].ewm(span=12).mean()
    df['EMA26'] = df['Close'].ewm(span=26).mean()
    df['MACD'] = df['EMA12'] - df['EMA26']
    df['Signal'] = df['MACD'].ewm(span=9).mean()
    for i in range(2, 8):
        lr = df.iloc[-1]
        slr = df.iloc[-i]
        if (slr['Signal'] > lr['Signal'] and slr['MACD'] < lr['MACD']):
            # MACD about to cross above signal so BUY
            return 'Cross Above', 'green'
        elif (slr['Signal'] < lr['Signal'] and slr['MACD'] > lr['MACD']):
            #MACD about to cross below signal so SELL
            return 'Cross Below', 'red'
        else: #No crossing upcoming, HOLD
            continue
    return 'No Cross', 'grey'
#used this formula: https://www.investopedia.com/terms/m/macd.asp
#but coded into python myself

def close60Day(app, stock): #create df of close and change in price for last 60 days
    ticker = yf.Ticker(stock)
    temp = ticker.history(period='1mo')
    df = temp.drop(columns=['High', 'Low', 'Volume','Dividends', 'Stock Splits'])
    change = df['Close'].diff()
    df['PriceChange'] = change
    return df

def onStep(app):
    if app.loadbar <= (5/8)*app.width:
        app.loadbar += 15

def onMousePress(app, mouseX, mouseY):
    if app.screen == 0: #title screen
        if isIn(app, mouseX, mouseY, 225,(13/16)*app.height-25, 250, 50):
            app.screen = 1
        elif isIn(app, mouseX, mouseY, 525, (13/16)*app.height-25, 250, 50):
            app.screen = 3
    elif app.screen == 1: #main screen
        if isIn(app, mouseX, mouseY, 835, 15, 150, 60):
            app.screen = 3
        if isIn(app, mouseX, mouseY, 645, 15, 150, 60):
            app.screen = 2
        for db in app.dateButtons:
            if isIn(app, mouseX, mouseY, db.x, db.y, db.width, db.height):
                daysBack = db.weeksBack*7 + db.monthsBack*30
                app.plotpoints = app.datapoints[-daysBack:]
                app.highs = []
                app.lows = []
                for datapoint in app.plotpoints:
                    high = datapoint[1]
                    low = datapoint[2]
                    app.highs.append(high)
                    app.lows.append(low)
                for others in app.dateButtons: #toggle selected button
                    others.selected = -1
                db.selected = -db.selected
        for button in app.stockButtons:
            if isIn(app, mouseX, mouseY, button.x, button.y, button.width, button.height):
                app.stock = button.stock
                try:
                    app.data = getOpenHighLowCloseVol(app, app.stock, '1y')
                    app.datapoints = []
                    app.highs = []
                    app.lows = []
                    for date in app.data:
                        app.datapoints.append(app.data[date])
                    app.plotpoints = app.datapoints[-30:]
                    for datapoint in app.plotpoints:
                        high = datapoint[1]
                        low = datapoint[2]
                        app.highs.append(high)
                        app.lows.append(low)
                except:
                    pass
                for others in app.stockButtons: #toggle selected button
                    others.selected = -1
                button.selected = -button.selected
                for db in app.dateButtons:
                    db.selected = -1
    elif app.screen == 2:
        if isIn(app, mouseX, mouseY, 835, 15, 150, 60): 
            app.screen = 3
        if isIn(app, mouseX, mouseY, 745, 15, 150, 60):
            app.screen = 1
        for button in app.stockButtons:
            if isIn(app, mouseX, mouseY, button.x, button.y, button.width, button.height):
                app.stock = button.stock
                for others in app.stockButtons: #toggle selected button
                    others.selected = -1
                button.selected =  -button.selected
        for sb in app.statButtons:
            if isIn(app, mouseX, mouseY, sb.x, sb.y, sb.width, sb.height):
                if app.stock == None:
                    return
                app.metric = sb.metric
                for others in app.statButtons: #toggle selected button
                    others.selected = -1
                sb.selected = -sb.selected
    elif app.screen == 3:
        pass

def isIn(app, mouseX, mouseY, buttonLeftX, buttonTopY, width, height):
    buttonRightX = buttonLeftX + width
    buttonBotY = buttonTopY + height
    return (buttonTopY <= mouseY <= buttonBotY and 
            buttonLeftX <= mouseX <= buttonRightX)

def main():
    runApp(app)
main()
