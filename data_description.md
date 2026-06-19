# Data Description

This file explains the main columns used in the college football betting market efficiency project.

## Columns

### season

The year/season when the game was played.

### week

The week of the college football season.

### home_team

The team playing the game at their home location.

### away_team

The team playing away from home.

### home_conference

The conference that the home team belongs to.

### away_conference

The conference that the away team belongs to.

### home_score

The number of points scored by the home team.

### away_score

The number of points scored by the away team.

### spread

The betting market prediction for the expected point difference in the game. A negative spread means the home team is expected to win, while a positive spread means the home team is the underdog.

### actual_margin

The actual difference between the home team's score and the away team's score.

### home_covered

Shows whether the home team covered the spread. This means the home team performed better than the betting market predicted.

### spread_error

The difference between the actual margin and the predicted spread. It measures how accurate the betting prediction was.

### over_under

The predicted combined total score of both teams set by the betting market.

### total_points

The actual combined score of both teams.

### over_hit

Shows whether the actual total points were higher than the predicted over/under value.

### spread_group

A category created to group games based on whether the home team was a favorite or an underdog.
