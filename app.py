import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import os
# Import libraries used for creating the web app, handling data, and making visualizations

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CFB Betting Market Efficiency",
    page_icon="🏈",
    layout="wide"
)

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    # Load the cleaned college football dataset
    df = pd.read_csv("cfb_cleaned_data.csv")

    def spread_group(spread):
        if spread <= -14:
            return "Big Home Favorite"
        elif spread < 0:
            return "Small Home Favorite"
        elif spread == 0:
            return "Even Game"
        elif spread < 14:
            return "Small Home Underdog"
        else:
            return "Big Home Underdog"

    def conference_tier(conf):
        if conf in ["SEC", "Big Ten"]:
            return conf
        elif conf in ["ACC", "Big 12", "Pac-12"]:
            return "Other Power 5"
        elif pd.isna(conf):
            return "Unknown"
        else:
            return "Group of 5 / Ind"

    # create new columns used later for analysis and graphs
    df["spread_group"] = df["spread"].apply(spread_group)
    df["conf_tier"] = df["home_conference"].apply(conference_tier)
    return df

df = load_data()

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🏈 CFB Betting Market Efficiency")
st.markdown("**JEM207 — Data Processing in Python**")
st.markdown(
    "Explore whether the college football betting market is efficient — "
    "do spreads accurately predict outcomes, and is there a home team bias?"
)

st.divider()

# ── Introduction ──────────────────────────────────────────────────────────────
with st.expander("📖 About this project — Why does this matter?", expanded=True):
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("""
### College Football Betting is a Serious Financial Market

College football (CFB) is one of the **largest sports betting markets in the United States**.
According to the American Gaming Association, Americans legally wagered over **$100 billion on sports in 2023**,
with college football accounting for a significant share — particularly during the regular season and bowl games.

Unlike casual gambling, sports betting markets function similarly to **financial prediction markets**.
Oddsmakers at major sportsbooks (like DraftKings, FanDuel, and Caesars) employ teams of analysts and
use sophisticated models to set the **point spread** — the predicted margin of victory for the favored team.

### What is the Point Spread?

The spread is designed so that betting on either team is equally attractive.
In an **efficient market**, the spread should be an unbiased predictor of the actual game outcome —
meaning home teams should cover the spread roughly **50% of the time**.

If we find that home teams consistently cover more (or less) than 50%, it suggests the market has a
**systematic bias** — an inefficiency that could, in theory, be exploited by bettors.

### Why College Football Specifically?

- CFB has **hundreds of games per season** across many conferences, providing rich data
- Unlike the NFL, CFB teams vary **enormously in quality**, making accurate pricing harder
- The **SEC and Big Ten** are the most-watched and most-bet conferences — we test whether
  higher public attention leads to more accurate (efficient) pricing
- This mirrors real financial market research into whether **more liquid, widely-followed assets
  are priced more efficiently** than obscure ones

### Our Approach

We use **4 seasons of historical betting data (2020–2023)** from the College Football Data API
to test market efficiency across conferences, weeks, and spread sizes.
        """)

    with col2:
        st.markdown("### 📊 Key Facts")
        st.info("**$100B+**\nLegally wagered on sports in the US in 2023")
        st.success("**50%**\nExpected home cover rate in an efficient market")
        st.warning("**~62%**\nActual home cover rate we found in CFB")
        st.error("**12 pts**\nAverage market underestimation of home teams")
        st.markdown("""
---
**Data source:**
[College Football Data API](https://collegefootballdata.com)

**Seasons covered:**
2020, 2021, 2022, 2023

**Games analyzed:**
~2,600 regular season games
        """)

st.divider()

# ── Sidebar filters ───────────────────────────────────────────────────────────
st.sidebar.header("🔎 Filters")

all_seasons = sorted(df["season"].unique().tolist())
selected_seasons = st.sidebar.multiselect(
    "Season", all_seasons, default=all_seasons
)

all_conferences = sorted(df["home_conference"].dropna().unique().tolist())
selected_conferences = st.sidebar.multiselect(
    "Conference", all_conferences, default=all_conferences
)

all_weeks = sorted(df["week"].unique().tolist())
selected_weeks = st.sidebar.slider(
    "Week range",
    min_value=int(min(all_weeks)),
    max_value=int(max(all_weeks)),
    value=(int(min(all_weeks)), int(max(all_weeks)))
)

spread_min, spread_max = float(df["spread"].min()), float(df["spread"].max())
selected_spread = st.sidebar.slider(
    "Spread range",
    min_value=spread_min,
    max_value=spread_max,
    value=(spread_min, spread_max),
    step=0.5
)

