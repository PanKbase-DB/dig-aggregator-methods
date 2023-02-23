import argparse
from datetime import datetime

from pyspark.sql import SparkSession, DataFrame, Window
from pyspark.sql.functions import col, row_number, greatest, lit


def now_str():
    return str(datetime.now())


def inspect_df(df: DataFrame, name: str):
    n_rows = df.count()
    print("Dataframe ", name, " has ", n_rows, " rows.", "(", now_str(), ")")
    df.printSchema()
    n_rows_max = 23
    if n_rows > n_rows_max:
        df.sample(fraction=(n_rows_max / n_rows)).show()
    else:
        df.show()
    print('Done showing ', name, ' at ', now_str())


def main():
    """
    Arguments: none
    """
    print('Hello! The time is now ', now_str())
    print('Now building argument parser')
    arg_parser = argparse.ArgumentParser(prog='gene-id-map.py')
    arg_parser.add_argument("--genes-dir", help="gene data dir", required=True)
    arg_parser.add_argument("--variants-dir", help="variant data dir", required=True)
    arg_parser.add_argument("--out-dir", help="output dir", required=True)
    print('Now parsing CLI arguments')
    cli_args = arg_parser.parse_args()
    files_glob = 'part-*'
    genes_glob = cli_args.genes_dir + files_glob
    variants_glob = cli_args.variants_dir + files_glob
    out_dir = cli_args.out_dir
    print('Gene data dir: ', genes_glob)
    print('Variant effects data dir: ', variants_glob)
    print('Output dir: ', out_dir)
    spark = SparkSession.builder.appName('nearest_gene').getOrCreate()
    genes = spark.read.json(genes_glob).select("chromosome", "start", "end", "ensembl")
    variants = spark.read.json(variants_glob).select("varId", "chromosome", "position")
    joined = genes.join(variants, ["chromosome"])
    distances = \
        joined.withColumn("distance", greatest(col("start") - col("position"), col("position") - col("end"), lit(0)))\
            .withColumn("length", col("end") - col("start"))
    inspect_df(distances, "distance")
    distances_by_gene = Window.partitionBy("ensembl").orderBy(col("distance", "length"))
    nearest = distances.withColumn("row", row_number().over(distances_by_gene)).filter(col("row") == 1).drop("row")
    inspect_df(nearest, "nearest")
    nearest.write.mode('overwrite').json(out_dir)
    print('Done with work, therefore stopping Spark')
    spark.stop()
    print('Spark stopped')


if __name__ == '__main__':
    main()
