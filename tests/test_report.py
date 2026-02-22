"""report 모듈 단위 테스트."""

from io import BytesIO

import openpyxl

from src.report import assign_work_numbers, build_report, generate_report_bytes


def _make_submission(student_id: str, name: str, feedback: str) -> dict:
    """테스트용 제출물 dict를 생성하는 헬퍼."""
    return {
        "학번": student_id,
        "이름": name,
        "evaluation": {
            "scores": [{"번호": 1, "점수": 5}],
            "feedback": feedback,
        },
    }


class TestAssignWorkNumbers:
    """assign_work_numbers 함수 테스트."""

    def test_single_student_single_work(self):
        """학생 1명, 작품 1개일 때 작품번호 1이 부여된다."""
        submissions = [_make_submission("10305", "홍길동", "잘 썼습니다.")]

        result = assign_work_numbers(submissions)

        assert len(result) == 1
        assert result[0]["작품번호"] == 1

    def test_single_student_multiple_works(self):
        """학생 1명, 작품 여러 개일 때 순서대로 1, 2, 3이 부여된다."""
        submissions = [
            _make_submission("10305", "홍길동", "피드백A"),
            _make_submission("10305", "홍길동", "피드백B"),
            _make_submission("10305", "홍길동", "피드백C"),
        ]

        result = assign_work_numbers(submissions)

        assert [r["작품번호"] for r in result] == [1, 2, 3]

    def test_multiple_students_independent_numbering(self):
        """서로 다른 학생은 각각 독립적으로 작품번호가 부여된다."""
        submissions = [
            _make_submission("10305", "홍길동", "피드백1"),
            _make_submission("20101", "김철수", "피드백2"),
            _make_submission("10305", "홍길동", "피드백3"),
            _make_submission("20101", "김철수", "피드백4"),
        ]

        result = assign_work_numbers(submissions)

        hong = [r for r in result if r["학번"] == "10305"]
        kim = [r for r in result if r["학번"] == "20101"]
        assert [h["작품번호"] for h in hong] == [1, 2]
        assert [k["작품번호"] for k in kim] == [1, 2]

    def test_preserves_appearance_order(self):
        """원본 리스트의 등장 순서에 따라 작품번호가 부여된다."""
        submissions = [
            _make_submission("10305", "홍길동", "첫번째"),
            _make_submission("10305", "홍길동", "두번째"),
        ]

        result = assign_work_numbers(submissions)

        assert result[0]["피드백"] == "첫번째"
        assert result[0]["작품번호"] == 1
        assert result[1]["피드백"] == "두번째"
        assert result[1]["작품번호"] == 2

    def test_feedback_extracted_from_evaluation(self):
        """evaluation dict에서 feedback 값이 피드백 키로 추출된다."""
        submissions = [_make_submission("10305", "홍길동", "구체적 피드백 내용")]

        result = assign_work_numbers(submissions)

        assert result[0]["피드백"] == "구체적 피드백 내용"

    def test_output_keys(self):
        """반환되는 dict에 학번, 이름, 작품번호, 피드백 키만 존재한다."""
        submissions = [_make_submission("10305", "홍길동", "피드백")]

        result = assign_work_numbers(submissions)

        assert set(result[0].keys()) == {"학번", "이름", "작품번호", "피드백"}

    def test_empty_input(self):
        """빈 리스트 입력 시 빈 리스트를 반환한다."""
        result = assign_work_numbers([])

        assert result == []

    def test_student_name_preserved(self):
        """학번과 이름이 원본 값 그대로 유지된다."""
        submissions = [_make_submission("30210", "이영희", "피드백")]

        result = assign_work_numbers(submissions)

        assert result[0]["학번"] == "30210"
        assert result[0]["이름"] == "이영희"


