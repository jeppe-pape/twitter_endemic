import json
import math
import os

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx


from twint_test import get_specific_names, hashify


names = get_specific_names()

def collect():
	df = pd.DataFrame()

	in_folder = "results"

	for e, fname in enumerate(os.listdir(in_folder)):

		#Find the correct species name for given file
		i = 0
		while hashify(names[i]) + "_results.json" != fname:
			i +=1
		species = names[i]

		#Get the data from .json file
		with open(os.path.join(in_folder, fname)) as f:
			json_file = json.load(f)


		for index,info in json_file.items():

			if info["Species"][0] not in df.columns:
				df[info["Species"][0]] = 0
			if species not in df.columns:
				df[species] = 0

			if species not in df.index:
				df.loc[species] = pd.Series(0, index=df.columns)
			if info["Species"][0] not in df.index:
				df.loc[info["Species"][0]] = pd.Series(0, index=df.columns)

			df.loc[species,info["Species"][0]] += 1

		print(e,fname)


	df.to_csv("matrix.csv")

df = pd.read_csv("matrix.csv", index_col=0)
G = nx.from_pandas_adjacency(df)
for e in G.edges:
	print(e)
print(nx.info(G))
nx.draw_networkx(G, pos=nx.drawing.layout.spring_layout(G, k=0.06, iterations=20), node_size=20,
	node_color=(0,0,0),
	alpha = 0.5,
	edge_cmap=plt.viridis,
	edge_vmin=0,
	edge_vmax=10,
	with_labels=False,
	font_size = 10)
plt.axis("off")
plt.show()