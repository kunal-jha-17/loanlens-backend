from __future__ import annotations

from pathlib import Path

import yaml


class CfnSafeLoader(yaml.SafeLoader):
    pass


def _unknown_tag(loader, tag_suffix, node):
    if isinstance(node, yaml.ScalarNode):
        return loader.construct_scalar(node)
    if isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    return loader.construct_mapping(node)


CfnSafeLoader.add_multi_constructor("!", _unknown_tag)


def test_template_has_required_resources_and_handlers() -> None:
    template = yaml.load(Path("template.yaml").read_text(encoding="utf-8"), Loader=CfnSafeLoader)
    resources = template["Resources"]

    assert "LoanLensUploadBucket" in resources
    assert "LoanLensRulesTable" in resources
    assert "LoanLensDlaSnapshotTable" in resources
    assert "LoanLensInteractionLogsTable" in resources
    assert resources["LoanLensProcessFunction"]["Properties"]["Handler"] == "functions.loanlens_process_handler.lambda_handler"
    assert resources["LoanLensExtractionFunction"]["Properties"]["Handler"] == "functions.extraction_handler.lambda_handler"
