# Augmentation-Tuning-via-BO

### Introduction
This Github repository contains only the code of the developed methodology for extracting visual quality inspection knowledge and transforming it into a usable format, as shown in the flow chart below (Figure 4.1). The output of this methodology can then be used to warm start any BO implementation as described in the bachelor thesis. This repository does not include the implementation of the Bayesian Optimization (BO) of the data augmentation policies, as it contains work of other students and researchers at Fraunhofer IPT that is not intended to be published for this bachelor thesis.

### Expert Knowledge Extraction - Flow Chart
First, the expert is queried to evaluate individual augmentations, either by removing an augmentation operation from the search space entirely, or by modifying only the strength by specifying a range of strengths.
Latin Hypercube Sampling (LHS) is then used to sample uniformly from this pruned search space.
The second query presents the sampled sub-policy points to the expert and lets them decide which ones to use as starting points for the warm started BO.

![alt text](flow-chart.png)

---

### Steps 1-3: First Expert Query and Search Space Pruning
The first query includes the min-max values mentioned above to limit the range of strengths from which the BO algorithm can choose, while the invalid checkbox completely removes the selected augmentation. The slider simulates the individual augmentation strength by applying it to 5 different images to experiment with the effects of augmentation strength.

![alt text](search-space-shaping.png)

---

### Steps 4-5: Second Expert Query and LHS Sampling
The second query presents the final augmented images to the expert. As explained in the bachelor thesis, the applied augmentations are not the individual ones, but the LHS-sampled augmentation sub-policies. Thus, each image was augmented by augmentation 1 with the probability and strength chosen by BO, and then augmented by augmentation 2 with it's respective probability and strength.

![alt text](initial-points.png)