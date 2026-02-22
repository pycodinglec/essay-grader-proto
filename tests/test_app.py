"""app.py 비즈니스 로직 헬퍼 함수 테스트.

Streamlit UI 렌더링은 직접 테스트하지 않고,
추출된 비즈니스 로직 함수(run_ocr_and_identify, run_grading)를 테스트한다.
"""

from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# run_ocr_and_identify 테스트
# ---------------------------------------------------------------------------


class TestRunOcrAndIdentify:
    """run_ocr_and_identify 함수 테스트."""

    @patch("app.essay_splitter")
    @patch("app.submission")
    @patch("app.ocr")
    def test_returns_submissions_and_unidentified(self, mock_ocr, mock_sub, mock_splitter):
        """OCR 결과를 기반으로 제출물과 미식별 파일을 반환한다."""
        from app import run_ocr_and_identify

        mock_ocr.ocr_file.side_effect = [
            [{"학번": "10301", "이름": "홍길동", "에세이텍스트": "에세이 내용"}],
            [{"학번": "", "이름": "", "에세이텍스트": "식별불가 텍스트"}],
        ]
        mock_splitter.split_essays.side_effect = lambda x: x
        expected_subs = [{"학번": "10301", "이름": "홍길동", "에세이텍스트": "에세이 내용"}]
        expected_unid = ["unknown.png"]
        mock_sub.build_submissions.return_value = (expected_subs, expected_unid)

        files_data = [
            ("essay1.png", b"fake_png"),
            ("unknown.png", b"fake_png2"),
        ]

        subs, unid = run_ocr_and_identify(files_data)

        assert subs == expected_subs
        assert unid == expected_unid
        assert mock_ocr.ocr_file.call_count == 2
        mock_sub.build_submissions.assert_called_once()

    @patch("app.essay_splitter")
    @patch("app.submission")
    @patch("app.ocr")
    def test_builds_correct_file_ocr_results_structure(self, mock_ocr, mock_sub, mock_splitter):
        """ocr_file 결과를 (filename, [dict,...]) 형태로 essay_splitter에 전달한다."""
        from app import run_ocr_and_identify

        page1 = {"학번": "10305", "이름": "홍길동", "에세이텍스트": "페이지1"}
        page2 = {"학번": "", "이름": "", "에세이텍스트": "페이지2"}
        mock_ocr.ocr_file.side_effect = [
            [page1, page2],
        ]
        mock_splitter.split_essays.side_effect = lambda x: x
        mock_sub.build_submissions.return_value = ([], [])

        run_ocr_and_identify([("doc.pdf", b"fake_pdf")])

        call_args = mock_sub.build_submissions.call_args[0][0]
        assert len(call_args) == 1
        assert call_args[0][0] == "doc.pdf"
        assert call_args[0][1] == [page1, page2]

    @patch("app.essay_splitter")
    @patch("app.submission")
    @patch("app.ocr")
    def test_empty_file_list(self, mock_ocr, mock_sub, mock_splitter):
        """빈 파일 리스트 입력 시 빈 결과를 반환한다."""
        from app import run_ocr_and_identify

        mock_splitter.split_essays.side_effect = lambda x: x
        mock_sub.build_submissions.return_value = ([], [])

        subs, unid = run_ocr_and_identify([])

        assert subs == []
        assert unid == []
        mock_ocr.ocr_file.assert_not_called()

    @patch("app.essay_splitter")
    @patch("app.submission")
    @patch("app.ocr")
    def test_multiple_files_ocr_called_for_each(self, mock_ocr, mock_sub, mock_splitter):
        """여러 파일에 대해 각각 ocr_file을 호출한다."""
        from app import run_ocr_and_identify

        mock_ocr.ocr_file.side_effect = [
            [{"학번": "", "이름": "", "에세이텍스트": "t1"}],
            [{"학번": "", "이름": "", "에세이텍스트": "t2"}],
            [{"학번": "", "이름": "", "에세이텍스트": "t3"}],
        ]
        mock_splitter.split_essays.side_effect = lambda x: x
        mock_sub.build_submissions.return_value = ([], [])

        files = [
            ("a.png", b"a"),
            ("b.jpg", b"b"),
            ("c.pdf", b"c"),
        ]
        run_ocr_and_identify(files)

        assert mock_ocr.ocr_file.call_count == 3
        call_args_list = mock_sub.build_submissions.call_args[0][0]
        assert len(call_args_list) == 3

    @patch("app.submission")
    @patch("app.essay_splitter")
    @patch("app.ocr")
    def test_calls_essay_splitter_before_build_submissions(self, mock_ocr, mock_splitter, mock_sub):
        """OCR 결과를 essay_splitter.split_essays에 전달한다."""
        from app import run_ocr_and_identify

        page = {"학번": "10301", "이름": "홍길동", "에세이텍스트": "내용"}
        mock_ocr.ocr_file.return_value = [page]
        mock_splitter.split_essays.return_value = [("essay1.png", [page])]
        mock_sub.build_submissions.return_value = ([{"학번": "10301"}], [])

        run_ocr_and_identify([("essay1.png", b"fake")])

        mock_splitter.split_essays.assert_called_once()
        call_args = mock_splitter.split_essays.call_args[0][0]
        assert len(call_args) == 1
        assert call_args[0][0] == "essay1.png"

    @patch("app.submission")
    @patch("app.essay_splitter")
    @patch("app.ocr")
    def test_passes_split_results_to_build_submissions(self, mock_ocr, mock_splitter, mock_sub):
        """essay_splitter 결과가 build_submissions에 전달된다."""
        from app import run_ocr_and_identify

        page1 = {"학번": "10301", "이름": "홍길동", "에세이텍스트": "내용1"}
        page2 = {"학번": "10302", "이름": "김영희", "에세이텍스트": "내용2"}
        mock_ocr.ocr_file.return_value = [page1, page2]
        split_output = [("scan.pdf#1", [page1]), ("scan.pdf#2", [page2])]
        mock_splitter.split_essays.return_value = split_output
        mock_sub.build_submissions.return_value = ([], [])

        run_ocr_and_identify([("scan.pdf", b"fake")])

        mock_sub.build_submissions.assert_called_once_with(split_output)


