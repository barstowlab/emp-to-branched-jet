# ------------------------------------------------------------------------------------------------ #
def ExportStoichiometricMatrix(sMatrixT, reactions_full, compoundsUnique_full, mergedIOStatus):

	outputMatrix = []
	
	k = 0
	compoundHeadersString = ''
	compoundHeadersString += ','
	while k < len(compoundsUnique_full):
		compoundHeadersString += str(compoundsUnique_full[k]) + ','
		k += 1
	
	compoundHeadersString += '\n'
	outputMatrix.append(compoundHeadersString)
	
	k = 0
	ioStatusHeaderString = ''
	ioStatusHeaderString += ','
	while k < len(mergedIOStatus):
		ioStatusHeaderString += str(mergedIOStatus[k]) + ','
		k += 1
	
	ioStatusHeaderString += '\n'
	outputMatrix.append(ioStatusHeaderString)
	
	outputString = ''
	i = 0
	
	while i < len(reactions_full):
		rowString = ''
		rowString += reactions_full[i]
		rowString += ','
		
		j = 0
		while j < len(sMatrixT[i]):
			matrixElement = sMatrixT[i][j]
			rowString += str(matrixElement)
			rowString += ','
			j += 1
		
		# This adds an extra couple of columns for references (or at least pretend refs)
		rowString += ','
		rowString += '\n'
	
		outputMatrix.append(rowString)
		i += 1
		
	return outputMatrix
# ------------------------------------------------------------------------------------------------ #


import re
from numpy import unique, int8
from utils.balanceUtils import SolveFluxBalanceEquation, ConvertIndexedSMatrix, \
ImportReactionFile, GenerateIndexedSMatrixT, PrintStoichiometry, GenerateMergedIOStatusList, \
ImportIOStatus
from os.path import join
from utils.vectorOutput import generateOutputMatrixWithHeaders, writeOutputMatrix
from utils.specutils12 import ensure_dir
import pdb



aaIOStatusDirName = 'input/jetfuel_iostatus'
co2IOStatusDirName = 'input/co2_iostatus'
aaReactionsDirName = 'input/jetfuel_reactions'
co2ReactionsDirName = 'input/co2_reactions'


aaIOStatusFileNames = [\
'2-4dimethylhexaneADO_iostatus.csv', \
'2-4dimethyloctaneADO_iostatus.csv', \
'2-4dimethyldecaneADO_iostatus.csv', \
'2-5dimethylheptaneADO_iostatus.csv', \
'2-5dimethylnonaneADO_iostatus.csv', \
'3-5dimethyloctaneADO_iostatus.csv', \
'3-5dimethyldecaneADO_iostatus.csv', \
'2-4-6trimethyloctaneADO_iostatus.csv', \
'2-4-6-trimethyldecaneADO_iostatus.csv', \
'2-4-6-8-tetramethyldecaneADO_iostatus.csv', \
]

aaReactionsFileNames = [\
'2-4dimethylhexaneADO_reactions.txt', \
'2-4dimethyloctaneADO_reactions.txt', \
'2-4dimethyldecaneADO_reactions.txt', \
'2-5dimethylheptaneADO_reactions.txt', \
'2-5dimethylnonaneADO_reactions.txt', \
'3-5dimethyloctaneADO_reactions.txt', \
'3-5dimethyldecaneADO_reactions.txt', \
'2-4-6trimethyloctaneADO_reactions.txt', \
'2-4-6-trimethyldecaneADO_reactions.txt', \
'2-4-6-8-tetramethyldecaneADO_reactions.txt', \
]

co2ReactionsFileNames = [\
'CBB_reactions.txt', \
]

co2IOStatusFileNames = [\
'CBB_iostatus.csv', \
]


reactantsToGet = ['ATP', 'NADH', 'Fdred', 'Sulfate', 'N2', 'CO2', 'HCO2-', 'H2O', 'Hplus', 'CO']
reactantOutputFilePath = 'output/Output-Fig-4C&D/Data-Fig-4C&D.csv'
outputDir = 'output/Output-Fig-4C&D/'
ensure_dir(outputDir)
reactantOutputFilePath = 'output/Output-Fig-4C&D/stable-nReactants.csv'
ensure_dir(reactantOutputFilePath)


# ------------------------------------------------------------------------------------------------ #
# Generate a set of dictionaries for amino acid io status

aa_ioStatusDict = {}
for fileName in aaIOStatusFileNames:
	
	prefix = os.path.splitext(fileName)[0].split('_')[0]
	ioStatusAAFilePath = os.path.join(aaIOStatusDirName, fileName)
	iostatusAA = ImportIOStatus(ioStatusAAFilePath)
	
	aa_ioStatusDict[prefix] = iostatusAA
# ------------------------------------------------------------------------------------------------ #


# ------------------------------------------------------------------------------------------------ #
# Generate a set of dictionaries for co2 io status

co2_ioStatusDict = {}
for fileName in co2IOStatusFileNames:	

	prefix = os.path.splitext(fileName)[0].split('_')[0]
	ioStatusCO2FilePath = os.path.join(co2IOStatusDirName, fileName)
	iostatusCO2 = ImportIOStatus(ioStatusCO2FilePath)
	
	co2_ioStatusDict[prefix] = iostatusCO2
# ------------------------------------------------------------------------------------------------ #


# ------------------------------------------------------------------------------------------------ #
# Generate a set of dictionaries for aa reactions

aa_reactionDict = {}
for fileName in aaReactionsFileNames:	

	prefix = os.path.splitext(fileName)[0].split('_')[0]
	aa_reactionFilePath = os.path.join(aaReactionsDirName, fileName)

	compounds_AA, reactions_AA, sMatrixTKeyIndexed_AA = \
	ImportReactionFile(aa_reactionFilePath, reactionArrow='???')
	
	aa_reactionDict[prefix] = [compounds_AA, reactions_AA, sMatrixTKeyIndexed_AA]
