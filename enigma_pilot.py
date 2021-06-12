operating_directory="C:\\git\\StormBreaker\\Enigma"
chromeDriver_path="C:\git\StormBreaker\Enigma\chromedriver.exe"
excludeStocks=['YESBANK','IDEA','GOLDBEES','JUNIORBEES']

from Zerodha_workflow import zerodha_workflow as z
z=z.zerodha_workflow(operating_directory,chromeDriver_path)

from Trendlyn_workflow import trendlyn_workflow as t
t=t.trendlyn_workflow(operating_directory,chromeDriver_path)

from Enigma import enigma as engm
e=engm.enigma(operating_directory,chromeDriver_path,excludeStocks)

e.data.to_excel('support_resistance.xlsx',index=False)