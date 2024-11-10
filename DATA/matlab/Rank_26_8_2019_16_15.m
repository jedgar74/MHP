[labels,x,y] = readColData('Rank_26_8_2019_16_15.txt', 7, 0, 1)
boxplot(y, 'orientation', 'horizontal', 'labels',{'HBBOSA','ILS','HBBOILS','GA','SA','BBO'})
xlabel('rank')
