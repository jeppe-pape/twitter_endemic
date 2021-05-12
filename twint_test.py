import os
import json
import sys
import argparse
import re
import math

import twint
import pandas as pd

def parse_args():
    desc = "Download mentions of endemic species from twitter using twint"
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument("-q", "--query",
                        help="Specific hashtag to get query from. Format this in capitalized text with spaces (ex. 'Bluefin Shark', not 'bluefinshark'")

    parser.add_argument("--all",
    										action="store_true",
                        help="Flag for processing all endemic species (from specific_names.json file")

    parser.add_argument("--partition",
    										type=int,
    										nargs=2,
                        help="Used when distributing all-search across multiple systems. Format: '{num_divisions} {your division}', ex. --partition 5 2")


    parser.add_argument("--dont_search_bodytext",
    										action="store_false",
                        help="Flag for searching just the hashtag ('#bluefinshark') and NOT the full species name ('Bluefin Shark')")

    parser.add_argument("--overwrite",
    										action="store_true",
                        help="Flag if you want to overwrite the existing results")

    parser.add_argument("--verbose",
    										action="store_true",
                        help="Flag if you want to print all incoming tweets")

    parser.add_argument("-m", "--max_results",
    										default = 10000,
                        help="The maximum number of tweets to return for given hashtag")

    parser.add_argument("--tweet_dir",
    										default = "tweets",
                        help="Directory to store all tweets to do analysis upon. Default 'tweets/'")

    parser.add_argument("-o", "--out_dir",
    										default = "results",
                        help="Directory to store results. Default 'results/'")

    args = parser.parse_args()
    return args


def search_and_store(query, num_tweets = 10000, english_only = True):
	"""Uses twint to search for tweets on given """
	c = twint.Config()
	#c.Username = "red panda"
	c.Search = query
	if english_only: c.Lang = "en"
	c.Store_csv = True
	c.Limit = num_tweets
	c.Popular_tweets = True
	c.Output = os.path.join(args.tweet_dir, query + ".csv")
	c.Show_hashtags = True
	c.Hide_output = not args.verbose

	twint.run.Search(c)


def get_hashtags(d):
	hashtags = []
	for p in d["hashtags"]:
	 hashtags += p[2:-2].split("', '")
	return hashtags

def hashify(phrase):
	return "#" + phrase.replace(" ", "")


def get_common_names(only_english = True, remove_vague = True):
	d = pd.read_csv("redlist_data/common_names.csv")

	if only_english:
		d = d.loc[d["language"] == "English"]

	l = list(d["name"])

	if remove_vague:
		new_list = []
		for i, n in enumerate(l):
			string_extend = ";".join(l).replace(n,"",1)
			if n not in string_extend:
				
				new_list.append(n)
			else:
				print(i, n)
		l = new_list

	#remove weird \t artifacts from data
	l = [name.replace("\t", "") for name in l]
	print(l)
	return l


def get_specific_names(removes = []):
	f = open('specific_names.json', "r", encoding='utf-8')
	names = json.loads(f.read())

	for r in removes:
		try:	names.remove(r)
		except: pass
	return names	


def query_cycle(species, max_results = 10000):
	print(f"Looking up {species}...")

	query = hashify(species)

	# Skip if results already loaded (except overwrite)
	if os.path.exists(os.path.join(args.out_dir, query + "_results.json")):

		if not args.overwrite:
			print(f"Results for {species} already found.. Skipping (pass --overwrite to overwrite)")
			return

	# If no tweets collected, collect tweets
	if not os.path.exists(os.path.join(args.tweet_dir + query + ".csv")):
		print(f"Getting tweets for {species}... This can take a while")
		search_and_store(query, num_tweets = max_results)

	#Load tweets into dataframe
	try:
		tweets = pd.read_csv(os.path.join(args.tweet_dir, query + ".csv"))
	except FileNotFoundError:
		print("Probably no tweets found for given species :( Returning...")
		return

	#Import endemic species list and remove itself
	names = get_specific_names(removes = [species]) 



	l_tweets = list(tweets.loc[tweets["language"] == "en", "tweet"])
	hits = {}
	for i, t in enumerate(l_tweets):
		#t = re.split("; |, | |\"", t)

		hit_species = []

		for n in names:
			if args.dont_search_bodytext:
				if (n in t) or (hashify(n.lower()) in t.lower()):
					hit_species.append(n)

			else:
				print("Second")
				if hashify(n.lower()) in t.lower():
					hit_species.append(n)				

		if len(hit_species) > 0:
			hits[i] = {"Tweet": t, "Species": hit_species}
			print(hits[i])

	print(hits)

	with open(os.path.join(args.out_dir, query + "_results.json"), "w") as f:
		json.dump(hits, f, indent=4)


def main():
	global args 
	args = parse_args()

	#args.query = "Clown knifefish"
	args.all = True
	args.partition = [5,2]

	#Go through all species
	if args.all:
		ns = get_specific_names()

		if args.partition is not None:
			assert args.partition[1] < args.partition [0], "Partition index must be lower than number of divisions"
			
			binsize = math.ceil(len(ns) / args.partition[0])
			start = binsize * args.partition[1]


			for species_name in ns[start:start+binsize]:
				query_cycle(species_name, max_results	= args.max_results)

		for species_name in ns:
			query_cycle(species_name, max_results	= args.max_results)		


	#Only go through given species
	else:

		assert args.query is not None, "Error - empty query"
		query_cycle(args.query, max_results	= args.max_results)



if __name__ == "__main__":
	main()