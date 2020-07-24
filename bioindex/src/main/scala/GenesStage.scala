package org.broadinstitute.dig.aggregator.methods.bioindex

import org.broadinstitute.dig.aggregator.core._
import org.broadinstitute.dig.aws._
import org.broadinstitute.dig.aws.emr._

/** The final result of all aggregator methods is building the Bio Index. All
  * outputs are to the dig-bio-index bucket in S3.
  */
class GenesStage(implicit context: Context) extends Stage {
  val genes = Input.Source.Dataset("genes/")

  /** Input sources. */
  override val sources: Seq[Input.Source] = Seq(genes)

  /** Rules for mapping input to outputs. */
  override val rules: PartialFunction[Input, Outputs] = {
    case genes() => Outputs.Named("genes")
  }

  /** Output to Job steps. */
  override def make(output: String): Job = {
    new Job(Job.PySpark(resourceUri("genes.py")))
  }
}
