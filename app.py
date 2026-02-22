"""서논술형 에세이 자동 채점 웹 애플리케이션.

Streamlit 기반 UI로, 에세이 업로드 -> OCR -> 제출물 식별 ->
채점기준 검증 -> 3-LLM 평가 -> report.xlsx 생성 파이프라인을 제공한다.
"""

from collections.abc import Callable

import streamlit as st

from src import auth, config, essay_splitter, evaluator, file_handler, ocr, report, rubric, submission

st.set_page_config(page_title="에세이 자동 채점", layout="wide")

SPLITTER_PROMPT_DESCRIPTION = (
    "다음은 에세이 분할에 사용되는 프롬프트의 구조입니다.\n\n"
    "prompt injection 방어 문구 + 페이지별 OCR 결과(학번/이름/텍스트 100자) "
    "+ JSON 배열 응답 요청"
)


def show_prompts_section() -> None:
    """사용 중인 LLM 프롬프트를 expander로 표시한다."""
    with st.expander("사용 중인 프롬프트 확인"):
        st.subheader("OCR 프롬프트")
        st.code(ocr.OCR_PROMPT, language=None)
        st.subheader("에세이 분할 프롬프트")
        st.text(SPLITTER_PROMPT_DESCRIPTION)
        st.code(essay_splitter.build_splitter_prompt([
            {"학번": "10305", "이름": "홍길동", "에세이텍스트": "(예시)"}
        ]), language=None)
        st.subheader("채점 프롬프트")
        st.code(evaluator.EVALUATION_PROMPT_TEMPLATE, language=None)