# ── Apply filters ─────────────────────────────────────────────────────────────
# apply user selected filters to update the dataset shown in the app
filtered = df[
    (df["season"].isin(selected_seasons)) &
    (df["home_conference"].isin(selected_conferences)) &
    (df["week"] >= selected_weeks[0]) &
    (df["week"] <= selected_weeks[1]) &
    (df["spread"] >= selected_spread[0]) &
    (df["spread"] <= selected_spread[1])
]

if filtered.empty:
    st.warning("No games match the selected filters. Try adjusting the sidebar.")
    st.stop()

# ── KPI metrics ───────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

# calculate summary statistics used to evaluate betting market efficiency
cover_rate = filtered["home_covered"].mean() * 100
over_rate = filtered["over_hit"].mean() * 100
avg_spread_error = filtered["spread_error"].mean()
total_games = len(filtered)

col1.metric("📊 Games Analyzed", f"{total_games:,}")
col2.metric("🏠 Home Cover Rate", f"{cover_rate:.1f}%", delta=f"{cover_rate - 50:.1f}% vs 50%")
col3.metric("⬆️ Over Hit Rate", f"{over_rate:.1f}%", delta=f"{over_rate - 50:.1f}% vs 50%")
col4.metric("📉 Avg Spread Error", f"{avg_spread_error:.2f} pts")

st.divider()

# ── Section 1: Overall analysis ───────────────────────────────────────────────
st.subheader("📈 Overall Market Efficiency")

col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(6, 4))
    cover_counts = filtered["home_covered"].value_counts()
    cover_counts.index = ["Covered" if x else "Not Covered" for x in cover_counts.index]
    ax.bar(cover_counts.index, cover_counts.values, color=["salmon", "skyblue"])
    ax.set_title("Home Team Cover vs Not Cover")
    ax.set_ylabel("Number of Games")
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    st.pyplot(fig)
    plt.close()

with col2:
    fig, ax = plt.subplots(figsize=(6, 4))
    filtered["spread_error"].plot(kind="hist", bins=30, color="skyblue", edgecolor="black", ax=ax)
    ax.axvline(0, color="red", linestyle="--", label="0 (perfect prediction)")
    ax.set_title("Distribution of Spread Errors")
    ax.set_xlabel("Spread Error (Actual - Predicted)")
    ax.set_ylabel("Number of Games")
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    st.pyplot(fig)
    plt.close()

st.divider()

# ── Section 2: By season ──────────────────────────────────────────────────────
st.subheader("📅 Cover Rate by Season")

# calculate home cover rate for each season
season_cover = filtered.groupby("season")["home_covered"].mean() * 100

fig, ax = plt.subplots(figsize=(8, 4))
ax.bar(season_cover.index.astype(str), season_cover.values, color="steelblue")
ax.axhline(50, color="red", linestyle="--", label="50% (efficient market)")
ax.set_title("Home Cover Rate by Season")
ax.set_xlabel("Season")
ax.set_ylabel("Cover Rate (%)")
ax.legend()
ax.grid(axis="y", linestyle="--", alpha=0.7)
st.pyplot(fig)
plt.close()

st.divider()

# ── Section 3: By week ────────────────────────────────────────────────────────
st.subheader("📆 Cover Rate by Week")

# analyze how home cover rates change throughout the season
week_cover = filtered.groupby("week")["home_covered"].mean() * 100

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(week_cover.index, week_cover.values, marker="o", color="steelblue", linewidth=2)
ax.axhline(50, color="red", linestyle="--", label="50% (efficient market)")
ax.set_title("Home Cover Rate by Week")
ax.set_xlabel("Week")
ax.set_ylabel("Cover Rate (%)")
ax.legend()
ax.grid(alpha=0.3)
st.pyplot(fig)
plt.close()

st.divider()

# ── Section 4: By spread group ────────────────────────────────────────────────
st.subheader("📊 Cover Rate by Spread Group")

group_order = ["Big Home Favorite", "Small Home Favorite", "Even Game", "Small Home Underdog", "Big Home Underdog"]
# compare cover rates between different spread categories
group_cover = filtered.groupby("spread_group")["home_covered"].mean() * 100
group_cover = group_cover.reindex(group_order).dropna()

fig, ax = plt.subplots(figsize=(9, 4))
ax.bar(group_cover.index, group_cover.values, color="teal")
ax.axhline(50, color="red", linestyle="--", label="50% (efficient market)")
ax.set_title("Home Cover Rate by Spread Group")
ax.set_ylabel("Cover Rate (%)")
ax.legend()
ax.grid(axis="y", linestyle="--", alpha=0.7)
plt.xticks(rotation=15)
plt.tight_layout()
st.pyplot(fig)
plt.close()

