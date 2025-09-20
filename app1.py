import streamlit as st
import pandas as pd
import time

# ---------------- Page Setup ----------------
st.set_page_config(page_title="학급 회장 투표", page_icon="🗳️", layout="centered")
st.title("🗳️ 학급 회장 투표")
st.divider()

# ---------------- Session State Initialization ----------------
for key, default in {
    "votes": {}, "candidate_list": [],
    "total_voters": 0, "voter_count": 0,
    "abstain_count": 0, "results_revealed": False
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ---------------- Helper Function ----------------
def reset_poll():
    st.session_state.votes = {}
    st.session_state.candidate_list = []
    st.session_state.total_voters = 0
    st.session_state.voter_count = 0
    st.session_state.abstain_count = 0
    st.session_state.results_revealed = False

# ---------------- Tabs ----------------
tab1, tab2, tab3 = st.tabs(["⚙️ 설정", "🗳️ 투표", "📊 결과"])

# ---------------- Page 1: Setup ----------------
with tab1:
    st.subheader("투표 설정")
    candidates_input = st.text_input("후보자 이름들을 쉼표(,)로 구분하세요", "철수, 영희, 민수")
    total_voters_input = st.number_input("총 투표자 수", min_value=1, value=5, step=1)

    if st.button("설정 저장"):
        candidate_list = [c.strip() for c in candidates_input.split(",") if c.strip()]
        if candidate_list:
            st.session_state.candidate_list = candidate_list
            st.session_state.votes = {name: 0 for name in candidate_list}
            st.session_state.total_voters = total_voters_input
            st.session_state.voter_count = 0
            st.session_state.abstain_count = 0
            st.success("✅ 투표 설정이 저장되었습니다!")

# ---------------- Page 2: Voting ----------------
with tab2:
    if not st.session_state.candidate_list:
        st.info("먼저 후보자와 투표자 수를 설정하세요.")
    elif st.session_state.voter_count < st.session_state.total_voters:
        st.subheader("🗳️ 투표 진행 중")
        options = st.session_state.candidate_list + ["기권"]
        choice = st.radio("당신의 선택은?", options)

        if st.button("투표하기"):
            if choice == "기권":
                st.session_state.abstain_count += 1
            else:
                st.session_state.votes[choice] += 1

            st.session_state.voter_count += 1
            st.success(f"투표 완료! ({st.session_state.voter_count}/{st.session_state.total_voters})")

        # Progress bar
        st.progress(st.session_state.voter_count / st.session_state.total_voters)
        st.write(f"투표 현황: {st.session_state.voter_count}/{st.session_state.total_voters}")

    else:
        st.success("✅ 모든 투표가 완료되었습니다. 결과 탭에서 확인하세요!")

# ---------------- Page 3: Results ----------------
with tab3:
    if not st.session_state.candidate_list:
        st.info("먼저 투표를 설정하고 진행하세요.")
    elif st.session_state.voter_count < st.session_state.total_voters:
        st.warning("⏳ 아직 모든 투표가 완료되지 않았습니다.")
    else:
        if not st.session_state.results_revealed:
            placeholder = st.empty()
            placeholder.info("📊 득표를 집계 중입니다...")
            time.sleep(2)
            placeholder.empty()
            st.session_state.results_revealed = True

        # Count all votes including abstentions for majority calculation
        candidate_votes = {k: v for k, v in st.session_state.votes.items()}
        majority_needed = st.session_state.total_voters / 2

        max_votes = max(candidate_votes.values()) if candidate_votes else 0
        winners = [name for name, count in candidate_votes.items() if count == max_votes]

        # Results logic
        if len(winners) > 1:
            st.warning("⚠️ 무승부! 동점 후보로 재투표 필요")
            st.snow()
        elif max_votes <= majority_needed and len(candidate_votes) > 1:
            st.warning("⚠️ 과반수 미달! 상위 두 후보로 재투표 필요")
        else:
            st.header("🎉 최종 승자 🎉")
            st.success(winners[0])
            st.balloons()

        # DataFrame for charts
        df = pd.DataFrame({
            "후보자": list(candidate_votes.keys()) + ["기권"],
            "득표수": list(candidate_votes.values()) + [st.session_state.abstain_count]
        })

        st.subheader("📊 투표 결과 (막대 그래프)")
        st.bar_chart(df.set_index("후보자"))

        st.subheader("📜 투표 요약")
        for name, count in candidate_votes.items():
            st.write(f"✅ {name}: {count}표")
        st.write(f"✅ 기권: {st.session_state.abstain_count}표")

        turnout = (st.session_state.voter_count / st.session_state.total_voters) * 100
        st.info(f"📈 투표율: {turnout:.1f}%")

        # Export CSV
        if st.download_button(
            "📥 결과 CSV 다운로드",
            df.to_csv(index=False).encode("utf-8"),
            "poll_results.csv",
            "text/csv"
        ):
            st.success("CSV 파일이 다운로드되었습니다.")