class TestGenerateReportBytes:
    """generate_report_bytes 함수 테스트."""

    def _load_workbook(self, xlsx_bytes: bytes) -> openpyxl.Workbook:
        """바이트에서 워크북을 로드하는 헬퍼."""
        return openpyxl.load_workbook(BytesIO(xlsx_bytes))

    def test_returns_bytes(self):
        """반환값이 bytes 타입이다."""
        data = [{"학번": "10305", "이름": "홍길동", "작품번호": 1, "피드백": "좋음"}]

        result = generate_report_bytes(data)

        assert isinstance(result, bytes)

    def test_valid_xlsx(self):
        """반환된 bytes가 유효한 xlsx 파일이다."""
        data = [{"학번": "10305", "이름": "홍길동", "작품번호": 1, "피드백": "좋음"}]

        result = generate_report_bytes(data)
        wb = self._load_workbook(result)

        assert wb.active is not None

    def test_correct_headers(self):
        """첫 행에 학번, 이름, 작품번호, 피드백 헤더가 있다."""
        data = [{"학번": "10305", "이름": "홍길동", "작품번호": 1, "피드백": "좋음"}]

        result = generate_report_bytes(data)
        ws = self._load_workbook(result).active

        headers = [ws.cell(row=1, column=c).value for c in range(1, 5)]
        assert headers == ["학번", "이름", "작품번호", "피드백"]

    def test_correct_data_rows(self):
        """데이터 행이 올바르게 기록된다."""
        data = [
            {"학번": "10305", "이름": "홍길동", "작품번호": 1, "피드백": "피드백A"},
        ]

        result = generate_report_bytes(data)
        ws = self._load_workbook(result).active

        row = [ws.cell(row=2, column=c).value for c in range(1, 5)]
        assert row == ["10305", "홍길동", 1, "피드백A"]

    def test_sorted_by_student_id_then_work_number(self):
        """행이 학번 오름차순, 그 다음 작품번호 오름차순으로 정렬된다."""
        data = [
            {"학번": "20101", "이름": "김철수", "작품번호": 2, "피드백": "B"},
            {"학번": "10305", "이름": "홍길동", "작품번호": 1, "피드백": "A"},
            {"학번": "20101", "이름": "김철수", "작품번호": 1, "피드백": "C"},
            {"학번": "10305", "이름": "홍길동", "작품번호": 2, "피드백": "D"},
        ]

        result = generate_report_bytes(data)
        ws = self._load_workbook(result).active

        rows = []
        for r in range(2, 6):
            rows.append([ws.cell(row=r, column=c).value for c in range(1, 5)])

        assert rows[0][0] == "10305"
        assert rows[0][2] == 1
        assert rows[1][0] == "10305"
        assert rows[1][2] == 2
        assert rows[2][0] == "20101"
        assert rows[2][2] == 1
        assert rows[3][0] == "20101"
        assert rows[3][2] == 2

    def test_empty_data_returns_headers_only(self):
        """빈 데이터 시 헤더만 있는 xlsx를 반환한다."""
        result = generate_report_bytes([])
        ws = self._load_workbook(result).active

        headers = [ws.cell(row=1, column=c).value for c in range(1, 5)]
        assert headers == ["학번", "이름", "작품번호", "피드백"]
        assert ws.cell(row=2, column=1).value is None

    def test_multiple_rows_count(self):
        """데이터 행 수가 입력과 일치한다 (헤더 제외)."""
        data = [
            {"학번": "10305", "이름": "홍길동", "작품번호": 1, "피드백": "A"},
            {"학번": "10305", "이름": "홍길동", "작품번호": 2, "피드백": "B"},
            {"학번": "20101", "이름": "김철수", "작품번호": 1, "피드백": "C"},
        ]

        result = generate_report_bytes(data)
        ws = self._load_workbook(result).active

        assert ws.max_row == 4  # 1 header + 3 data rows


class TestBuildReport:
    """build_report 함수 통합 테스트."""

    def test_returns_bytes(self):
        """build_report는 bytes를 반환한다."""
        submissions = [_make_submission("10305", "홍길동", "좋음")]

        result = build_report(submissions)

        assert isinstance(result, bytes)

    def test_end_to_end_single_student(self):
        """단일 학생 제출물에 대해 올바른 xlsx를 생성한다."""
        submissions = [_make_submission("10305", "홍길동", "우수한 에세이")]

        result = build_report(submissions)
        ws = openpyxl.load_workbook(BytesIO(result)).active

        headers = [ws.cell(row=1, column=c).value for c in range(1, 5)]
        assert headers == ["학번", "이름", "작품번호", "피드백"]

        row = [ws.cell(row=2, column=c).value for c in range(1, 5)]
        assert row == ["10305", "홍길동", 1, "우수한 에세이"]

    def test_end_to_end_multiple_students_sorted(self):
        """다수 학생 제출물이 학번/작품번호 기준 정렬된 xlsx를 생성한다."""
        submissions = [
            _make_submission("20101", "김철수", "피드백1"),
            _make_submission("10305", "홍길동", "피드백2"),
            _make_submission("20101", "김철수", "피드백3"),
        ]

        result = build_report(submissions)
        ws = openpyxl.load_workbook(BytesIO(result)).active

        # 10305 먼저, 그 다음 20101
        assert ws.cell(row=2, column=1).value == "10305"
        assert ws.cell(row=2, column=3).value == 1
        assert ws.cell(row=3, column=1).value == "20101"
        assert ws.cell(row=3, column=3).value == 1
        assert ws.cell(row=4, column=1).value == "20101"
        assert ws.cell(row=4, column=3).value == 2

    def test_empty_submissions(self):
        """빈 제출물 리스트에 대해 헤더만 있는 xlsx를 반환한다."""
        result = build_report([])
        ws = openpyxl.load_workbook(BytesIO(result)).active

        headers = [ws.cell(row=1, column=c).value for c in range(1, 5)]
        assert headers == ["학번", "이름", "작품번호", "피드백"]
        assert ws.cell(row=2, column=1).value is None