st.divider()

# ── Section 5: Conference analysis ────────────────────────────────────────────
st.subheader("🏟️ Conference Analysis")

tab1, tab2 = st.tabs(["All Conferences", "SEC vs Big Ten"])

with tab1:
    df_conf = filtered.dropna(subset=["home_conference"])
    if df_conf.empty:
        st.warning("No conference data available for the current filters.")
    else:
        conf_stats = df_conf.groupby("home_conference").agg(
            games=("home_covered", "count"),
            cover_rate=("home_covered", "mean"),
            avg_spread_error=("spread_error", "mean")
        ).reset_index()
        conf_stats["cover_rate"] = conf_stats["cover_rate"] * 100
        conf_stats = conf_stats[conf_stats["games"] >= 10].sort_values("cover_rate", ascending=True)

        col1, col2 = st.columns(2)

        with col1:
            fig, ax = plt.subplots(figsize=(6, max(4, len(conf_stats) * 0.4)))
            ax.barh(conf_stats["home_conference"], conf_stats["cover_rate"], color="steelblue")
            ax.axvline(50, color="red", linestyle="--", label="50% (efficient market)")
            ax.set_title("Home Cover Rate by Conference")
            ax.set_xlabel("Cover Rate (%)")
            ax.legend()
            ax.grid(axis="x", linestyle="--", alpha=0.7)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()

        with col2:
            fig, ax = plt.subplots(figsize=(6, max(4, len(conf_stats) * 0.4)))
            conf_err = conf_stats.sort_values("avg_spread_error", ascending=True)
            ax.barh(conf_err["home_conference"], conf_err["avg_spread_error"], color="teal")
            ax.axvline(0, color="red", linestyle="--", label="0 (no bias)")
            ax.set_title("Avg Spread Error by Conference")
            ax.set_xlabel("Avg Spread Error")
            ax.legend()
            ax.grid(axis="x", linestyle="--", alpha=0.7)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()

with tab2:
    sec_bigten = filtered[filtered["home_conference"].isin(["SEC", "Big Ten"])]

    if sec_bigten.empty:
        st.warning("No SEC or Big Ten data available for the current filters.")
    else:
        tier_stats = filtered[filtered["conf_tier"] != "Unknown"].groupby("conf_tier").agg(
            games=("home_covered", "count"),
            cover_rate=("home_covered", "mean"),
            avg_spread_error=("spread_error", "mean")
        ).reset_index()
        tier_stats["cover_rate"] = tier_stats["cover_rate"] * 100
        tier_stats = tier_stats.sort_values("cover_rate", ascending=False)

        col1, col2 = st.columns(2)

        with col1:
            fig, ax = plt.subplots(figsize=(6, 4))
            colors = {"SEC": "#003087", "Big Ten": "#CC0000", "Other Power 5": "steelblue", "Group of 5 / Ind": "gray"}
            bar_colors = [colors.get(t, "gray") for t in tier_stats["conf_tier"]]
            ax.bar(tier_stats["conf_tier"], tier_stats["cover_rate"], color=bar_colors)
            ax.axhline(50, color="red", linestyle="--", label="50% (efficient market)")
            ax.set_title("Cover Rate: SEC & Big Ten vs Others")
            ax.set_ylabel("Cover Rate (%)")
            ax.legend()
            ax.grid(axis="y", linestyle="--", alpha=0.7)
            plt.xticks(rotation=15)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()

        with col2:
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.bar(tier_stats["conf_tier"], tier_stats["avg_spread_error"], color=bar_colors)
            ax.axhline(0, color="red", linestyle="--", label="0 (no bias)")
            ax.set_title("Avg Spread Error: SEC & Big Ten vs Others")
            ax.set_ylabel("Avg Spread Error")
            ax.legend()
            ax.grid(axis="y", linestyle="--", alpha=0.7)
            plt.xticks(rotation=15)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()

        st.markdown("#### Season-by-Season: SEC vs Big Ten")
        season_conf = sec_bigten.groupby(["season", "home_conference"]).agg(
            cover_rate=("home_covered", "mean"),
            avg_spread_error=("spread_error", "mean")
        ).reset_index()
        season_conf["cover_rate"] = season_conf["cover_rate"] * 100

        sec = season_conf[season_conf["home_conference"] == "SEC"]
        big10 = season_conf[season_conf["home_conference"] == "Big Ten"]

        col1, col2 = st.columns(2)

        with col1:
            fig, ax = plt.subplots(figsize=(6, 4))
            if not sec.empty:
                ax.plot(sec["season"], sec["cover_rate"], marker="o", label="SEC", color="#003087", linewidth=2)
            if not big10.empty:
                ax.plot(big10["season"], big10["cover_rate"], marker="s", label="Big Ten", color="#CC0000", linewidth=2)
            ax.axhline(50, color="gray", linestyle="--", label="50% (efficient market)")
            ax.set_title("Cover Rate by Season")
            ax.set_xlabel("Season")
            ax.set_ylabel("Cover Rate (%)")
            ax.legend()
            ax.grid(alpha=0.3)
            st.pyplot(fig)
            plt.close()

        with col2:
            fig, ax = plt.subplots(figsize=(6, 4))
            if not sec.empty:
                ax.plot(sec["season"], sec["avg_spread_error"], marker="o", label="SEC", color="#003087", linewidth=2)
            if not big10.empty:
                ax.plot(big10["season"], big10["avg_spread_error"], marker="s", label="Big Ten", color="#CC0000", linewidth=2)
            ax.axhline(0, color="gray", linestyle="--", label="0 (no bias)")
            ax.set_title("Avg Spread Error by Season")
            ax.set_xlabel("Season")
            ax.set_ylabel("Avg Spread Error")
            ax.legend()
            ax.grid(alpha=0.3)
            st.pyplot(fig)
            plt.close()

