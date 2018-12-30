import talib
import numpy


# Volatility Indicator Functions
def ATR(high=None, low=None, close=None, timeperiod=14, **kwargs):
    # Average True Range
    # returns a real number
    return talib.ATR(high, low, close, timeperiod)


def NATR(high=None, low=None, close=None, timeperiod=14, **kwargs):
    # Normalized Average True Range
    # returns a real number
    return talib.NATR(high, low, close, timeperiod)


def TRANGE(high, low, close):
    # True Range
    # returns a real number
    return talib.TRANGE(high, low, close)


def ADX(high=None, low=None, close=None, timeperiod=14, **kwargs):
    return talib.ADX(high, low, close, timeperiod)


def ADXR(high=None, low=None, close=None, timeperiod=14, **kwargs):
    return talib.ADXR(high, low, close, timeperiod)


def APO(close=None, fastperiod=12, slowperiod=26, matype=0, **kwargs):
    return talib.APO(close, fastperiod, slowperiod, matype)


def AROON(high=None, low=None, timeperiod=14, **kwargs):
    aroondown, aroonup = talib.AROON(high, low, timeperiod)
    return aroondown, aroonup


def AROONOSC(high=None, low=None, timeperiod=14, **kwargs):
    return talib.AROONOSC(high, low, timeperiod)


def CCI(high=None, low=None, close=None, timeperiod=14, **kwargs):
    return talib.CCI(high, low, timeperiod)


def CMO(close=None, timeperiod=14, **kwargs):
    return talib.CMO(close, timeperiod)


def DX(high=None, low=None, close=None, timeperiod=14, **kwargs):
    return talib.DX(high, low, close, timeperiod)


def MACD(close=None, fastperiod=12, slowperiod=26, signalperiod=14, **kwargs):
    # retorno abaixo somente funciona no grafico de 1 minuto onde positivo ponto de compra negativo ponto de venda
    # return macd[-1] - signal[-1]
    # sys.stderr.write('fastperiod=%.2f, slowperiod=%.2f, signalperiod=%.2f\n' % (float(fastperiod), float(slowperiod), float(signalperiod)))
    macd, signal, hist = talib.MACD(close, fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod)
    return macd, signal, hist


def MACDEXT(close=None, fastperiod=12, fastmatype=0, slowperiod=26, slowmatype=0, signalperiod=9, signalmatype=0,
            **kwargs):
    macd, macdsignal, macdhist = talib.MACDEXT(close, fastperiod, fastmatype, slowperiod, slowmatype, signalperiod,
                                               signalmatype)
    return macd, macdsignal, macdhist


def MACDFIX(close=None, signalperiod=9, **kwargs):
    macd, macdsignal, macdhist = talib.MACDFIX(close, signalperiod)
    return macd, macdsignal, macdhist


def MFI(high=None, low=None, close=None, volume=None, timeperiod=14, **kwargs):
    return talib.MFI(high, low, close, volume, timeperiod)


def MINUS_DI(high=None, low=None, close=None, timeperiod=14, **kwargs):
    return talib.MINUS_DI(high, low, close, timeperiod)


def MINUS_DM(high=None, low=None, timeperiod=14, **kwargs):
    return talib.MINUS_DM(high, low, timeperiod)


def MOM(close=None, timeperiod=10, **kwargs):
    return talib.MOM(close, timeperiod)


def PLUS_DI(high=None, low=None, close=None, timeperiod=14, **kwargs):
    return talib.PLUS_DI(high, low, close, timeperiod)


def PLUS_DM(high=None, low=None, timeperiod=14, **kwargs):
    return talib.PLUS_DM(high, low, timeperiod)


def PPO(close=None, fastperiod=12, slowperiod=26, matype=0, **kwargs):
    return talib.PPO(close, fastperiod, slowperiod, matype)


def ROC(close=None, timeperiod=10, **kwargs):
    return talib.ROC(close, timeperiod)


