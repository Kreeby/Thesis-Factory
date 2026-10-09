from thesis_factory.domain.primary_source import (
    PrimarySourceCandidate,
)
from thesis_factory.domain.proposal_verification import (
    ProposalVerificationTask,
    VerificationLane,
)


def deterministic_dataset_candidates(
    task: ProposalVerificationTask,
) -> tuple[
    PrimarySourceCandidate,
    ...,
]:
    if (
        task.lane
        != VerificationLane.DATASET_PRIMARY
    ):
        return ()

    text = " ".join(
        (
            task.requirement.question,
            task.requirement.why_needed,
        )
    ).casefold()

    if (
        "heloc" in text
        or "fico" in text
    ):
        return (
            PrimarySourceCandidate(
                url=(
                    "https://community.fico.com/s/"
                    "explainable-machine-learning-challenge"
                ),
                title=(
                    "FICO Explainable Machine Learning "
                    "Challenge"
                ),
            ),
            PrimarySourceCandidate(
                url=(
                    "https://www.fico.com/en/newsroom/"
                    "fico-announces-winners-of-inaugural-"
                    "xml-challenge"
                ),
                title=(
                    "FICO Announces Winners of "
                    "Inaugural xML Challenge"
                ),
            ),
            PrimarySourceCandidate(
                url=(
                    "https://investors.fico.com/"
                    "news-releases/news-release-details/"
                    "fico-announces-winners-inaugural-"
                    "xml-challenge"
                ),
                title=(
                    "FICO investor release for "
                    "xML Challenge"
                ),
            ),
        )

    if (
        "german credit" in text
        or "statlog" in text
    ):
        return (
            PrimarySourceCandidate(
                url=(
                    "https://archive.ics.uci.edu/"
                    "dataset/144/"
                    "statlog+german+credit+data"
                ),
                title=(
                    "UCI Statlog German Credit Data"
                ),
            ),
            PrimarySourceCandidate(
                url=(
                    "https://archive.ics.uci.edu/"
                    "dataset/573/"
                    "south+german+credit+update"
                ),
                title=(
                    "UCI South German Credit update"
                ),
            ),
        )

    if (
        "home credit" in text
        or "kaggle" in text
    ):
        return (
            PrimarySourceCandidate(
                url=(
                    "https://www.kaggle.com/"
                    "competitions/"
                    "home-credit-default-risk/data"
                ),
                title=(
                    "Home Credit Default Risk — Data"
                ),
            ),
            PrimarySourceCandidate(
                url=(
                    "https://www.kaggle.com/"
                    "competitions/"
                    "home-credit-default-risk/"
                    "overview/evaluation"
                ),
                title=(
                    "Home Credit Default Risk — "
                    "Evaluation"
                ),
            ),
            PrimarySourceCandidate(
                url=(
                    "https://www.kaggle.com/"
                    "competitions/"
                    "home-credit-default-risk/rules"
                ),
                title=(
                    "Home Credit Default Risk — Rules"
                ),
            ),
        )

    return ()