# ---------------------------------------------------------------------------
# run_grading 테스트
# ---------------------------------------------------------------------------


class TestRunGrading:
    """run_grading 함수 테스트."""

    @patch("app.report")
    @patch("app.evaluator")
    def test_normal_flow_all_succeed(self, mock_eval, mock_report):
        """모든 제출물이 성공적으로 채점되면 report_bytes와 None 에러를 반환한다."""
        from app import run_grading

        eval_result = {
            "scores": [{"번호": 1, "점수": 10}],
            "feedback": "잘 작성했습니다.",
        }
        mock_eval.evaluate_essay.return_value = eval_result
        mock_report.build_report.return_value = b"fake_xlsx_data"

        submissions = [
            {"학번": "10301", "이름": "홍길동", "에세이텍스트": "에세이1"},
            {"학번": "10302", "이름": "김영희", "에세이텍스트": "에세이2"},
        ]
        rubric_text = "번호 | 채점기준 | 배점\n1 | 논리성 | 10"

        graded, report_bytes, error_msg = run_grading(submissions, rubric_text)

        assert len(graded) == 2
        assert report_bytes == b"fake_xlsx_data"
        assert error_msg is None
        assert mock_eval.evaluate_essay.call_count == 2

    @patch("app.report")
    @patch("app.evaluator")
    def test_graded_submissions_contain_evaluation(self, mock_eval, mock_report):
        """채점 결과가 제출물 dict에 '평가결과' 키로 추가된다."""
        from app import run_grading

        eval_result = {
            "scores": [{"번호": 1, "점수": 8}],
            "feedback": "좋습니다.",
        }
        mock_eval.evaluate_essay.return_value = eval_result
        mock_report.build_report.return_value = b"xlsx"

        submissions = [
            {"학번": "10301", "이름": "홍길동", "에세이텍스트": "에세이1"},
        ]

        graded, _, _ = run_grading(submissions, "rubric")

        assert graded[0]["평가결과"] == eval_result

    @patch("app.report")
    @patch("app.evaluator")
    def test_mid_process_error_returns_partial_results(
        self, mock_eval, mock_report
    ):
        """채점 중 에러 발생 시 부분 결과와 에러 메시지를 반환한다."""
        from app import run_grading

        eval_result = {
            "scores": [{"번호": 1, "점수": 10}],
            "feedback": "좋음",
        }
        mock_eval.evaluate_essay.side_effect = [
            eval_result,
            Exception("API 오류"),
        ]
        mock_report.build_report.return_value = b"partial_xlsx"

        submissions = [
            {"학번": "10301", "이름": "홍길동", "에세이텍스트": "에세이1"},
            {"학번": "10302", "이름": "김영희", "에세이텍스트": "에세이2"},
        ]

        graded, report_bytes, error_msg = run_grading(submissions, "rubric")

        assert len(graded) == 1
        assert report_bytes == b"partial_xlsx"
        assert error_msg is not None
        assert "2번째" in error_msg

    @patch("app.report")
    @patch("app.evaluator")
    def test_error_message_format(self, mock_eval, mock_report):
        """에러 메시지가 올바른 한국어 형식으로 작성된다."""
        from app import run_grading

        mock_eval.evaluate_essay.side_effect = Exception("timeout")
        mock_report.build_report.return_value = b"empty_xlsx"

        submissions = [
            {"학번": "10301", "이름": "홍길동", "에세이텍스트": "에세이1"},
        ]

        _, _, error_msg = run_grading(submissions, "rubric")

        assert "1번째 작업물에서 에러가 발생" in error_msg
        assert "작업을 지속할 수 없습니다" in error_msg
        assert "다운로드" in error_msg
        assert "페이지를 새로 고치면 작업이 소실됩니다" in error_msg

    @patch("app.report")
    @patch("app.evaluator")
    def test_evaluate_returns_none_treated_as_error(
        self, mock_eval, mock_report
    ):
        """evaluate_essay가 None을 반환하면 에러로 처리한다."""
        from app import run_grading

        mock_eval.evaluate_essay.side_effect = [
            {"scores": [{"번호": 1, "점수": 5}], "feedback": "OK"},
            None,
        ]
        mock_report.build_report.return_value = b"partial"

        submissions = [
            {"학번": "10301", "이름": "홍길동", "에세이텍스트": "에세이1"},
            {"학번": "10302", "이름": "김영희", "에세이텍스트": "에세이2"},
        ]

        graded, _, error_msg = run_grading(submissions, "rubric")

        assert len(graded) == 1
        assert error_msg is not None
        assert "2번째" in error_msg

    @patch("app.report")
    @patch("app.evaluator")
    def test_report_build_called_with_graded_submissions(
        self, mock_eval, mock_report
    ):
        """report.build_report가 채점된 제출물 리스트를 인자로 호출된다."""
        from app import run_grading

        eval_result = {
            "scores": [{"번호": 1, "점수": 10}],
            "feedback": "피드백",
        }
        mock_eval.evaluate_essay.return_value = eval_result
        mock_report.build_report.return_value = b"xlsx"

        submissions = [
            {"학번": "10301", "이름": "홍길동", "에세이텍스트": "에세이1"},
        ]

        run_grading(submissions, "rubric")

        call_args = mock_report.build_report.call_args[0][0]
        assert len(call_args) == 1
        assert call_args[0]["평가결과"] == eval_result

    @patch("app.report")
    @patch("app.evaluator")
    def test_empty_submissions_returns_empty(self, mock_eval, mock_report):
        """빈 제출물 리스트에 대해 빈 결과를 반환한다."""
        from app import run_grading

        mock_report.build_report.return_value = b"empty"

        graded, report_bytes, error_msg = run_grading([], "rubric")

        assert graded == []
        assert report_bytes == b"empty"
        assert error_msg is None
        mock_eval.evaluate_essay.assert_not_called()

    @patch("app.report")
    @patch("app.evaluator")
    def test_error_on_third_of_five_submissions(self, mock_eval, mock_report):
        """5개 제출물 중 3번째에서 에러 발생 시 2개만 채점 결과에 포함."""
        from app import run_grading

        eval_result = {
            "scores": [{"번호": 1, "점수": 10}],
            "feedback": "좋음",
        }
        mock_eval.evaluate_essay.side_effect = [
            eval_result,
            eval_result,
            Exception("3rd error"),
        ]
        mock_report.build_report.return_value = b"partial"

        submissions = [
            {"학번": f"1030{i}", "이름": f"학생{i}", "에세이텍스트": f"에세이{i}"}
            for i in range(1, 6)
        ]

        graded, _, error_msg = run_grading(submissions, "rubric")

        assert len(graded) == 2
        assert "3번째" in error_msg


