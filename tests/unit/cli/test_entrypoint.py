import re
import sys
from pathlib import Path
from typing import Callable
from unittest.mock import patch

import pytest

from ytdl_sub.cli.entrypoint import _download_subscriptions_from_yaml_files
from ytdl_sub.cli.entrypoint import main
from ytdl_sub.subscriptions.subscription import Subscription
from ytdl_sub.utils.exceptions import ExperimentalFeatureNotEnabled

####################################################################################################
# SHARED FIXTURES


####################################################################################################
# PERSIST LOGS FIXTURES + TESTS


@pytest.mark.parametrize("dry_run", [True, False])
@pytest.mark.parametrize("mock_success_output", [True, False])
@pytest.mark.parametrize("keep_successful_logs", [True, False])
def test_subscription_logs_write_to_file(
    persist_logs_directory: str,
    persist_logs_config_factory: Callable,
    mock_subscription_download_factory: Callable,
    music_video_subscription_path: Path,
    dry_run: bool,
    mock_success_output: bool,
    keep_successful_logs: bool,
):
    num_subscriptions = 2
    config = persist_logs_config_factory(keep_successful_logs=keep_successful_logs)
    subscription_paths = [str(music_video_subscription_path)] * num_subscriptions

    with patch.object(
        Subscription,
        "download",
        new=mock_subscription_download_factory(mock_success_output=mock_success_output),
        # mock datetime to be an index to be able to run instantly
    ), patch("ytdl_sub.cli.entrypoint._log_time", side_effect=[str(idx) for idx in range(10)]):
        try:
            _download_subscriptions_from_yaml_files(
                config=config,
                subscription_paths=subscription_paths,
                update_with_info_json=False,
                dry_run=dry_run,
            )
        except ValueError:
            assert not mock_success_output

    log_directory_files = list(Path(persist_logs_directory).rglob("*"))

    # If dry run or success but success logging disabled, expect 0 log files
    if dry_run or (mock_success_output and not keep_successful_logs):
        assert len(log_directory_files) == 0
        return
    # If not success, expect 2 log files for both sub errors
    elif not mock_success_output:
        assert len(log_directory_files) == 2
        for log_path in log_directory_files:
            assert bool(re.match(r"\d\.john_smith\.error\.log", log_path.name))
            with open(log_path, "r", encoding="utf-8") as log_file:
                assert log_file.readlines()[-1] == (
                    f"Please upload the error log file '{str(log_path)}' and make a Github issue "
                    f"at https://github.com/jmbannon/ytdl-sub/issues with your config and "
                    f"command/subscription yaml file to reproduce. Thanks for trying ytdl-sub!\n"
                )
    # If success and success logging, expect 3 log files
    else:
        assert len(log_directory_files) == num_subscriptions
        for log_file_path in log_directory_files:
            assert bool(re.match(r"\d\.john_smith\.success\.log", log_file_path.name))
            with open(log_file_path, "r", encoding="utf-8") as log_file:
                assert (
                    log_file.readlines()[-1]
                    == "[ytdl-sub] name=john_smith success=True dry_run=False\n"
                )


def test_update_with_info_json_requires_experimental_flag(
    music_video_config_path: Path,
    music_video_subscription_path: Path,
) -> None:
    with patch.object(
        sys,
        "argv",
        [
            "ytdl-sub",
            "--config",
            str(music_video_config_path),
            "sub",
            str(music_video_subscription_path),
            "--update-with-info-json",
        ],
    ), pytest.raises(ExperimentalFeatureNotEnabled):
        _ = main()