st.divider()

# ── Section 6: Over/Under Analysis ───────────────────────────────────────────
st.subheader("⬆️ Over/Under Analysis")
st.markdown("Does the market accurately predict total points scored? An efficient market would expect the over to hit ~50% of the time.")

ou_filtered = filtered.dropna(subset=["over_under", "over_hit"])

if ou_filtered.empty:
    st.warning("No Over/Under data available for the current filters.")
else:
    col1, col2 = st.columns(2)

    with col1:
        ou_season = ou_filtered.groupby("season")["over_hit"].mean() * 100
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(ou_season.index.astype(str), ou_season.values, color="orange")
        ax.axhline(50, color="red", linestyle="--", label="50% (efficient market)")
        ax.set_title("Over Hit Rate by Season")
        ax.set_xlabel("Season")
        ax.set_ylabel("Over Hit Rate (%)")
        ax.legend()
        ax.grid(axis="y", linestyle="--", alpha=0.7)
        st.pyplot(fig)
        plt.close()

    with col2:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.scatter(ou_filtered["over_under"], ou_filtered["total_points"], alpha=0.3, color="orange")
        min_val = min(ou_filtered["over_under"].min(), ou_filtered["total_points"].min())
        max_val = max(ou_filtered["over_under"].max(), ou_filtered["total_points"].max())
        ax.plot([min_val, max_val], [min_val, max_val], color="red", linestyle="--", label="Perfect prediction")
        ax.set_title("Over/Under Line vs Total Points Scored")
        ax.set_xlabel("Over/Under Line")
        ax.set_ylabel("Actual Total Points")
        ax.legend()
        ax.grid(alpha=0.3)
        st.pyplot(fig)
        plt.close()

    col1, col2 = st.columns(2)
    with col1:
        ou_conf = ou_filtered.dropna(subset=["home_conference"])
        if not ou_conf.empty:
            ou_conf_stats = ou_conf.groupby("home_conference").agg(
                games=("over_hit", "count"),
                over_rate=("over_hit", "mean")
            ).reset_index()
            ou_conf_stats["over_rate"] = ou_conf_stats["over_rate"] * 100
            ou_conf_stats = ou_conf_stats[ou_conf_stats["games"] >= 10].sort_values("over_rate", ascending=True)

            fig, ax = plt.subplots(figsize=(6, max(4, len(ou_conf_stats) * 0.4)))
            ax.barh(ou_conf_stats["home_conference"], ou_conf_stats["over_rate"], color="orange")
            ax.axvline(50, color="red", linestyle="--", label="50% (efficient market)")
            ax.set_title("Over Hit Rate by Conference")
            ax.set_xlabel("Over Hit Rate (%)")
            ax.legend()
            ax.grid(axis="x", linestyle="--", alpha=0.7)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()

    with col2:
        st.markdown("#### Over/Under Summary")
        overall_ou = ou_filtered["over_hit"].mean() * 100
        avg_ou_line = ou_filtered["over_under"].mean()
        avg_total = ou_filtered["total_points"].mean()
        st.metric("Overall Over Hit Rate", f"{overall_ou:.1f}%", delta=f"{overall_ou - 50:.1f}% vs 50%")
        st.metric("Avg Over/Under Line", f"{avg_ou_line:.1f} pts")
        st.metric("Avg Actual Total Points", f"{avg_total:.1f} pts")
        st.markdown(
            "If the over hits significantly more or less than 50%, "
            "it suggests the market systematically misprices total scoring."
        )

