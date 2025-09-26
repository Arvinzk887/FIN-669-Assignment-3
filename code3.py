import math
import matplotlib.pyplot as plt

SellPrice = float(input('Your selling price per unit is: '))
Variable = float(input('Variable cost is: '))
Fixed = float(input('Fixed cost for the year is: '))

CM = SellPrice - Variable #Contribution Margin
print(f'\n\n Your contribution margin per unit is: {CM:2f}')

BEP = Fixed/CM #Break Even Point
BEPS = Fixed/(CM/SellPrice) 

print(f'\n\n Your break even point in units is: {BEP:2f}'
+ f'\n\n Your break even point in sales is: {BEPS:2f}')
