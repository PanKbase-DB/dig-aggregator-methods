package org.broadinstitute.dig.aggregator.methods.bioindex

import org.broadinstitute.dig.aggregator.core._
import org.broadinstitute.dig.aws._
import org.broadinstitute.dig.aws.emr._

/** The final result of all aggregator methods is building the BioIndex. All
  * outputs are to the dig-bio-index bucket in S3.
  */
class GlobalEnrichmentStage(implicit context: Context) extends Stage {
  val enrichment = Input.Source.Success("out/gregor/enrichment/*/")
  val tissues    = Input.Source.Dataset("tissues/ontology/")

  /** Input sources. */
  override val sources: Seq[Input.Source] = Seq(enrichment, tissues)

  /** Rules for mapping input to outputs. */
  override val rules: PartialFunction[Input, Outputs] = {
    case _ => Outputs.Named("enrichment")
  }

  /** Output to Job steps. */
  override def make(output: String): Job = {
    new Job(Job.PySpark(resourceUri("globalEnrichment.py")))
  }
}