def init_session_state() -> None:
    """세션 상태 키를 기본값으로 초기화한다."""
    defaults = {
        "authenticated": False,
        "uploaded_files_data": [],
        "submissions": [],
        "unidentified": [],
        "rubric_data": [],
        "rubric_text": "",
        "grading_complete": False,
        "report_bytes": b"",
        "grading_error": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def format_progress_message(total: int, current: int) -> str:
    """채점 진행률 메시지를 생성한다.

    Args:
        total: 전체 제출물 수.
        current: 현재 채점 중인 문서 번호 (1-based).

    Returns:
        "n개의 제출물 중 k번째 문서를 채점중..." 형식 문자열.
    """
    return f"{total}개의 제출물 중 {current}번째 문서를 채점중..."


def format_ocr_progress_message(total: int, current: int) -> str:
    """OCR 진행률 메시지를 생성한다.

    Args:
        total: 전체 파일 수.
        current: 현재 OCR 중인 파일 번호 (1-based).

    Returns:
        "N개 파일 중 K번째 파일 OCR 중..." 형식 문자열.
    """
    return f"{total}개 파일 중 {current}번째 파일 OCR 중..."


def build_error_message(k: int) -> str:
    """채점 중 에러 발생 시 표시할 한국어 메시지를 생성한다.

    Args:
        k: 에러가 발생한 작업물 번호 (1-based).

    Returns:
        에러 안내 메시지 문자열.
    """
    return (
        f"{k}번째 작업물에서 에러가 발생하여 작업을 지속할 수 없습니다. "
        "다음 버튼을 눌러 현재까지 진행된 파일을 다운로드하십시오. "
        "페이지를 새로 고치면 작업이 소실됩니다."
    )


def run_ocr_and_identify(
    files_data: list[tuple[str, bytes]],
    on_progress: Callable[[int, int], None] | None = None,
) -> tuple[list[dict], list[str]]:
    """파일 목록에 대해 OCR을 수행하고 제출물을 식별한다.

    Args:
        files_data: (파일명, 바이트) 튜플 리스트.
        on_progress: 각 파일 OCR 시작 전 호출되는 콜백(current, total).

    Returns:
        (식별된_제출물_리스트, 미식별_파일명_리스트) 튜플.
    """
    file_ocr_results: list[tuple[str, list[dict]]] = []
    total = len(files_data)
    for i, (filename, file_bytes) in enumerate(files_data, start=1):
        if on_progress is not None:
            on_progress(i, total)
        ocr_results = ocr.ocr_file(filename, file_bytes)
        file_ocr_results.append((filename, ocr_results))
    split_results = essay_splitter.split_essays(file_ocr_results)
    return submission.build_submissions(split_results)


def run_grading(
    submissions: list[dict],
    rubric_text: str,
    on_progress: Callable[[int, int], None] | None = None,
) -> tuple[list[dict], bytes, str | None]:
    """제출물을 3-LLM으로 채점하고 리포트를 생성한다.

    Args:
        submissions: 제출물 dict 리스트.
        rubric_text: 채점기준표 텍스트.
        on_progress: 각 에세이 채점 시작 전 호출되는 콜백(current, total).

    Returns:
        (채점완료_제출물, report_bytes, 에러메시지_또는_None) 튜플.
    """
    graded: list[dict] = []
    error_msg: str | None = None
    total = len(submissions)

    for i, sub in enumerate(submissions, start=1):
        if on_progress is not None:
            on_progress(i, total)
        try:
            result = evaluator.evaluate_essay(
                sub["에세이텍스트"], rubric_text
            )
            if result is None:
                error_msg = build_error_message(i)
                break
            graded_sub = {**sub, "평가결과": result}
            graded.append(graded_sub)
        except Exception:  # noqa: BLE001
            error_msg = build_error_message(i)
            break

    report_bytes = report.build_report(graded)
    return graded, report_bytes, error_msg


def show_login_page() -> None:
    """패스워드 입력 UI를 표시하고 인증을 처리한다."""
    st.title("에세이 자동 채점 시스템")
    st.subheader("로그인")

    password = st.text_input(
        "패스워드를 입력하세요", type="password", key="password_input"
    )
    if st.button("로그인", key="login_btn"):
        if auth.verify_password(password, config.PASSWORD_HASH):
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("패스워드가 올바르지 않습니다.")


def _process_essay_uploads(uploaded_files) -> list[tuple[str, bytes]]:
    """업로드된 에세이 파일들을 처리하여 (파일명, 바이트) 리스트로 변환한다.

    Args:
        uploaded_files: Streamlit 업로드 파일 객체 리스트.

    Returns:
        처리된 (파일명, 바이트) 튜플 리스트.
    """
    all_files: list[tuple[str, bytes]] = []
    for uf in uploaded_files:
        try:
            processed = file_handler.process_uploaded_file(
                uf.name, uf.getvalue()
            )
            all_files.extend(processed)
        except ValueError as e:
            st.error(f"파일 처리 오류 ({uf.name}): {e}")
    return all_files


def show_upload_section() -> None:
    """에세이 파일 업로드 UI를 표시한다."""
    st.subheader("2. 에세이 파일 업로드")
    uploaded_files = st.file_uploader(
        "에세이 파일을 업로드하세요 (PDF/이미지/ZIP)",
        type=["pdf", "png", "jpg", "jpeg", "zip"],
        accept_multiple_files=True,
        key="essay_uploader",
    )

    if uploaded_files and st.button("에세이 파일 처리", key="process_essays"):
        all_files = _process_essay_uploads(uploaded_files)
        if all_files:
            st.session_state.uploaded_files_data = all_files
            st.session_state.submissions = []
            st.session_state.unidentified = []
            st.success(f"{len(all_files)}개의 파일이 처리되었습니다.")
            _run_ocr_with_progress()


def _run_ocr_with_progress() -> None:
    """OCR 및 제출물 식별을 진행률 바와 함께 실행한다."""
    files_data = st.session_state.uploaded_files_data
    progress_bar = st.progress(0)
    status_text = st.empty()

    def _on_progress(current: int, total: int) -> None:
        status_text.text(format_ocr_progress_message(total, current))
        progress_bar.progress((current - 1) / total if total > 0 else 0)

    subs, unid = run_ocr_and_identify(files_data, on_progress=_on_progress)
    st.session_state.submissions = subs
    st.session_state.unidentified = unid
    progress_bar.progress(1.0)
    status_text.text("OCR 완료!")


def show_identification_results(
    submissions_list: list[dict], unidentified: list[str]
) -> None:
    """제출물 식별 결과를 표시한다.

    Args:
        submissions_list: 식별된 제출물 dict 리스트.
        unidentified: 미식별 파일명 리스트.
    """
    st.subheader("3. 제출물 식별 결과")

    if submissions_list:
        display_text = submission.format_submissions_for_display(
            submissions_list
        )
        st.text(display_text)
        st.info(f"총 {len(submissions_list)}개의 제출물이 식별되었습니다.")

    if unidentified:
        st.warning(
            f"다음 파일에서 학생 정보를 식별할 수 없습니다: "
            f"{', '.join(unidentified)}\n\n"
            "문제가 있는 파일을 제외한 후 페이지를 새로 고쳐 "
            "다시 시작해 주세요."
        )


def _validate_and_parse_rubric(rubric_file) -> None:
    """채점기준표 파일을 검증하고 파싱하여 세션 상태에 저장한다."""
    file_bytes = rubric_file.getvalue()
    valid, msg = rubric.validate_rubric(file_bytes)

    if not valid:
        st.error(f"채점기준표 오류: {msg}")
        return

    parsed = rubric.parse_rubric(file_bytes)
    st.session_state.rubric_data = parsed
    st.session_state.rubric_text = rubric.format_rubric_for_display(parsed)
    st.success("채점기준표가 검증되었습니다.")


def show_rubric_section() -> None:
    """채점기준표 업로드 및 검증 UI를 표시한다."""
    st.subheader("1. 채점기준표 업로드")
    rubric_file = st.file_uploader(
        "채점기준표 xlsx 파일을 업로드하세요",
        type=["xlsx"],
        key="rubric_uploader",
    )

    if rubric_file and st.button("채점기준표 확인", key="validate_rubric"):
        _validate_and_parse_rubric(rubric_file)

    if st.session_state.rubric_data:
        display = rubric.format_rubric_for_display(
            st.session_state.rubric_data
        )
        st.text(display)


def _execute_grading() -> None:
    """채점 프로세스를 실행하고 진행률을 표시한다."""
    subs = st.session_state.submissions
    rubric_text = st.session_state.rubric_text
    progress_bar = st.progress(0)
    status_text = st.empty()

    def _on_progress(current: int, total: int) -> None:
        status_text.text(format_progress_message(total, current))
        progress_bar.progress((current - 1) / total)

    graded, report_bytes, error_msg = run_grading(
        subs, rubric_text, on_progress=_on_progress
    )

    st.session_state.report_bytes = report_bytes
    st.session_state.grading_error = error_msg
    st.session_state.grading_complete = True

    if error_msg:
        st.error(error_msg)
    else:
        progress_bar.progress(1.0)
        status_text.text("채점이 완료되었습니다!")


def show_grading_section() -> None:
    """채점 시작 버튼 및 진행률 UI를 표시한다."""
    st.subheader("4. 채점 실행")

    can_start = (
        st.session_state.submissions
        and st.session_state.rubric_data
        and not st.session_state.grading_complete
    )

    if can_start and st.button("채점 시작", key="start_grading"):
        _execute_grading()


def show_download_section(
    report_bytes: bytes, error_msg: str | None
) -> None:
    """리포트 다운로드 버튼을 표시한다.

    Args:
        report_bytes: report.xlsx 바이트 데이터.
        error_msg: 에러 메시지 (없으면 None).
    """
    st.subheader("5. 결과 다운로드")

    if error_msg:
        st.error(error_msg)

    if report_bytes:
        st.download_button(
            label="report.xlsx 다운로드",
            data=report_bytes,
            file_name="report.xlsx",
            mime="application/vnd.openxmlformats-officedocument"
            ".spreadsheetml.sheet",
            key="download_report",
        )


def main() -> None:
    """앱 메인 진입점: 세션 상태 초기화 및 파이프라인 흐름 제어."""
    init_session_state()

    if not st.session_state.authenticated:
        show_login_page()
        return

    st.title("에세이 자동 채점 시스템")

    show_prompts_section()

    show_rubric_section()

    if st.session_state.rubric_data:
        show_upload_section()

    if st.session_state.submissions:
        show_identification_results(
            st.session_state.submissions,
            st.session_state.unidentified,
        )

    if st.session_state.rubric_data and st.session_state.submissions:
        show_grading_section()

    if st.session_state.grading_complete:
        show_download_section(
            st.session_state.report_bytes,
            st.session_state.grading_error,
        )


main()