st.divider()

# ── Section 7: Biggest Upsets ─────────────────────────────────────────────────
st.subheader("😱 Biggest Market Surprises")
st.markdown("Games where the betting market was most wrong — largest difference between predicted and actual margin.")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 🔴 Biggest Home Underdog Wins")
    st.caption("Games where home team massively outperformed the spread")
    upsets = filtered.nlargest(10, "spread_error")[[
        "season", "week", "home_team", "away_team",
        "spread", "actual_margin", "spread_error"
    ]].reset_index(drop=True)
    upsets.columns = ["Season", "Week", "Home", "Away", "Spread", "Actual Margin", "Spread Error"]
    upsets.index += 1
    st.dataframe(upsets, use_container_width=True)

with col2:
    st.markdown("#### 🔵 Biggest Home Favorite Flops")
    st.caption("Games where home team massively underperformed the spread")
    flops = filtered.nsmallest(10, "spread_error")[[
        "season", "week", "home_team", "away_team",
        "spread", "actual_margin", "spread_error"
    ]].reset_index(drop=True)
    flops.columns = ["Season", "Week", "Home", "Away", "Spread", "Actual Margin", "Spread Error"]
    flops.index += 1
    st.dataframe(flops, use_container_width=True)

st.divider()

# ── Section 8: Conclusion ─────────────────────────────────────────────────────
st.subheader("📝 Conclusion")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
### What Did We Find?

Our analysis of **~2,600 CFB games across 4 seasons (2020–2023)** reveals that the college football
betting market is **informative but not fully efficient**.

**Key findings:**

**1. Home team bias exists**
Home teams cover the spread ~62% of the time — well above the 50% expected in an efficient market.
This suggests oddsmakers systematically undervalue home field advantage in college football.

**2. The market is directionally accurate but imprecise**
The spread correctly identifies the stronger team in most cases, but the actual margin of victory
frequently deviates significantly from the predicted spread — average spread error is ~12 points.

**3. Conference matters**
The SEC and Big Ten — the most-watched and most-bet conferences — show different efficiency
patterns compared to smaller conferences. This mirrors findings in financial markets where
more liquid, widely-followed assets tend to be priced more accurately.

**4. The Over/Under is reasonably efficient**
Unlike the spread, the over/under hits close to 50% of the time across most seasons and
conferences, suggesting the market prices total scoring more accurately than game margins.

**5. Big favorites almost always cover**
When the home team is a large favorite (spread <= -14), cover rates approach ~99%.
This makes intuitive sense — large talent gaps are hard to overcome regardless of home field.

### Bottom Line
The CFB betting market behaves similarly to other financial prediction markets —
it incorporates publicly available information reasonably well, but systematic biases
(particularly around home field advantage) persist, suggesting the market is not fully efficient.
    """)

with col2:
    st.markdown("### 📊 Summary Stats")
    st.metric("Home Cover Rate", f"{filtered['home_covered'].mean()*100:.1f}%", delta=f"{filtered['home_covered'].mean()*100 - 50:.1f}% above efficient")
    ou_rate = filtered.dropna(subset=["over_hit"])["over_hit"].mean() * 100
    st.metric("Over Hit Rate", f"{ou_rate:.1f}%", delta=f"{ou_rate - 50:.1f}% vs 50%")
    st.metric("Avg Spread Error", f"{filtered['spread_error'].mean():.1f} pts")
    st.metric("Games Analyzed", f"{len(filtered):,}")
    st.markdown("---")
    st.markdown("""
**Project:** JEM207 — Data Processing in Python

**Data:** College Football Data API

**Seasons:** 2020–2023

**Method:** Historical spread vs actual margin comparison across conferences, weeks, and spread sizes
    """)

st.divider()

# ── Section 9: Raw data explorer ─────────────────────────────────────────────
st.subheader("🔍 Raw Data Explorer")

with st.expander("Click to view filtered data"):
    st.dataframe(
        filtered[[
            "season", "week", "home_team", "away_team", "home_conference",
            "home_score", "away_score", "spread", "actual_margin",
            "home_covered", "spread_error", "over_under", "over_hit"
        ]].reset_index(drop=True),
        use_container_width=True
    )
    st.caption(f"Showing {len(filtered):,} games")

st.divider()
st.caption("Data source: College Football Data API (collegefootballdata.com) | JEM207 Project")
