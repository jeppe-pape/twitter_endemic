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

	in_folder = "C:/users/jeppe/desktop/results"

	for e, fname in enumerate(os.listdir(in_folder)):

		#Find the correct species name for given file
		i = 0

		while hashify(names[i].replace("'", "_")) + "_results.json" != fname:
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

#collect()
df = pd.read_csv("matrix.csv", index_col=0)
G = nx.from_pandas_adjacency(df)

nx.write_weighted_edgelist(G, "edgelist.csv", delimiter=",")
edge_df = pd.read_csv("edgelist.csv",names=["From","To","Weight"])
print(edge_df)
pos = nx.drawing.layout.spring_layout(G, k=0.05, iterations=50, dim=3)

first = pd.DataFrame(edge_df["From"].map(pos).tolist(), columns=["P(0)", "P(1)", "P(2)"])
second = pd.DataFrame(edge_df["To"].map(pos).tolist(), columns=["P(0)", "P(1)", "P(2)"])
print(first)
first.to_csv("first_edge.csv")
second.to_csv("second_edge.csv")
out_df = pd.DataFrame.from_dict(pos, orient="index",columns=["P(0)", "P(1)", "P(2)"])

#print(out_df)
out_df.to_csv("positions.csv")

def draw():
	nx.draw_networkx(G, pos=nx.drawing.layout.spring_layout(G, k=0.05, iterations=50), node_size=20,
		node_color=(0,0,0),
		alpha = 0.1,
		edge_cmap=plt.viridis,
		edge_vmin=0,
		edge_vmax=10,
		with_labels=False,
		font_size = 10)
	plt.axis("off")
	plt.show()