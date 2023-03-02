# ------------------------------------------------------------------------------------------------ #
# Fig5A&B,py
# Created by TJ Sheppard
# Last updated: 2023-03-02
# Code to recreate figures 5A and 5B in "Efficiency Estimates for Electromicrobial Production of 
# Branched Chain Hydrocarbons". 
# ------------------------------------------------------------------------------------------------ #


from rewiredcarbon.scenario import ImportScenarioTable, CalculateScenarioEfficiencies, \
Plot_Efficiency_Bargraph, Generate_EfficienciesDict_Keys_Sorted_by_Efficiency, \
Export_Efficiency_Bargraph

from rewiredcarbon.utils import ensure_dir

from os.path import join
# ------------------------------------------------------------------------------------------------ #
# Get input and outputs all set up
outputDir = 'output'

scenarioTableFileName = 'input/Fig-5A&B.csv'
outputFilenameFuelMassEff = join(outputDir, 'Fig-5A.csv')
outputFilenameEff = join(outputDir, 'Fig-5B.csv')

ensure_dir(outputFilenameEff)
ensure_dir(outputFilenameFuelMassEff)

ensure_dir(outputFilenameEff)
ensure_dir(outputFilenameFuelMassEff)
# ------------------------------------------------------------------------------------------------ #

# ------------------------------------------------------------------------------------------------ #
# Do the calculation 

# Import the input data
scenarioDict = ImportScenarioTable(scenarioTableFileName)

# Calculate efficiencies
efficienciesDict = CalculateScenarioEfficiencies(scenarioDict)
# ------------------------------------------------------------------------------------------------ #


# ------------------------------------------------------------------------------------------------ #
# Plot the results

keysArray = list(efficienciesDict.keys())

# Plot the energy consumption per unit mass (Fig. 5A)
# Note, in the paper, we plot out energy consumption per mole. We do this conversion in a 
# Excel spreadsheet, which is included in this repository, We will get this code to output in terms
# of energy per mole in a later version. 
Plot_Efficiency_Bargraph(efficienciesDict, 'effTotalElectricalFuelMassEfficiency', \
'effTotalElectricalFuelMassEfficiency_lowerError', \
'effTotalElectricalFuelMassEfficiency_upperError', keysToPlot=keysArray)


Export_Efficiency_Bargraph(outputFilenameFuelMassEff, efficienciesDict, scenarioDict, \
'effTotalElectricalFuelMassEfficiency', 'effTotalElectricalFuelMassEfficiency_lowerError', \
'effTotalElectricalFuelMassEfficiency_upperError', keysToPlot=keysArray)


# Plot the energy conversion efficiency (Fig. 5B)
Plot_Efficiency_Bargraph(efficienciesDict, 'effTotalElectricalToFuel', \
'effTotalElectricalToFuel_lowerError', 'effTotalElectricalToFuel_upperError', keysToPlot=keysArray)

Export_Efficiency_Bargraph(outputFilenameEff, efficienciesDict, scenarioDict, \
'effTotalElectricalToFuel', 'effTotalElectricalToFuel_lowerError', \
'effTotalElectricalToFuel_upperError', keysToPlot=keysArray)

# ------------------------------------------------------------------------------------------------ #