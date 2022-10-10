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
    if args.ancestry == 'Mixed':
        srcdir = f's3://dig-analysis-data/out/metaanalysis/clumped/*/part-*'
        outdir = f's3://{s3_bucket}/associations/clump'
    else:
        srcdir = f's3://dig-analysis-data/out/metaanalysis/ancestry-clumped/*/ancestry={args.ancestry_specific}/part-*'
        outdir = f's3://{s3_bucket}/ancestry-associations/clump/{args.ancestry_specific}'

    clumps = spark.read.json(srcdir)\
        .withColumn('ancestry', lit(args.ancestry_specific))

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
