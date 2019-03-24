import requests

link = "http://www.aastocks.com/en/usq/quote/quote.aspx?symbol=AMZN"
# https://stockcharts.com/h-sc/ui?s=AMZN
# https://www.chartjs.org
the_page = requests.get(link).content


print(the_page)