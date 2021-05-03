package org.broadinstitute.dig.aggregator.methods.basset

import org.broadinstitute.dig.aggregator.core._
import org.broadinstitute.dig.aws._
import org.broadinstitute.dig.aws.emr._
import org.broadinstitute.dig.aws.Ec2.Strategy
import org.broadinstitute.dig.aws.MemorySize

/** This is a stage in your method.
  *
  * Stages take one or more inputs and generate one or more outputs. Each
  * stage consists of a...
  *
  *   - list of input sources;
  *   - rules mapping inputs to outputs;
  *   - make function that returns a job used to produce a given output
  *
  * Optionally, a stage can also override...
  *
  *   - its name, which defaults to its class name
  *   - the cluster definition used to provision EC2 instances
  */
class BassetStage(implicit context: Context) extends Stage {

  /** Cluster configuration used when running this stage. The super
    * class already has a default configuration defined, so it's easier
    * to just copy and override specific parts of it.
    */
  override val cluster: ClusterDef = super.cluster.copy(
    masterInstanceType = Strategy.computeOptimized(),
    instances = 1,
    masterVolumeSizeInGB = 60,
    stepConcurrency = 3,
    applications = Seq.empty,
    bootstrapScripts = Seq(
      new BootstrapScript(resourceUri("bassetBootstrap.sh"))
    )
  )

  /** Input sources need to be declared so they can be used in rules.
    *
    * Input sources are a glob-like S3 prefix to an object in S3. Wildcards
    * can be pattern matched in the rules of the stage.
    */
  val variants: Input.Source = Input.Source.Success("out/varianteffect/variants/")

  /** When run, all the input sources here will be checked to see if they
    * are new or updated.
    */
  override val sources: Seq[Input.Source] = Seq(variants)

  /** For every input that is new/updated, this partial function is called,
    * which pattern matches it against the inputs sources defined above and
    * maps them to the output(s) that should be built.
    *
    * In our variants input source, there are two wildcards in the S3 prefix,
    * which are matched to the dataset name and phenotype. The dataset is
    * ignored, and the name of the phenotype is used as the output.
    */
  override val rules: PartialFunction[Input, Outputs] = {
    case variants() => Outputs.Named("basset")
  }

  /** Additional resources we need to write to S3 before the job runs.
    */
  override def additionalResources: Seq[String] = Seq(
    "dcc_basset_lib.py",
    "fullBassetScript.py"
  )

  /** Once all the rules have been applied to the new and updated inputs,
    * each of the outputs that needs built is send here. A job is returned,
    * which is the series of steps that need to be executed on the cluster
    * in order for the final output to be successfully built.
    *
    * It is assumed that all outputs for a given stage are independent of
    * each other and can be executed in parallel across multiple, identical
    * clusters.
    */
  override def make(output: String): Job = {
    val bassetScript = resourceUri("bassetScript.sh")

    // get all the variant part files to process, use only the part filename
    val objects = context.s3.ls(s"out/varianteffect/variants/")
    val parts   = objects.map(_.key.split('/').last).filter(_.startsWith("part-"))
    val steps   = parts.map(part => Job.Script(bassetScript, part))

    // create the job; run steps in parallel
    new Job(steps, parallelSteps = true)
  }

  /** Before the jobs actually run, perform this operation.
    */
  override def prepareJob(output: String): Unit = {
    context.s3.rm("out/basset/")
  }

  /** On success, write the _SUCCESS file in the output directory.
    */
  override def success(output: String): Unit = {
    context.s3.touch("out/basset/_SUCCESS")
    ()
  }
}