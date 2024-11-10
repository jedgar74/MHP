[labels,x,y] = readColData('Rank_17_7_2019_9_46.txt', 7, 0, 1)
boxplot(y, 'orientation', 'horizontal', 'labels',{'g','d','MINn','c','b','a'})
xlabel('rank')
