import re

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode

from bioindex.lib.utils import camel_case_str


def main():
    """
    Arguments: none
    """
    spark = SparkSession.builder.appName('bioindex').getOrCreate()

    # source and output directories
    srcdir = f's3://dig-analysis-data/out/varianteffect/effects/*.json'
    outdir = f's3://dig-bio-index/transcript_consequences'

    # load the common effect data
    df = spark.read.json(srcdir)

    # join before exploding (faster) to get dbSNP
    df = df \
        .select(df.id.alias('varId'), df.transcript_consequences) \
        .withColumn('cqs', explode(df.transcript_consequences)) \
        .select(
            col('varId'),
            col('seq_region_name').alias('chromosome'),
            col('start').alias('position'),
            col('cqs.*'),
        )

    # rename all the columns to guarantee camel-case of consequence fields
    for column in df.columns:
        df = df.withColumnRenamed(column, camel_case_str(column))

    # output the consequences, ordered by variant so they are together
    df.drop('domains') \
        .orderBy(['chromosome', 'position']),
        .write \
        .mode('overwrite') \
        .json(outdir)

    # done
    spark.stop()


# entry point
if __name__ == '__main__':
    main()
