[labels,x,y] = readColData('Rank_26_8_2019_16_20.txt', 7, 0, 1)
boxplot(y, 'orientation', 'horizontal', 'labels',{'ILS','HBBOILS','HBBOSA','GA','SA','BBO'})
xlabel('rank')
