# Databricks notebook source
df = spark.read.json("/Volumes/raw/pokemon/pokemon_raw/pokemons_list/")
# by reading this way, passing only the folder name, Spark will infer the schema
# we don't read unique files with spark, because it is parallelized
# so we pass only the folder's name, and the spark will mix all the files
# in only one dataframe
df.distinct().coalesce(1).write.format("delta").mode("overwrite").saveAsTable("bronze.pokemon.tb_pokemon_list")
# coalesce means that we want to have only one file in the folder
# it happens becaus spark works and saves in partitions, due to it's parallelization
# so we want to have only one file, so we use coalesce
