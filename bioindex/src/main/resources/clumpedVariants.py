import argparse

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import lit


def main():
    """
    Arguments:  ancestry- str indicating which ancestry to run the analysis against
    """
    opts = argparse.ArgumentParser()
    opts.add_argument('--ancestry', type=str, required=True)
    args = opts.parse_args()

    spark = SparkSession.builder.appName('bioindex').getOrCreate()

    # source and output locations
    s3_bucket = 'dig-bio-index'
    srcdir = f's3://dig-analysis-data/out/credible_sets/merged/*/{args.ancestry}/part-*'
    if args.ancestry == 'Mixed':
        outdir = f's3://{s3_bucket}/associations/clump'
    else:
        outdir = f's3://{s3_bucket}/ancestry-associations/clump/{args.ancestry}'

    clumps = spark.read.json(srcdir)\
        .withColumn('ancestry', lit(args.ancestry))
    clumps = clumps \
        .withColumn('clump', clumps.credibleSetId) \
        .filter(clumps.source != 'credible_set') \
        .drop('credibleSetId')

    common_dir = 's3://dig-analysis-data/out/varianteffect/common'
    common = spark.read.json(f'{common_dir}/part-*')

    # join to get and common fields
    clumps = clumps.join(common, on='varId', how='left_outer')

    # write out all the clumped associations sorted by phenotype and clump
    clumps.orderBy(['phenotype', 'clump', 'pValue']) \
        .write \
        .mode('overwrite') \
        .json(outdir)

    # done
    spark.stop()


if __name__ == '__main__':
    main()
