from param import JET#, PEACH
from crawler import crawlerJet

#crawler_module:
#   ProcessAirLineResponse(targetDate, airlineResponse):
#   GetAirLineResponse(date, origin, destination, proxy):

TARGET_CRAWLER_INFO = [{
    'param_module': JET,
    'crawler_module': crawlerJet
#}, {
#    'param_module': PEACH,
#    'crawler_func'
}]