def ROCP(close=None, timeperiod=10, **kwargs):
    return talib.ROCP(close, timeperiod)


# ROCR - Rate of change ratio: (price/prevPrice)
def ROCR(close=None, timeperiod=10, **kwargs):
    return talib.ROCR(close, timeperiod)


def ROCR100(close=None, timeperiod=10, **kwargs):
    return talib.ROCR100(close, timeperiod)


def RSI(close=None, signalperiod=14, **kwargs):
    return talib.RSI(close * 1000, signalperiod) / 1000


def STOCH(high=None, low=None, close=None, fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3,
          slowd_matype=0, **kwargs):
    slowk, slowd = talib.STOCH(high, low, close, fastk_period, slowk_period, slowk_matype, slowd_period, slowd_matype)
    return slowk, slowd


def STOCHF(high=None, low=None, close=None, fastk_period=5, fastd_period=3, fastd_matype=0, **kwargs):
    fastk, fastd = talib.STOCHF(high, low, close, fastk_period, fastd_period, fastd_matype)
    return fastk, fastd


def STOCHRSI(close=None, timeperiod=14, fastk_period=5, fastd_period=3, fastd_matype=0, **kwargs):
    fastk, fastd = talib.STOCHRSI(close, timeperiod, fastk_period, fastd_period, fastd_matype)
    return fastk, fastd


def TRIX(close=None, timeperiod=30, **kwargs):
    return talib.TRIX(close, timeperiod)


def ULTOSC(high=None, low=None, close=None, timeperiod1=7, timeperiod2=14, timeperiod3=28, **kwargs):
    return talib.ULTOSC(high, low, close, timeperiod1, timeperiod2, timeperiod3)


def WILLR(high=None, low=None, close=None, timeperiod=14, **kwargs):
    return talib.WILLR(high, low, close, timeperiod)


# Overlap Sudies Functions

def SAR(high, low, acceleration=0.02, maximum=0.02, **kwargs):
    return talib.SAR(high * 1000, low * 1000, acceleration, maximum) / 1000


def DMI(high=None, low=None, close=None, timeperiod_adx=14, timeperiod_di=14, **kwargs):
    adx = ADX(high, low, close, timeperiod_adx)
    di_plus = PLUS_DI(high, low, close, timeperiod_di)
    di_minus = MINUS_DI(high, low, close, timeperiod_di)

    return adx, di_plus, di_minus


