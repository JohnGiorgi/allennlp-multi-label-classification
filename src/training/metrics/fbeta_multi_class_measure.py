from typing import List, Optional, Union

import torch
from allennlp.common.checks import ConfigurationError
from allennlp.training.metrics import FBetaMeasure, Metric
from overrides import overrides


@Metric.register("fbeta_multi_label")
class FBetaMeasureMultiLabel(FBetaMeasure):
    """Compute precision, recall, F-measure and support for each class.

    The precision is the ratio `tp / (tp + fp)` where `tp` is the number of
    true positives and `fp` the number of false positives. The precision is
    intuitively the ability of the classifier not to label as positive a sample
    that is negative.

    The recall is the ratio `tp / (tp + fn)` where `tp` is the number of
    true positives and `fn` the number of false negatives. The recall is
    intuitively the ability of the classifier to find all the positive samples.

    The F-beta score can be interpreted as a weighted harmonic mean of
    the precision and recall, where an F-beta score reaches its best
    value at 1 and worst score at 0.

    If we have precision and recall, the F-beta score is simply:
    `F-beta = (1 + beta ** 2) * precision * recall / (beta ** 2 * precision + recall)`

    The F-beta score weights recall more than precision by a factor of
    `beta`. `beta == 1.0` means recall and precision are equally important.

    The support is the number of occurrences of each class in `y_true`.

    # Parameters

    beta : `float`, optional (default = 1.0)
        The strength of recall versus precision in the F-score.

    average : string, [None (default), 'micro', 'macro', 'weighted']
        If `None`, the scores for each class are returned. Otherwise, this
        determines the type of averaging performed on the data:

        `'micro'`:
            Calculate metrics globally by counting the total true positives,
            false negatives and false positives.
        `'macro'`:
            Calculate metrics for each label, and find their unweighted mean.
            This does not take label imbalance into account.
        `'weighted'`:
            Calculate metrics for each label, and find their average weighted
            by support (the number of true instances for each label). This
            alters 'macro' to account for label imbalance; it can result in an
            F-score that is not between precision and recall.

    labels: `list`, optional
        The set of labels to include and their order if `average is None`.
        Labels present in the data can be excluded, for example to calculate a
        multi-class average ignoring a majority negative class. Labels not present
        in the data will result in 0 components in a macro or weighted average.

    """

    def __init__(
        self,
        beta: float = 1.0,
        average: str = None,
        labels: List[int] = None,
        threshold: float = 0.5,
    ) -> None:
        average_options = {None, "micro", "macro", "weighted"}
        if average not in average_options:
            raise ConfigurationError(f"`average` has to be one of {average_options}.")
        if beta <= 0:
            raise ConfigurationError("`beta` should be >0 in the F-beta score.")
        if labels is not None and len(labels) == 0:
            raise ConfigurationError("`labels` cannot be an empty list.")
        self._beta = beta
        self._average = average
        self._labels = labels
        self._threshold = threshold

        # statistics
        # the total number of true positive instances under each class
        # Shape: (num_classes, )
        self._true_positive_sum: Union[None, torch.Tensor] = None
        # the total number of instances
        # Shape: (num_classes, )
        self._total_sum: Union[None, torch.Tensor] = None
        # the total number of instances under each _predicted_ class,
        # including true positives and false positives
        # Shape: (num_classes, )
        self._pred_sum: Union[None, torch.Tensor] = None
        # the total number of instances under each _true_ class,
        # including true positives and false negatives
        # Shape: (num_classes, )
        self._true_sum: Union[None, torch.Tensor] = None

    @overrides
    def __call__(
        self,
        predictions: torch.Tensor,
        gold_labels: torch.Tensor,
        mask: Optional[torch.BoolTensor] = None,
    ):
        """
        # Parameters

        predictions : `torch.Tensor`, required.
            A tensor of predictions of shape (batch_size, ..., num_classes).
        gold_labels : `torch.Tensor`, required.
            A tensor of integer class label of shape (batch_size, ...). It must be the same
            shape as the `predictions` tensor without the `num_classes` dimension.
        mask : `torch.BoolTensor`, optional (default = None).
            A masking tensor the same size as `gold_labels`.
        """
        predictions, gold_labels, mask = self.detach_tensors(predictions, gold_labels, mask)

        # Calculate true_positive_sum, true_negative_sum, pred_sum, true_sum
        num_classes = predictions.size(-1)
        if (gold_labels >= num_classes).any():
            raise ConfigurationError(
                "A gold label passed to FBetaMeasure contains "
                f"an id >= {num_classes}, the number of classes."
            )

        # It means we call this metric at the first time
        # when `self._true_positive_sum` is None.
        if self._true_positive_sum is None:
            self._true_positive_sum = torch.zeros(num_classes, device=predictions.device)
            self._true_sum = torch.zeros(num_classes, device=predictions.device)
            self._pred_sum = torch.zeros(num_classes, device=predictions.device)
            self._total_sum = torch.zeros(num_classes, device=predictions.device)

        if mask is None:
            mask = torch.ones_like(gold_labels).bool()
        gold_labels = gold_labels.float()

        threshold_predictions = predictions
        threshold_predictions[predictions >= self._threshold] = 1
        threshold_predictions[predictions < self._threshold] = 0

        true_positives = (gold_labels == threshold_predictions) & mask
        true_positive_sum = true_positives.sum(dim=0).float()
        pred_sum = threshold_predictions.sum(dim=0).float()
        true_sum = gold_labels.sum(dim=0).float()
        total_sum = torch.ones_like(true_sum).float()

        self._true_positive_sum += true_positive_sum
        self._pred_sum += pred_sum
        self._true_sum += true_sum
        self._total_sum += total_sum