# ---------------------------------------------------------------------------
# progress_message 테스트
# ---------------------------------------------------------------------------


class TestProgressMessage:
    """진행률 메시지 포맷 테스트."""

    def test_format_progress_message(self):
        """진행률 메시지가 올바른 형식으로 생성된다."""
        from app import format_progress_message

        msg = format_progress_message(total=10, current=3)
        assert msg == "10개의 제출물 중 3번째 문서를 채점중..."

    def test_format_progress_message_first(self):
        """첫 번째 문서의 진행률 메시지."""
        from app import format_progress_message

        msg = format_progress_message(total=5, current=1)
        assert msg == "5개의 제출물 중 1번째 문서를 채점중..."

    def test_format_progress_message_last(self):
        """마지막 문서의 진행률 메시지."""
        from app import format_progress_message

        msg = format_progress_message(total=3, current=3)
        assert msg == "3개의 제출물 중 3번째 문서를 채점중..."


# ---------------------------------------------------------------------------
# build_error_message 테스트
# ---------------------------------------------------------------------------


class TestBuildErrorMessage:
    """에러 메시지 생성 함수 테스트."""

    def test_error_message_contains_index(self):
        """에러 메시지에 작업물 번호가 포함된다."""
        from app import build_error_message

        msg = build_error_message(k=5)
        assert "5번째 작업물에서 에러가 발생" in msg

    def test_error_message_contains_required_phrases(self):
        """에러 메시지에 필요한 안내 문구가 모두 포함된다."""
        from app import build_error_message

        msg = build_error_message(k=1)
        assert "작업을 지속할 수 없습니다" in msg
        assert "다운로드" in msg
        assert "페이지를 새로 고치면 작업이 소실됩니다" in msg