# Super Trend
# method to calculate SuperTrend indicator
# input each record and get upper band, lower band, final upper band,
# final lower band and SuperTrend indicator band
def ST(high, low, close, period=10, multiplier=3, **kwargs):
    """
    Function to compute SuperTrend

    Args :
        period : Integer indicates the period of computation in terms of number of candles
        multiplier : Integer indicates value to multiply the ATR

    Returns :
        uband, lband, finaluband, finallband, supert


    """

    """
    SuperTrend Algorithm :

        BASIC UPPERBAND = (HIGH + LOW) / 2 + Multiplier * ATR
        BASIC LOWERBAND = (HIGH + LOW) / 2 - Multiplier * ATR

        FINAL UPPERBAND = IF( (Current BASICUPPERBAND < Previous FINAL UPPERBAND) or (Previous Close > Previous FINAL UPPERBAND))
                            THEN (Current BASIC UPPERBAND) ELSE Previous FINALUPPERBAND)
        FINAL LOWERBAND = IF( (Current BASIC LOWERBAND > Previous FINAL LOWERBAND) or (Previous Close < Previous FINAL LOWERBAND))
                            THEN (Current BASIC LOWERBAND) ELSE Previous FINAL LOWERBAND)

        SUPERTREND = IF((Previous SUPERTREND = Previous FINAL UPPERBAND) and (Current Close <= Current FINAL UPPERBAND)) THEN
                        Current FINAL UPPERBAND
                    ELSE
                        IF((Previous SUPERTREND = Previous FINAL UPPERBAND) and (Current Close > Current FINAL UPPERBAND)) THEN
                            Current FINAL LOWERBAND
                        ELSE
                            IF((Previous SUPERTREND = Previous FINAL LOWERBAND) and (Current Close >= Current FINAL LOWERBAND)) THEN
                                Current FINAL LOWERBAND
                            ELSE
                                IF((Previous SUPERTREND = Previous FINAL LOWERBAND) and (Current Close < Current FINAL LOWERBAND)) THEN
                                    Current FINAL UPPERBAND
    """

    _atr = ATR(high, low, close, period)
    _uband = []
    _lband = []
    _finaluband = []
    _finallband = []
    _supert = []

    _uband.insert(0, 0.0)
    _lband.insert(0, 0.4)

    _uband = (high + low) / 2 + multiplier * _atr
    _lband = (high + low) / 2 - multiplier * _atr

    for i in range(0, len(close)):
        if i < period:
            _uband[i] = 0.0
            _lband[i] = 0.0
            _finaluband.append(0.0)
            _finallband.append(0.0)
        else:
            _finaluband.append(
                _uband[i] if _uband[i] < _finaluband[i - 1] or close[i - 1] > _finaluband[i - 1] else _finaluband[
                    i - 1])
            _finallband.append(
                _lband[i] if _lband[i] > _finallband[i - 1] or close[i - 1] < _finallband[i - 1] else _finallband[
                    i - 1])
    # Set the Supertrend value
    for i in range(0, len(close)):
        if i < period:
            _supert.append(0.0)
        else:
            _supert.append((_finaluband[i]
                            if ((_supert[i - 1] == _finaluband[i - 1]) and (close[i] <= _finaluband[i]))
                            else (_finallband[i]
                                  if ((_supert[i - 1] == _finaluband[i - 1]) and (close[i] > _finaluband[i]))
                                  else (_finallband[i]
                                        if ((_supert[i - 1] == _finallband[i - 1]) and (close[i] >= _finallband[i]))
                                        else (_finaluband[i]
                                              if (
                    (_supert[i - 1] == _finallband[i - 1]) and (close[i] < _finallband[i]))
                                              else 0.0
                                              )))))

    return _uband, _lband, _finaluband, _finallband, _supert


# # cabra pressure stalker indicator
# def CPSI(text=None, depth=None, near=1, mid=1.5, far=3.0, **kwargs):
#     if not text or not depth:
#         return False, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
#
#     range1 = c_double(near)
#     range2 = c_double(mid)
#     range3 = c_double(far)
#     bid = c_double(0.0)
#     ask = c_double(0.0)
#     spread = c_double(0.0)
#     near = c_double(0.0)
#     mid = c_double(0.0)
#     far = c_double(0.0)
#     text = text.encode('utf-8')
#
#     success = lib.get_pressure(text, depth, range1, range2, range3, byref(bid), byref(ask), byref(spread), byref(near),
#                                byref(mid), byref(far))
#
#     if success > 0:
#         return True, near.value, mid.value, far.value, bid.value, ask.value, spread.value
#     elif success == -1:
#         # print "Erro: Ask sem depth suficiente..."
#         return False, near.value, mid.value, far.value, bid.value, ask.value, spread.value
#     elif success == -2:
#         # print "Erro: Bid sem depth suficiente..."
#         return False, near.value, mid.value, far.value, bid.value, ask.value, spread.value
#     return False, near.value, mid.value, far.value, bid.value, ask.value, spread.value


# Volume Indicator Functions

def OBV(close, volume, **kwargs):
    return talib.OBV(close, volume)


def BBANDS(close, matype=talib.MA_Type.T3, **kwargs):
    upper, middle, lower = talib.BBANDS(close * 1000, matype)
    return upper / 1000, middle / 1000, lower / 1000