# ------------------------------------------------------------------------------------------------ #


# ------------------------------------------------------------------------------------------------ #
# Generate a set of dictionaries for co2 reactions

co2_reactionDict = {}
for fileName in co2ReactionsFileNames:	

	prefix = os.path.splitext(fileName)[0].split('_')[0]
	co2_reactionFilePath = os.path.join(co2ReactionsDirName, fileName)

	compounds_co2, reactions_co2, sMatrixTKeyIndexed_co2 = \
	ImportReactionFile(co2_reactionFilePath, reactionArrow='???')
	
	co2_reactionDict[prefix] = [compounds_co2, reactions_co2, sMatrixTKeyIndexed_co2]
# ------------------------------------------------------------------------------------------------ #


# ------------------------------------------------------------------------------------------------ #
# Loop over each compound and generate a stoichiometric matrix for each CO2 fixation method

aaKeys = aa_reactionDict.keys()
co2Keys = co2_reactionDict.keys()

# Generate a scenario dict

scenarioDict = {}
scenarioReactantsDict = {}
scenarioTargetDict = {}

for aaKey in aaKeys:

	# Import the unique compound synthesis reactions here
	[compounds_AA, reactions_AA, sMatrixTKeyIndexed_AA] = aa_reactionDict[aaKey]
	iostatusAA = aa_ioStatusDict[aaKey]

	# Loop over each carbon-fixation reactions here
	for co2Key in co2Keys:

		scenarioKey = aaKey + '_' + co2Key
		scenarioReactantsDict[scenarioKey] = {}
		scenarioTargetDict[scenarioKey] = {}
		
		print(scenarioKey)
		
		[compounds_CO2, reactions_CO2, sMatrixTKeyIndexed_CO2] = co2_reactionDict[co2Key]
		iostatusCO2 = co2_ioStatusDict[co2Key]

		reactions_full = list(reactions_CO2) + list(reactions_AA)
		compounds_full = list(compounds_CO2) + list(compounds_AA)
		compoundsUnique_full = list(unique(compounds_full))

		sMatrixTKeyIndexed = GenerateIndexedSMatrixT(compoundsUnique_full, reactions_full, \
		reactionArrow='???')
		
		

		mergedIOStatus, ioStatusCO2Dict, ioStatusAADict = \
		GenerateMergedIOStatusList(compoundsUnique_full, iostatusCO2, iostatusAA)

		# Convert the stoichiometric matrix to a non-key indexed matrix
		sMatrixT = ConvertIndexedSMatrix(sMatrixTKeyIndexed, compoundsUnique_full)
		sMatrix = sMatrixT.transpose()

		[fVectorOpt, cDotVectorOpt, cDotVectorOptNorm, result] = \
		SolveFluxBalanceEquation(sMatrix, reactions_full, compoundsUnique_full, mergedIOStatus)
	
		scenarioDict[scenarioKey] = [fVectorOpt, cDotVectorOpt, cDotVectorOptNorm, result, \
		compoundsUnique_full, reactions_full, sMatrixTKeyIndexed]
		
		for reactantToGet in reactantsToGet:
			# If the reactant to query isn't in the list of reactants for this matrix, record 0
			if reactantToGet not in compoundsUnique_full:
				scenarioReactantsDict[scenarioKey][reactantToGet] = 0
			
			# On the other hand, if it is, add the number of if to its array
			elif reactantToGet in compoundsUnique_full:
				reactantIndex = compoundsUnique_full.index(reactantToGet)
				nReactant = cDotVectorOptNorm[reactantIndex]
				scenarioReactantsDict[scenarioKey][reactantToGet] = nReactant
	
		i = 0
		while i < len(compoundsUnique_full):
			ioStatusReactant = mergedIOStatus[i]
				
			if ioStatusReactant == 'Target':	
				scenarioTargetDict[scenarioKey][compoundsUnique_full[i]] = cDotVectorOptNorm[i]
				
			i += 1
		
		oMatrix = \
		ExportStoichiometricMatrix(sMatrixT, reactions_full, compoundsUnique_full, mergedIOStatus)
		
		writeOutputMatrix(join(outputDir, scenarioKey + '.csv'), oMatrix)
		
# ------------------------------------------------------------------------------------------------ #


# ------------------------------------------------------------------------------------------------ #
# Output the results of stoichiometry calculation as a table

scenarioKeys = list(scenarioReactantsDict.keys())
nReactantsDict = {}

for reactantToGet in reactantsToGet:
	nReactantsDict[reactantToGet] = []
	for key in scenarioKeys:
		nReactantsDict[reactantToGet].append(scenarioReactantsDict[key][reactantToGet])

targetsArray = []
nTargetsArray = []

for key in scenarioKeys:
	targetMoleculeKeys = scenarioTargetDict[key].keys()
	targetMolecule = list(targetMoleculeKeys)[0]
	nTargetMolecule = scenarioTargetDict[key][targetMolecule]
	targetsArray.append(targetMolecule)
	nTargetsArray.append(nTargetMolecule)
	

headers = ['Scenario'] + reactantsToGet + ['Target Molecule', 'Target']
vectorList = [scenarioKeys]

for reactantToGet in reactantsToGet:
	vectorList.append(array(nReactantsDict[reactantToGet], float)*-1)

vectorList.append(targetsArray)
vectorList.append(array(nTargetsArray, float))

oMatrix = generateOutputMatrixWithHeaders(vectorList, headers, delimeter=',')
writeOutputMatrix(reactantOutputFilePath, oMatrix)
# ------------------------------------------------------------------------------------------------ #


		
		

